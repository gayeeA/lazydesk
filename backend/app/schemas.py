from pydantic import BaseModel
CATEGORIES = ["Documents","Certificates","Resumes","Projects","Notes","Images","Other"]
class ApproveItem(BaseModel):
    id: str
    category: str
    filename: str
class ApproveRequest(BaseModel):
    items: list[ApproveItem]
