from pydantic import BaseModel, Field
from typing import Optional


class ProductAttributes(BaseModel):
    product: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    craft: Optional[str] = None
    material: Optional[str] = None
    technique: Optional[str] = None
    state: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)