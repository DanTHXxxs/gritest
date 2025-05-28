import os
import discord
from discord.ext import commands
from discord.ui import View, Button
from myserver import server_on  # ถ้ามีระบบนี้

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

chanrole_id = 982259566664376401

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
    channel = bot.get_channel(chanrole_id)

    # ลบข้อความเก่าที่เป็น embed "ยืนยันตัวตน" ทั้งหมดก่อน
    async for msg in channel.history(limit=100):
        if msg.author == bot.user and msg.embeds:
            if msg.embeds[0].title == "ยืนยันตัวตน":
                await msg.delete()

    embed = discord.Embed(
        title="ยืนยันตัวตน",
        description=f"กดปุ่ม ✅ เพื่อรับยศ **{role.name}**",
        color=discord.Color.green()
    )
    view = RoleButtonView(role)
    await channel.send(embed=embed, view=view)
    await ctx.send(f"สร้างปุ่มแจกยศ {role.name} แล้ว")

# ระบบกดอีโมจิรับยศ
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
    if payload.message_id != role_message_id or payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    emoji = str(payload.emoji)
    role_id = EMOJI_ROLE_MAP.get(emoji)
    if not role_id:
        return

    role = guild.get_role(role_id)
    member = guild.get_member(payload.user_id)
    if role and member:
        await member.add_roles(role)

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id != role_message_id or payload.user_id == bot.user.id:
        return

    guild = bot.get_guild(payload.guild_id)
    emoji = str(payload.emoji)
    role_id = EMOJI_ROLE_MAP.get(emoji)
    if not role_id:
        return

    role = guild.get_role(role_id)
    member = guild.get_member(payload.user_id)
    if role and member:
        await member.remove_roles(role)

server_on()

if TOKEN:
    bot.run(TOKEN)
else:
    print("กรุณาตั้งค่าตัวแปร DISCORD_TOKEN ก่อนเรียกใช้งาน")
