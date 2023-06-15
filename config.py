import os
import logging
from dotenv import load_dotenv
load_dotenv()
log_path = os.getenv('LOG_PATH', logging.INFO)
log_file_name = os.getenv('LOG_FILE', logging.INFO)
log_level = os.getenv('LOG_LEVEL', logging.INFO)
logFormatter = logging.Formatter(
    "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
logger = logging.getLogger()

fileHandler = logging.FileHandler(
    "{0}/{1}.log".format(log_path, log_file_name), mode='a', encoding='utf-8')
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)
logger.setLevel(log_level)

output_folder = os.getenv('OUTPUT_FOLDER')
recent_api_url = os.getenv('RECENT_API_URL')
top_api_url = os.getenv('TOP_API_URL')
image_url_key = os.getenv('IMAGE_URL_KEY')
allow_proxy = os.getenv('ALLOW_PROXY')
proxy = os.getenv('PROXY')
recent_folder_name = os.getenv('RECENT_FOLDER_NAME')
top_folder_name = os.getenv('TOP_FOLDER_NAME')
home_page_url=os.getenv('HOME_PAGE')
