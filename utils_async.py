import requests
import json
from tqdm import tqdm
from config import *
from datetime import datetime
import aiohttp,asyncio
from aiohttp_socks import ProxyConnector

proxies={}
if allow_proxy:
    proxies={
        'http':proxy,
        'https':proxy
    }
async def download_image_async(client_session,name,folder,image_url):
    payload = {}
    headers = {
    'authority': 'cdn.midjourney.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': '_ga=GA1.1.671488160.1672770946; _ga_Q0DQ5L7K0D=GS1.1.1686762591.2.0.1686762994.0.0.0',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    async with client_session.get(image_url, headers=headers,data=payload) as resp:
        response = await resp.read()
        with open(f'{folder}/{name}','wb') as f:
            f.write(response)
    # response = requests.request("GET", image_url, headers=headers, data=payload,proxies=proxies)
    # with open(f'{folder}/{name}','wb') as f:
    #     f.write(response.content)

async def download_images_async(image_urls,folder):
    start = datetime.now()
    proxy=os.getenv('PROXY',None)
    if proxy:
        proxy=proxy.replace('socks5h','socks5')
        connector = ProxyConnector.from_url(proxy)
        Client = aiohttp.ClientSession(trust_env=True,connector=connector)
    else:
        Client = aiohttp.ClientSession(trust_env=True)
    Tasks = []
    for i, image in enumerate( tqdm(image_urls) ):
        id,url=image
        name=f'{str(id)}.png'
        if os.path.exists(f'{folder}/{name}'):
            print('image exists:',name)
            continue
        Tasks.append(download_image_async(
            client_session=Client,name=name,folder=folder,image_url=url))
    try:
        count=len(Tasks)
        if count > 0:
            await asyncio.gather(*Tasks)
        diff = datetime.now() - start
        print(f'{count} items downloaded in {diff.seconds} seconds')
    except Exception as e:
        print(e)
        pass
    finally:
        await Client.close()



async def download_from_url_async(json_data,name):
    payload = {}
    headers = {
    'authority': 'www.midjourney.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cookie': '__Secure-next-auth.callback-url=https%3A%2F%2Fwww.midjourney.com; imageSize=medium; imageLayout_2=hover; getImageAspect=2; fullWidth=false; showHoverIcons=true; _ga=GA1.1.812127157.1686762200; __Host-next-auth.csrf-token=1f58cf18e499fd4ab57c5f76ba43e66934374a4ff93e012ae08c18ad4b99b7a8%7C93c4b67a7b73c56188872fbc28ba4e3424f48e72016f4441aee1ccb1ac0141cf; _ga_Q0DQ5L7K0D=GS1.1.1686762199.1.1.1686762206.0.0.0; _dd_s=rum=0&expire=1686763106695',
    'if-none-match': 'W/"2c263-XaWxzShIhHZf2Kgv4hAcqauZSNU"',
    'referer': 'https://www.midjourney.com/showcase/recent/',
    'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }

    response = requests.request("GET", recent_api_url, headers=headers, data=payload,proxies=proxies)
    text=response.text
    if response.status_code != 200:
        raise Exception(f'Error: {text}')
    result=json.loads(text)
    if not'pageProps' in result or 'jobs' not in result['pageProps']:
        raise Exception(f'response is changed: {text}')

    jobs=result['pageProps']['jobs']
    image_paths=[(x['id'],x[image_url_key][0]) for x in jobs if len(x[image_url_key])>0]

    now=datetime.now().strftime('%Y_%m_%d')
    current_datetime_folder=f'{output_folder}/{now}/{name}/'
    os.makedirs(current_datetime_folder, exist_ok=True)

    with open(f'{current_datetime_folder}/{name}_data.json','w',encoding='utf-8') as f:
        f.write(json.dumps(result,indent=4,ensure_ascii=False))
    await download_images_async(image_paths,current_datetime_folder)

async def get_recent_images_async():
    await download_from_url_async(recent_api_url,recent_folder_name)

async def get_top_images_async():
    await download_from_url_async(top_api_url,top_folder_name)


async def get_all_images_async():
    print('getting recent images')
    await get_recent_images_async()
    print('getting top images')
    await get_top_images_async()
