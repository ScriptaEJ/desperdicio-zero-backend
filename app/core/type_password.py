from typing import Annotated
from pydantic.types import StringConstraints
from pydantic.functional_validators import AfterValidator

def validate_password(value: str) -> str:
    if not any(c.islower() for c in value):
        raise ValueError("Deve conter letra minúscula")
    if not any(c.isupper() for c in value):
        raise ValueError("Deve conter letra maiúscula")
    if not any(c.isdigit() for c in value):
        raise ValueError("Deve conter número")
    if not any(not c.isalnum() for c in value):
        raise ValueError("Deve conter caractere especial")
    return value

PasswordStr = Annotated[
    str,
    StringConstraints(min_length=8),
    AfterValidator(validate_password)
]