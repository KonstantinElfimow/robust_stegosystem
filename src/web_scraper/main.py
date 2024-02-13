import asyncio
import csv
import datetime
import pathlib
import time
import re
import aiohttp
import requests
from bs4 import BeautifulSoup
import pandas as pd
import urllib.parse
from typing import Iterable, Callable
import httpx
import html.parser

data = []

HEADERS = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36'
}
URL = 'https://ru.freepik.com/photos/котики'

# IMAGES_FORMATS: tuple = tuple(['jpg', 'jpeg', 'png', 'bmp'])
# LINK_PATTERN: str = r'https://.*?\.(' + '|'.join(IMAGES_FORMATS) + ')\?'
#
#
# async def fetch_page_data(session, page: int):
#     url = f'{URL}/{page}'
#     print(f'[INFO] Парсинг страницы {page}')
#     async with session.get(url=url, headers=HEADERS) as response:
#         await asyncio.sleep(0.3)
#
#         response_text = await response.text()
#         soup = BeautifulSoup(response_text, 'lxml')
#
#         image_containers = (soup
#                             .find('div', {'class': 'list-content'})
#                             .find_all('figure', {'data-type': 'photo'})
#                             )
#
#         for image_container in image_containers:
#             try:
#                 image_url = image_container.get('data-image').strip()
#                 format_match = re.search(LINK_PATTERN, image_url)
#                 if format_match:
#                     link = image_url.split('?')[0]
#                 else:
#                     raise Exception(f'{image_url}')
#             except Exception as e:
#                 print(e)
#                 link = None
#             finally:
#                 data.append(link)
#
#
# async def gather_data():
#     async with aiohttp.ClientSession() as session:
#         response = await session.get(url=URL, headers=HEADERS)
#         soup = BeautifulSoup(await response.text(), 'lxml')
#         pages_count = 1 # int(soup.find('span', {'class': 'pagination__pages'}).text)
#
#         tasks = []
#
#         for page in range(1, pages_count + 1):
#             task = asyncio.create_task(fetch_page_data(session, page))
#             tasks.append(task)
#
#         await asyncio.gather(*tasks)
#
#
# def main():
#     start_time = time.time()
#     asyncio.run(gather_data())
#     cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')
#
#     with open(f'images_links_{cur_time}.csv', mode='w', newline='') as file:
#         writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
#         writer.writerow(['image_link'])
#
#     with open(f'images_links_{cur_time}.csv', mode='a', newline='') as file:
#         writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
#         for row in data:
#             writer.writerow([row])
#
#     finish_time = time.time() - start_time
#     print(f'Затраченное время на работу скрипта: {finish_time}')
#
#
# if __name__ == '__main__':
#     # main()
#     df = pd.read_csv('images_links_13_02_2024_15_17.csv', sep=',', skipinitialspace=True)
#     print(df)
#     print(df.shape)
    # req = requests.get(url, headers=headers)
    # src = req.text
    # with open('index.html', 'w', encoding='utf-16') as file:
    #     file.write(src)
    # lnk = 'https://img.freepik.com/free-photo/view-of-3d-adorable-cat-with-fluffy-clouds_23-2151113432.jpg'
    # with open(basename(lnk), 'wb') as file:
    #     file.write(requests.get(lnk).content)

ALLOWED_FORMATS: tuple = tuple(['jpg', 'jpeg', 'png', 'bmp'])
LINK_PATTERN: str = r'https://.*?\.(' + '|'.join(ALLOWED_FORMATS) + ')\?'


class WebCrawler:
    def __init__(
            self,
            client: httpx.AsyncClient,
            urls: Iterable[str],
            filterer: Iterable[str],
            workers: int = 10,
            limit: int = 25,
    ):
        self.client = client

        self.start_urls = set(urls)
        self.todo = asyncio.Queue()
        self.seen = set()
        self.done = set()

        self.filterer = filterer
        self.num_workers = workers
        self.limit = limit
        self.total = 0

    async def run(self):
        await self.on_found_links(self.start_urls)
        workers = [asyncio.create_task(self.worker()) for _ in range(self.num_workers)]
        await self.todo.join()

        for worker in workers:
            worker.cancel()

    async def worker(self):
        while True:
            try:
                await self.process_one()
            except asyncio.CancelledError:
                return

    async def process_one(self):
        url = await self.todo.get()
        try:
            await self.crawl(url)
        except Exception as e:
            pass
        finally:
            self.todo.task_done()

    async def crawl(self, url: str):
        await asyncio.sleep(.1)

        response = await self.client.get(url, follow_redirects=True)
        found_links = await self.parse_links(base=response.text)

        await self.on_found_links(found_links)

        self.done.add(url)

    async def on_found_links(self, urls: set[str]):
        new = urls - self.seen
        self.seen.update(new)

        # await save to database or file here...

        for url in new:
            await self.put_todo(url)

    async def put_todo(self, url: str):
        if self.total >= self.limit:
            return
        self.total += 1
        await self.todo.put(url)

    async def parse_links(self, base: str) -> set[str]:
        found_links = {''}

        return found_links


async def main():
    response = requests.get(url=URL, headers=HEADERS)
    soup = BeautifulSoup(response.content, 'lxml')
    pages_count = 1 # int(soup.find('span', {'class': 'pagination__pages'}).text)

    start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        crawler = WebCrawler(
            client=client,
            urls=[f'https://ru.freepik.com/котики/{i}' for i in range(1, pages_count + 1)],
            filterer={'tag': 'figure', 'attrs': 'data-image'},
            workers=5,
            limit=30)
        await crawler.run()
    end = time.perf_counter()

    seen = sorted(crawler.seen)
    print('Results:')
    for url in seen:
        print(url)
    print(f'Crawled: {len(crawler.done)} URLs')
    print(f'Found: {len(seen)} URLs')
    print(f'Done in {end - start:.2f}s')


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
