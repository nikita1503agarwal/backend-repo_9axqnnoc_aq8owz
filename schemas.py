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

from pydantic import BaseModel, Field, EmailStr
from typing import Optional

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Mobile Legends specific schemas

class MlbbPackage(BaseModel):
    """
    MLBB diamond package offering
    Collection name: "mlbbpackage"
    """
    name: str = Field(..., description="Display name, e.g., 86 Diamonds")
    diamonds: int = Field(..., ge=1, description="Number of diamonds included")
    bonus: Optional[int] = Field(0, ge=0, description="Bonus diamonds, if any")
    price: float = Field(..., ge=0, description="Price in USD")
    popular: bool = Field(False, description="Highlight this package in UI")

class Order(BaseModel):
    """
    Order placed by a customer for MLBB top-up
    Collection name: "order"
    """
    game: str = Field("mlbb", description="Game identifier")
    player_id: str = Field(..., description="MLBB Player ID")
    server_id: str = Field(..., description="MLBB Server ID")
    package_id: str = Field(..., description="Reference to MlbbPackage _id as string")
    package_name: str = Field(..., description="Package display name at time of purchase")
    diamonds: int = Field(..., ge=1, description="Diamonds purchased")
    price: float = Field(..., ge=0, description="Order amount in USD")
    contact_email: Optional[EmailStr] = Field(None, description="Contact email for receipt/updates")
    status: str = Field("pending", description="Order status: pending, paid, completed, failed")
