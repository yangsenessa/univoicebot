from loguru import logger
from telegram import Update
from telegram import File
from pydub import AudioSegment
from telegram.ext import ContextTypes
import tempfile
import os
import base64
import json
import subprocess
import re
import oss2
import uuid

import sys
sys.path.append('..')
from comfyai import telegram_bot_endpoint

endpoint = 'http://oss-us-east-1.aliyuncs.com'

#oss
def get_oss_bucket():
   bucket_name = 'univoice'
   access_key_id=os.getenv("OSS_ACCESS_KEY_ID")
   access_key_secret = os.getenv("OSS_ACCESS_KEY_SECRET")
   
   bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name=bucket_name)
   return bucket


def get_oss_download_url(key:str):
    logger.debug("Get oss with key:" + key)
    bucket = get_oss_bucket()
    url =  bucket.sign_url('GET', key, 3600*24*7)
    return url

async def parsewav(user_token:str, voice_file:File,context:ContextTypes.DEFAULT_TYPE):
   with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp_ogg_file:
         await voice_file.download_to_drive(tmp_ogg_file.name)
         tmp_ogg_file.flush()
         os.fsync(tmp_ogg_file.fileno())    
         logger.info(f"ogg dir: {tmp_ogg_file.name}")

         # Convert OGG to WAV
         with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav_file:
              audio = AudioSegment.from_ogg(tmp_ogg_file.name)
              audio.export(tmp_wav_file.name, format="wav")
              logger.info(f"wav dir: {tmp_wav_file.name}")
              audiowav = AudioSegment.from_file(tmp_wav_file,format="wav")
 
              # transfer to BASE64
              base64_audio = base64.b64encode(audiowav.export(format="wav").read())
              #with tempfile.NamedTemporaryFile(delete=False,suffix=".txt") as tmp_txt_file:
              #     tmp_txt_file.write(base64_audio)

              tmp_ogg_file.close()
              os.remove(tmp_ogg_file.name)
              tmp_wk_json =  parseAudioBase64IntoWorkflow(base64_audio)
              return tmp_wk_json

async def save_voice( voice_file:File):
     with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp_ogg_file:
          await voice_file.download_to_drive(tmp_ogg_file.name)
          tmp_ogg_file.flush()
          os.fsync(tmp_ogg_file.fileno())
          logger.info(f"ogg dir: {tmp_ogg_file.name}")
          with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_wav_file:
              audio = AudioSegment.from_ogg(tmp_ogg_file.name)
              audio.export(tmp_wav_file.name, format="wav")
              logger.info(f"wav dir: {tmp_wav_file.name}")
              oss_key=str(uuid.uuid4())+str(tmp_wav_file.name)
   #   return tmp_ogg_file.name
     #set_environment_variables()
     # 调用编译好的二进制文件
              logger.info(f'Upload file={tmp_wav_file.name}')
              result = get_oss_bucket().put_object_from_file(oss_key,tmp_wav_file.name)
              tmp_ogg_file.close()
              os.remove(tmp_ogg_file.name)
       
              tmp_wav_file.close()
              os.remove(tmp_wav_file.name)

              return oss_key
         

     '''result = subprocess.run(
        #--['/home/ubuntu/app/bin/example', 'upload','--make-car=true',tmp_ogg_file.name],
        ['/home/ubuntu/app/bin/example', 'upload',tmp_ogg_file.name],
        #['D:\\project\\titan-storage-sdk\\example\\example', 'upload', tmp_ogg_file.name],
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE,
         text=True
     )

     if result.returncode == 0:
         logger.info("Upload successful")
         logger.info(f"Output stdout:{result.stdout}")
         logger.info(f"Output stderr:{result.stderr}")
         os.remove(tmp_ogg_file.name)
         match = re.search(r'cid ([a-zA-Z0-9]+)', result.stderr)
         if match:
             cid = match.group(1)
             print("Extracted CID:", cid)
             return cid
         else:
             print("CID not found in the output.")
             return ""
     else:
         print("Upload failed")
         print("Error:", result.stderr)
         return ""
     '''

#transfer wkflow content
def parseAudioBase64IntoWorkflow(base64date:bytes):
    wk_filename = "musetalk-comfyui-workflow.json"
    comfyai_path = os.path.abspath(os.path.dirname(__file__))
    wk_path = os.path.join(comfyai_path,"workflows",wk_filename)
    logger.info(f"wk_path:{wk_path}")

    try:
         with open(wk_path) as json_file:
              json_wk_data = json.load(json_file)
              audio_encoded = base64date.decode()
      
              audioitem=[]
              audioitem.append(f"data:audio/wav;base64,{audio_encoded}")
              json_wk_data["prompt"]["147"]["inputs"]["audios"]["base64"] = audioitem

              tmp_wk_file = "tmp_" + wk_filename
              tmp_wk_path = os.path.join(comfyai_path,"workflows", tmp_wk_file)

              with open(tmp_wk_path,"w") as tmp_json_file:
                   json.dump(json_wk_data,tmp_json_file)
                   tmp_json_file.flush()
              return json_wk_data
              
    
    except Exception as e:
         logger.error(f"Some exception happend:  {str(e)}")
         
#load video default
def loadVideoDefault():
     videofile = "sun.mp4"
     comfyai_path = os.path.abspath(os.path.dirname(__file__))
     video_path = os.path.join(comfyai_path,"video",videofile)
     logger.info(f"Video template path :{video_path}")
     
     try:
          file = open(video_path,'r')
          return file
     except Exception as e:
          logger.error(f"Load video file fail: {str(e)}")  

     return None  


#hook function for ws_client
#usertoken = user_id % chart_id
def do_send_video(usertoken:str,context:ContextTypes.DEFAULT_TYPE, video:File):
    context.bot.send_video(usertoken.split('-')[1], video, supports_streaming=True)
