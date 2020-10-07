def clean_name(name: str) -> str:
    # if it's an int, do nothing
    try:
        int(name)
    except Exception:
        pass
    else:
        return name

    if name == "PSYCHIC_TYPE" or name == "PSYCHIC_M":
        return "Psychic"
    return " ".join(name.split("_")).title()
