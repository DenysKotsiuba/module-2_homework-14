from pydantic import BaseModel, Field, EmailStr

from datetime import date


class ContactModel(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(regex=r"\+380\(\d{2}\)\d{3}-\d{2}-\d{2}")
    birth_date: date 
    additional_data: None


class ContactResponseModel(BaseModel):
    id: int = Field(examples=[1])
    first_name: str 
    last_name: str
    email: EmailStr 
    phone: str
    birth_date: date 
    additional_data: None | str

    class Config:
        orm_mode = True