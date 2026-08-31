## classify_intent, generate_pandas_code, validate_code, execute_code, format_answer - as graph nodes

import pandas as pd
from state import GraphState
from llm_client import ask_llm
from utils.file_utils import get_file_type
from pypdf import PdfReader
from docx import Document
from utils.rag_utils import chunk_text, embed_chunks, store_chunks, retrieve_relevant_chunks

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
    You are a pandas code generator. Given a user query and sample data from one or more
    sheets in an Excel file, write ONE line (or a few lines) of pandas code that answers the query.

    Rules:
    - The data is provided as a dict called `sheets`, where each key is a sheet name and each
      value is a DataFrame for that sheet (e.g. sheets["Sheet1"])
    - Reference the correct sheet by name based on the schema/sample data provided
    - Do not include import statements or any sheet-loading code
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
    sample data context from one or more Excel sheets. Check that:
    - The code only uses pandas operations on the `sheets` dict (accessing DataFrames via sheets["SheetName"])
    - It does not use file I/O, os, sys, subprocess, network calls, or exec/eval
    - It references sheet names and column names that actually exist in the schema
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
    namespace = {"sheets": state["df"], "pd": pd}
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
    
    elif extension == "json":
        import json
        with open(file_path, "r") as f:
            data = json.load(f)
        text = json.dumps(data, indent=2)
    else:
        text = ""
    
     # NEW: chunk, embed, store
    chunks = chunk_text(text)
    embeddings = embed_chunks(chunks)
    store_chunks(chunks, embeddings, doc_id=state["document_path"])
    
    return {"schema_context": text}

def load_document_node(state: GraphState) -> dict:
    sheets = pd.read_excel(state["document_path"], sheet_name=None)
    
    schema_parts = []
    for sheet_name, df in sheets.items():
        sample = find_sample_rows(df)
        if sample is not None:
            schema_parts.append(f"Sheet: {sheet_name}\n{sample.to_string()}")
        else:
            schema_parts.append(f"Sheet: {sheet_name}\n(No data found in first {50} rows)")
    
    schema_context = "\n\n".join(schema_parts)
    
    return {
        "df": sheets,
        "schema_context": schema_context
    }

def route_by_file_type(state: GraphState) -> str:
    file_type = get_file_type(state["document_path"])
    return file_type

def text_qa_node(state: GraphState) -> dict:
    system_prompt = "You are a helpful assistant. Answer the user's question using only the information in the provided document text. If the answer isn't in the text, say so."
    
    relevant_chunks = retrieve_relevant_chunks(state["user_query"], doc_id=state["document_path"], n_results=2)
    context_text = "\n\n".join(relevant_chunks) 

    history = state["conversation_history"]
    
    history_text = "\n".join(f"{msg['role']}: {msg['content']}" for msg in history)
    
    user_content = f"Conversation so far:\n{history_text}\n\nDocument text:\n{context_text}\n\nQuestion: {state['user_query']}"
    
    answer = ask_llm(user_content, system_prompt)
    
    return {"final_answer": answer}

def find_sample_rows(df, chunk_size: int = 5, max_rows: int = 50):
    for start in range(0, max_rows, chunk_size):
        chunk = df.iloc[start:start + chunk_size]
        
        # a chunk might be all-NaN (empty rows) — need to check if it's
        # genuinely empty before deciding to move to the next chunk.
        # pandas DataFrames have a method for dropping rows that are
        # entirely NaN — look up .dropna() and its "how" parameter
        non_empty = chunk.dropna(how="all")
        
        if not non_empty.empty:
            return chunk
    
    return None  # scanned up to max_rows, found nothing