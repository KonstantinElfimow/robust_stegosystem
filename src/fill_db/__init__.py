from concurrent.futures import ThreadPoolExecutor
import csv
import io
import requests
from PIL import Image
from src.robust_hashing import average_hash, dhash, phash
from src.db.singleton import MongoDBSingleton
from src.utils.image_conversion import bit_planes_scaled_gray_image
from src.utils.image_metrics import complexity_metric
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_images(url, db, hash_size):
    response = requests.get(url)
    if response.status_code == 200:
        with Image.open(io.BytesIO(response.content)) as image:
            planes = bit_planes_scaled_gray_image(image)
            complexity = complexity_metric(planes)
            ah = average_hash(image, hash_size).value
            ph = phash(image, hash_size).value
            dh = dhash(image, hash_size).value
            data = {'image_url': url,
                    'complexity': complexity,
                    'average_hash': average_hash,
                    'phash': phash,
                    'dhash': dhash,
                    'hash_size': hash_size}
            try:
                db.create(data=data, key='image_url')
                logger.info(f'{url}: успех!')
            except Exception as e:
                logger.error(f'{url}: неудача! Error: {str(e)}')
    else:
        logger.error(f'{url}: неудача! HTTP status code: {response.status_code}')


def load_csv_to_set(file_path):
    data_set = set()
    with open(file_path, 'r', newline='') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            data_set.add(row[0])
    return data_set


def fill_db(link_source: str, hash_size: int, max_workers: int = 3):
    db = MongoDBSingleton().db
    source = load_csv_to_set(link_source)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while source:
            url = source.pop()
            executor.submit(download_images, url, db, hash_size)
