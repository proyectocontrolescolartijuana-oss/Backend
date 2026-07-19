def to_create_data(data):
    if hasattr(data, "model_dump"):
        return data.model_dump()

    return dict(data)


def to_update_data(data):
    if hasattr(data, "model_dump"):
        return data.model_dump(exclude_unset=True)

    return dict(data)
