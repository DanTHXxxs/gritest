import os
import discord
import asyncio
import aiohttp
import pytz
from discord.ext import commands, tasks
from datetime import datetime
import json


from myserver import server_on

# โหลด TOKEN จาก Environment Variable
TOKEN = os.environ.get("DISCORD_TOKEN")


WEATHER_CHANNEL_ID = 1371471375361114182  # แชนแนลสำหรับอากาศ
STATUS_CHANNEL_ID = 1371468773403660338  # แชนแนลสำหรับสถานะกลุ่ม
GUILD_ID = 905530303467094027
API_KEY = '56c594de7daca68b44c11aa5feb133d1'

fggchannel_id = 1372933691894136864  # แก้ตาม Channel ของคุณ
message_file = "status_message_id.json"
statusx_message = None
update_interval = 10  # วินาที


intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

LOCATIONS = [
    {"name": "🟢ภาคเหนือ | เชียงใหม่", "lat": 18.7883, "lon": 98.9853},
    {"name": "เชียงราย", "lat": 19.9105, "lon": 99.8406},
    {"name": "ลำพูน", "lat": 18.5739, "lon": 99.0087},
    {"name": "ลำปาง", "lat": 18.2888, "lon": 99.4909},
    {"name": "น่าน", "lat": 18.7832, "lon": 100.7800},
    {"name": "พะเยา", "lat": 19.1927, "lon": 99.8785},
    {"name": "แพร่", "lat": 18.1446, "lon": 100.1403},
    {"name": "แม่ฮ่องสอน", "lat": 19.3001, "lon": 97.9654},
    {"name": "ตาก", "lat": 16.8838, "lon": 99.1290},
    {"name": "สุโขทัย", "lat": 17.0078, "lon": 99.8235},
    {"name": "อุตรดิตถ์", "lat": 17.6200, "lon": 100.0999},

    {"name": "🟤ภาคตะวันออกเฉียงเหนือ | ขอนแก่น", "lat": 16.4322, "lon": 102.8236},
    {"name": "นครราชสีมา", "lat": 14.9799, "lon": 102.0977},
    {"name": "อุบลราชธานี", "lat": 15.2448, "lon": 104.8473},
    {"name": "อุดรธานี", "lat": 17.4157, "lon": 102.7859},
    {"name": "มหาสารคาม", "lat": 16.1809, "lon": 103.3003},
    {"name": "ร้อยเอ็ด", "lat": 16.0567, "lon": 103.6539},
    {"name": "กาฬสินธุ์", "lat": 16.4316, "lon": 103.5060},
    {"name": "สกลนคร", "lat": 17.1674, "lon": 104.1480},
    {"name": "นครพนม", "lat": 17.4089, "lon": 104.7784},
    {"name": "มุกดาหาร", "lat": 16.5453, "lon": 104.7235},
    {"name": "บึงกาฬ", "lat": 18.3606, "lon": 103.6463},
    {"name": "หนองคาย", "lat": 17.8783, "lon": 102.7413},
    {"name": "หนองบัวลำภู", "lat": 17.2290, "lon": 102.4260},
    {"name": "ศรีสะเกษ", "lat": 15.1186, "lon": 104.3294},
    {"name": "สุรินทร์", "lat": 14.8818, "lon": 103.4937},
    {"name": "บุรีรัมย์", "lat": 15.0000, "lon": 103.1167},
    {"name": "ชัยภูมิ", "lat": 15.8061, "lon": 102.0316},
    {"name": "ยโสธร", "lat": 15.7941, "lon": 104.1453},
    {"name": "อำนาจเจริญ", "lat": 15.8585, "lon": 104.6280},

    {"name": "🔵ภาคกลาง | กรุงเทพมหานคร", "lat": 13.7563, "lon": 100.5018},
    {"name": "นครนายก", "lat": 14.2066, "lon": 101.2131},
    {"name": "นนทบุรี", "lat": 13.8600, "lon": 100.5140},
    {"name": "ปทุมธานี", "lat": 14.0208, "lon": 100.5250},
    {"name": "พระนครศรีอยุธยา", "lat": 14.3532, "lon": 100.5689},
    {"name": "ลพบุรี", "lat": 14.7995, "lon": 100.6534},
    {"name": "สระบุรี", "lat": 14.5289, "lon": 100.9101},
    {"name": "สิงห์บุรี", "lat": 14.8936, "lon": 100.3969},
    {"name": "ชัยนาท", "lat": 15.1860, "lon": 100.1235},
    {"name": "อ่างทอง", "lat": 14.5896, "lon": 100.4550},
    {"name": "นครปฐม", "lat": 13.8199, "lon": 100.0621},
    {"name": "สมุทรปราการ", "lat": 13.5991, "lon": 100.5998},
    {"name": "สมุทรสาคร", "lat": 13.5475, "lon": 100.2740},
    {"name": "สมุทรสงคราม", "lat": 13.4149, "lon": 100.0023},
    {"name": "สุพรรณบุรี", "lat": 14.4745, "lon": 100.1226},
    {"name": "อุทัยธานี", "lat": 15.3795, "lon": 100.0246},
    {"name": "นครสวรรค์", "lat": 15.7047, "lon": 100.1372},
    {"name": "กำแพงเพชร", "lat": 16.4828, "lon": 99.5227},
    {"name": "พิจิตร", "lat": 16.4419, "lon": 100.3488},
    {"name": "เพชรบูรณ์", "lat": 16.4190, "lon": 101.1606},
    {"name": "พิษณุโลก", "lat": 16.8289, "lon": 100.2729},

    {"name": "🟡ภาคตะวันตก | กาญจนบุรี", "lat": 14.0228, "lon": 99.5328},
    {"name": "ราชบุรี", "lat": 13.5362, "lon": 99.8171},
    {"name": "ประจวบคีรีขันธ์", "lat": 11.8149, "lon": 99.7976},
    {"name": "เพชรบุรี", "lat": 13.1111, "lon": 99.9447},
    {"name": "ตาก", "lat": 16.8838, "lon": 99.1290},

    {"name": "🟣ภาคตะวันออก | ฉะเชิงเทรา", "lat": 13.6883, "lon": 101.0778},
    {"name": "ชลบุรี", "lat": 13.3611, "lon": 100.9847},
    {"name": "ระยอง", "lat": 12.6814, "lon": 101.2772},
    {"name": "จันทบุรี", "lat": 12.6113, "lon": 102.1035},
    {"name": "ตราด", "lat": 12.2436, "lon": 102.5151},
    {"name": "ปราจีนบุรี", "lat": 14.0500, "lon": 101.3667},
    {"name": "สระแก้ว", "lat": 13.8210, "lon": 102.0646},

    {"name": "🔴ภาคใต้ | นครศรีธรรมราช", "lat": 8.4304, "lon": 99.9631},
    {"name": "สงขลา", "lat": 7.1998, "lon": 100.5954},
    {"name": "พัทลุง", "lat": 7.6170, "lon": 100.0779},
    {"name": "ตรัง", "lat": 7.5569, "lon": 99.6114},
    {"name": "กระบี่", "lat": 8.0863, "lon": 98.9063},
    {"name": "พังงา", "lat": 8.4500, "lon": 98.5333},
    {"name": "ภูเก็ต", "lat": 7.8804, "lon": 98.3923},
    {"name": "ระนอง", "lat": 9.9622, "lon": 98.6365},
    {"name": "ชุมพร", "lat": 10.4931, "lon": 99.1800},
    {"name": "สุราษฎร์ธานี", "lat": 9.1401, "lon": 99.3337},
    {"name": "ยะลา", "lat": 6.5412, "lon": 101.2803},
    {"name": "ปัตตานี", "lat": 6.8698, "lon": 101.2501},
    {"name": "นราธิวาส", "lat": 6.4254, "lon": 101.8253},
    {"name": "สตูล", "lat": 6.6238, "lon": 100.0668}
]



important_days = {
    "01-01": "วันขึ้นปีใหม่",
    "14-02": "วันวาเลนไทน์",
    "06-04": "วันจักรี",
    "13-04": "วันสงกรานต์",
    "14-04": "วันสงกรานต์",
    "15-04": "วันสงกรานต์",
    "01-05": "วันแรงงานแห่งชาติ",
    "04-05": "วันฉัตรมงคล",
    "11-05": "วันวิสาขบูชา",
    "03-06": "วันเฉลิมพระชนมพรรษาสมเด็จพระนางเจ้าฯ",
    "28-07": "วันเฉลิมพระชนมพรรษาพระบาทสมเด็จพระเจ้าอยู่หัว",
    "12-08": "วันแม่แห่งชาติ",
    "13-10": "วันคล้ายวันสวรรคตรัชกาลที่ 9",
    "23-10": "วันปิยมหาราช",
    "05-12": "วันพ่อแห่งชาติ / วันชาติ",
    "10-12": "วันรัฐธรรมนูญ",
    "31-12": "วันสิ้นปี"
}







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
        
        
def get_thai_season():
    now = datetime.now()
    day = now.day
    month = now.month
    if month == 3 or month == 4 or (month == 5 and day <= 14):
        return "ฤดูร้อน🔥"
    elif (month == 5 and day >= 15) or (6 <= month <= 10):
        return "ฤดูฝน🌧️"
    else:
        return "ฤดูหนาว🥶"

def get_today_event():
    today = datetime.now().strftime("%d-%m")
    return important_days.get(today, "วันปกติ☀️")

def get_thai_datetime_string():
    now = datetime.now()
    day_name = thai_days[now.weekday()]
    day = now.day
    month_name = thai_months[now.month -1]
    year = now.year + 543
    time_str = now.strftime("%H:%M:%S")
    return f"{day_name} ที่ {day} {month_name} พ.ศ. {year} เวลา {time_str}"


@tasks.loop(seconds=update_interval)
async def update_status():
    global statusx_message

    channel = bot.get_channel(fggchannel_id)
    season = get_thai_season()
    event = get_today_event()
    now = datetime.now()
    updated_time = get_thai_datetime_string()

    embed = discord.Embed(
        title="เทศกาล / ฤดูกาลในประเทศ 🇹🇭",
        description=(
            f"**เทศกาลวันนี้:** {event}\n"
            f"**ฤดูกาลอยู่ช่วง:** {season}\n\n"
            f"**〔⏰〕อัปเดตข้อมูลเมื่อ:** {updated_time}\n"
            f"**〔🔄〕อัปเดตอัตโนมัติทุกๆ {update_interval} วินาที**"
        ),
        color=discord.Color.orange()
    )

    if statusx_message is None:
        statusx_message = await channel.send(embed=embed)
        # บันทึก message_id ลงไฟล์
        with open(message_file, "w") as f:
            json.dump({"message_id": statusx_message.id}, f)
    else:
        await statusx_message.edit(embed=embed)
        

@bot.event
async def on_ready():
    print(f"ล็อกอินแล้วเป็น {bot.user}")
    update_weather.start()
    update_group_status.start()
    global statusx_message
    print(f"บอทพร้อมใช้งานแล้ว: {bot.user}")
    channel = bot.get_channel(fggchannel_id)

    # โหลด message_id จากไฟล์
    if os.path.exists(message_file):
        with open(message_file, "r") as f:
            data = json.load(f)
            try:
                statusx_message = await channel.fetch_message(data["message_id"])
            except discord.NotFound:
                statusx_message = None

    update_status.start()

server_on()

bot.run(TOKEN)
