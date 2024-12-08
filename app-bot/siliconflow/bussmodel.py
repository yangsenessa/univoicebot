from enum import Enum
from pydantic import BaseModel

class GenAIResult(BaseModel):
    img_path:str|None
    video_path:str|None
    dimension:str|None

class GenAItype(Enum):
    Lable = 1
    Image = 2
    Video = 3
    All = 4
