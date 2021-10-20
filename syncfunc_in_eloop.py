# loop.run_in_executor, start in the separate thread

import asyncio
from urllib.request import urlopen


# a synchronous function
def sync_get_url(url):
    return urlopen(url).read()


# func for processing sync_function in the thread pool executor
async def load_url(url, loop=None):
    if loop is None:
        raise KeyError("there should be a loop obj")
    future = loop.run_in_executor(None, sync_get_url, url)
    # run_in_executor means to start the code in the inner thread pool executor of the event loop
    response = await future  # we need to wait for completion of the future_obj
    print(len(response))


loop = asyncio.get_event_loop()
loop.run_until_complete(load_url("https://google.com", loop=loop))
# Run the event loop until a Future is done.
# Return the Future's result, or raise its exception.
