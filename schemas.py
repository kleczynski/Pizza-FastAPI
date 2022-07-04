from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    id:Optional[int]
    username:str
    email:str
    password:str
    is_staff:Optional[bool]
    is_active:Optional[bool]

    class Config:
        orm_mode = True
        schema_extra={
            'example':{
                "username": "johndoe",
                "email": "johndoe@example.com",
                "password": "secret",
                "is_staff": False,
                "is_active": True
            }
        }

class Settings(BaseModel):
    auth_jwt_secret_key:str='7045a7504c7b2432a93a338ac1a124b7352fa3b7447ea672a4e87ee39ec524f3'

class LoginModel(BaseModel):
    username:str
    password:str


class OrderModel(BaseModel):
    id:Optional[int]
    quantity:int
    order_status:Optional[str]="PENDING"
    pizza_sizes:str="SMALL"
    flavour:Optional[str]
    user_id:Optional[int]

    class Config:
        orm_mode = True
        schema_extra = {
            "example":{
                "quantity": 2,
                "pizza_sizes": "LARGE",
                "flavour": "spicy",
            }
        }

class OrderStatusModel(BaseModel):
    order_status:Optional[str] = "PENDING"

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "order_status": "PENDING"
            }
        }