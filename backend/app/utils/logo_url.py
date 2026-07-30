def construir_url_logo(valor: str | None) -> str | None:
    if not valor:
        return None

    if valor.startswith(
        (
            "http://",
            "https://",
            "/carreras/logos/",
            "blob:",
            "data:",
        )
    ):
        return valor

    if valor.startswith("logos-carreras/"):
        return f"/carreras/logos/{valor}"

    return f"/carreras/logos/logos-carreras/{valor}"
