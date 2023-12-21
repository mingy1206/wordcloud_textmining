from typing import List
from pydantic import BaseModel


class DataModel(BaseModel):
    font: str
    baseImage: str
    urls: List[str]
