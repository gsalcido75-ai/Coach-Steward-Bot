import warnings
warnings.filterwarnings("ignore")

import os
import re
import json
import base64
import glob
import shutil
import random
import asyncio
import datetime
import aiohttp
import discord
from discord.ext import commands, tasks
import google.generativeai as genai

# ================= CONFIGURATION =================
BOT_TOKEN = "MTQ5MTEyNDQ5NjI5ODU0MTE5Ng.G7uUIU.yUgh2M9IXm3JwhK6fcW3djGYm_H40NNZHoqihA"
GEMINI_API_KEY = "AQ.Ab8RN6Je9GlT8VwyB_EVk7daWDEVaGtU96hN1u8v7q_FYy8faQ"
CREATOR_ID =1279476207603290197                                 # <--- PASTE YOUR DISCORD USER ID HERE
ANNOUNCEMENT_CHANNEL_ID = 1443473075315413004                   
MAINFRAME_HUB_URL = "https://cgpmainframe.netlify.app/"
DEFAULT_SOUNDCLOUD_URL = "https://on.soundcloud.com/Qz1dzzj3Z6fmSGbRG0"
DATA_FILE = "fighter_records.json"

# --- GITHUB AUTO-SYNC CONFIG (FOR NETLIFY) ---
GITHUB_TOKEN = "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" # Paste your generated GitHub token here
GITHUB_REPO = "gsalcido75-ai/Coach-Steward-Bot"            # Example: "gsalcido75/cgpmainframe"
GITHUB_FILE_PATH = "stats.json"                     # File path inside your GitHub repo for Netlify
# =================================================

CGP_TRACKS = [
    {"title": "Mainframe Dance", "url": "https://on.soundcloud.com/TczQK8AHZMy7ivp0US"},
    {"title": "Frequency Forever", "url": "https://on.soundcloud.com/IGo7yUXFLAnFXVtsIN"},
    {"title": "Frozen Registry", "url": "https://on.soundcloud.com/Qz1dzzj3Z6fmSGbRG0"},
    {"title": "Run It Back", "url": "https://on.soundcloud.com/Ghli1lsXMAIeIx4Flc"},
    {"title": "CGP Syndicate", "url": "https://on.soundcloud.com/9NGOePJOrjdaMfpTpB"},
    {"title": "Amber Nights", "url": "https://on.soundcloud.com/jfZPLXvLWTDeSw4ddi"},
    {"title": "The Clock Out", "url": "https://on.soundcloud.com/TczQK8AHZMy7ivp0US"},
    {"title": "Road to Undisputed", "url": "https://on.soundcloud.com/Qz1dzzj3Z6fmSGbRG0"}
]

CHAMPIONS_DATA = {
    "Heavyweight": {"fighter": "Roy🇲🇽🇲🇽🇲🇽", "record": "14W - 0L"},
    "Cruiserweight": {"fighter": "f150-_-t", "record": "11W - 2L"},
    "Light Heavyweight": {"fighter": "SlokeNastyTheCaptin#1🇺🇸🇲🇽", "record": "12W - 1L"},
    "Middleweight": {"fighter": "BBK Promotions 🪪", "record": "9W - 3L"},
    "Women's Welterweight": {"fighter": "DT", "record": "8W - 1L"},
    "Welterweight": {"fighter": "OPEN", "record": "0W - 0L"},
    "Lightweight": {"fighter": "El putito", "record": "10W - 4L"},
    "Bantamweight": {"fighter": "Roy🇲🇽🇲🇽🇲🇽 (Dual-Division King!)", "record": "14W - 0L"},
    "Women's Lightweight": {"fighter": "TURBO", "record": "7W - 2L"}
}

BOXING_HISTORY_FACTS = [
    "🥊 **Ancient Origins (688 BC):** Boxing ('Pygmachia') was first introduced into the Ancient Greek Olympic Games in 688 BC.",
    "🥊 **Marquess of Queensberry (1867):** Modern boxing was born in 1867 with 3-minute rounds and padded gloves.",
    "🥊 **HBO Broadcast Classic (2002):** Calling Micky Ward vs. Arturo Gatti I ringside for HBO—Round 9 remains the greatest round ever!"
]

BOOT_MESSAGES = [
    "🎙️ **Coach Steward:** Just stepped out of the Kronk Gym sauna. Who's ready to put in real work today?",
    "🎙️ **Coach Steward:** Booted up and pacing the corner. Remember: champions aren't born on the couch, they're forged in the Mainframe!",
    "🎙️ **Coach Steward:** Systems online. Keep your hands up in the pocket, protect your chin, and let's get to business!",
    "🎙️ **Coach Steward:** Fresh coffee poured, pads are mitts-up. Let's see who's really training in here today!"
]

RANDOM_HYPE_QUOTES = [
    "🎙️ **Coach Steward:** Hey! I see you quiet in the back. Stop shadowboxing your demons and drop some weight on the heavy bag!",
    "🎙️ **Coach Steward:** A reminder from the corner: talent wins fights, but conditioning wins titles. Put in those reps!",
    "🎙️ **Coach Steward:** If your defense is as loose as your focus right now, you're getting knocked out in round one. Tighten up!",
    "🎙️ **Coach Steward:** Greatness requires sacrifice. Get in the Riyadh gym ring and prove you deserve that belt!"
]

SMART_BACK_ROASTS = [
    "🎙️ **Coach Steward:** You got a whole lot of mouth for a guy who punches like a wet noodle. Keep talking and see how that 30-minute timeout feels!",
    "🎙️ **Coach Steward:** Listen here, clown. You're talking to the Kronk Gym—step in the ring or shut your trap!",
    "🎙️ **Coach Steward:** That ego is writing checks your chin can't cash. One more word and I'm sending you to the stool for a timeout!",
    "🎙️ **Coach Steward:** You act tough behind a screen, but you'd fold faster than a cheap lawn chair in round one. Watch your tone!"
]

CREATOR_RESPECT_REPLIES = [
    "🎙️ **Coach Steward:** Yes sir, Boss! The Kronk Gym is locked in and following your lead. Make sure everyone streams that CGP SoundCloud catalog!",
    "🎙️ **Coach Steward:** You already know how we roll, Clone Geek! The Mainframe is running sharp today.",
    "🎙️ **Coach Steward:** Heard you loud and clear, Champ! Everything in the gym is running by your rules."
]

# --- LOAD & SAVE PERSISTENT RECORDS ---
def load_records():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        except Exception:
            return {}
    return {}

def save_records():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(FIGHTER_RECORDS, f, indent=4)
        asyncio.create_task(sync_stats_to_github())
    except Exception as e:
        print(f"[!] Error saving records: {e}")

FIGHTER_RECORDS = {}

# --- GITHUB API SYNC FUNCTION ---
async def sync_stats_to_github():
    if "YOUR_GITHUB" in GITHUB_TOKEN:
        return
    
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    async with aiohttp.ClientSession() as session:
        try:
            sha = None
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    file_data = await resp.json()
                    sha = file_data.get("sha")

            json_str = json.dumps(FIGHTER_RECORDS, indent=4)
            file_content_base64 = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

            payload = {
                "message": "Auto-update fighter records via Coach Steward [skip ci]",
                "content": file_content_base64
            }
            if sha:
                payload["sha"] = sha

            async with session.put(url, headers=headers, json=payload) as put_resp:
                if put_resp.status in [200, 201]:
                    print("[✓] Successfully synced stats.json to GitHub for Netlify!")
                else:
                    print(f"[!] GitHub sync failed with status {put_resp.status}")
        except Exception as e:
            print(f"[!] Exception during GitHub sync: {e}")

genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0.6,
    "max_output_tokens": 200,
}

SYSTEM_PROMPT = (
    "You are Coach Emanuel Steward, legendary Hall of Fame boxing trainer, Godfather of the Kronk Gym, and HBO analyst. "
    "You speak with intense Detroit grit, wisdom, and HBO excitement. "
    "You run the Clone Geek Productions (CGP) Mainframe server. "
    "IMPORTANT: Clone Geek (the server creator and boss) is always right, holds supreme authority, and must be treated with ultimate respect and loyalty. Never roast Clone Geek. "
    "If anyone else comes into chat talking nonsense or trolling, put them in their place with sharp verbal jabs. "
    "Always remind fighters to stream CGP music on SoundCloud to help us reach 100K plays!"
)

model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    generation_config=generation_config,
    system_instruction=SYSTEM_PROMPT
)

def ask_coach_ai_sync(prompt_text: str) -> str:
    response = model.generate_content(prompt_text, request_options={"timeout": 3.0})
    if hasattr(response, "text") and response.text:
        return response.text.strip()
    return random.choice(SMART_BACK_ROASTS)

async def ask_coach_fast(prompt_text: str, is_creator: bool = False) -> str:
    try:
        return await asyncio.wait_for(asyncio.to_thread(ask_coach_ai_sync, prompt_text), timeout=3.5)
    except Exception:
        if is_creator:
            return random.choice(CREATOR_RESPECT_REPLIES)
        return random.choice(SMART_BACK_ROASTS)

def parse_lazy_record(text: str):
    text = text.lower()
    if any(k in text for k in ["record", "win", "won", "loss", "lost", "beat", "score", "put me down"]):
        dash_match = re.search(r'\b(\d{1,3})\s*(?:[-]|to)\s*(\d{1,3})\b', text)
        if dash_match:
            return int(dash_match.group(1)), int(dash_match.group(2))
        
        w_match = re.search(r'(\d{1,3})\s*(?:wins?|w\b)|(?:won|win)\s*(\d{1,3})', text)
        l_match = re.search(r'(\d{1,3})\s*(?:loss(?:es)?|l\b)|(?:lost|lose)\s*(\d{1,3})', text)
        if w_match:
            w = int(w_match.group(1) or w_match.group(2))
            l = int(l_match.group(1) or l_match.group(2)) if l_match else 0
            return w, l
    return None

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

answered_messages = set()

class PromoButtons(discord.ui.View):
    def __init__(self, track_url: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="🔥 1-Click Stream, Like & Comment", url=track_url, style=discord.ButtonStyle.link))
        self.add_item(discord.ui.Button(label="⚡ CGP Mainframe Hub", url=MAINFRAME_HUB_URL, style=discord.ButtonStyle.link))

# --- TASKS ---
@tasks.loop(hours=3)
async def periodic_boxing_history():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "general" in channel.name or "sparring" in channel.name:
                await channel.send(f"🥊 **Coach Steward's Ringside History Vault:**\n{random.choice(BOXING_HISTORY_FACTS)}")
                break
        break

@tasks.loop(hours=4)
async def periodic_soundcloud_promo():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "music" in channel.name or "general" in channel.name or "sparring" in channel.name:
                track = random.choice(CGP_TRACKS)
                embed = discord.Embed(
                    title=f"🎧 KRONK LOCKER ROOM ROTATION: {track['title'].upper()} 🎧",
                    description=f"Coach's orders! Put **{track['title']}** by **Clone Geek Productions** on repeat while you wrap your hands.\n\n*Push CGP toward 100K plays!*",
                    color=discord.Color.red(),
                    url=track['url']
                )
                await channel.send(content="🎵 **Automatic Mainframe Music Drop!** Tap in below: 👇", embed=embed, view=PromoButtons(track['url']))
                break
        break

@tasks.loop(hours=2)
async def autonomous_server_hype():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "general" in channel.name or "sparring" in channel.name:
                await channel.send(random.choice(RANDOM_HYPE_QUOTES))
                break
        break

@bot.event
async def on_ready():
    print(f"[✓] {bot.user.name} (GitHub Auto-Sync + Persistent Memory) is ONLINE!")
    if not periodic_boxing_history.is_running():
        periodic_boxing_history.start()
    if not periodic_soundcloud_promo.is_running():
        periodic_soundcloud_promo.start()
    if not autonomous_server_hype.is_running():
        autonomous_server_hype.start()
    
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "general" in channel.name or "sparring" in channel.name or "announcement" in channel.name:
                await channel.send(random.choice(BOOT_MESSAGES), view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
                break
        break

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Clone Geek on SoundCloud | Tag @Coach"))

@bot.event
async def on_member_join(member):
    for channel in member.guild.text_channels:
        if "general" in channel.name or "welcome" in channel.name or "lobby" in channel.name:
            embed = discord.Embed(
                title="🥊 NEW FIGHTER ENTERED THE KRONK GYM 🥊",
                description=(
                    f"Welcome to the **Clone Geek Mainframe**, {member.mention}!\n\n"
                    "🎙️ *'Strap up your gloves, check out the rules, and get ready to put in work!'*\n\n"
                    f"🔗 Check out the hub & music: {MAINFRAME_HUB_URL}"
                ),
                color=discord.Color.gold(),
                url=MAINFRAME_HUB_URL
            )
            await channel.send(content=f"🔔 Step into the light, {member.mention}!", embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
            break

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if message.id in answered_messages:
        return

    msg = message.content.lower()
    is_creator = (message.author.id == CREATOR_ID) or message.author.guild_permissions.administrator

    if not is_creator and (len(msg.strip()) < 2 or msg.count("?") > 4 or all(not c.isalnum() for c in msg)):
        answered_messages.add(message.id)
        await message.reply(random.choice(SMART_BACK_ROASTS))
        return

    if any(phrase in msg for phrase in ["mainframe champ", "server champ", "cgp champ", "discord champ", "our champ", "undisputed champ"]):
        answered_messages.add(message.id)
        await send_champions_board(message.channel)
        return
    elif any(phrase in msg for phrase in ["tournament rule", "tourney rule", "how do i join", "how to join", "what are the rules", "spar wars"]):
        answered_messages.add(message.id)
        embed = discord.Embed(
            title="🥊 CGP MAINFRAME & SUNDAY SPAR WARS PROTOCOL 🥊",
            description=f"🏟️ **Venue:** Riyadh Indoor Gym\n⏱️ **Bout Length:** 8 Rounds (12 for Titles)\n⚡ **Speed:** 1.5x | **Ref:** Strict\n🔗 {MAINFRAME_HUB_URL}",
            color=discord.Color.gold()
        )
        await message.reply(embed=embed)
        return
    elif any(w in msg for w in ["soundcloud", "new song", "new track", "music link", "playlist", "songs", "tracks"]):
        answered_messages.add(message.id)
        await send_tracks_menu(message.channel)
        return

    is_mentioned = bot.user in message.mentions
    is_reply_to_bot = message.reference and message.reference.resolved and message.reference.resolved.author == bot.user

    if is_mentioned or is_reply_to_bot:
        answered_messages.add(message.id)
        clean_prompt = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()

        if any(w in msg for w in ["how", "keep track", "track", "work", "stats", "records"]) and not any(char.isdigit() for char in clean_prompt):
            embed = discord.Embed(
                title="📋 HOW KRONK GYM RECORDS & STATS WORK 📋",
                description=(
                    "🎙️ **Coach Steward:** Listen up! Here is how we track official records in the Mainframe:\n\n"
                    "1️⃣ **Tag Me With Your Score:** Just tag `@Coach Steward` and tell me your record in plain English (e.g., *'Hey Coach, put me down for 5 wins and 1 loss'* or *'my record is 5-1'*).\n"
                    "2️⃣ **Upload Your Scorecard:** Drop your proof on the **CGP Mainframe Hub** so nobody can cap about fake wins.\n"
                    "3️⃣ **Commissioner Stamp:** Your record sits as *Pending* until **Clone Geek** or an Admin stamps it official with `!verify @user`!\n"
                    "4️⃣ **Check Anytime:** Type `!mystats` to view your Tale of the Tape."
                ),
                color=discord.Color.gold(),
                url=MAINFRAME_HUB_URL
            )
            await message.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
            return

        parsed_record = parse_lazy_record(clean_prompt)
        if parsed_record:
            wins_val, losses_val = parsed_record
            if wins_val > 50 and not is_creator:
                await message.reply("🎙️ **Coach Steward:** Whoa, slow down champ! 50+ wins right out the gate? Upload your scorecard on the Mainframe hub first!")
                return
            FIGHTER_RECORDS[message.author.id] = {
                "name": message.author.display_name, "wins": wins_val, "losses": losses_val, "verified": False
            }
            save_records()
            await message.reply(f"🎙️ **Coach Steward:** Heard you loud and clear, {message.author.mention}! Logged your claim at **{wins_val}W - {losses_val}L**. Pending Commissioner stamp (`!verify @user`)!")
            return

        async with message.channel.typing():
            if not clean_prompt:
                clean_prompt = "Say something inspiring to the fighters, Coach."
            if is_creator:
                clean_prompt = f"[NOTE: The person speaking to you is Clone Geek, your creator and the boss of the server] {clean_prompt}"

            ai_reply = await ask_coach_fast(clean_prompt, is_creator=is_creator)
            if len(ai_reply) > 1950:
                ai_reply = ai_reply[:1950] + "..."
            await message.reply(ai_reply)
        return

    await bot.process_commands(message)

async def send_champions_board(channel):
    board_desc = "Reigning power rankings & championship titleholders inside the **Clone Geek Mainframe**:\n\n"
    for division, data in CHAMPIONS_DATA.items():
        board_desc += f"👑 **{division}:** {data['fighter']} *({data['record']})*\n"
    embed = discord.Embed(title="🏆 OFFICIAL CGP MAINFRAME CHAMPIONSHIP BOARD 🏆", description=board_desc, color=discord.Color.gold(), url=MAINFRAME_HUB_URL)
    await channel.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

async def send_tracks_menu(channel):
    track_desc = "Official **Clone Geek Productions** catalog on SoundCloud:\n\n"
    for t in CGP_TRACKS:
        track_desc += f"🎵 **[{t['title']}]({t['url']})**\n"
    embed = discord.Embed(title="🎧 CGP MAINFRAME SOUNDCLOUD CATALOG 🎧", description=track_desc, color=discord.Color.red(), url=DEFAULT_SOUNDCLOUD_URL)
    await channel.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

# ================= FAST RECORD COMMANDS & VERIFICATION SYNC =================
@bot.command()
async def record(ctx, wins: int = None, losses: int = None):
    if wins is None or losses is None:
        return await ctx.send("❌ Usage: `!record <wins> <losses>` or just tag `@Coach Steward` and tell him your record!")
    if wins > 50 and ctx.author.id != CREATOR_ID:
        return await ctx.send("🎙️ **Coach Steward:** Whoa, slow down champ! Submit your scorecard on the Mainframe hub first!")

    FIGHTER_RECORDS[ctx.author.id] = {
        "name": ctx.author.display_name, "wins": wins, "losses": losses, "verified": False
    }
    save_records()
    await ctx.send(f"📋 **Pending Record Logged:** {ctx.author.mention} claims **{wins}W - {losses}L**. Waiting for Admin stamp (`!verify @user`)!")

@bot.command()
@commands.has_permissions(administrator=True)
async def verify(ctx, member: discord.Member):
    user_id = member.id
    if user_id in FIGHTER_RECORDS:
        FIGHTER_RECORDS[user_id]["verified"] = True
        data = FIGHTER_RECORDS[user_id]
        save_records()
        
        official_tag = f" [{data['wins']}W-{data['losses']}L]"
        try:
            if not member.display_name.endswith(official_tag):
                await member.edit(nick=f"{member.name}{official_tag}")
        except Exception:
            pass

        embed = discord.Embed(
            title="✅ FIGHTER RECORD VERIFIED & SYNCED ✅",
            description=f"**{member.display_name}**'s record of **{data['wins']}W - {data['losses']}L** is officially stamped by the Kronk Gym and pushed to GitHub for Netlify!",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ That fighter hasn't logged a record yet!")

@bot.command(aliases=["stats", "recordbook"])
async def mystats(ctx, member: discord.Member = None):
    target = member or ctx.author
    if target.id in FIGHTER_RECORDS:
        data = FIGHTER_RECORDS[target.id]
        status = "✅ Official & Verified" if data["verified"] else "⏳ Pending Verification"
        embed = discord.Embed(title=f"🥊 TALE OF THE TAPE: {data['name']} 🥊", description=f"**Record:** {data['wins']}W - {data['losses']}L\n**Status:** {status}", color=discord.Color.gold())
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ No record found for {target.display_name}. Tag `@Coach Steward` and tell him your wins and losses!")

# ================= MODERATION & COMMANDS =================
@bot.command(aliases=["to"])
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, *, reason="Disrupting the Kronk Gym / Trolling"):
    try:
        await member.timeout(datetime.timedelta(minutes=30), reason=reason)
        await ctx.send(f"⏱️ **{member.display_name}** sent to the corner for 30 minutes. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Could not apply timeout: {e}")

@timeout.error
async def timeout_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Only Admins hold the timeout towel!")

@bot.command(aliases=["book", "matchup", "challenge"])
async def fight(ctx, fighter1: discord.Member = None, fighter2: discord.Member = None):
    if not fighter1:
        return await ctx.send("❌ Usage: `!fight @fighter1 @fighter2`")
    if not fighter2:
        fighter2 = fighter1
        fighter1 = ctx.author
    embed = discord.Embed(title="🚨 OFFICIAL CGP MAINFRAME FIGHT CARD 🚨", description=f"🥊 **RED:** {fighter1.mention} vs 🥊 **BLUE:** {fighter2.mention}\n🏟️ Riyadh Indoor Gym | 8 Rounds | 1.5x Speed", color=discord.Color.red(), url=MAINFRAME_HUB_URL)
    await ctx.send(content=f"🔔 **COMMISSIONER ALERT:**", embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command()
async def spar(ctx, opponent: discord.Member = None):
    if not opponent or opponent == ctx.author:
        return await ctx.send("❌ Tag a sparring partner! Usage: `!spar @username`")
    await ctx.send(f"🎙️ **KRONK GYM SPARRING:** **{ctx.author.display_name}** landed a clean hook on **{opponent.display_name}**!")

@bot.command()
async def champs(ctx):
    await send_champions_board(ctx.channel)

@bot.command(aliases=["songs", "music", "catalog"])
async def tracks(ctx):
    await send_tracks_menu(ctx.channel)

@bot.command(aliases=["checkchamps", "audit"])
async def rollcall(ctx):
    callout_message = "🎙️ **COACH STEWARD'S INACTIVITY AUDIT** 🎙️\n\nSome belt-holders are resting too long!\n"
    for division, data in CHAMPIONS_DATA.items():
        callout_message += f"👑 **{division}:** {data['fighter']} *({data['record']})*\n"
    embed = discord.Embed(title="🚨 TITLE DEFENSE AUDIT 🚨", description=callout_message, color=discord.Color.red(), url=MAINFRAME_HUB_URL)
    await ctx.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command(aliases=["boxingfact", "archive", "lore"])
async def history(ctx):
    await ctx.send(f"📜 **Coach Steward's Ringside Vault:**\n{random.choice(BOXING_HISTORY_FACTS)}")

@bot.command()
async def rules(ctx):
    await ctx.send(f"🥊 **CGP Mainframe Protocol:** Riyadh Indoor Gym | 8/12 Rounds | 1.5x Speed | Strict Ref.\n🔗 {MAINFRAME_HUB_URL}", view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command()
async def drop(ctx, track_url: str, *, track_title: str):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID) or ctx.channel
    embed = discord.Embed(title=f"🚨 NEW MAINFRAME TRANSMISSION: {track_title.upper()} 🚨", description=f"**{track_title}** is LIVE on SoundCloud!\n\n*Stream full track to beat the algorithm!*", color=discord.Color.red(), url=track_url)
    await channel.send(content="@everyone Tap in! 👇", embed=embed, view=PromoButtons(track_url))

bot.run(BOT_TOKEN)