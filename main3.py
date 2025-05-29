import discord
from discord.ext import commands
import json
import os

from myserver import server_on  # สำหรับ Replit หรือโฮสต์ที่ใช้ keep-alive

TOKEN = os.environ.get("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


def load_json(file):
    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f)

# โหลดข้อมูลจากไฟล์ JSON
manga_data = load_json("CartooTonMang/BbMangaO.json")
ln_data = load_json("CartooTonMang/MmLineNovelO.json")


def get_page_image_url(base_url: str, chapter: int, page: int) -> str:
    return f"{base_url}/{chapter}/{page}.jpg"


class ReaderView(discord.ui.View):
    def __init__(self, user, title, base_url, total_chapters, chapter, total_pages):
        super().__init__(timeout=None)
        self.user = user
        self.title = title
        self.base_url = base_url
        self.chapter = chapter
        self.page = 1
        self.total_pages = total_pages
        self.total_chapters = total_chapters

    async def update_embed(self, interaction):
        embed = discord.Embed(title=f"{self.title} - ตอนที่ {self.chapter} หน้า {self.page}")
        embed.set_image(url=get_page_image_url(self.base_url, self.chapter, self.page))
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="⬅️ ย้อนหน้า", style=discord.ButtonStyle.primary)
    async def back(self, interaction, button):
        if interaction.user != self.user:
            return await interaction.response.send_message("คุณไม่ได้เปิดหน้านี้", ephemeral=True)
        if self.page > 1:
            self.page -= 1
        await self.update_embed(interaction)

    @discord.ui.button(label="➡️ หน้าถัดไป", style=discord.ButtonStyle.primary)
    async def next(self, interaction, button):
        if interaction.user != self.user:
            return await interaction.response.send_message("คุณไม่ได้เปิดหน้านี้", ephemeral=True)
        if self.page < self.total_pages:
            self.page += 1
        await self.update_embed(interaction)

    @discord.ui.button(label="⏪ ตอนก่อนหน้า", style=discord.ButtonStyle.success)
    async def prev_chapter(self, interaction, button):
        if interaction.user != self.user:
            return await interaction.response.send_message("คุณไม่ได้เปิดหน้านี้", ephemeral=True)
        if self.chapter > 1:
            self.chapter -= 1
            self.page = 1
        await self.update_embed(interaction)

    @discord.ui.button(label="⏩ ตอนถัดไป", style=discord.ButtonStyle.success)
    async def next_chapter(self, interaction, button):
        if interaction.user != self.user:
            return await interaction.response.send_message("คุณไม่ได้เปิดหน้านี้", ephemeral=True)
        if self.chapter < self.total_chapters:
            self.chapter += 1
            self.page = 1
        await self.update_embed(interaction)

    @discord.ui.button(label="🔄 รีโหลด", style=discord.ButtonStyle.secondary)
    async def reload(self, interaction, button):
        if interaction.user != self.user:
            return await interaction.response.send_message("คุณไม่ได้เปิดหน้านี้", ephemeral=True)
        await self.update_embed(interaction)


class ChapterRangeSelect(discord.ui.Select):
    def __init__(self, user, title, base_url, total_chapters):
        self.user = user
        self.title = title
        self.base_url = base_url
        self.total_chapters = total_chapters

        options = []
        for i in range(1, total_chapters + 1, 20):
            end = min(i + 19, total_chapters)
            options.append(discord.SelectOption(label=f"ตอนที่ {i}–{end}", value=f"{i}-{end}"))

        super().__init__(placeholder="เลือกช่วงตอน...", options=options)

    async def callback(self, interaction: discord.Interaction):
        start, end = map(int, self.values[0].split('-'))
        view = discord.ui.View(timeout=None)
        view.add_item(SingleChapterSelect(
            user=self.user,
            title=self.title,
            base_url=self.base_url,
            total_chapters=self.total_chapters,
            start=start,
            end=end
        ))
        await interaction.response.send_message("เลือกตอน:", view=view, ephemeral=True)


class SingleChapterSelect(discord.ui.Select):
    def __init__(self, user, title, base_url, total_chapters, start, end):
        self.user = user
        self.title = title
        self.base_url = base_url
        self.total_chapters = total_chapters

        options = [
            discord.SelectOption(label=f"ตอนที่ {i}", value=str(i))
            for i in range(start, end + 1)
        ]
        super().__init__(placeholder="เลือกตอนในช่วงนี้...", options=options)

    async def callback(self, interaction: discord.Interaction):
        chapter = int(self.values[0])
        await interaction.response.send_message(
            f"กำลังโหลด {self.title} ตอนที่ {chapter}...",
            view=ReaderView(
                user=self.user,
                title=self.title,
                base_url=self.base_url,
                total_chapters=self.total_chapters,
                chapter=chapter,
                total_pages=20
            ),
            ephemeral=True
        )


class TitleDropdown(discord.ui.Select):
    def __init__(self, user, data, label):
        self.user = user
        self.data = data
        options = [
            discord.SelectOption(label=title, description=f"{info['chapters']} ตอน")
            for title, info in list(data.items())[:25]
        ]
        super().__init__(placeholder=f"เลือกเรื่อง {label}...", options=options)

    async def callback(self, interaction: discord.Interaction):
        title = self.values[0]
        info = self.data[title]
        view = discord.ui.View(timeout=None)
        view.add_item(ChapterRangeSelect(
            user=self.user,
            title=title,
            base_url=info['link'],
            total_chapters=info['chapters']
        ))
        await interaction.response.send_message(f"เลือกช่วงตอนของ **{title}**:", view=view, ephemeral=True)


class TypeDropdown(discord.ui.Select):
    def __init__(self, user):
        self.user = user
        options = [
            discord.SelectOption(label="มังงะ | Manga"),
            discord.SelectOption(label="ไลน์โนเวล | Light Novel")
        ]
        super().__init__(placeholder="เลือกประเภท...", options=options)

    async def callback(self, interaction: discord.Interaction):
        view = discord.ui.View(timeout=None)
        if self.values[0].startswith("มังงะ"):
            view.add_item(TitleDropdown(self.user, manga_data, "มังงะ"))
        else:
            view.add_item(TitleDropdown(self.user, ln_data, "ไลท์โนเวล"))
        await interaction.response.send_message("เลือกเรื่อง:", view=view, ephemeral=True)


class DropdownStart(discord.ui.View):
    def __init__(self, user):
        super().__init__(timeout=None)
        self.add_item(TypeDropdown(user))


@bot.command()
async def test(ctx):
    try:
        await ctx.send("เลือกประเภทที่คุณต้องการ:", view=DropdownStart(user=ctx.author))
    except Exception as e:
        await ctx.send(f"เกิดข้อผิดพลาด: {e}")
        print(f"[ERROR IN TEST COMMAND]: {e}")


server_on()
bot.run(TOKEN)
