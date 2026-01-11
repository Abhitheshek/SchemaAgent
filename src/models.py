from pydantic import BaseModel
from typing import List, Optional

class SchemeDetails(BaseModel):
    title: str
    url: str
    description: Optional[str] = None
    eligibility: Optional[str] = None
    benefits: Optional[str] = None
    application_process: Optional[str] = None
    documents_required: Optional[str] = None

class ScrapedData(BaseModel):
    query: Optional[str] = None
    filter_state: Optional[str] = None
    filter_category: Optional[str] = None
    filter_age: Optional[int] = None
    schemes: List[SchemeDetails]
