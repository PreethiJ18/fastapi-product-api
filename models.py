from sqlalchemy import Column, Integer, String, Float
from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    category = Column(String(255))
    price = Column(Float)
    stock = Column(Integer, nullable=False, default=0)
    stock = Column(Integer, default=0)
    