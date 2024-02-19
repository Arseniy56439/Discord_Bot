import discord
from discord.ext import commands
from datetime import datetime
import logging
import asyncio
import aiohttp
import os

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('discord')
handler = logging.FileHandler(filename='discord_server.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

PREFIX = '/'
intents = discord.Intents.all()
intents.voice_states = True
intents.members = True
bot = commands.Bot(command_prefix=PREFIX, intents=intents)
TOKEN = 'MTIwODkyNDc2MjI2MTI5OTI1MA.Gw2sZF.3UtnoxHUm5IDQn8Rkgcb_1gKE-jP4vY-N-H3G0'

channel_members = {}
voice_time = {}
message_count = {}

python = 'python'  # Предполагается, что 'python' доступен в переменной среды PATH
allowed_channel_id = 1208945786826526760
timeout_role_id = 1208957029964709909

channel_names = {
    1208924111712034857: 'channel1',
    1208924111712034858: 'channel2',
    1208924111712034859: 'channel3',
}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


async def create_temporary_voice_channel(member):
    guild = member.guild
    author = member

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(connect=True),
        author: discord.PermissionOverwrite(connect=True)
    }

    new_channel = await guild.create_voice_channel(f'{author.name}s-channel', overwrites=overwrites)
    await author.move_to(new_channel)

    channel_members[new_channel.id] = [author]

    await asyncio.sleep(43200)  # Ждем 12 часов
    if new_channel.id in channel_members:
        await new_channel.delete()
        del channel_members[new_channel.id]


@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and before.channel.id in channel_members:
        if member in channel_members[before.channel.id]:
            channel_members[before.channel.id].remove(member)

        if len(channel_members[before.channel.id]) == 0:
            await asyncio.sleep(1)  # Ждем 1 секунду
            await before.channel.delete()
            del channel_members[before.channel.id]

    if before.channel is None and after.channel is not None and after.channel.id == 1208940005825843231:
        await create_temporary_voice_channel(member)


async def log_message(message):
    channel_name = channel_names.get(message.channel.id, 'Unknown Channel')
    logging.info(f'[{datetime.now().strftime("%Y-%m-%d")}] [{datetime.now().strftime("%H:%M:%S")}] [{channel_name}]: @{message.author}: {message.content}')
    await bot.get_channel(1208992420184981554).send(f'[{datetime.now().strftime("%Y-%m-%d")}] [{datetime.now().strftime("%H:%M:%S")}] [{channel_name}]: @{message.author}: {message.content}')


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id in channel_names:
        await log_message(message)

    # Добавляем дату и время к отправляемым сообщениям в определенном канале
    if message.channel.id == 1208992420184981554:
        await message.channel.send(f'[{datetime.now().strftime("%Y-%m-%d")}] [{datetime.now().strftime("%H:%M:%S")}] {message.content}')

    # Отслеживаем количество сообщений пользователя
    if message.channel.id == 1208992420184981554:
        if message.author.id not in message_count:
            message_count[message.author.id] = 0
        message_count[message.author.id] += 1


# Запуск бота
bot.run(TOKEN)
