def get_file_type(file_path: str) -> str:
    extension = file_path.split(".")[-1]
    if extension in ("xls", "xlsx"):
        file_type = "tabular"
    else:
        file_type = "text"
    
    return file_type