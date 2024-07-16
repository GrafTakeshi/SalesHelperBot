from aiogram.types import Message
from aiogram import Bot, Dispatcher

async def get_start(message: Message, bot: Bot):
    await bot.send_message(message.from_user.id, f'привет {message.from_user.first_name}')