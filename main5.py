import os
import json
import discord
import pytz
from discord.ext import commands, tasks
from datetime import datetime
from discord.ui import View, Button
from myserver import server_on  # ถ้ามีระบบนี้

# โหลด TOKEN จาก Environment Variable
TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

channel_id = 1372933691894136864
chanrole_id = 982259566664376401
changetfree_id = 987661935757639680
message_file = "status_message_id.json"

status_message = 1373323014145314977
update_interval = 10

important_days = {
    "01-01": "วันขึ้นปีใหม่", "14-02": "วันวาเลนไทน์", "06-04": "วันจักรี",
    "13-04": "วันสงกรานต์", "14-04": "วันสงกรานต์", "15-04": "วันสงกรานต์",
    "01-05": "วันแรงงานแห่งชาติ", "04-05": "วันฉัตรมงคล", "11-05": "วันวิสาขบูชา",
    "03-06": "วันเฉลิมพระชนมพรรษาสมเด็จพระนางเจ้าฯ", "28-07": "วันเฉลิมพระชนมพรรษาพระบาทสมเด็จพระเจ้าอยู่หัว",
    "12-08": "วันแม่แห่งชาติ", "13-10": "วันคล้ายวันสวรรคตรัชกาลที่ 9", "23-10": "วันปิยมหาราช",
    "05-12": "วันพ่อแห่งชาติ / วันชาติ", "10-12": "วันรัฐธรรมนูญ", "31-12": "วันสิ้นปี"
}

thai_days = ["วันจันทร์", "วันอังคาร", "วันพุธ", "วันพฤหัสบดี", "วันศุกร์", "วันเสาร์", "วันอาทิตย์"]
thai_months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
               "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]



def get_thai_season():
    now = datetime.now()
    day = now.day
    month = now.month
    if month in [3, 4] or (month == 5 and day < 15):
        return "ฤดูร้อน🔥"
    elif (month == 5 and day >= 15) or (6 <= month <= 10):
        return "ฤดูฝน🌧️"
    else:
        return "ฤดูหนาว🥶"

def get_today_event():
    today = datetime.now().strftime("%d-%m")
    return important_days.get(today, "วันปกติ☀️")

def get_thai_datetime_string():
    now = datetime.now(pytz.timezone("Asia/Bangkok"))
    day_name = thai_days[now.weekday()]
    day = now.day
    month_name = thai_months[now.month - 1]
    year = now.year + 543
    time_str = now.strftime("%H:%M:%S")
    return f"{day_name} ที่ {day} {month_name} พ.ศ. {year} เวลา {time_str}"


@bot.event
async def on_ready():
    global status_message
    print(f"บอทพร้อมใช้งานแล้ว: {bot.user}")
    channel = bot.get_channel(channel_id)

    if os.path.exists(message_file):
        with open(message_file, "r") as f:
            data = json.load(f)
            try:
                status_message = await channel.fetch_message(data["message_id"])
            except discord.NotFound:
                print("ไม่พบข้อความเก่า กำลังสร้างข้อความใหม่...")
                status_message = None
    else:
        status_message = None

    update_status.start()











class RoleButtonView(View):
    def __init__(self, role: discord.Role):
        super().__init__(timeout=None)
        self.role = role

    @discord.ui.button(label="✅", style=discord.ButtonStyle.green, custom_id="give_role")
    async def give_role(self, interaction: discord.Interaction, button: Button):
        member = interaction.user
        if self.role in member.roles:
            await member.remove_roles(self.role)
            await interaction.response.send_message(f"ลบยศ {self.role.name} ออกเรียบร้อย", ephemeral=True)
        else:
            await member.add_roles(self.role)
            await interaction.response.send_message(f"ให้ยศ {self.role.name} เรียบร้อย", ephemeral=True)

@bot.command()
async def setrolebutton(ctx, role: discord.Role):
    channel = bot.get_chan@tasks.loop(minutes=5)
async def update_status():
    global status_message
    channel = bot.get_channel(channel_id)
    season = get_thai_season()
    event = get_today_event()
    updated_time = get_thai_datetime_string()

    embed = discord.Embed(
        title="เทศกาล / ฤดูกาลในประเทศไทย 🇹🇭",
        description=(
            f"**เทศกาลวันนี้:** {event}\n"
            f"**ฤดูกาลอยู่ช่วง:** {season}\n\n"
            f"**〔⏰〕อัปเดตข้อมูลเมื่อ:** {updated_time}\n"
            f"**〔🔄〕อัปเดตอัตโนมัติทุกๆ 5 นาที**"
        ),
        color=discord.Color.orange()
    )

    if status_message is None:
        status_message = await channel.send(embed=embed)
        with open(message_file, "w") as f:
            json.dump({"message_id": status_message.id}, f)
    else:
        try:
            await status_message.edit(embed=embed)
        except discord.NotFound:
            # ลบข้อความเก่า (ถ้ามี ID ในไฟล์แต่ไม่เจอใน Discord)
            try:
                old_msg = await channel.fetch_message(status_message.id)
                await old_msg.delete()
            except:
                pass
            status_message = await channel.send(embed=embed)
            with open(message_file, "w") as f:
                json.dump({"message_id": status_message.id}, f)nel(chanrole_id)

    # ลบข้อความล่าสุดของบอทในช่องนี้ (ถ้ามี)
    async for msg in channel.history(limit=50):
        if msg.author == bot.user and msg.embeds and msg.embeds[0].title == "ยืนยันตัวตน":
            await msg.delete()
            break

    embed = discord.Embed(
        title="ยืนยันตัวตน",
        description=f"กดอีโมจิ ✅ เพื่อรับยศ **{role.name}**",
        color=discord.Color.green()
    )
    view = RoleButtonView(role)
    await channel.send(embed=embed, view=view)
    await ctx.send(f"สร้างปุ่มแจกยศ {role.name} แล้ว")

# อีโมจิกับ Role Map
EMOJI_ROLE_MAP = {
    "🧑": 988733621051457576,
    "👩": 988733716551598150,
    "📜": 984717703401070622,
    "🎁": 1015983929217536122,
    "👽": 1015986592134987786,
    "🤡": 1015985917758029974,
    "🎶": 1015986860247490681,
    "😱": 986991079524036719,
    "👻": 994935629202858137,
    "👨‍💻": 989179183194308629,
    "🍍": 1015983410793152564,
}

role_message_id = 1373307799869722644

@bot.command()
async def sendroles(ctx):
    global role_message_id

    content = """**รับบทบาท**
🧑 | <@&988733621051457576> 
👩 | <@&988733716551598150> 
--------
📜 | <@&984717703401070622> 
🎁 | <@&1015983929217536122> 
--------
👽 | <@&1015986592134987786> 
🤡 | <@&1015985917758029974> 
🎶 | <@&1015986860247490681> 
😱 | <@&986991079524036719> 
👻 | <@&994935629202858137> 
👨‍💻 | <@&989179183194308629> 
--------
🍍 | <@&1015983410793152564>"""

    msg = await ctx.send(content)
    role_message_id = msg.id

    for emoji in EMOJI_ROLE_MAP.keys():
        await msg.add_reaction(emoji)

@bot.event
async def on_raw_reaction_add(payload):
    global role_message_id
    if payload.message_id != role_message_id or payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    emoji = str(payload.emoji)
    role_id = EMOJI_ROLE_MAP.get(emoji)
    if not role_id:
        return

    role = guild.get_role(role_id)
    member = guild.get_member(payload.user_id)
    if role and member:
        await member.add_roles(role)
        print(f"Added role {role.name} to {member.name}")

@bot.event
async def on_raw_reaction_remove(payload):
    global role_message_id
    if payload.message_id != role_message_id or payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    emoji = str(payload.emoji)
    role_id = EMOJI_ROLE_MAP.get(emoji)
    if not role_id:
        return

    role = guild.get_role(role_id)
    member = guild.get_member(payload.user_id)
    if role and member:
        await member.remove_roles(role)
        print(f"Removed role {role.name} from {member.name}")


server_on()

# เริ่มรันบอท
if TOKEN:
    bot.run(TOKEN)
else:
    print("กรุณาตั้งค่าตัวแปร DISCORD_TOKEN ก่อนเรียกใช้งาน")
