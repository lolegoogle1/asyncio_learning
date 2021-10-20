# asyncio.Task,several coroutines start

import asyncio


async def sleep_task(num):
    for i in range(5):
        print(f"process task: {num} iter: {i}")
        await asyncio.sleep(1)

    return num

# ensure_future or create_task
loop = asyncio.get_event_loop()

task_list = [loop.create_task(sleep_task(i)) for i in range(2)]

# There are three options how to process the tasks

# *The First one - pass task list into asyncio.wait object, which passes to the run_until_complete

loop.run_until_complete(asyncio.wait(task_list))
# *The second one - to create task on place and pass
loop.run_until_complete(loop.create_task(sleep_task(3)))

# *The third option - to create asyncio.gather with list of the task to be done.
# **Returns a list with result of the work for each task per element
loop.run_until_complete(asyncio.gather(
    sleep_task(10),
    sleep_task(20),
))