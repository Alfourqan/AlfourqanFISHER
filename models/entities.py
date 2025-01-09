from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Product:
    id: int
    name: str
    price: float
    stock: float
    category_id: int

@dataclass
class Category:
    id: int
    name: str

@dataclass
class Customer:
    id: int
    name: str
    phone: str
    address: str

@dataclass
class Supplier:
    id: int
    name: str
    phone: str
    address: str

@dataclass
class Sale:
    id: int
    date: datetime
    customer_id: int
    total: float
    items: List['SaleItem']
    payment_method: str
    discount: float = 0.0
    tax: float = 0.0
    barcode: str = None

@dataclass
class SaleItem:
    id: int
    sale_id: int
    product_id: int
    quantity: float
    price: float
