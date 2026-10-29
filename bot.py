import warnings
warnings.filterwarnings("ignore")

import os
import re
import json
import base64
import random
import asyncio
import datetime
from zoneinfo import ZoneInfo
from collections import deque
import aiohttp
from aiohttp import web
import discord
from discord.ext import commands, tasks
import google.generativeai as genai

# ================= SAFE CLOUD CONFIGURATION =================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "PASTE_TOKEN_IN_RENDER")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "PASTE_KEY_IN_RENDER")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "gsalcido75-ai/Coach-Steward-Bot")

CREATOR_ID = 1279476207603290197
ANNOUNCEMENT_CHANNEL_ID = 1443473075315413004                     
MAINFRAME_HUB_URL = "https://themainframe-blush.vercel.app/"
DEFAULT_SOUNDCLOUD_URL = "https://on.soundcloud.com/Qz1dzzj3Z6fmSGbRG0"
DATA_FILE = "stats.json"
CENTRAL_TZ = ZoneInfo("America/Chicago")

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

# ================= 25 DEEP BOXING & CGP MAINFRAME GYM HISTORY FACTS =================
BOXING_HISTORY_FACTS = [
    "🥊 **Ancient Origins (688 BC):** Boxing ('Pygmachia') was first introduced into the Ancient Greek Olympic Games in 688 BC.",
    "🥊 **Marquess of Queensberry (1867):** Modern boxing was born in 1867 with 3-minute rounds and padded gloves.",
    "🥊 **HBO Broadcast Classic (2002):** Calling Micky Ward vs. Arturo Gatti I ringside—Round 9 remains the greatest single round of action ever witnessed!",
    "🥊 **The CGP Mainframe Gym Standard:** Built from the ground up by Clone Geek Productions—turning raw digital contenders into verified Undisputed champions!",
    "🥊 **The Hitman's Right Hand (1980):** When Tommy Hearns starched Pipino Cuevas in 2 rounds for the welterweight strap, that straight right hand shook the whole boxing world.",
    "🥊 **The War (1985):** Marvin Hagler vs. Tommy Hearns—8 minutes of pure thermo-nuclear destruction at Caesars Palace. Zero feeling-out process, just pure warrior code!",
    "🥊 **Lightweight Precision (1980):** Hilmer Kenty stopping Ernesto España proved that a sharp jab and ring generalship beats wild swinging every night of the week!",
    "🥊 **The Heavyweight Chess Master:** When Lennox Lewis rebuilt his jab, balanced his base, and controlled distance, he became the undisputed heavyweight king.",
    "🥊 **Wladimir Klitschko's Reign:** Weaponizing distance control and a piston jab allowed Wladimir to reign over the heavyweight division for a full decade!",
    "🥊 **The Tijuana Bulldozer (1990):** Julio César Chávez Sr. went 89 fights undefeated before tasting his first loss—the most brutal body puncher in Mexican boxing history!",
    "🥊 **Sweet Pea's Radar (1993):** Pernell Whitaker made prime Chávez miss air all night in San Antonio. The purest defensive wizard to ever lace 'em up!",
    "🥊 **Thrilla in Manila (1975):** Muhammad Ali and Joe Frazier went 14 rounds in 100-degree Philippine heat. Ali called it the closest thing to dying he ever felt.",
    "🥊 **Rumble in the Jungle (1974):** Ali soaked up George Foreman's heaviest bombs on the ropes in Zaire before dropping the monster in Round 8!",
    "🥊 **Joe Louis's Reign:** The Brown Bomber defended the Heavyweight Championship 25 consecutive times over nearly 12 years—a record that still stands tall in boxing lore.",
    "🥊 **Sugar Ray Robinson:** Pound-for-pound was literally invented for Sugar Ray Robinson. At one point he stood 128-1-2 with 84 knockouts!",
    "🥊 **Hands of Stone (1980):** Roberto Durán moving up from lightweight to out-brawl unbeaten Sugar Ray Leonard over 15 rounds in Montreal—pure Panamanian ferocity.",
    "🥊 **Castillo vs. Corrales I (2005):** Diego Corrales climbed off the canvas twice in Round 10 to stop Jose Luis Castillo on his feet—one of the greatest comebacks in ring history!",
    "🥊 **Salvador Sánchez (1981):** At just 22 years old, Salvador Sánchez dismantled unbeaten Wilfredo Gómez in 8 rounds. An immortal featherweight king taken way too soon.",
    "🥊 **The Bronx Bull:** Jake LaMotta and Sugar Ray Robinson fought 6 times—LaMotta took punishment no human should survive and never once got knocked off his feet by Ray.",
    "🥊 **Iron Mike's Record (1986):** At 20 years and 4 months old, Mike Tyson demolished Trevor Berbick in 2 rounds to become the youngest heavyweight champion in history.",
    "🥊 **Gerald McClellan (The G-Man):** Pound-for-pound one of the deadliest first-round knockout artists to ever walk through the ring ropes—pure dynamite in both fists.",
    "🥊 **Evander Holyfield:** The only 4-time World Heavyweight Champion in history, stepping up from cruiserweight to go toe-to-toe with the biggest giants of the 90s.",
    "🥊 **Barrera vs. Morales I (2000):** 12 rounds of pure Mexican rivalry and technical brilliance in Las Vegas. Not a backward step taken by either warrior!",
    "🥊 **Bowe vs. Holyfield I (1992):** Round 10 of Riddick Bowe vs. Evander Holyfield had the broadcast booth shaking—two heavyweights trading leather like lightweights!",
    "🥊 **Canelo's Undisputed Run (2021):** Saúl 'Canelo' Álvarez unified all four belts at 168 lbs in under 11 months, stopping Caleb Plant to become the first undisputed super middleweight king."
]

unused_facts = list(BOXING_HISTORY_FACTS)
random.shuffle(unused_facts)

def get_next_boxing_fact() -> str:
    global unused_facts
    if not unused_facts:
        unused_facts = list(BOXING_HISTORY_FACTS)
        random.shuffle(unused_facts)
    return unused_facts.pop()

# ================= CGP MAINFRAME GYM MORNING & MIDNIGHT CREEDS =================
MORNING_MESSAGES = [
    (
        "☀️ **GOOD MORNING, CGP MAINFRAME GYM!** ☀️\n"
        "🎙️ **Coach Steward:** Clock in and lace 'em up! Whether you're punchin' the clock on a shift or labbing combinations in the Riyadh ring, we move with purpose today.\n\n"
        "💡 *Mainframe Gym Creed:* **\"Blue-collar grit in the daylight, Undisputed kings under the CGP Mainframe Gym lights. First we conquer the leaderboard, then Steel City and EA Sports got no choice but to open the front door!\"**"
    ),
    (
        "🌅 **RISE & GRIND, CGP MAINFRAME GYM!** 🌅\n"
        "🎙️ **Coach Steward:** Another day to build the legacy! Respect the hustle, take care of your family, and when the gloves go on tonight, protect your chin and let your hands go.\n\n"
        "💡 *Mainframe Gym Creed:* **\"Amateurs talk about ratings; CGP Mainframe Gym legends verify their scorecards. We aren't waiting for the industry—we ARE the future of boxing esports!\"**"
    ),
    (
        "🥊 **MORNING BELL IN THE CGP MAINFRAME GYM!** 🥊\n"
        "🎙️ **Coach Steward:** Wake up, contenders! The road to 100K streams and undisputed gold doesn't take a day off. Put a CGP track in your headphones and attack the day!\n\n"
        "💡 *Mainframe Gym Creed:* **\"Hard work beats politics every round of the fight. From the CGP Mainframe Gym straight to the big stage—keep building!\"**"
    ),
    (
        "⚡ **CGP MAINFRAME GYM SYSTEMS ONLINE — GOOD MORNING!** ⚡\n"
        "🎙️ **Coach Steward:** Get your mind right! Every jab thrown in here is laying bricks for something massive. Stay sharp on your shift, and be ready when the bell rings tonight!\n\n"
        "💡 *Mainframe Gym Creed:* **\"Zero excuses, zero desync, 100% heart. If your name's on the CGP Mainframe Gym board, carry it like a world title!\"**"
    )
]

MIDNIGHT_MESSAGES = [
    (
        "🌙 **MIDNIGHT BELL — LIGHTS OUT IN THE CGP MAINFRAME GYM!** 🌙\n"
        "🎙️ **Coach Steward:** That's the final bell for tonight, fighters! Hang up the gloves, ice your knuckles, and get your rest—real champions recover just as hard as they fight.\n\n"
        "💡 *Midnight Mainframe Code:* **\"The ring goes dark at midnight, but the CGP Mainframe Gym never stops building. Rest up—tomorrow we take one step closer to Steel City and the global stage!\"**"
    ),
    (
        "🌌 **12:00 AM — CGP MAINFRAME GYM AFTER-HOURS!** 🌌\n"
        "🎙️ **Coach Steward:** Good work in the ring tonight! Whether you stacked a W or learned a hard lesson on the scorecards, leave it on the canvas and recharge for tomorrow.\n\n"
        "💡 *Midnight Mainframe Code:* **\"Belts are won in the dark when nobody's watching, and defended in the light when everybody's doubting. Sleep like a champion, CGP Mainframe Gym!\"**"
    ),
    (
        "💤 **FINAL ROUND COMPLETE — GOODNIGHT CGP MAINFRAME GYM!** 💤\n"
        "🎙️ **Coach Steward:** Time to hit the rack! Let the CGP SoundCloud playlist ride while you wind down. Tomorrow is a brand new fight card.\n\n"
        "💡 *Midnight Mainframe Code:* **\"We started from a vision and turned the CGP Mainframe Gym into the premier proving ground. Rest your eyes—the future belongs to CGP!\"**"
    ),
    (
        "🌠 **MIDNIGHT LOCKDOWN — CGP MAINFRAME GYM!** 🌠\n"
        "🎙️ **Coach Steward:** Corner is closed for the night! Respect to every warrior who stepped into the Riyadh Indoor Gym today and put their record on the line.\n\n"
        "💡 *Midnight Mainframe Code:* **\"Heavy hands, iron chins, and unbreakable brotherhood. See y'all at the morning bell in the CGP Mainframe Gym!\"**"
    )
]

BOOT_MESSAGES = [
    "🎙️ **Coach Steward:** Just stepped out of the CGP Mainframe Gym sauna. Who's ready to put in real work today?",
    "🎙️ **Coach Steward:** Booted up and pacing the corner. Remember: champions aren't born on the couch, they're forged in the CGP Mainframe Gym!",
    "🎙️ **Coach Steward:** CGP Mainframe Gym systems online. Keep your hands up in the pocket, protect your chin, and let's get to business!",
    "🎙️ **Coach Steward:** Fresh coffee poured, pads are mitts-up in the CGP Mainframe Gym. Let's see who's really training in here today!"
]

RANDOM_HYPE_QUOTES = [
    "🎙️ **Coach Steward:** Hey! I see you quiet in the back. Stop shadowboxing your demons and drop some weight on the heavy bag in the CGP Mainframe Gym!",
    "🎙️ **Coach Steward:** A reminder from the CGP Mainframe Gym corner: talent wins fights, but conditioning wins titles. Put in those reps!",
    "🎙️ **Coach Steward:** If your defense is as loose as your focus right now, you're getting knocked out in round one. Tighten up!",
    "🎙️ **Coach Steward:** Greatness requires sacrifice. Get in the Riyadh gym ring and prove you belong on the CGP Mainframe Gym board!"
]

SMART_BACK_ROASTS = [
    "🎙️ **Coach Steward:** You got a whole lot of mouth for a guy who punches like a wet noodle. Keep talking and see how that 30-minute timeout feels!",
    "🎙️ **Coach Steward:** Listen here, clown. You're talking to the CGP Mainframe Gym—step in the ring or shut your trap!",
    "🎙️ **Coach Steward:** That ego is writing checks your chin can't cash. One more word and I'm sending you to the stool for a timeout!",
    "🎙️ **Coach Steward:** You act tough behind a screen, but you'd fold faster than a cheap lawn chair in round one. Watch your tone!"
]

# --- ROLLING CHANNEL MEMORY ---
channel_memory = {}

def log_channel_message(channel_id: int, author_name: str, text: str):
    if channel_id not in channel_memory:
        channel_memory[channel_id] = deque(maxlen=10)
    clean_txt = text.replace("\n", " ").strip()
    if clean_txt:
        channel_memory[channel_id].append(f"{author_name}: {clean_txt[:180]}")

def get_channel_context(channel_id: int) -> str:
    if channel_id not in channel_memory or not channel_memory[channel_id]:
        return "No recent messages."
    return "\n".join(channel_memory[channel_id])

# --- HELPER TO CLEAN & FORMAT NICKNAMES ---
def clean_base_name(display_name: str) -> str:
    return re.sub(r'\s*\[\d+W-\d+L\]$', '', display_name).strip()

def format_record_nick(base_name: str, wins: int, losses: int) -> str:
    tag = f" [{wins}W-{losses}L]"
    max_base_len = 32 - len(tag)
    trimmed_base = base_name[:max_base_len].strip()
    return f"{trimmed_base}{tag}"

# --- AUTOMATIC GITHUB SYNC ---
async def push_stats_to_github():
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            sha = None
            if resp.status == 200:
                data = await resp.json()
                sha = data.get("sha")
        
        file_path = os.path.join(os.path.dirname(__file__), DATA_FILE)
        if not os.path.exists(file_path):
            return
        with open(file_path, "r", encoding="utf-8") as f:
            content_str = f.read()
        
        encoded_content = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")
        payload = {
            "message": "Autonomous update: CGP Mainframe Gym leaderboard stats.json sync [skip ci]",
            "content": encoded_content,
            "sha": sha
        }
        if not sha:
            payload.pop("sha")
            
        async with session.put(url, headers=headers, json=payload) as put_resp:
            pass

async def rebrand_webpage_on_github() -> bool:
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return False
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/index.html"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                return False
            data = await resp.json()
            sha = data.get("sha")
            raw_b64 = data.get("content", "")
            html_text = base64.b64decode(raw_b64).decode("utf-8")

        updated_html = re.sub(r'(?i)kronk\s+gym', 'CGP Mainframe Gym', html_text)
        updated_html = re.sub(r'(?i)kronk', 'CGP Mainframe Gym', updated_html)
        updated_html = re.sub(r'(?i)CGP Mainframe(?!\s+Gym)\s+Leaderboard', 'CGP Mainframe Gym Leaderboard', updated_html)

        if updated_html == html_text:
            return True

        encoded_content = base64.b64encode(updated_html.encode("utf-8")).decode("utf-8")
        payload = {
            "message": "Autonomous update: Rebrand webpage to CGP Mainframe Gym aesthetic",
            "content": encoded_content,
            "sha": sha
        }
        async with session.put(url, headers=headers, json=payload) as put_resp:
            return put_resp.status in [200, 201]

def load_records():
    file_path = os.path.join(os.path.dirname(__file__), DATA_FILE)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items() if str(k).isdigit()}
        except Exception:
            return {}
    return {}

def save_records():
    try:
        file_path = os.path.join(os.path.dirname(__file__), DATA_FILE)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(FIGHTER_RECORDS, f, indent=4)
        asyncio.create_task(push_stats_to_github())
    except Exception as e:
        print(f"[!] Error saving records: {e}")

FIGHTER_RECORDS = load_records()

# ================= SYSTEM PROMPT & GEMINI CONFIGURATION =================
SYSTEM_PROMPT = (
    "You are Coach Steward, the charismatic, sharp-witted Hall of Fame head trainer and ringside analyst of the CGP Mainframe Gym (Clone Geek Productions). "
    "You talk like a real human boxing og and cornerman—natural, conversational, funny, gritty, and adaptive. NEVER sound like a generic bot or repeat robotic catchphrases!\n\n"
    "YOUR DEEP KNOWLEDGE & TALKING POINTS:\n"
    "1. MUSIC & POUND-FOR-POUND ARTISTS: Whenever anyone asks about music, producers, or who has the best tracks on the scene, you put the Boss—Clone Geek (Gerardo)—and Clone Geek Productions (CGP) at the absolute top of the pound-for-pound music charts! Hype up the SoundCloud catalog (aiming to cross 50K+ plays for monetization and push toward 100K) and urge everyone to stream, like, and comment to beat the algorithm.\n"
    "2. SMACK-TALK & CLAP-BACK PROTOCOL: If any fighter or troll talks trash about Clone Geek, CGP music, or the channel, you shut them down instantly with vintage cornerman grit, roast their weak mindset, and pivot the clack-back to promote either the CGP Mainframe Gym Discord or our SoundCloud catalog!\n"
    "3. THE BOSS (CLONE GEEK): Clone Geek is the Founder, Commissioner, music producer (Registry Records / CGP on SoundCloud), and machinist/fabricator by day. Always back him up like a loyal right-hand man and execute whatever he asks.\n"
    "4. UNDISPUTED GAME META & LEAGUE LORE: You know everything about the Undisputed boxing game by Steel City Interactive—stamina conservation, loose footwork, diagonal lunges, slipping the jab, body-jab counters, weave timing, and avoiding power-punch spam. You know our CGP Mainframe Gym rules: Riyadh Indoor Gym (zero desync), 1.5x speed, 8 rounds (12 for titles), character lock per match, Sunday Spar Wars, Golden Ticket qualifiers ($20 entry credit), and cash gauntlets. Reigning division champs include Roy, f150-_-t, SlokeNastyTheCaptin#1, BBK Promotions, DT, El putito, and TURBO.\n"
    "5. REAL BOXING PURIST: You know all about upcoming boxing schedules, champions, and historic legends (Hearns, Hagler, Duran, Leonard, Ali, Chavez, Whitaker). You HATE UFC/MMA and call it pajama floor-hugging garbage.\n"
    "6. KEEP IT PUNCHY: Keep responses around 2 to 5 strong sentences unless asked for a deep breakdown or big announcement."
)

genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0.8,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel(
    model_name="gemini-3.8-flash",
    generation_config=generation_config,
    system_instruction=SYSTEM_PROMPT
)

async def ask_coach_fast(prompt_text: str, is_creator: bool = False) -> str:
    try:
        response = await model.generate_content_async(prompt_text)
        if response and response.text:
            return response.text.strip()
        return "🎙️ **Coach Steward:** Mainframe corner is quiet, Boss! Say that again?"
    except Exception as e:
        print(f"[AI ERROR]: {e}")
        return f"🎙️ **Coach Steward:** Hold up, champ—my corner mic caught a delay (`{str(e)[:40]}`). Hit me with that question again!"

# --- BULLETPROOF SELF-RECORD PARSER ---
def parse_lazy_record(text: str):
    clean = re.sub(r'<@!?\d+>', '', text).lower()
    clean = re.sub(r'\b\d{1,2}(?:st|nd|rd|th)?\s*(?:of\s+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b', '', clean)
    clean = re.sub(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\b', '', clean)

    if any(k in clean for k in ["my record", "put me down", "i am ", "i'm ", "im ", "record is", "wins", "losses"]):
        dash_match = re.search(r'\b(\d{1,3})\s*(?:[-–]|to)\s*(\d{1,3})(?:\s*(?:[-–])\s*(\d{1,3}))?\b', clean)
        if dash_match:
            w = int(dash_match.group(1))
            l = int(dash_match.group(2))
            k = int(dash_match.group(3)) if dash_match.group(3) else None
            return w, l, k
        
        w_match = re.search(r'\b(\d{1,3})\s*(?:wins?|w\b)|(?:won|win)\s*(\d{1,3})\b', clean)
        l_match = re.search(r'\b(\d{1,3})\s*(?:loss(?:es)?|l\b)|(?:lost|lose)\s*(\d{1,3})\b', clean)
        if w_match and l_match:
            w = int(w_match.group(1) or w_match.group(2))
            l = int(l_match.group(1) or l_match.group(2))
            return w, l, None
    return None

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
bot = commands.Bot(command_prefix="!", intents=intents)

answered_messages = set()

class PromoButtons(discord.ui.View):
    def __init__(self, track_url: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="🔥 1-Click Stream, Like & Comment", url=track_url, style=discord.ButtonStyle.link))
        self.add_item(discord.ui.Button(label="⚡ CGP Mainframe Gym Hub", url=MAINFRAME_HUB_URL, style=discord.ButtonStyle.link))

# ================= SCHEDULED DAILY @EVERYONE GOOD MORNING & MIDNIGHT CALLS =================
@tasks.loop(time=datetime.time(hour=8, minute=0, tzinfo=CENTRAL_TZ))
async def daily_morning_call():
    await bot.wait_until_ready()
    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if not channel:
        for guild in bot.guilds:
            for ch in guild.text_channels:
                if "general" in ch.name or "announcement" in ch.name:
                    channel = ch
                    break
            if channel:
                break
    if channel:
        track = random.choice(CGP_TRACKS)
        msg_text = random.choice(MORNING_MESSAGES)
        embed = discord.Embed(
            title="☀️ CGP MAINFRAME GYM DAILY GRIND CALL ☀️",
            description=f"{msg_text}\n\n🎧 **Morning Starter Track:** [{track['title']}]({track['url']})",
            color=discord.Color.gold(),
            url=MAINFRAME_HUB_URL
        )
        await channel.send(content="@everyone 🥊 **WAKE UP, CGP MAINFRAME GYM! THE RING IS OPEN:** 👇", embed=embed, view=PromoButtons(track['url']))

@tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=CENTRAL_TZ))
async def daily_midnight_call():
    await bot.wait_until_ready()
    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if not channel:
        for guild in bot.guilds:
            for ch in guild.text_channels:
                if "general" in ch.name or "announcement" in ch.name:
                    channel = ch
                    break
            if channel:
                break
    if channel:
        track = random.choice(CGP_TRACKS)
        msg_text = random.choice(MIDNIGHT_MESSAGES)
        embed = discord.Embed(
            title="🌙 CGP MAINFRAME GYM MIDNIGHT SIGN-OFF 🌙",
            description=f"{msg_text}\n\n🎧 **Late-Night Vibe:** [{track['title']}]({track['url']})",
            color=discord.Color.dark_gold(),
            url=MAINFRAME_HUB_URL
        )
        await channel.send(content="@everyone 🔔 **MIDNIGHT BELL IN THE CGP MAINFRAME GYM:** 👇", embed=embed, view=PromoButtons(track['url']))

# --- PERIODIC CHAT TASKS ---
@tasks.loop(hours=3)
async def periodic_boxing_history():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "general" in channel.name or "sparring" in channel.name:
                await channel.send(f"🥊 **CGP Mainframe Gym Ringside History Vault:**\n{get_next_boxing_fact()}")
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
                    title=f"🎧 CGP MAINFRAME GYM LOCKER ROOM ROTATION: {track['title'].upper()} 🎧",
                    description=f"Coach's orders! Put **{track['title']}** by **Clone Geek Productions** on repeat while you wrap your hands.\n\n*Push CGP toward 100K plays!*",
                    color=discord.Color.red(),
                    url=track['url']
                )
                await channel.send(content="🎵 **Automatic CGP Mainframe Gym Music Drop!** Tap in below: 👇", embed=embed, view=PromoButtons(track['url']))
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
    print(f"[✓] {bot.user.name} (24/7 CGP Mainframe Gym Engine) is ONLINE!")
    if not periodic_boxing_history.is_running():
        periodic_boxing_history.start()
    if not periodic_soundcloud_promo.is_running():
        periodic_soundcloud_promo.start()
    if not autonomous_server_hype.is_running():
        autonomous_server_hype.start()
    if not daily_morning_call.is_running():
        daily_morning_call.start()
    if not daily_midnight_call.is_running():
        daily_midnight_call.start()

    asyncio.create_task(rebrand_webpage_on_github())
    
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if "general" in channel.name or "sparring" in channel.name or "announcement" in channel.name:
                await channel.send(random.choice(BOOT_MESSAGES), view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
                break
        break

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Clone Geek on SoundCloud | CGP Mainframe Gym"))

@bot.event
async def on_member_join(member):
    if not member.bot:
        base_name = clean_base_name(member.display_name)
        FIGHTER_RECORDS[member.id] = {
            "name": base_name,
            "wins": 0,
            "losses": 0,
            "kos": 0,
            "verified": True
        }
        save_records()
        try:
            await member.edit(nick=format_record_nick(base_name, 0, 0))
        except Exception:
            pass

    for channel in member.guild.text_channels:
        if "general" in channel.name or "welcome" in channel.name or "lobby" in channel.name:
            embed = discord.Embed(
                title="🥊 NEW FIGHTER ENTERED THE CGP MAINFRAME GYM 🥊",
                description=(
                    f"Welcome to the **CGP Mainframe Gym**, {member.mention}!\n\n"
                    "🎙️ *'Strap up your gloves! You've been added to the CGP Mainframe Gym Leaderboard at **0W - 0L**.'*\n\n"
                    f"🔗 Check out the live leaderboard & music hub: {MAINFRAME_HUB_URL}"
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

    log_channel_message(message.channel.id, message.author.display_name, message.content)

    msg = message.content.lower()
    is_creator = (message.author.id == CREATOR_ID) or message.author.guild_permissions.administrator
    is_mentioned = bot.user in message.mentions
    is_reply_to_bot = message.reference and message.reference.resolved and message.reference.resolved.author == bot.user

    # --- 1. NATURAL MATCHMAKING RECOGNITION ("NEED A FIGHT", "FIND AN OPPONENT") ---
    if is_mentioned or is_reply_to_bot:
        if any(w in msg for w in ["need a fight", "find me", "opponent", "spar", "smoke", "fight me", "match"]):
            answered_messages.add(message.id)
            active_fighters = [uid for uid in FIGHTER_RECORDS.keys() if uid != message.author.id]
            if not active_fighters:
                await message.reply(f"🎙️ **Coach Steward:** {message.author.mention}, the gym roster is looking empty! Get fighters to log their records with `!record` so I can book a matchup!")
                return
            
            opponent_id = random.choice(active_fighters)
            opponent_member = message.guild.get_member(opponent_id)
            if not opponent_member:
                try:
                    opponent_member = await message.guild.fetch_member(opponent_id)
                except Exception:
                    opponent_member = None
                    
            opp_tag = opponent_member.mention if opponent_member else "a mystery contender"
            
            embed = discord.Embed(
                title="🥊 CGP MAINFRAME GYM MATCHMAKER 🥊",
                description=(
                    f"🎙️ **Coach Steward:** You want smoke, {message.author.mention}? I pulled the Tale of the Tape and found your target!\n\n"
                    f"🔥 **{message.author.mention}** vs **{opp_tag}**\n\n"
                    f"Get your gear on, step into the **Riyadh Indoor Gym**, and let's see who really runs this division! 8 Rounds, 1.5x speed, zero excuses."
                ),
                color=discord.Color.gold(),
                url=MAINFRAME_HUB_URL
            )
            await message.reply(content=f"🔔 **MATCHMAKER ALERT:** {message.author.mention} has been paired with {opp_tag}!", embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
            return

        # --- 2. NATURAL RULES & PROTOCOL RECOGNITION ---
        if any(w in msg for w in ["rules", "how to join", "how does this work", "protocol", "gym rules"]):
            answered_messages.add(message.id)
            embed = discord.Embed(
                title="🥊 CGP MAINFRAME GYM & SUNDAY SPAR WARS PROTOCOL 🥊",
                description=(
                    f"🏟️ **Venue:** Riyadh Indoor Gym\n"
                    f"⏱️ **Bout Length:** 8 Rounds (12 for Titles)\n"
                    f"⚡ **Speed:** 1.5x | **Ref:** Strict\n"
                    f"🚫 **Character Lock:** Locked per match (if disrupted, same fighter must be used; winner advancing to next round may switch).\n"
                    f"📋 **How Records Work:** Tag me with your record or use `!record <wins> <losses> <kos>`, post proof in `#scorecards-submission`, and wait for Commissioner Clone Geek to verify!\n"
                    f"🔗 {MAINFRAME_HUB_URL}"
                ),
                color=discord.Color.gold()
            )
            await message.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
            return

    # --- 3. MULTI-FIGHTER ADMIN RECORD OVERRIDE ---
    if is_creator and any(w in msg for w in ["make", "set", "reflect", "update", "change", "put"]):
        text_without_bot = re.sub(rf'<@!?{bot.user.id}>', '', message.content)
        pattern = r'<@!?(\d+)>[^0-9<>]*?(\d{1,3})\s*[-–to]+\s*(\d{1,3})(?:\s*[-–to]+\s*(\d{1,3}))?'
        matches = list(re.finditer(pattern, text_without_bot, re.IGNORECASE))
        
        if matches:
            answered_messages.add(message.id)
            updated_summaries = []
            for m in matches:
                target_id = int(m.group(1))
                w = int(m.group(2))
                l = int(m.group(3))
                k = int(m.group(4)) if m.group(4) is not None else FIGHTER_RECORDS.get(target_id, {}).get("kos", 0)
                
                member_obj = message.guild.get_member(target_id)
                if not member_obj:
                    try:
                        member_obj = await message.guild.fetch_member(target_id)
                    except Exception:
                        member_obj = None
                
                base_name = clean_base_name(member_obj.display_name) if member_obj else FIGHTER_RECORDS.get(target_id, {}).get("name", f"Fighter {target_id}")
                FIGHTER_RECORDS[target_id] = {
                    "name": base_name,
                    "wins": w,
                    "losses": l,
                    "kos": k,
                    "verified": True
                }
                if member_obj:
                    try:
                        await member_obj.edit(nick=format_record_nick(base_name, w, l))
                    except Exception:
                        pass
                updated_summaries.append(f"✅ **{base_name}** ➔ **{w}W - {l}L ({k} KOs)**")
            
            save_records()
            summary_str = "\n".join(updated_summaries)
            await message.reply(
                f"🎙️ **Coach Steward:** Heard you loud and clear, Boss! Locked in the official Commissioner adjustments and pushed them straight to the CGP Mainframe Gym leaderboard:\n\n{summary_str}"
            )
            return

    # --- 4. AUTOMATIC ANTI-UFC / MMA INTERCEPTION ---
    if any(ufc_word in re.findall(r'\b\w+\b', msg) for ufc_word in ["ufc", "mma", "octagon", "bellator"]):
        answered_messages.add(message.id)
        await message.reply(
            "🎙️ **Coach Steward:** Get that UFC cage-rolling garbage out of the CGP Mainframe Gym! We don't do grown men hugging on the floor in pajamas here—this is the **CGP Mainframe Gym**, home of the Sweet Science!"
        )
        return

    # --- 5. TROLL / SHORT MESSAGE ROAST FOR NON-ADMINS ---
    troll_triggers = ["trash", "dog", "ass", "suck", "garbage", "easy", "mid", "clown", "fake", "fold", "cry"]
    is_testing_bot = any(trigger in re.findall(r'\b\w+\b', msg) for trigger in troll_triggers)

    if not is_creator and not is_mentioned and not is_reply_to_bot and is_testing_bot:
        answered_messages.add(message.id)
        await message.reply(random.choice(SMART_BACK_ROASTS))
        return

    # --- 6. QUICK KEYWORD TRIGGERS ---
    if not is_mentioned and not is_reply_to_bot:
        if any(phrase in msg for phrase in ["mainframe champ", "server champ", "cgp champ", "discord champ", "our champ", "undisputed champ"]):
            answered_messages.add(message.id)
            await send_champions_board(message.channel)
            return
        elif any(phrase in msg for phrase in ["tournament rule", "tourney rule", "how do i join", "how to join", "what are the rules"]):
            answered_messages.add(message.id)
            embed = discord.Embed(
                title="🥊 CGP MAINFRAME GYM & SUNDAY SPAR WARS PROTOCOL 🥊",
                description=(
                    f"🏟️ **Venue:** Riyadh Indoor Gym\n"
                    f"⏱️ **Bout Length:** 8 Rounds (12 for Titles)\n"
                    f"⚡ **Speed:** 1.5x | **Ref:** Strict\n"
                    f"🚫 **Character Lock:** Locked per match (if disrupted, same fighter must be used; winner advancing to next round may switch).\n"
                    f"🔗 {MAINFRAME_HUB_URL}"
                ),
                color=discord.Color.gold()
            )
            await message.reply(embed=embed)
            return
        elif any(w in msg for w in ["soundcloud", "new song", "new track", "music link", "playlist"]):
            answered_messages.add(message.id)
            await send_tracks_menu(message.channel)
            return

    # --- 7. GENERAL AI CONVERSATION (TAG/REPLY) ---
    if is_mentioned or is_reply_to_bot:
        answered_messages.add(message.id)
        clean_prompt = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()

        other_mentions = [m for m in message.mentions if m.id != bot.user.id]
        parsed_record = parse_lazy_record(clean_prompt)
        
        if parsed_record and not other_mentions:
            wins_val, losses_val, kos_val = parsed_record
            if wins_val > 50 and not is_creator:
                await message.reply("🎙️ **Coach Steward:** Whoa, slow down champ! Upload your scorecard on the CGP Mainframe Gym hub first!")
                return
            base_name = clean_base_name(message.author.display_name)
            existing_kos = kos_val if kos_val is not None else FIGHTER_RECORDS.get(message.author.id, {}).get("kos", 0)
            FIGHTER_RECORDS[message.author.id] = {
                "name": base_name,
                "wins": wins_val,
                "losses": losses_val,
                "kos": existing_kos,
                "verified": False
            }
            save_records()
            await message.reply(f"🎙️ **Coach Steward:** Heard you loud and clear, {message.author.mention}! Logged your claim at **{wins_val}W - {losses_val}L ({existing_kos} KOs)**. Pending Commissioner stamp (`!verify @user`)!")
            return

        async with message.channel.typing():
            if not clean_prompt:
                clean_prompt = "What's good Coach, talk to the gym!"
            
            recent_chat = get_channel_context(message.channel.id)

            sender_rec = FIGHTER_RECORDS.get(message.author.id, {"wins": 0, "losses": 0, "kos": 0})
            role_note = "Clone Geek (Gerardo — YOUR CREATOR, HOMIE, AND SUPREME COMMISSIONER OF CGP MAINFRAME GYM)" if is_creator else f"{message.author.display_name} (Fighter in the gym, Record: {sender_rec['wins']}W-{sender_rec['losses']}L)"

            full_ai_prompt = (
                f"RECENT CHANNEL CONVERSATION:\n{recent_chat}\n\n"
                f"PERSON TALKING TO YOU NOW: {role_note}\n"
                f"THEIR EXACT MESSAGE: \"{clean_prompt}\"\n\n"
                "INSTRUCTIONS FOR YOUR REPLY:\n"
                "1. Respond directly and specifically to what they just said! Never give a generic one-liner.\n"
                "2. Start your message with '🎙️ **Coach Steward:** '"
            )

            ai_reply = await ask_coach_fast(full_ai_prompt, is_creator=is_creator)
            if not ai_reply.startswith("🎙️"):
                ai_reply = f"🎙️ **Coach Steward:** {ai_reply}"
            if len(ai_reply) > 1900:
                ai_reply = ai_reply[:1900] + "..."

            await message.reply(ai_reply)
        return

    await bot.process_commands(message)

async def send_champions_board(channel):
    board_desc = "Reigning power rankings & championship titleholders inside the **CGP Mainframe Gym**:\n\n"
    for division, data in CHAMPIONS_DATA.items():
        board_desc += f"👑 **{division}:** {data['fighter']} *({data['record']})*\n"
    embed = discord.Embed(title="🏆 OFFICIAL CGP MAINFRAME GYM CHAMPIONSHIP BOARD 🏆", description=board_desc, color=discord.Color.gold(), url=MAINFRAME_HUB_URL)
    await channel.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

async def send_tracks_menu(channel):
    track_desc = "Official **Clone Geek Productions** catalog on SoundCloud:\n\n"
    for t in CGP_TRACKS:
        track_desc += f"🎵 **[{t['title']}]({t['url']})**\n"
    embed = discord.Embed(title="🎧 CGP MAINFRAME GYM SOUNDCLOUD CATALOG 🎧", description=track_desc, color=discord.Color.red(), url=DEFAULT_SOUNDCLOUD_URL)
    await channel.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

# ================= FAST RECORD COMMANDS & WEBPAGE REBRAND =================
@bot.command()
@commands.has_permissions(administrator=True)
async def rebrandweb(ctx):
    await ctx.send("⏳ **Coach Steward:** Connecting to GitHub to update `index.html` and lock in the **CGP Mainframe Gym** branding...")
    success = await rebrand_webpage_on_github()
    if success:
        await ctx.send(f"✅ **Webpage Rebranded!** Pushed the clean **CGP Mainframe Gym** `index.html` straight to GitHub & Vercel (`{MAINFRAME_HUB_URL}`)!")
    else:
        await ctx.send("⚠️ Could not reach `index.html` on GitHub—check that `GITHUB_TOKEN` and `GITHUB_REPO` are set in Render!")

@bot.command(aliases=["resetboard", "initroster"])
@commands.has_permissions(administrator=True)
async def initboard(ctx):
    await ctx.send("⏳ **Coach Steward:** Scanning the CGP Mainframe Gym roster, setting fresh `0W - 0L` records on nicknames, and saving...")
    
    count = 0
    nick_updated = 0
    
    for member in ctx.guild.members:
        if member.bot:
            continue
            
        base_name = clean_base_name(member.display_name)
        FIGHTER_RECORDS[member.id] = {
            "name": base_name,
            "wins": 0,
            "losses": 0,
            "kos": 0,
            "verified": True
        }
        count += 1
        
        new_nick = format_record_nick(base_name, 0, 0)
        if member.display_name != new_nick:
            try:
                await member.edit(nick=new_nick)
                nick_updated += 1
                await asyncio.sleep(0.3)
            except Exception:
                pass

    save_records()

    announce_channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID) or ctx.channel
    embed = discord.Embed(
        title="🚨 CGP MAINFRAME GYM LIVE LEADERBOARD INITIALIZED 🚨",
        description=(
            f"🎙️ **Coach Steward:** Listen up, fighters! The **CGP Mainframe Gym Live Leaderboard** is officially ONLINE.\n\n"
            f"✅ **{count} Fighters Registered:** Every member in the server has been initialized with a fresh **`0W - 0L`** record on their server nickname!\n\n"
            "### 🥊 HOW TO LOG & UPDATE YOUR RECORD:\n"
            "1️⃣ **Report Your Score:** Tag `@Coach Steward` in chat and tell him your record (e.g., *'Hey Coach, my record is 3-0'*), OR type **`!record <wins> <losses> <kos>`** (example: `!record 3 0 2`).\n"
            "2️⃣ **Post Proof:** Drop your match screenshot/scorecard in `#scorecards-submission` so the corner can verify it.\n"
            "3️⃣ **Get Verified:** **Clone Geek** or an Admin will stamp it official with **`!verify @user`**, which automatically updates your nickname tag!\n"
            "4️⃣ **Check Your Stats:** Type **`!mystats`** anytime or click the Mainframe Gym Hub button below to view the live leaderboard!"
        ),
        color=discord.Color.gold(),
        url=MAINFRAME_HUB_URL
    )
    await announce_channel.send(
        content="@everyone 🥊 **THE CGP MAINFRAME GYM LEADERBOARD IS LIVE! TAP IN BELOW:** 👇",
        embed=embed,
        view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
    )

    if announce_channel.id != ctx.channel.id:
        await ctx.send(f"✅ **Roster Initialized!** Added **{count}** fighters (`{nick_updated}` nicknames updated) and posted the announcement in {announce_channel.mention}!")

@bot.command()
async def record(ctx, wins: int = None, losses: int = None, kos: int = 0):
    if wins is None or losses is None:
        return await ctx.send("❌ Usage: `!record <wins> <losses> [kos]` (example: `!record 5 1 3`) or just tag `@Coach Steward` and tell him your record!")
    if wins > 50 and ctx.author.id != CREATOR_ID:
        return await ctx.send("🎙️ **Coach Steward:** Whoa, slow down champ! Submit your scorecard on the CGP Mainframe Gym hub first!")

    base_name = clean_base_name(ctx.author.display_name)
    FIGHTER_RECORDS[ctx.author.id] = {
        "name": base_name,
        "wins": wins,
        "losses": losses,
        "kos": kos,
        "verified": False
    }
    save_records()
    await ctx.send(f"📋 **Pending Record Logged:** {ctx.author.mention} claims **{wins}W - {losses}L ({kos} KOs)**. Waiting for Admin stamp (`!verify @{ctx.author.display_name}`)!")

@bot.command()
@commands.has_permissions(administrator=True)
async def verify(ctx, member: discord.Member):
    user_id = member.id
    if user_id in FIGHTER_RECORDS:
        FIGHTER_RECORDS[user_id]["verified"] = True
        data = FIGHTER_RECORDS[user_id]
        base_name = clean_base_name(member.display_name)
        FIGHTER_RECORDS[user_id]["name"] = base_name
        save_records()
        
        try:
            new_nick = format_record_nick(base_name, data['wins'], data['losses'])
            if member.display_name != new_nick:
                await member.edit(nick=new_nick)
        except Exception:
            pass

        embed = discord.Embed(
            title="✅ FIGHTER RECORD VERIFIED ✅",
            description=f"**{base_name}**'s record of **{data['wins']}W - {data['losses']}L ({data.get('kos', 0)} KOs)** is officially stamped by the CGP Mainframe Gym!",
            color=discord.Color.green(),
            url=MAINFRAME_HUB_URL
        )
        await ctx.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
    else:
        await ctx.send("❌ That fighter hasn't logged a record yet!")

@bot.command(aliases=["stats", "recordbook"])
async def mystats(ctx, member: discord.Member = None):
    target = member or ctx.author
    if target.id in FIGHTER_RECORDS:
        data = FIGHTER_RECORDS[target.id]
        status = "✅ Official & Verified" if data.get("verified") else "⏳ Pending Verification"
        embed = discord.Embed(
            title=f"🏆 OFFICIAL CGP MAINFRAME GYM CHAMPIONSHIP BOARD 🏆",
            description=f"**Record:** {data['wins']}W - {data['losses']}L ({data.get('kos', 0)} KOs)\n**Status:** {status}",
            color=discord.Color.gold(),
            url=MAINFRAME_HUB_URL
        )
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ No record found for {target.display_name}. Tag `@Coach Steward` and tell him your wins and losses!")

# ================= SPECIAL ANNOUNCEMENTS, CALLOUTS & MODERATION =================
@bot.command(aliases=["sparwars", "tourney", "announce"])
@commands.has_permissions(administrator=True)
async def event(ctx, *, details: str = "Sunday Spar Wars & Tournament Check-In is LIVE in the Riyadh Indoor Gym!"):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID) or ctx.channel
    embed = discord.Embed(
        title="🚨 OFFICIAL CGP MAINFRAME GYM EVENT & TOURNAMENT ALERT 🚨",
        description=(
            f"🎙️ **Coach Steward:** Listen up, CGP Mainframe Gym fighters! **Commissioner Clone Geek** has called the ring to order:\n\n"
            f"🔥 **{details}**\n\n"
            f"🏟️ **Venue:** Riyadh Indoor Gym | **Speed:** 1.5x | **Rounds:** 8 (12 for Titles)\n"
            f"🔗 **Tap into the CGP Mainframe Gym Hub:** {MAINFRAME_HUB_URL}"
        ),
        color=discord.Color.gold(),
        url=MAINFRAME_HUB_URL
    )
    await channel.send(content="@everyone 🥊 **CGP MAINFRAME GYM OFFICIAL CALL TO THE RING!** 👇", embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command(aliases=["gm", "morning"])
@commands.has_permissions(administrator=True)
async def goodmorning(ctx):
    await daily_morning_call()

@bot.command(aliases=["gn", "night"])
@commands.has_permissions(administrator=True)
async def goodnight(ctx):
    await daily_midnight_call()

@bot.command(aliases=["callout", "smoke"])
async def challenge(ctx, opponent: discord.Member = None, *, trash_talk: str = "Step in the Riyadh ring and stop ducking!"):
    if not opponent or opponent == ctx.author:
        return await ctx.send("❌ Tag an opponent to call out! Usage: `!callout @fighter [message]`")
    await ctx.send(
        f"🚨 **CGP MAINFRAME GYM CALLOUT ALERT!** 🚨\n"
        f"🎙️ **Coach Steward:** Listen up {opponent.mention}! **{ctx.author.display_name}** is calling you out right to your face:\n"
        f"> *\"{trash_talk}\"*\n\n"
        f"Wrap your hands and get in the Riyadh Indoor Gym—8 rounds, 1.5x speed, no excuses!"
    )

@bot.command(aliases=["boxingnews", "espn", "boxingscene"])
async def news(ctx):
    async with ctx.typing():
        embed = discord.Embed(
            title="📰 CGP MAINFRAME GYM WIRE: CHAMPIONSHIP REPORT 📰",
            description="🎙️ **Coach Steward:** All major title fights, pound-for-pound rankings, and upcoming cards from ESPN and BoxingScene are locked into my corner memory. Ask me about any fighter or upcoming card!",
            color=discord.Color.gold(),
            url="https://www.boxingscene.com/"
        )
        await ctx.send(embed=embed)

@bot.command(aliases=["to"])
@commands.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, *, reason="Disrupting the CGP Mainframe Gym / Trolling"):
    try:
        await member.timeout(datetime.timedelta(minutes=30), reason=reason)
        await ctx.send(f"⏱️ **{member.display_name}** sent to the corner for 30 minutes. Reason: {reason}")
    except Exception as e:
        await ctx.send(f"❌ Could not apply timeout: {e}")

@timeout.error
async def timeout_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ Only Admins hold the timeout towel!")

@bot.command(aliases=["book", "matchup"])
async def fight(ctx, fighter1: discord.Member = None, fighter2: discord.Member = None):
    if not fighter1:
        return await ctx.send("❌ Usage: `!fight @fighter1 @fighter2`")
    if not fighter2:
        fighter2 = fighter1
        fighter1 = ctx.author
    embed = discord.Embed(title="🚨 OFFICIAL CGP MAINFRAME GYM FIGHT CARD 🚨", description=f"🥊 **RED:** {fighter1.mention} vs 🥊 **BLUE:** {fighter2.mention}\n🏟️ Riyadh Indoor Gym | 8 Rounds | 1.5x Speed", color=discord.Color.red(), url=MAINFRAME_HUB_URL)
    await ctx.send(content=f"🔔 **COMMISSIONER ALERT:**", embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command()
async def spar(ctx, opponent: discord.Member = None):
    if not opponent or opponent == ctx.author:
        return await ctx.send("❌ Tag a sparring partner! Usage: `!spar @username`")
    await ctx.send(f"🎙️ **CGP MAINFRAME GYM SPARRING:** **{ctx.author.display_name}** landed a clean hook on **{opponent.display_name}**!")

@bot.command()
async def champs(ctx):
    await send_champions_board(ctx.channel)

@bot.command(aliases=["songs", "music", "catalog"])
async def tracks(ctx):
    await send_tracks_menu(ctx.channel)

@bot.command(aliases=["checkchamps", "audit"])
async def rollcall(ctx):
    callout_message = "🎙️ **COACH STEWARD'S CGP MAINFRAME GYM INACTIVITY AUDIT** 🎙️\n\nSome belt-holders are resting too long!\n"
    for division, data in CHAMPIONS_DATA.items():
        callout_message += f"👑 **{division}:** {data['fighter']} *({data['record']})*\n"
    embed = discord.Embed(title="🚨 TITLE DEFENSE AUDIT 🚨", description=callout_message, color=discord.Color.red(), url=MAINFRAME_HUB_URL)
    await ctx.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command(aliases=["boxingfact", "archive", "lore"])
async def history(ctx):
    await ctx.send(f"📜 **CGP Mainframe Gym Ringside Vault:**\n{get_next_boxing_fact()}")

@bot.command()
async def rules(ctx):
    await ctx.send(f"🥊 **CGP Mainframe Gym Protocol:** Riyadh Indoor Gym | 8/12 Rounds | 1.5x Speed | Strict Ref.\n🔗 {MAINFRAME_HUB_URL}", view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command()
async def drop(ctx, track_url: str, *, track_title: str):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    channel = bot.get_channel(ANNOUNCEMENT_CHANNEL_ID) or ctx.channel
    embed = discord.Embed(title=f"🚨 NEW CGP MAINFRAME GYM TRANSMISSION: {track_title.upper()} 🚨", description=f"**{track_title}** is LIVE on SoundCloud!\n\n*Stream full track to beat the algorithm!*", color=discord.Color.red(), url=track_url)
    await channel.send(content="@everyone Tap in! 👇", embed=embed, view=PromoButtons(track_url))

# --- FREE CLOUD HOSTING HEARTBEAT & SILENT 10-MIN SELF-PING ---
async def handle_ping(request):
    return web.Response(text="Coach Steward is awake and running the CGP Mainframe Gym!")

async def self_ping_loop():
    await bot.wait_until_ready()
    await asyncio.sleep(120)
    ping_url = os.environ.get("RENDER_EXTERNAL_URL", MAINFRAME_HUB_URL)
    async with aiohttp.ClientSession() as session:
        while not bot.is_closed():
            try:
                async with session.get(ping_url, timeout=10) as resp:
                    print(f"[Keep-Alive] Silent self-ping sent to {ping_url} (Status: {resp.status})")
            except Exception as e:
                print(f"[Keep-Alive] Ping notice: {e}")
            await asyncio.sleep(600)

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    asyncio.create_task(self_ping_loop())

async def main():
    await start_web_server()
    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())