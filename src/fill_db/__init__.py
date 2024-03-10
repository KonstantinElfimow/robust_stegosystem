from concurrent.futures import ThreadPoolExecutor
import csv
from io import BytesIO
import requests
from PIL import Image
from src import robust_hashing
from src.db.singleton import MongoDBSingleton
from src.utils.image_conversion import bit_planes_scaled_gray_image
from src.utils.image_metrics import complexity_metric
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_images(urls, db, hash_size):
    for url in urls:
        response = requests.get(url)
        if response.status_code == 200:
            with Image.open(BytesIO(response.content)) as image:
                planes = bit_planes_scaled_gray_image(image)
                complexity = complexity_metric(planes)
                average_hash = robust_hashing.average_hash(image, hash_size).value
                phash = robust_hashing.phash(image, hash_size).value
                dhash = robust_hashing.dhash(image, hash_size).value
                data = {'image_url': url,
                        'complexity': complexity,
                        'average_hash': average_hash,
                        'phash': phash,
                        'dhash': dhash}
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


def fill_db(link_source: str, hash_size: int, batch_size: int = 10, max_workers: int = 3):
    db = MongoDBSingleton().db
    image_urls = load_csv_to_set(link_source)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        urls_batches = [list(image_urls)[i:i + batch_size] for i in range(0, len(image_urls), batch_size)]
        for urls_batch in urls_batches:
            executor.submit(download_images, urls_batch, db, hash_size)
