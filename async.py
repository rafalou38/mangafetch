import async_eel
import asyncio
import api

loop = asyncio.get_event_loop()


@async_eel.expose
async def search(query):
    print("searched", query)
    result, pages = api.search(query)
    async_eel.add_results(result)
    print("found p", 1)
    asyncio.sleep(0.1)
    if pages:
        for page in range(eval(pages))[2:]:
            print("found p", page)
            nresult, _ = api.search(query, page)
            result = result + nresult
            # pprint(result)
            async_eel.add_results(nresult)
            asyncio.sleep(0.1)
    # return result


@async_eel.expose
async def get_info(id):
    print("get_info", id)
    return api.get_info(id)


# @async_eel.expose                         # Expose this function to Javascript
# async def say_hello_py(x):
#     print('Hello from %s' % x)


async def main():
    # Set web files folder
    async_eel.init("public")
    await async_eel.start("index.html", cmdline_args=["--incognito"])  # Start

    # await say_hello_py('Python World!')
    # await async_eel.say_hello_js('Python World!')()  # Call a Javascript function
    # print("OK")


if __name__ == "__main__":
    asyncio.run_coroutine_threadsafe(main(), loop)
    loop.run_forever()
