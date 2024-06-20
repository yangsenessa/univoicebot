from loguru import logger
from telegram import Update
from telegram import File
from pydub import AudioSegment
import tempfile
import os
import base64
import json

async def parsewav(voice_file:File):
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
              with tempfile.NamedTemporaryFile(delete=False,suffix=".txt") as tmp_txt_file:
                   tmp_txt_file.write(base64_audio)

              tmp_ogg_file.close()
              os.remove(tmp_ogg_file.name)
              tmp_wk_json = await parseAudioBase64IntoWorkflow(base64_audio)

#transfer wkflow content
async def parseAudioBase64IntoWorkflow(base64date:bytes):
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
         
    
