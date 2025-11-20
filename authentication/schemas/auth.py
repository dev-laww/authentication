from pydantic import EmailStr

from ..core.base import BaseModel


class EmailLogin(BaseModel):
    email: EmailStr
    password: str


class Register(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
