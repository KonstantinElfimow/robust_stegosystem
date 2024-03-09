import threading


class DownloaderSingleton(object):
    _instance = None

    def __new__(cls):
        """ Создает singleton объект, если он не создан,
          или иначе возвращает предыдущий singleton объект """
        if cls._instance is None:
            cls._instance = super(DownloaderSingleton, cls).__new__(cls)
        return cls._instance


class ParallelDownloader(threading.Thread):
    """ Download the images parallelly """

    def __init__(self, thread_id, name, counter):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        print('Начало потока: ', self.name)
        # function to download the images
        download_images(self.name)
        print('Конец потока: ', self.name)


def download_images(thread_name):
    # singleton instance
    singleton = DownloaderSingleton()
    # visited_url has a set of URLs.
    # Here we will fetch each URL and
    # download the images in it.
    while singleton.visited_url:
        # pop the url to download the images
        url = singleton.visited_url.pop()

        http = httplib2.Http()
        print(thread_name, 'Downloading images from', url)

        try:
            status, response = http.request(url)
        except Exception:
            continue

        # parse the web page to find all images
        bs = BeautifulSoup(response, "html.parser")

        # Find all <img> tags
        images = BeautifulSoup.findAll(bs, 'img')

        for image in images:
            src = image.get('src')
            src = urljoin(url, src)

            basename = os.path.basename(src)
            print('basename:', basename)

            if basename != '':
                if src not in singleton.image_downloaded:
                    singleton.image_downloaded.add(src)
                    print('Downloading', src)
                    # Download the images to local system
                    urllib.request.urlretrieve(src, os.path.join('images', basename))
                    print(thread_name, 'finished downloading images from', url)


def fill_db():
    singleton = DownloaderSingleton()
    singleton.

    thread1 = ParallelDownloader(1, "Thread-1", 1)
    thread2 = ParallelDownloader(2, "Thread-2", 2)

    # Start new threads
    thread1.start()
    thread2.start()