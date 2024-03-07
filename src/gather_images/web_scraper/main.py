import asyncio
import csv
import datetime
import random
import time
import re
import aiohttp
from bs4 import BeautifulSoup


HEADERS = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}
URL = 'https://www.freepik.com/search'

ALLOWED_FORMATS: tuple = tuple(['jpg', 'jpeg', 'png', 'bmp'])
LINK_PATTERN: str = r'https://.*?\.(' + '|'.join(ALLOWED_FORMATS) + ')\?'

data = []


async def fetch_page_data(session, url: str, page: int):
    url = url + f'&page={page}'
    print(f'[INFO] Парсинг страницы {page}')
    async with session.get(url=url, headers=HEADERS) as response:
        await asyncio.sleep(random.uniform(2, 4))

        response_text = await response.text()
        soup = BeautifulSoup(response_text, 'lxml')

        image_containers = (soup
                            .find('div', {'class': 'list-content'})
                            .find_all('figure', {'data-type': 'photo'})
                            )

        for image_container in image_containers:
            try:
                image_url = image_container.get('data-image').strip()
                format_match = re.search(LINK_PATTERN, image_url)
                if format_match:
                    link = image_url.split('?')[0]
                    data.append(link)
                else:
                    raise Exception(f'{image_url}')
            except Exception as e:
                print(e)


async def gather_data():
    s = {'cats', 'dogs', 'fish', 'mouse'}
    for obj in s:
        async with aiohttp.ClientSession() as session:
            url = URL + f'?query={obj}'
            response = await session.get(url=url, headers=HEADERS)
            soup = BeautifulSoup(await response.text(), 'lxml')
            pages_count = int(soup.find('span', {'class': 'pagination__pages'}).text)

            tasks = []

            for page in range(1, pages_count + 1):
                task = asyncio.create_task(fetch_page_data(session, url, page))
                tasks.append(task)

            await asyncio.gather(*tasks)


def main():
    start = time.perf_counter()
    asyncio.run(gather_data())

    cur_time = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M')
    with open(f'images_links_{cur_time}.csv', mode='w', newline='') as file:
        writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['image_link'])

    with open(f'images_links_{cur_time}.csv', mode='a', newline='') as file:
        writer = csv.writer(file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
        for row in data:
            writer.writerow([row])

    end = time.perf_counter()
    print(f'Время сбора: {end - start:.2f} сек')


if __name__ == '__main__':
    main()


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