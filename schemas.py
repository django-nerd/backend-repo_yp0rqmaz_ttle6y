"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Core domain schemas for the government portal

class Department(BaseModel):
    name: str = Field(..., description="Department name")
    description: str = Field(..., description="Short summary of what the department does")
    email: Optional[str] = Field(None, description="Public contact email")
    phone: Optional[str] = Field(None, description="Public contact phone")
    address: Optional[str] = Field(None, description="Office address")
    services: Optional[List[str]] = Field(default_factory=list, description="List of key services provided")

class News(BaseModel):
    title: str
    body: str
    department: Optional[str] = Field(None, description="Related department name")
    published_at: Optional[datetime] = None

class Event(BaseModel):
    title: str
    description: str
    location: str
    start_date: datetime
    end_date: Optional[datetime] = None
    department: Optional[str] = None

class Vacancy(BaseModel):
    title: str
    department: str
    description: str
    location: str
    closing_date: datetime

class Employee(BaseModel):
    name: str
    department: str
    position: str
    email: Optional[str] = None

class Complaint(BaseModel):
    name: str
    email: Optional[str] = None
    subject: str
    message: str
    department: Optional[str] = None

# Example schemas (kept for reference; not used by the app but fine to keep installed):
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True

class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
