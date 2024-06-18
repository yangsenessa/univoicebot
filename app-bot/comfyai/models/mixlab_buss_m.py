# Buss domain models
from pydantic import BaseModel

#/mixlab/workflow
class WorkflowQuery(BaseModel):
    token:str
    task:str
    filename:str
    category:str|None = None
