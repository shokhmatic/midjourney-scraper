from config import logger, logging, output_folder,recent_api_url,top_api_url
import asyncio
import click

from crawlers.base import CrawlerBase

@click.command()
@click.option('--run-async', default=False, help='Download images Async')
@click.option('--loglevel', default=None,
              help='Log level', type=click.Choice(list(logging.getLevelNamesMapping().keys()), case_sensitive=False))
def run(run_async, loglevel):
    try:
        crawler = CrawlerBase()
        crawler.get_token()
        crawler.get_recent_images()
        # token=get_token_from_home_page()
        # logger.info(f'token={token}')
        # recent_url=recent_api_url.format(token=token)
        # top_url=top_api_url.format(token=token)
        # if loglevel:
        #     logger.setLevel(loglevel.upper())
        # logger.info('started')
        # if run_async:
        #     loop = asyncio.new_event_loop()
        #     asyncio.set_event_loop(loop)
        #     try:
        #         loop.run_until_complete(get_all_images_async())
        #     except KeyboardInterrupt:
        #         pass
        # else:
        #     get_all_images(recent_url,top_url)
        logger.info('finished')

    except Exception as e:
        logger.error(e)

if __name__ == '__main__':
    run()
