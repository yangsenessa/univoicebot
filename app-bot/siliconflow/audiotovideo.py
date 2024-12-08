from . import logger, MODEL_TEXT, MODEL_IMAGE, MODEL_AUDIO
from tqdm import tqdm
import requests
import os
from moviepy import AudioFileClip, ImageClip, CompositeVideoClip, VideoFileClip
from moviepy.video import fx as vfx
import json
import uuid
from typing import Optional
from .config import SILICON_FLOW_API_TOKEN
from .bussmodel import GenAIResult, GenAItype

class AudioToVideo:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.siliconflow.cn/v1"
        # Mask API token in logs
        masked_token = f"...{api_token[-4:]}" if api_token else "None"
        logger.info(f"AudioToVideo initialized with API token ending in {masked_token}")

    def _get_masked_headers(self):
        """Return headers with masked API token for logging"""
        masked_headers = self.headers.copy()
        if 'Authorization' in masked_headers:
            token = masked_headers['Authorization'].split()[-1]
            masked_headers['Authorization'] = f"Bearer ...{token[-4:]}"
        return masked_headers

    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Convert audio to text using SiliconFlow API"""
        url = f"{self.base_url}/audio/transcriptions"
        logger.info(f"Starting audio transcription for file: {audio_path}")
        
        if not os.path.exists(audio_path):
            logger.error(f"Audio file not found: {audio_path}")
            return None
        
        try:
            # Get file size for progress bar
            file_size = os.path.getsize(audio_path)
            
            # Prepare multipart form data with progress bar
            with tqdm(total=file_size, unit='B', unit_scale=True, desc="Uploading audio") as pbar:
                class ProgressFileWrapper:
                    def __init__(self, fd):
                        self.fd = fd
                        self.progress = 0

                    def read(self, size=-1):
                        data = self.fd.read(size)
                        if data:
                            pbar.update(len(data))
                        return data

                    def seek(self, *args):
                        return self.fd.seek(*args)

                    def tell(self):
                        return self.fd.tell()

                    def close(self):
                        return self.fd.close()

                with open(audio_path, 'rb') as f:
                    files = {
                        'file': ('audio.mp3', ProgressFileWrapper(f), 'audio/mpeg'),
                        'model': (None, MODEL_AUDIO)
                    }
                    
                    headers = {
                        "Authorization": f"Bearer {self.api_token}"
                    }
                    
                    try:
                        logger.debug(f"Making POST request to {url}")
                        response = requests.post(url, files=files, headers=headers)
                        response.raise_for_status()
                        result = response.json()
                        logger.info("Audio transcription successful")
                        logger.debug(f"Transcription result: {result}")
                        return result.get('text')
                    except requests.exceptions.RequestException as e:
                        logger.error(f"Network error during transcription: {str(e)}", exc_info=True)
                        return None
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing API response: {str(e)}", exc_info=True)
                        return None
                
        except Exception as e:
            logger.error(f"Unexpected error in transcription: {str(e)}", exc_info=True)
            return None

    def optimize_text(self, text: str) -> Optional[str]:
        """Optimize text for image generation using SiliconFlow API"""
        url = f"{self.base_url}/chat/completions"
        logger.info("Starting text optimization")
        logger.debug(f"Input text: {text}")
        
        prompt = f"""请基于以下文本，生成一幅画面的详细描述。描述要具体且富有视觉细节：

{text}

请用英文回答，因为后续需要给text-to-image模型使用。字数控制在100字以内"""
        
        payload = {
            "model": MODEL_TEXT,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"}
        }

        try:
            logger.debug(f"Making POST request to {url} with payload: {json.dumps(payload, indent=2)}")
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            result = response.json()
            optimized_text = result.get('choices', [{}])[0].get('message', {}).get('content')
            logger.info("Text optimization successful")
            logger.debug(f"Optimized text: {optimized_text}")
            return optimized_text
        except Exception as e:
            logger.error(f"Error in text optimization: {e}")
            return None

    def generate_image(self, prompt: str, output_path: str = "generated_image.png") -> Optional[str]:
        """Generate image from text using SiliconFlow API"""
        url = f"{self.base_url}/images/generations"
        logger.info("Starting image generation")
        logger.debug(f"Prompt: {prompt}")
        
        payload = {
            "model": MODEL_IMAGE,
            "prompt": prompt,
            "image_size": "1024x1024",
            "batch_size": 1,
            "num_inference_steps": 20,
            "guidance_scale": 15,
            "prompt_enhancement": False
        }

        try:
            logger.debug(f"Making POST request to {url}")
            logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")
            logger.debug(f"Request headers: {json.dumps(self._get_masked_headers(), indent=2)}")  # Use masked headers for logging
            
            response = requests.post(url, json=payload, headers=self.headers)
            
            # Log the response details
            logger.debug(f"Response status code: {response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            logger.debug(f"Response content: {response.text}")
            
            response.raise_for_status()
            
            # Save the image
            image_data = response.json().get('data', [{}])[0].get('url')
            if image_data:
                logger.info(f"Image generation successful, downloading from: {image_data}")
                image_response = requests.get(image_data)
                with open(output_path, 'wb') as f:
                    f.write(image_response.content)
                logger.info(f"Image saved to: {output_path}")
                return output_path
            else:
                logger.error("No image URL in response")
                return None
        except Exception as e:
            logger.error(f"Error in image generation: {e}")
            return None

    def create_video(self, image_path: str, audio_path: str, output_path: str = "output.mp4"):
        """Create video from image and audio"""
        audio = None
        image = None
        final_video = None
        try:
            logger.info("Creating final video")
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # 加载音频
            logger.debug("Loading audio file...")
            audio = AudioFileClip(audio_path)
            
            # 创建图片剪辑
            logger.debug("Loading image file...")
            image = ImageClip(image_path, duration=audio.duration)
            
            # 使用图片的原始尺寸创建视频
            logger.debug("Compositing video...")
            final_video = CompositeVideoClip([image], size=(image.size))
            final_video.audio = audio
            
            # 写入输出文件
            logger.info("Rendering final video...")
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                threads=4,
                preset='medium'
            )
            
            logger.info(f"Video creation successful, saved to: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error in video creation: {str(e)}", exc_info=True)
            return None
        finally:
            # 清理资源
            for clip in [audio, image, final_video]:
                if clip is not None:
                    try:
                        clip.close()
                    except Exception as e:
                        logger.error(f"Error closing clip: {str(e)}")

    def process(self, audio_path: str, genType:GenAItype, output_video_path: str = "output.mp4")->GenAIResult:
        """Process the entire pipeline from audio to video"""
        result= GenAIResult(img_path=None,video_path=None,dimension=None)
        # Step 1: Audio to text
        logger.info("Converting audio to text...")
        audio_text:str
        curr_pre:str = str(uuid.uuid4())
        out_img_path=curr_pre+".png"
        output_video_path = curr_pre+".mp4"
        if 1<=genType.value:
           audio_text = self.transcribe_audio(audio_path)
           if not audio_text:
              return result
           else:
              result.dimension = audio_text
        
        
        # Step 2: Optimize text for image generation
        optimized_text:str
        if 2<= genType.value:
            logger.info("Optimizing text for image generation...")
            optimized_text = self.optimize_text(audio_text)
            if not optimized_text:
               return result
        
        # Step 3: Generate image
        if 3 <= genType.value:
           logger.info("Generating image from text...")
           image_path = self.generate_image(optimized_text,out_img_path)
           if not image_path:
              return result
           else:
              result.img_path = image_path
        
        # Step 4: Create video
        logger.info("Creating final video...")
        video_path = self.create_video(image_path, audio_path, output_video_path)
        
        if not video_path:
            logger.warning("Creating video error!")     
            return result   
        else:
            logger.info(f"Process completed successfully! Video saved to: {output_video_path}")
            result.video_path = video_path
        return result

def do_process(path:str,genAIType:GenAItype) ->GenAIResult:
    # Validate input file exists
    if not os.path.exists(path):
        logger.error(f"Error: Audio file '{path}' does not exist")
        return
    
     # Get API token from config
    processor = AudioToVideo(SILICON_FLOW_API_TOKEN)

    result=processor.process(path,genType=genAIType)

    if result:
        logger.info("Processing completed successfully!")
        return result

    else:
        logger.error("Processing failed!")









    
