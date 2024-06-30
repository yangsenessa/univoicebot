from pytonconnect import TonConnect
from .tcstorage import TcStorage
from  . import config

def get_connector(chat_id: int):
    return TonConnect(config.MANIFEST_URL, storage=TcStorage(chat_id))
