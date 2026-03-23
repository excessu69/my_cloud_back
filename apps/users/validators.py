import re
from django.core.exceptions import ValidationError


def validate_username(value):
    """
    Валидирует username.

    Должен содержать только латинские буквы и цифры,
    начинаться с буквы, длина 4-20 символов.
    """
    if not re.match(r'^[A-Za-z][A-Za-z0-9]{3,19}$', value):
        raise ValidationError(
            'Логин должен содержать только латинские буквы и цифры, '
            'начинаться с буквы и быть длиной от 4 до 20 символов.'
        )


def validate_password(value):
    """
    Валидирует пароль.

    Минимум 6 символов, должна быть заглавная буква,
    цифра и спецсимвол.
    """
    if len(value) < 6:
        raise ValidationError('Пароль должен быть не менее 6 символов.')

    if not re.search(r'[A-Z]', value):
        raise ValidationError('Пароль должен содержать хотя бы одну заглавную букву.')

    if not re.search(r'\d', value):
        raise ValidationError('Пароль должен содержать хотя бы одну цифру.')

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
        raise ValidationError('Пароль должен содержать хотя бы один спецсимвол.')