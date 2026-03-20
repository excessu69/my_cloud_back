import os
import uuid


def generate_stored_name(original_name: str) -> str:
    _, ext = os.path.splitext(original_name)
    return f'{uuid.uuid4()}{ext}'