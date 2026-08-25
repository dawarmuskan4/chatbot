from graph import graph


def run_query(user_query: str, document_path: str = None, has_document: bool = False):
    initial_state = {
        "user_query": user_query,
        "has_document": has_document,
        "document_path": document_path,
        "intent": None,
        "df": None,
        "schema_context": None,
        "code": None,
        "previous_error": None,
        "validation_result": None,
        "retry_count": 0,
        "execution_result": None,
        "final_answer": None,
    }
    result = graph.invoke(initial_state)
    return result["final_answer"]


if __name__ == "__main__":
    print("=== Step 1: query company_policy.pdf ===")
    answer1 = run_query(
        "What is the equipment stipend?",
        document_path="testfiles/company_policy.pdf",
        has_document=True,
    )
    print(answer1)

    print("\n=== Step 2: query project_notes.docx ===")
    answer2 = run_query(
        "Who owns the frontend redesign?",
        document_path="testfiles/project_notes.docx",
        has_document=True,
    )
    print(answer2)

    print("\n=== Step 3: query company_policy.pdf AGAIN (checks for cross-contamination) ===")
    answer3 = run_query(
        "What is the equipment stipend?",
        document_path="testfiles/company_policy.pdf",
        has_document=True,
    )
    print(answer3)