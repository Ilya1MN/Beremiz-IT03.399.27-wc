def hello(request: dict) -> str:
    """
    Привилегированный системный вызов.
    """
    return " ".join(["Hello", request["name"]])