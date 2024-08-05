from fastapi import APIRouter,Depends,HTTPException,Request,Query,File, Form, UploadFile
from fastapi.responses import JSONResponse
from loguru import logger
from urllib.parse import quote
from sqlalchemy.orm import Session
import requests
import json
from datetime import datetime
import time
import os


router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#getuserappinfo
@router.get("/univoice/getuserappinfo.do")
def do_getuserappinfo(userid=Query(None), db:Session = Depends(get_db)):
    

