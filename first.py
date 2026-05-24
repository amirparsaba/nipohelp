from balethon import Client
import asyncio

bot = Client("1016889348:Y16g4uqr9yt7xdsp-NG2oVLesoedlPVlXwQ")  # Replace "TOKEN" with your actual token here


async def main():
    await bot.send_message("926798520", "Hello", None)  # Replace "@username" with your actual username here


asyncio.run(main())