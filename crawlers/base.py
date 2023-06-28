from abc import ABC, abstractmethod
from config import *
import requests
import json
from tqdm import tqdm
from datetime import datetime
# from repository import ImageRepository
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from datetime import datetime
import asyncio
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from webdriver_manager.chrome import ChromeDriverManager
from seleniumwire import webdriver
import cloudscraper

class CrawlerBase(ABC):
    def __init__(self,folder=None):
        self.folder = None

        self.token = None
        self.cookies = None
        self.headers = {
            'authority': 'www.midjourney.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'max-age=0',
            'cookie': '__Secure-next-auth.callback-url=https%3A%2F%2Fwww.midjourney.com; imageSize=medium; imageLayout_2=hover; getImageAspect=2; fullWidth=false; showHoverIcons=true; _ga=GA1.1.812127157.1686762200; __Host-next-auth.csrf-token=1f58cf18e499fd4ab57c5f76ba43e66934374a4ff93e012ae08c18ad4b99b7a8%7C93c4b67a7b73c56188872fbc28ba4e3424f48e72016f4441aee1ccb1ac0141cf; __stripe_mid=da9fc2b7-2f93-4c7d-821c-faad07bde5a03aeb7a; cf_chl_2=fffdc140c1e2b38; cf_clearance=J390jsVb7oy8HyfPqWiUVK1vYEDYg7D20.Hf2rouzwA-1687849838-0-250; _ga_Q0DQ5L7K0D=GS1.1.1687849848.3.1.1687850484.0.0.0; __cf_bm=f..FHmIVd.4mcx90S_BohNe2B1ioN8WumtCYIVgB0CI-1687850492-0-ASbTKQUGus2yY7IIU0/Y4WDbxlXJCViqLLqiDWiyAxCF3N0ZHY3PejZheHYdjvJ6XniXIAUaEman3XPSythcGPA=; _dd_s=rum=0&expire=1687852367853; __cf_bm=EVGDOxoCPlZZPhpg2m9tUp56DUHiYDLbRwdfV6.HUFo-1687851531-0-AXXH1c8huZ1z6TeWN+onPhAt3IY70+5V9SXsS639xhjnl11TXhDMAtBHiKVSuYXg7KTivJMx+pC5CKTg5OzTl8k=',
            'referer': 'https://www.midjourney.com/showcase/recent/?__cf_chl_tk=iTcPbAYxmSpxZUKyFx.gwOwJ2GgC68sVfO39N3S2W5k-1687849838-0-gaNycGzNDZA',
            'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
        }
        self.proxies = {}
        if allow_proxy:
            self.proxies = {
                'http': proxy,
                'https': proxy
            }
        options = webdriver.ChromeOptions()
        # options.headless = True
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")
        # options.add_argument("--headless=chrome")
        # options.add_argument("disable-gpu")
        # options.add_argument("start-maximized")
        # options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.add_experimental_option('useAutomationExtension', False)
        proxy_selenium = proxy.replace('socks5h://', 'socks5://')
        # proxy_selenium=proxy
        options.add_argument('--proxy-server=' + proxy_selenium)
        # self.driver = uc.Chrome(options=options,
        #                         service=ChromeService(ChromeDriverManager().install()))
        self.scraper = cloudscraper.create_scraper()
    def get_token(self):
        url=home_page_url


        res=self.scraper.get(url,proxies=self.proxies)
        token = res.text.split('"buildId":"')[-1].split('"')[0]
        # self.driver.get(url)
        # WebDriverWait(self.driver, 20).until(
        #     lambda driver: driver.title == 'Midjourney Showcase')
        # content = self.driver.page_source
        # self.driver.save_screenshot('bypass_cloudflare.png')
        # token = content.split('"buildId":"')[-1].split('"')[0]
        self.token = token
        return token

    def get_recent_images(self):
        url=recent_api_url.format(token=self.token)
        self.download_from_url(url,'recent')

    def get_top_images(self):
        url=top_api_url.format(token=self.token)
        self.download_from_url(url,'top')

    def download_image(self,name, folder, image_url):
        payload = {}

        logger.info(f'download image {name}')


        response = self.scraper.get(image_url,proxies=self.proxies)
        # response = requests.request(
        #     "GET", image_url,
        #      headers=self.headers,
        #      data=payload,
        #       proxies=self.proxies)

        with open(f'{folder}/{name}', 'wb') as f:
            f.write(response.content)

    def download_images(self,image_urls,folder):
        start = datetime.now()
        count = 0
        for i, image in enumerate(tqdm(image_urls)):
            id, url = image
            name = f'{str(id)}.png'
            if os.path.exists(f'{folder}/{name}'):
                logger.info(f'image exists: {name}')
                continue
            self.download_image(name, folder, url)
            count += 1
        diff = datetime.now() - start
        logger.info(f'{count} items downloaded in {diff.seconds} seconds')

    def download_from_url(self,url, name):
        payload = {}
        logger.info('start request to get json data')
        res= self.scraper.get(url,proxies=self.proxies)
        result=json.loads(res.text)
        # self.driver.get(url)
        # WebDriverWait(self.driver, 20).until(
        #     lambda driver: 'pageProps' in driver.page_source )
        # body = self.driver.find_element(By.TAG_NAME,'Body')
        # # html = self.driver.page_source
        # self.driver.save_screenshot('bypass_cloudflare.png')
        # result = json.loads(body.text)

        # write to file

        nowdate = datetime.now().strftime('%Y_%m_%d')
        current_datetime_folder = f'{output_folder}/{nowdate}/{name}/'
        os.makedirs(current_datetime_folder, exist_ok=True)

        nowtime = datetime.now().strftime('%H_%M')
        filename = f'{current_datetime_folder}/{name}_{nowtime}.json'
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(json.dumps(result, indent=4, ensure_ascii=False))

        # extract images
        if not 'pageProps' in result or 'jobs' not in result['pageProps']:
            raise Exception(f'response is changed: {text}')

        jobs = result['pageProps']['jobs']
        if not isinstance(jobs, list) or image_url_key not in jobs[0]:
            raise Exception(f'response is changed: {text}')

        available_jobs = [x for x in jobs if len(x[image_url_key]) > 0]
        image_paths = [(x['id'], x[image_url_key][0])
                       for x in available_jobs]

        # inser sql
        # ImageRepository.insert_images(available_jobs)

        self.download_images(image_paths, current_datetime_folder)

    def get_all_images(self):
        logger.info('getting recent images')
        self.get_recent_images()
        logger.info('getting top images')
        self.get_top_images()

    def __delattr__(self):
        if self.driver:
            self.driver.close()
