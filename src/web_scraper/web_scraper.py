import asyncio
import csv
import datetime
import json
import os
import random
import re
import aiohttp
from aiohttp import ClientSession
from asyncio import Queue
from bs4 import BeautifulSoup
import time


with open('../../config.json', encoding='utf-8', mode='r') as f:
    params = json.load(f)
    MINIMUM_SIZE = 2 ** int(params['hash_size'])
    del params


HEADERS = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
URL = 'https://www.freepik.com/search'
LINK_PATTERN: str = r'https://img.freepik.com/(premium-photo|free-photo)/[\w-]+\.(jpg|jpeg|bmp|png)'


FILE_PATH: str = ''
if True:
    # Определение пути к директории на две директории выше текущей
    save_dir = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    save_dir = os.path.abspath(os.path.join(save_dir, os.pardir))

    # Добавление пути к папке ресурсов и папке с изображениями
    save_dir = os.path.join(save_dir, 'resources', 'image_links')

    # Проверка существования директории, и если её нет, создание
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')
    FILE_PATH = os.path.join(save_dir, f'images_links_{cur_time}.csv')


async def fetch_page_data(session: ClientSession, url: str, page: int) -> set:
    url = f'{url}&page={page}'
    async with session.get(url=url, headers=HEADERS) as response:
        await asyncio.sleep(random.uniform(2, 4))
        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')
        image_links = set()

        try:
            image_containers = soup.find('div', {'class': 'list-content'}).find_all('figure', {'data-type': 'photo'})
            for image_container in image_containers:
                image_url = image_container.get('data-image').strip()
                format_match = re.search(LINK_PATTERN, image_url)
                if format_match:
                    link = image_url.split('?')[0]
                    image_links.add(link)
                    print(link)
        except (AttributeError, Exception) as e:
            print(f'An error occurred: {e}')

        return image_links


async def gather_data(categories_queue: Queue) -> set:
    data = set()
    while not categories_queue.empty():
        obj = await categories_queue.get()
        if len(data) > MINIMUM_SIZE:
            return data
        async with aiohttp.ClientSession() as session:
            url = f'{URL}?query={obj}'
            response = await session.get(url=url, headers=HEADERS)
            soup = BeautifulSoup(await response.text(), 'lxml')
            pages_count = int(soup.find('span', {'class': 'pagination__pages'}).text)

            tasks = [fetch_page_data(session, url, page) for page in range(1, pages_count + 1)]
            results = await asyncio.gather(*tasks)
            for result in results:
                data.update(result)

    return data


def write_to_csv(data: set):
    with open(FILE_PATH, mode='a', newline='') as file:
        writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow([row])


async def fill_queue(categories_queue: Queue):
    with open('categories.txt', mode='r', encoding='utf-8') as file:
        for line in file:
            await categories_queue.put(line.strip())


async def main():
    categories_queue = Queue()
    await fill_queue(categories_queue)
    start = time.perf_counter()
    data = await gather_data(categories_queue)
    write_to_csv(data)
    end = time.perf_counter()
    print(f'Время сбора: {end - start:.2f} сек')


if __name__ == '__main__':
    asyncio.run(main())
