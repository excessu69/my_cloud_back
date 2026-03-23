import os
import uuid


def generate_stored_name(original_name: str) -> str:
    """
    Генерирует уникальное имя файла для хранения.

    Добавляет UUID к расширению оригинального файла.

    Args:
        original_name (str): Оригинальное имя файла.

    Returns:
        str: Уникальное имя файла с расширением.
    """
    _, ext = os.path.splitext(original_name)
    return f'{uuid.uuid4()}{ext}'