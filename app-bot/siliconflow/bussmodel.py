from enum import Enum

class GenAIResult():
    img_path:str
    video_path:str
    dimension:str

class GenAItype(Enum):
    Lable = 1
    Image = 2
    Video = 3
