import os
import discord
import asyncio
import aiohttp
import pytz
from discord.ext import commands, tasks
from datetime import datetime


from myserver import server_on

# โหลด TOKEN จาก Environment Variable
TOKEN = os.environ.get("DISCORD_TOKEN")


WEATHER_CHANNEL_ID = 1371471375361114182  # แชนแนลสำหรับอากาศ
STATUS_CHANNEL_ID = 1371468773403660338  # แชนแนลสำหรับสถานะกลุ่ม
GUILD_ID = 905530303467094027
API_KEY = '56c594de7daca68b44c11aa5feb133d1'

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOCATIONS = [
    {"name": "กรุงเทพมหานคร", "lat": 13.7563, "lon": 100.5018},
    {"name": "อุทัยธานี", "lat": 15.4712, "lon": 99.6799},
    {"name": "ชัยนาท", "lat": 15.0743, "lon": 100.1301},
    {"name": "เชียงราย", "lat": 19.9126, "lon": 99.8310},
    {"name": "เชียงใหม่", "lat": 18.7883, "lon": 98.9853}
]

thai_days = {
    'Monday': 'วันจันทร์',
    'Tuesday': 'วันอังคาร',
    'Wednesday': 'วันพุธ',
    'Thursday': 'วันพฤหัสบดี',
    'Friday': 'วันศุกร์',
    'Saturday': 'วันเสาร์',
    'Sunday': 'วันอาทิตย์'
}

thai_months = {
    'January': 'มกราคม',
    'February': 'กุมภาพันธ์',
    'March': 'มีนาคม',
    'April': 'เมษายน',
    'May': 'พฤษภาคม',
    'June': 'มิถุนายน',
    'July': 'กรกฎาคม',
    'August': 'สิงหาคม',
    'September': 'กันยายน',
    'October': 'ตุลาคม',
    'November': 'พฤศจิกายน',
    'December': 'ธันวาคม'
}

WEATHER_MESSAGE_ID = 1371491919401717770
STATUS_MESSAGE_ID = 1371491918076448798

async def get_weather(location):
    async with aiohttp.ClientSession() as session:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={location['lat']}&lon={location['lon']}&appid={API_KEY}&units=metric&lang=th"
        async with session.get(url) as response:
            data = await response.json()
            if response.status == 200:
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                return f"{location['name']}: {temp}°C, {desc}"
            else:
                return f"{location['name']}: ข้อมูลไม่พร้อมใช้งาน (รหัส {response.status})"

@tasks.loop(minutes=1)
async def update_weather():
    global WEATHER_MESSAGE_ID
    weather_channel = bot.get_channel(WEATHER_CHANNEL_ID)

    lines = []
    for location in LOCATIONS:
        result = await get_weather(location)
        lines.append(result)

    # เพิ่มเวลาปัจจุบันในเขตเวลาไทย
    now = datetime.now(pytz.timezone("Asia/Bangkok"))
    day_th = thai_days[now.strftime('%A')]
    month_th = thai_months[now.strftime('%B')]
    year_th = now.year + 543
    update_time = f"{day_th} ที่ {now.day} {month_th} พ.ศ. {year_th} เวลา {now.strftime('%H:%M:%S')}"

    embed = discord.Embed(title="**รายงานสภาพอากาศ 🌦️**", color=0x3399ff)
    embed.description = "\n".join(lines) + f"\n\n〔⏰〕อัปเดตข้อมูลเมื่อ {update_time}"
    embed.set_footer(text="〔🔄〕อัปเดตอัตโนมัติทุกๆ 1 นาที")

    try:
        if WEATHER_MESSAGE_ID:
            msg = await weather_channel.fetch_message(WEATHER_MESSAGE_ID)
            await msg.edit(embed=embed)
        else:
            msg = await weather_channel.send(embed=embed)
            WEATHER_MESSAGE_ID = msg.id
    except discord.NotFound:
        msg = await weather_channel.send(embed=embed)
        WEATHER_MESSAGE_ID = msg.id


@tasks.loop(seconds=10)
async def update_group_status():
    global STATUS_MESSAGE_ID
    guild = bot.get_guild(GUILD_ID)
    status_channel = bot.get_channel(STATUS_CHANNEL_ID)

    if not guild or not status_channel:
        return

    online = sum(1 for m in guild.members if m.status != discord.Status.offline)
    offline = guild.member_count - online

    # แปลงวันที่สร้างเซิร์ฟเวอร์เป็นภาษาไทย พร้อมเวลาไทย
    created_at = guild.created_at.astimezone(pytz.timezone("Asia/Bangkok"))
    day_th = thai_days[created_at.strftime('%A')]
    month_th = thai_months[created_at.strftime('%B')]
    year_th = created_at.year + 543  # แปลงเป็น พ.ศ.
    created_date_str = f"{day_th} {created_at.day} {month_th} {year_th} เวลา {created_at.strftime('%H:%M:%S')}"

    embed = discord.Embed(title="**สถานะกลุ่ม พม่า | ขายไก่ย่าง🍗**", color=0x00cc99)
    embed.add_field(name="〔🔨〕สร้างเมื่อ", value=created_date_str, inline=False)
    embed.add_field(name="〔👥〕สมาชิกทั้งหมด", value=f"{guild.member_count} คน", inline=True)
    embed.add_field(name="〔🟢〕ออนไลน์", value=f"{online} คน", inline=True)
    embed.add_field(name="〔⚫〕ออฟไลน์", value=f"{offline} คน", inline=True)
    embed.set_footer(text="〔🔄〕อัปเดตอัตโนมัติทุกๆ 10 วินาที")

    try:
        if STATUS_MESSAGE_ID:
            msg = await status_channel.fetch_message(STATUS_MESSAGE_ID)
            await msg.edit(embed=embed)
        else:
            msg = await status_channel.send(embed=embed)
            STATUS_MESSAGE_ID = msg.id
    except discord.NotFound:
        msg = await status_channel.send(embed=embed)
        STATUS_MESSAGE_ID = msg.id

@bot.event
async def on_ready():
    print(f"ล็อกอินแล้วเป็น {bot.user}")
    update_weather.start()
    update_group_status.start()

server_on()

bot.run(TOKEN)
