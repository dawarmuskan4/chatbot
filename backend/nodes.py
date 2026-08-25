## classify_intent, generate_pandas_code, validate_code, execute_code, format_answer - as graph nodes

import pandas as pd
from state import GraphState
from llm_client import ask_llm
from file_utils import get_file_type
from pypdf import PdfReader
from docx import Document

def classify_intent_node(state: GraphState) -> dict:
    system_prompt = """ 
    You are an intent classifier. Given a user query, respond with EXACTLY one word
    - 'direct' if the query is general knowledge, math, or doesn't need a document
    - 'document' if the query requires lookign at uploaded document data
    
    Respond with the only single word, nothing else
    """
    
    user_content = f"has_document: {state["has_document"]}\nquery:{state["user_query"]}"
    
    raw_response = ask_llm(user_content, system_prompt)
    cleaned = raw_response.strip().lower()
    
    return {"intent": cleaned}

def generate_pandas_code_node(state:GraphState) -> dict:
    system_prompt = """
    You are a pandas code generator. Given a user query and sample data from a DataFrame called `df`,
    write ONE line (or a few lines) of pandas code that answers the query.
    
    Rules:
    - Assume the DataFrame is already loaded as `df` — do not include import statements or df creation
    - Store the final answer in a variable called `result`
    - Output ONLY the code, no explanation, no markdown code fences, no commentary
    """
    
    if state["previous_error"]:  
        user_content = f"Schema/sample data:\n{state["schema_context"]}\n\nQuery: {state["user_query"]}\n\nPrevious Error:{state["previous_error"]}"
    else:
        user_content = f"Schema/sample data:\n{state["schema_context"]}\n\nQuery: {state["user_query"]}"
    
    raw_code = ask_llm(user_content, system_prompt)
    
    if raw_code.startswith("```python"):
        cleaned_code = raw_code.replace("```python", "").replace("```", "").strip()
    else:
        cleaned_code = raw_code
    
    return {
        "code":cleaned_code,
        "retry_count": state["retry_count"]+1
    }

def validate_code_node(state:GraphState) -> dict:
    system_prompt = """
    You are a code safety and correctness reviewer. You will be given pandas code and 
    sample data context. Check that:
    - The code only uses pandas operations on a DataFrame called `df`
    - It does not use file I/O, os, sys, subprocess, network calls, or exec/eval
    - It references column names that actually exist in the schema
    - It assigns a final answer to a variable called `result`
    
    Respond in EXACTLY this format, nothing else:
    "valid" if the code passes all checks
    "invalid: <short reason>" if it fails any check
    """
    
    user_content = f"Schema/sample data:\n{state["schema_context"]}\n\nCode to review:\n{state['code']}"
    
    raw_response = ask_llm(user_content, system_prompt)
    
    cleaned = raw_response.strip().lower()
    
    return {'validation_result': cleaned}

def route_after_validation_node(state: GraphState) -> str:
    if state["validation_result"] == "valid":
        return "execute"
    elif state["retry_count"] < 3:
        return "retry"
    else:
        return "fail"
    
def execute_code_node(state: GraphState) -> dict:
    namespace = {"df": state["df"], "pd": pd}
    exec(state['code'], namespace)
    output = namespace["result"]
    return {"execution_result": output}

def format_answer_node(state: GraphState) -> dict:
    system_prompt = "You are a helpful assistant. Given a user's question and the computed result, answer clearly and naturally in a sentence or two."
    user_content = f"Question: {state["user_query"]}\nComputed result:\n{state["execution_result"]}"
    result = ask_llm(user_content, system_prompt)
    return {"final_answer": result}

def failure_node(state: GraphState) -> dict:
    system_prompt = "You are a helpful assistant. Given a user's query and attempts to find the right answers have been exhausted, answer clearly and naturally in a single sentence or two regretting we couldn't find the answer"
    user_content = f"Question: {state['user_query']}\nReason we couldn't generate a valid answer:\n{state['validation_result']}"
    result = ask_llm(user_content, system_prompt)
    return {"final_answer": result}

def load_text_document_node(state: GraphState) -> dict:
    file_path = state["document_path"]
    extension = file_path.split(".")[-1]
    
    if extension == "txt":
        with open(file_path, "r") as f:
            text = f.read()
    
    elif extension == "pdf":
        reader = PdfReader(file_path)
        text = "\n".join(page.extract_text() for page in reader.pages)
    
    elif extension in ("doc", "docx"):
        
        doc = Document(file_path)
        text = "\n".join(para.text for para in doc.paragraphs)
    
    else:
        text = ""
    
    return {"schema_context": text}

def load_document_node(state: GraphState) -> dict:
    df = pd.read_excel(state["document_path"])
    
    sample_rows = df.head().to_string()
    schema_context = f"""
    Sample data from the document:
    {sample_rows}
    """
    
    return {
        "df": df,
        "schema_context": schema_context
    }

def route_by_file_type(state: GraphState) -> str:
    file_type = get_file_type(state["document_path"])
    return file_type

def text_qa_node(state: GraphState) -> dict:
    system_prompt = "You are a helpful assistant. Answer the user's question using only the information in the provided document text. If the answer isn't in the text, say so."
    
    user_content = f"Document text:\n{state['schema_context']}\n\nQuestion: {state['user_query']}"
    
    answer = ask_llm(user_content, system_prompt)
    
    return {"final_answer": answer}