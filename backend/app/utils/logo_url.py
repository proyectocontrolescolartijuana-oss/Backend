def construir_url_logo(valor: str | None) -> str | None:
    if not valor:
        return None

    if valor.startswith(
        (
            "http://",
            "https://",
            "/static/",
            "/carreras/logos/",
            "blob:",
            "data:",
        )
    ):
        return valor

    if valor.startswith("logos-carreras/"):
        return f"http://localhost:8000/carreras/logos/{valor}"

    return f"http://localhost:8000/static/logos/{valor}"
