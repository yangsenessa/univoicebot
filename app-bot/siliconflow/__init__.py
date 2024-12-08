
import logging
import colorlog

# free model
MODEL_IMAGE = "stabilityai/stable-diffusion-3-5-large"
MODEL_AUDIO = "FunAudioLLM/SenseVoiceSmall"
MODEL_TEXT = "THUDM/glm-4-9b-chat"

# Configure colorful logging
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

# Add a file handler for persistent logging
file_handler = logging.FileHandler('audio_to_video.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(file_handler)