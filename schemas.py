from pydantic import BaseModel
from pydantic import ConfigDict

class ProductBase(BaseModel):
    name: str
    category: str
    price: float


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int
    stock: int

    model_config = ConfigDict(from_attributes=True) 
