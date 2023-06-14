from utils import get_all_images
from utils_async import get_all_images_async
from config import logger,logging,output_folder
import asyncio
import click

@click.command()
@click.option('--run-async' , default=False, help='Download images Async')
@click.option('--loglevel', default=None,
              help='Log level',type=click.Choice(list(logging.getLevelNamesMapping().keys()), case_sensitive=False))
def run(run_async,loglevel):
    if loglevel:
        logger.setLevel(loglevel.upper())
    logger.info('started')
    if run_async:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(get_all_images_async())
        except KeyboardInterrupt:
            pass
    else:
         get_all_images()
    logger.info('finished')

if __name__=='__main__':
    run()









