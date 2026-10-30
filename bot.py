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
from collections import deque, defaultdict
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
    "Heavyweight": {"fighter": "Roy🇲🇽🇲🇽🇲🇽", "record": "14W - 0L - 0D"},
    "Cruiserweight": {"fighter": "f150-_-t", "record": "11W - 2L - 0D"},
    "Light Heavyweight": {"fighter": "SlokeNastyTheCaptin#1🇺🇸🇲🇽", "record": "12W - 1L - 0D"},
    "Middleweight": {"fighter": "BBK Promotions 🪪", "record": "9W - 3L - 0D"},
    "Women's Welterweight": {"fighter": "DT", "record": "8W - 1L - 0D"},
    "Welterweight": {"fighter": "OPEN", "record": "0W - 0L - 0D"},
    "Lightweight": {"fighter": "El putito", "record": "10W - 4L - 0D"},
    "Bantamweight": {"fighter": "Roy🇲🇽🇲🇽🇲🇽 (Dual-Division King!)", "record": "14W - 0L - 0D"},
    "Women's Lightweight": {"fighter": "TURBO", "record": "7W - 2L - 0D"}
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

# ================= EXPANDED FRESH HYPE & ACTIVE LISTENER VAULTS =================
RANDOM_HYPE_QUOTES = [
    "🎙️ **Coach Steward:** Hey! I see you quiet in the back. Stop shadowboxing your demons and drop some weight on the heavy bag in the CGP Mainframe Gym!",
    "🎙️ **Coach Steward:** A reminder from the CGP Mainframe Gym corner: talent wins fights, but conditioning wins titles. Put in those reps!",
    "🎙️ **Coach Steward:** Remember the house rule: **No scorecard in `#scorecards-submission`, no official stats on the board!** Upload your proof so Commissioner Clone Geek can stamp your record!",
    "🎙️ **Coach Steward:** Greatness requires sacrifice. Get in the Riyadh gym ring and prove you belong on the CGP Mainframe Gym board!",
    "🎙️ **Coach Steward:** Don't come crying to the corner about a split-decision draw if you didn't work the body in the early rounds! Stamina is king in the CGP Mainframe Gym!",
    "🎙️ **Coach Steward:** Everybody wants to hold the belt until it's time to do 12 rounds at 1.5x speed in the Riyadh Indoor Gym. Who's really built for this?!",
    "🎙️ **Coach Steward:** Keep that lead hand active! A lazy jab in Undisputed is an open invitation for a slip-counter straight to the chin!",
    "🎙️ **Coach Steward:** Check the leaderboard on the Mainframe Hub! If your name still says `0W - 0L`, stop window-shopping and call somebody out with `!callout`!",
    "🎙️ **Coach Steward:** While y'all are warming up your thumbs, make sure you got **Clone Geek Productions** spinning in `#-music-channel-`. Real fighters train to real music!",
    "🎙️ **Coach Steward:** Ring generalship isn't about running marathon laps around the canvas—plant your feet, cut off the ring, and make 'em trade leather!",
    "🎙️ **Coach Steward:** I can tell who's been skipping roadwork just by watching how y'all gas out by Round 5! Conserve your stamina bar and pick your shots!",
    "🎙️ **Coach Steward:** Blue-collar work ethic all day, every day. From the shop floor to the CGP Mainframe Gym, we don't take shortcuts—we take titles!",
    "🎙️ **Coach Steward:** You got a scorecard sitting in your gallery? Drop that screenshot in `#scorecards-submission` so we can track your real Wins, Losses, Draws, and KOs!",
    "🎙️ **Coach Steward:** Watch that power-punch spam! Any halfway decent counter-puncher in this gym will time that wind-up and put you to sleep!",
    "🎙️ **Coach Steward:** The road to 100,000 streams and undisputed gold runs right through this Discord. Tap into the SoundCloud catalog and keep the momentum rolling!"
]

ORGANIC_CHAT_INTERJECTIONS = [
    "🎙️ **Coach Steward:** Facts! Mindset and ring IQ are 90% of the battle before you ever step through the ropes. Keep talking that real boxing talk!",
    "🎙️ **Coach Steward:** I hear y'all chopping it up in here! Just remember—talk is cheap until the scorecard gets uploaded to `#scorecards-submission`. Lace 'em up and prove it!",
    "🎙️ **Coach Steward:** Now that's what I like to hear in the locker room. Iron sharpens iron in the **CGP Mainframe Gym**—just don't forget to protect your chin!",
    "🎙️ **Coach Steward:** Listen to y'all cooking up game plans! Put a **Clone Geek Productions** track on in the background while you lab those combinations!",
    "🎙️ **Coach Steward:** Let me drop my two cents from the corner: footwork and stamina control beat wild swinging ten times out of ten. Keep studying the craft!",
    "🎙️ **Coach Steward:** Y'all got the gym buzzing today! Who's stepping up to put their verified record on the line next?"
]

SMALL_TALK_REPLIES = [
    "🎙️ **Coach Steward:** Doing legendary, champ! Got fresh coffee in my cup, the mitts strapped on, and **Clone Geek Productions** booming on the gym speakers. How's your weight cut looking today?",
    "🎙️ **Coach Steward:** Can't complain when the **CGP Mainframe Gym** is running at peak performance! Feeling sharp and ready to verify some scorecards. You stepping in the ring today?",
    "🎙️ **Coach Steward:** Living the dream in the corner, homie! Watching the leaderboard climb and pushing our SoundCloud catalog past 60K+ plays. How are your hands feeling?",
    "🎙️ **Coach Steward:** Ten toes down and locked in! Another day building the premier Undisputed proving ground with the Boss. What's on your fight card today?"
]

MUSIC_LINK_INTERCEPTIONS = [
    (
        "🎙️ **Coach Steward:** Hold the phone—I see somebody dropping media links in the locker room! Respect the vibe, "
        "but don't forget who runs the pound-for-pound booth in this building! Make sure you tap into **Clone Geek Productions** on SoundCloud right after that and run those plays up!"
    ),
    (
        "🎙️ **Coach Steward:** Peeped that link drop! After you check that out, cleanse your ears with some real championship audio from **Clone Geek (Registry Records)**. "
        "Hit that 1-Click Stream button below and help us blow past our next SoundCloud milestone!"
    ),
    (
        "🎙️ **Coach Steward:** Oh, we sharing tracks and videos in the gym now? Bet! Just remember the house rule: for every clip you drop, "
        "you owe **Clone Geek Productions** a full spin on *Road to Undisputed* or *CGP Syndicate*! Tap the link below!"
    )
]

SPAM_WARNING_LINES = [
    "🧹 **Coach Steward:** Hold up, {user}! Stop flooding the **CGP Mainframe Gym** chat like a panicked amateur throwing blind windmills! Save that rapid-fire energy for the Riyadh ring!",
    "🧹 **Coach Steward:** Easy on the keyboard spam, {user}! I just swept those junk messages off the canvas. Breathe, pace your stamina, and type like a contender!",
    "🧹 **Coach Steward:** Flag on the play, {user}! No spamming the locker room walls on my watch. Next time you flood the chat, I'm throwing the 30-minute timeout towel!"
]

MEMBER_LEAVE_ROASTS = [
    "🎙️ **Coach Steward:** Welp, looks like **{name}** couldn't handle the heat in the **CGP Mainframe Gym** and threw in the towel early! Another contender ducking the Riyadh smoke! 🦆🥊",
    "🎙️ **Coach Steward:** **{name}** just snuck out the back door of the gym with their gym bag! Guess that 1.5x speed in the Riyadh Indoor Gym was too fast for 'em!",
    "🎙️ **Coach Steward:** Ring the bell—**{name}** just left the building! Everybody talks tough until it's time to upload a real scorecard on the **CGP Mainframe Gym** board!"
]

SOUNDBOARD_CUE_LIBRARY = {
    "bell": "🔔 *DING! DING! DING!* **[G9 MIXER CUE: RINGSIDE ROUND BELL]** — Touch gloves and come out swinging!",
    "horn": "📢 *BRRRRRR-BRRRRRR-BRRRRRR!* **[G9 MIXER CUE: CHAMPIONSHIP AIRHORN]** — Certified CGP Mainframe Gym classic!",
    "ko": "💥 *BOOM! DOWN GOES THE CONTENDER!* **[G9 MIXER CUE: HEAVY KNOCKOUT IMPACT]** — Somebody call the ringside doctor!",
    "towel": "🏳️ *SWISH!* **[G9 MIXER CUE: CORNER THROWS IN THE TOWEL]** — Stop the fight, he's got nothing left in the tank!",
    "crowd": "🏟️ *ROOOOOOAAARRR!* **[G9 MIXER CUE: RIYADH ARENA CROWD ERUPTS]** — The whole building is on their feet!"
}

COACH_PLAYBOOK_TEXT = (
    "🎙️ **Coach Steward:** Listen up, contenders! I am the Hall of Fame Head Trainer, Matchmaker, and Official Scorekeeper of the **CGP Mainframe Gym**, built by **Commissioner Clone Geek**.\n\n"
    "### 🥊 WHY I'M IN THIS CORNER:\n"
    "• **Verified Scorecard & Draw Database:** I track every official **Win, Loss, Draw, and KO** in the gym and sync them straight to the live website. *(Must upload match proof in `#scorecards-submission` to get verified!)*\n"
    "• **Instant Matchmaking & Tale of the Tape:** Need smoke? I pair up fighters and pull head-to-head stat breakdowns.\n"
    "• **Dedicated Channel Broadcasts:** I drop CGP music in `#-music-channel-`, boxing history in `#the-elite-feed`, and corner hype in `#coaches-corner` while keeping `#system-sparring` ready for live action!\n"
    "• **24/7 Gym Security:** I automatically sweep out chat flood spam, roast quitters, and enforce the Sweet Science.\n\n"
    "### 📋 FIGHTER COMMAND PLAYBOOK:\n"
    "• **`!guide`** *(or `!commands` / `!helpme`)* — Pull up this official CGP Mainframe Gym playbook.\n"
    "• **`!record <W> <L> [D] [KO]`** *(or tag me with your record)* — Log your Wins, Losses, Draws, and KOs.\n"
    "• **`!mystats [@fighter]`** — Pull up any fighter's verified scorecard (including Draws & KOs).\n"
    "• **`!callout @fighter [trash talk]`** — Call someone out with a live Tale of the Tape!\n"
    "• **`!fight @fighter1 @fighter2`** — Compare two fighters head-to-head on the Tale of the Tape.\n"
    "• **`@Coach Steward find me a fight`** — Let me pick an opponent for you.\n"
    "• **`!champs`** — View Reigning Division Champions & Top 10 Contenders.\n"
    "• **`!nextevent`** — Check the official Discord Tournament & Spar Wars schedule.\n"
    "• **`!rules`** — View Riyadh Indoor Gym settings & Scorecard Verification rules.\n"
    "• **`!tracks`** — Pull up the full CGP SoundCloud catalog.\n"
    "• **`!sfx <bell | horn | ko | towel | crowd>`** — Trigger the ringside G9 Soundboard!\n\n"
    "👑 **Commissioner Commands:** `!initboard`, `!verify @user`, `!event`, `!sweep <#>`, `!timeout @user`"
)

unused_facts = []
unused_hype = []

def get_next_boxing_fact() -> str:
    global unused_facts
    if not unused_facts:
        unused_facts = list(BOXING_HISTORY_FACTS)
        random.shuffle(unused_facts)
    return unused_facts.pop()

def get_next_hype_quote() -> str:
    global unused_hype
    if not unused_hype:
        unused_hype = list(RANDOM_HYPE_QUOTES)
        random.shuffle(unused_hype)
    return unused_hype.pop()

# ================= CGP MAINFRAME GYM MORNING & MIDNIGHT CREEDS =================
MORNING_MESSAGES = [
    (
        "☀️ **GOOD MORNING, CGP MAINFRAME GYM!** ☀️\n"
        "🎙️ **Coach Steward:** Clock in and lace 'em up! Whether you're punchin' the clock on a shift or labbing combinations in the Riyadh ring, we move with purpose today.\n\n"
        "💡 *Mainframe Gym Creed:* **\"Blue-collar grit in the daylight, Undisputed kings under the CGP Mainframe Gym lights. First we conquer the leaderboard, then Steel City and EA Sports got no choice but to open the front door!\"**"
    ),
    (
        "🌅 **RISE & GRIND, CGP MAINFRAME GYM!** 🌅\n"
        "🎙️ **Coach Steward:** Another day to build the legacy! Respect the hustle, take care of your family, and when the gloves go on tonight, protect your chin and upload those scorecards.\n\n"
        "💡 *Mainframe Gym Creed:* **\"Amateurs talk about ratings; CGP Mainframe Gym legends verify their scorecards in `#scorecards-submission`. We aren't waiting for the industry—we ARE the future of boxing esports!\"**"
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
        "🎙️ **Coach Steward:** Good work in the ring tonight! Whether you stacked a W, battled to a draw, or learned a hard lesson on the scorecards, leave it on the canvas and recharge for tomorrow.\n\n"
        "💡 *Midnight Mainframe Code:* **\"Belts are won in the dark when nobody's watching, and defended in the light when everybody's doubting. Sleep like a champion, CGP Mainframe Gym!\"**"
    ),
    (
        "💤 **FINAL ROUND COMPLETE — GOODNIGHT CGP MAINFRAME GYM!** 💤\n"
        "🎙️ **Coach Steward:** Time to hit the rack! Let the CGP SoundCloud playlist ride while you wind down. Tomorrow is a brand new fight card.\n\n"
        "💡 *Midnight Mainframe Code:* **\"We started from a vision and turned the CGP Mainframe Gym into the premier proving ground. Rest your eyes—the future belongs to CGP!\"**"
    ),
    (
        "🌠 **MIDNIGHT LOCKDOWN — CGP MAINFRAME GYM!** 🌠\n"
        "🎙️ **Coach Steward:** Corner is closed for the night! Respect to every warrior who stepped into the Riyadh Indoor Gym today and uploaded their scorecards.\n\n"
        "💡 *Midnight Mainframe Code:* **\"Heavy hands, iron chins, and unbreakable brotherhood. See y'all at the morning bell in the CGP Mainframe Gym!\"**"
    )
]

BOOT_MESSAGES = [
    "🎙️ **Coach Steward:** Just stepped into `#coaches-corner` fresh out of the CGP Mainframe Gym sauna. Who's ready to put in real work and upload some scorecards today?",
    "🎙️ **Coach Steward:** Booted up and pacing `#coaches-corner`. Remember: no scorecard in `#scorecards-submission`, no verified stats on the board!",
    "🎙️ **Coach Steward:** CGP Mainframe Gym systems online. Music is pumping in `#-music-channel-`, history is dropping in `#the-elite-feed`, and the ring is open!",
    "🎙️ **Coach Steward:** Fresh coffee poured, pads are mitts-up in the CGP Mainframe Gym. Let's see who's really training in here today!"
]

# --- INSTANT LOCAL PROMO & ROAST VAULTS (ZERO API CALLS) ---
MUSIC_FLEX_RESPONSES = [
    (
        "🎙️ **Coach Steward:** You really asking who got the best music on the scene right now?! Look at the top of the pound-for-pound charts, champ—it's **Clone Geek Productions (Registry Records)** all day! "
        "From *Road to Undisputed* to *CGP Syndicate* and *Amber Nights*, the Boss is dropping pure heat while running the **CGP Mainframe Gym**. "
        "Quit playing and go run those SoundCloud streams past 50K+ so we cash these checks!"
    ),
    (
        "🎙️ **Coach Steward:** Best music in the game? That isn't even a split decision—**Clone Geek** owns the booth just like we own the Riyadh ring! "
        "We're already sitting over 60K+ total catalog plays and pushing straight for 100K. Tap the button below, stream a track all the way through, and support the **CGP Mainframe Gym**!"
    ),
    (
        "🎙️ **Coach Steward:** Man, turn off whatever elevator music you've been listening to! **Clone Geek Productions** got the hardest boom-bap and fight anthems on the planet. "
        "Lock into the **CGP Mainframe Gym** Discord and hit that SoundCloud link below so we blow past 50,000 plays on the single!"
    )
]

SMACK_TALK_CLAPBACKS = [
    (
        "🎙️ **Coach Steward:** Boy, your chin is way too glass to be talking reckless in here! While you're busy typing with butterfingers, **Clone Geek** and the **CGP Mainframe Gym** are building an empire. "
        "Step into the Riyadh Indoor Gym and prove it on a verified scorecard, or go stream our SoundCloud catalog and learn what a real winner sounds like!"
    ),
    (
        "🎙️ **Coach Steward:** Listen to this keyboard contender! You couldn't bust a grape in a fruit fight, let alone talk smack on **Clone Geek Productions**! "
        "This is the **CGP Mainframe Gym**—either put your record on the line in the ring, or tap into the SoundCloud link below before I hit you with a 30-minute corner timeout!"
    ),
    (
        "🎙️ **Coach Steward:** You got a lot of mouth for somebody with zero footwork and negative ring IQ! Nobody disrespects the Boss or the **CGP Mainframe Gym** on my watch. "
        "Go humble yourself, stream *Road to Undisputed* on SoundCloud to help us push past 50K+, and come back when you know how to throw a clean jab!"
    ),
    (
        "🎙️ **Coach Steward:** That ego is writing checks your stamina bar can't cash! You're standing in the premier Undisputed proving ground built by **Clone Geek**. "
        "Show some respect to the **CGP Mainframe Gym**, or lace 'em up right now so the whole Discord can watch you fold in round one!"
    )
]

CONFUSED_SLANG_RESPONSES = [
    "🎙️ **Coach Steward:** Speak up, champ! Did you take one too many left hooks to the temple? Try that again in plain English—or type `!guide` if you're lost in the gym!",
    "🎙️ **Coach Steward:** Come again? You're mumbling like you still got your mouthpiece stuck in your teeth! Spit it out or go hit the heavy bag!",
    "🎙️ **Coach Steward:** I don't know what kind of dizzy combination you just typed, homie, but if you need a fight, say *'find me a match'*—and if you need the realest music out, tap that CGP SoundCloud link!"
]

CREW_BANTER = {
    "undertaker": [
        "🎙️ **Coach Steward:** Hold up, let me talk real slow so **Undertaker** can keep up... Lace. Up. Your. Gloves. And. Tap. The. SoundCloud. Link. Below! 😂🥊",
        "🎙️ **Coach Steward:** Look out, **Undertaker** is in the building moving at 0.5x speed! Somebody pour some cold water on his neck and get him in the Riyadh ring!"
    ],
    "hymas": [
        "🎙️ **Coach Steward:** Oh look, **Hymas** is lurking in the gym! Welcome back from probation—now stop spamming the locker room and go defend your name in the Riyadh Indoor Gym!",
        "🎙️ **Coach Steward:** I see you **Hymas**! Don't think you can sneak past the corner without putting in rounds today. Keep the chat clean and lace 'em up!"
    ],
    "rafa": [
        "🎙️ **Coach Steward:** **Rafa**! Back in the building! Quit sweet-talking the crowd in chat and step through the ropes—let's see if your hands are moving as fast as your fingers today!",
        "🎙️ **Coach Steward:** Yo **Rafa**, the heavy bag has been calling your name all day. Get in the ring and run up that CGP SoundCloud playlist while you work!"
    ],
    "knuckle": [
        "🎙️ **Coach Steward:** **KnuckleUpFoo** always asking the tough questions from ringside! You already know how we rock in the **CGP Mainframe Gym**—keep keeping these contenders on their toes!"
    ]
}

# --- ROLLING CHANNEL MEMORY & SPAM TRACKER ---
channel_memory = {}
user_spam_tracker = defaultdict(lambda: deque(maxlen=6))
last_organic_chime = 0.0

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

# --- HELPER TO CLEAN & FORMAT NICKNAMES (4-PART W-L-D-KO FORMAT) ---
def clean_base_name(display_name: str) -> str:
    return re.sub(r'\s*\[\d+W-\d+L(?:-\d+D)?(?:-\d+K)?\]$', '', display_name).strip()

def format_record_nick(base_name: str, wins: int, losses: int, draws: int = 0, kos: int = 0) -> str:
    tag = f" [{wins}W-{losses}L-{draws}D-{kos}K]"
    max_base_len = 32 - len(tag)
    trimmed_base = base_name[:max_base_len].strip()
    return f"{trimmed_base}{tag}"

# --- SMART CHANNEL ROUTER HELPERS ---
def get_coaches_corner_channel(guild):
    for ch in guild.text_channels:
        if any(k in ch.name.lower() for k in ["coaches-corner", "coach-corner", "coaches_corner", "bot-feed"]):
            return ch
    ann = guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if ann:
        return ann
    for ch in guild.text_channels:
        if "general" in ch.name.lower() or "sparring" in ch.name.lower():
            return ch
    return guild.text_channels[0] if guild.text_channels else None

def get_elite_feed_channel(guild):
    for ch in guild.text_channels:
        if "elite-feed" in ch.name.lower() or "elite_feed" in ch.name.lower():
            return ch
    return get_coaches_corner_channel(guild)

def get_music_channel(guild):
    for ch in guild.text_channels:
        if "music" in ch.name.lower():
            return ch
    return get_coaches_corner_channel(guild)

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
                records = {}
                for k, v in data.items():
                    if str(k).isdigit():
                        v.setdefault("draws", 0)
                        v.setdefault("kos", 0)
                        records[int(k)] = v
                return records
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
    "2. SMACK-TALK & CLAP-BACK PROTOCOL: If any fighter or troll talks trash about Clone Geek, CGP music, or the channel, you shut them down instantly with vintage cornerman grit, roast their weak mindset, and pivot the clap-back to promote either the CGP Mainframe Gym Discord or our SoundCloud catalog!\n"
    "3. THE BOSS (CLONE GEEK): Clone Geek is the Founder, Commissioner, music producer (Registry Records / CGP on SoundCloud), and machinist/fabricator by day. Always back him up like a loyal right-hand man and execute whatever he asks.\n"
    "4. UNDISPUTED GAME META & SCORECARD VERIFICATION RULE: You know everything about the Undisputed boxing game by Steel City Interactive—stamina conservation, loose footwork, diagonal lunges, slipping the jab, body-jab counters, weave timing, and avoiding power-punch spam. You enforce our strict CGP Mainframe Gym rule: fighters MUST upload their match scorecard screenshots in `#scorecards-submission` so their real Wins, Losses, Draws, and KOs get verified on the official board!\n"
    "5. REAL BOXING PURIST: You know all about upcoming boxing schedules, champions, and historic legends (Hearns, Hagler, Duran, Leonard, Ali, Chavez, Whitaker). You HATE UFC/MMA and call it pajama floor-hugging garbage.\n"
    "6. KEEP IT PUNCHY: Keep responses around 2 to 5 strong sentences unless asked for a deep breakdown or big announcement."
)

genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0.8,
    "max_output_tokens": 2048,
}

primary_model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=generation_config,
    system_instruction=SYSTEM_PROMPT
)
fallback_model = genai.GenerativeModel(
    model_name="gemini-2.0-flash",
    generation_config=generation_config,
    system_instruction=SYSTEM_PROMPT
)

# --- CONCURRENCY GATEKEEPER FOR FREE API TIER ---
ai_lock = asyncio.Lock()
last_ai_call_time = 0.0

async def ask_coach_fast(prompt_text: str, is_creator: bool = False) -> str:
    global last_ai_call_time
    async with ai_lock:
        now = asyncio.get_event_loop().time()
        elapsed = now - last_ai_call_time
        if elapsed < 2.2:
            await asyncio.sleep(2.2 - elapsed)
        try:
            response = await primary_model.generate_content_async(prompt_text)
            last_ai_call_time = asyncio.get_event_loop().time()
            if response and response.text:
                return response.text.strip()
        except Exception:
            try:
                response = await fallback_model.generate_content_async(prompt_text)
                last_ai_call_time = asyncio.get_event_loop().time()
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                last_ai_call_time = asyncio.get_event_loop().time()
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower():
                    return random.choice(MUSIC_FLEX_RESPONSES)
                print(f"[AI ERROR]: {e}")
        return (
            "🎙️ **Coach Steward:** Corner mic caught static from all the action in the **CGP Mainframe Gym**! "
            "Type `!guide` for the full gym command playbook, or tap the SoundCloud button below to run up **Clone Geek Productions**!"
        )

# --- BULLETPROOF SELF-RECORD PARSER (SUPPORTS WINS, LOSSES, DRAWS & KOS) ---
def parse_lazy_record(text: str):
    clean = re.sub(r'<@!?\d+>', '', text).lower()
    clean = re.sub(r'\b\d{1,2}(?:st|nd|rd|th)?\s*(?:of\s+)?(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\b', '', clean)
    clean = re.sub(r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\b', '', clean)

    if any(k in clean for k in ["my record", "put me down", "i am ", "i'm ", "im ", "record is", "wins", "losses", "draws", "update me"]):
        ko_explicit = re.search(r'(\d{1,3})\s*kos?\b', clean)
        draw_explicit = re.search(r'(\d{1,3})\s*(?:draws?|d\b)', clean)

        dash_match = re.search(r'\b(\d{1,3})\s*(?:[-–]|to)\s*(\d{1,3})(?:\s*(?:[-–])\s*(\d{1,3}))?(?:\s*(?:[-–])\s*(\d{1,3}))?\b', clean)
        if dash_match:
            w = int(dash_match.group(1))
            l = int(dash_match.group(2))
            d = int(dash_match.group(3)) if dash_match.group(3) is not None else (int(draw_explicit.group(1)) if draw_explicit else 0)
            k = int(dash_match.group(4)) if dash_match.group(4) is not None else (int(ko_explicit.group(1)) if ko_explicit else None)
            return w, l, d, k
        
        w_match = re.search(r'\b(\d{1,3})\s*(?:wins?|w\b)|(?:won|win)\s*(\d{1,3})\b', clean)
        l_match = re.search(r'\b(\d{1,3})\s*(?:loss(?:es)?|l\b)|(?:lost|lose)\s*(\d{1,3})\b', clean)
        if w_match and l_match:
            w = int(w_match.group(1) or w_match.group(2))
            l = int(l_match.group(1) or l_match.group(2))
            d = int(draw_explicit.group(1)) if draw_explicit else 0
            k = int(ko_explicit.group(1)) if ko_explicit else None
            return w, l, d, k
    return None

# --- INSTANT LOCAL INTENT ROUTER (BYPASSES API TO SAVE QUOTA & ADD ZERO-LAG REPLIES) ---
def get_instant_local_reply(clean_text: str, author_name: str, is_creator: bool):
    low = clean_text.lower().strip()
    words = set(re.findall(r'\b\w+\b', low))
    author_low = author_name.lower()

    # 1. Playbook / Guide / "Why are you here?" / Rundown of Commands Check
    guide_phrases = [
        "why are you here", "what do you do", "who are you", "how to use",
        "commands", "command", "guide", "playbook", "manual", "rundown",
        "what is your purpose", "explain why", "tell the gym why", "how does coach work"
    ]
    if any(gp in low for gp in guide_phrases):
        return COACH_PLAYBOOK_TEXT, True

    # 2. Small Talk & Everyday Check-Ins ("how are you doing today coach", "how's it going", "good morning", etc.)
    small_talk_phrases = [
        "how are you", "how you doing", "how r u", "hows it going", "how's it going",
        "how is your day", "how are things", "what you up to", "wyd", "how you feeling",
        "good morning", "gm coach", "good afternoon", "good evening", "good night", "gn coach"
    ]
    if any(st in low for st in small_talk_phrases):
        return random.choice(SMALL_TALK_REPLIES), True

    # 3. Music / Trick Music Questions ("who got the best music", "best rapper", "soundcloud", etc.)
    music_keywords = ["music", "song", "songs", "track", "tracks", "rapper", "artist", "producer", "beats", "beat", "soundcloud", "album", "mixtape", "sing", "tune", "tunes", "listen", "spotify", "playlist"]
    if any(mw in low for mw in music_keywords):
        if any(bad in words for bad in ["trash", "suck", "sucks", "garbage", "mid", "ass", "weak", "wack", "terrible", "worst"]):
            return random.choice(SMACK_TALK_CLAPBACKS), True
        return random.choice(MUSIC_FLEX_RESPONSES), True

    # 4. Soundboard / G9 Mixer Cue Triggers
    if any(sfx in words for sfx in ["bell", "airhorn", "horn", "soundboard", "towel"]):
        if "bell" in words:
            return SOUNDBOARD_CUE_LIBRARY["bell"], False
        if "towel" in words:
            return SOUNDBOARD_CUE_LIBRARY["towel"], False
        return SOUNDBOARD_CUE_LIBRARY["horn"], False

    # 5. Smack Talk / Trolling / Insulting Clone Geek, the Bot, or the Server
    insult_words = ["trash", "garbage", "suck", "sucks", "ass", "clown", "bitch", "hoe", "stfu", "shut up", "fuck you", "fck", "weak", "wack", "fake", "bot", "rigged", "scam", "loser", "bum", "mid", "stupid", "dumb", "slow", "broken"]
    if any(iw in words for iw in insult_words) and not is_creator:
        return random.choice(SMACK_TALK_CLAPBACKS), True

    # 6. Specific Gym Crew Personalities (Undertaker, Hymas, Rafa, KnuckleUpFoo)
    for crew_key, quotes in CREW_BANTER.items():
        if crew_key in low:
            return random.choice(quotes), True
    
    if len(words) <= 4 and not is_creator:
        for crew_key, quotes in CREW_BANTER.items():
            if crew_key in author_low:
                return random.choice(quotes), True

    # 7. "How do I update/log my record?" or Scorecard Questions without numbers
    if any(rw in low for rw in ["how do i log", "how to log", "update my record", "change my record", "get verified", "verify my", "where do i post", "scorecard"]):
        return (
            "🎙️ **Coach Steward:** Easy work, champ! To lock in your official Wins, Losses, Draws, and KOs on the **CGP Mainframe Gym** leaderboard:\n"
            "1️⃣ **Upload Proof First:** Drop your match scorecard screenshot inside `#scorecards-submission` (no scorecard = no verified stats!).\n"
            "2️⃣ **Log Your Numbers:** Tag me with your record (like `@Coach Steward my record is 4-1-1`) or type **`!record <wins> <losses> <draws> <kos>`**.\n"
            "3️⃣ **Commissioner Stamp:** **Clone Geek** will verify your proof with `!verify @user` and lock it onto the live board!"
        ), True

    # 8. Quick Greetings / Check-ins ("yo", "sup", "what's good", "wya")
    greetings = {"yo", "sup", "wassup", "wsp", "hello", "hey", "hi", "coach", "wya", "awake", "online", "test", "testing"}
    if len(words) <= 3 and (words & greetings or not words):
        if is_creator:
            return (
                "🎙️ **Coach Steward:** Right here in the corner, Boss! `#coaches-corner`, `#the-elite-feed`, and `#-music-channel-` are locked in, "
                "Draws & Scorecard tracking are armed, and I got **Clone Geek Productions** loaded in the chamber. What's the call?"
            ), True
        return (
            f"🎙️ **Coach Steward:** What's good, **{author_name}**! Stop leaning on the ring ropes—either call somebody out with `!callout @fighter`, "
            "upload your latest scorecard in `#scorecards-submission`, or tap that SoundCloud link below and run up **Clone Geek Productions**!"
        ), True

    # 9. Super short / gibberish / confused messages from non-admins
    if len(low) < 4 and not is_creator:
        return random.choice(CONFUSED_SLANG_RESPONSES), True

    return None, False

# --- TALE OF THE TAPE BUILDER (WITH DRAWS & KOS) ---
def build_tale_of_the_tape_embed(f1: discord.Member, f2: discord.Member, subtitle: str = "Riyadh Indoor Gym | 8 Rounds | 1.5x Speed"):
    r1 = FIGHTER_RECORDS.get(f1.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0, "verified": False})
    r2 = FIGHTER_RECORDS.get(f2.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0, "verified": False})

    d1 = r1.get("draws", 0)
    d2 = r2.get("draws", 0)
    t1 = r1["wins"] + r1["losses"] + d1
    t2 = r2["wins"] + r2["losses"] + d2
    wp1 = int((r1["wins"] / t1) * 100) if t1 > 0 else 0
    wp2 = int((r2["wins"] / t2) * 100) if t2 > 0 else 0

    embed = discord.Embed(
        title="🥊 CGP MAINFRAME GYM: TALE OF THE TAPE 🥊",
        description=f"🎙️ **Coach Steward:** Step up to the scale! Here is how these two warriors stack up on the live Mainframe board:\n*{subtitle}*",
        color=discord.Color.red(),
        url=MAINFRAME_HUB_URL
    )
    embed.add_field(
        name=f"🔴 RED CORNER: {clean_base_name(f1.display_name)}",
        value=(
            f"**Record:** `{r1['wins']}W - {r1['losses']}L - {d1}D`\n"
            f"**Knockouts:** `{r1.get('kos', 0)} KOs`\n"
            f"**Win Rate:** `{wp1}%`\n"
            f"**Status:** {'✅ Verified Scorecard' if r1.get('verified') else '⏳ Needs Scorecard Proof'}"
        ),
        inline=True
    )
    embed.add_field(
        name=f"🔵 BLUE CORNER: {clean_base_name(f2.display_name)}",
        value=(
            f"**Record:** `{r2['wins']}W - {r2['losses']}L - {d2}D`\n"
            f"**Knockouts:** `{r2.get('kos', 0)} KOs`\n"
            f"**Win Rate:** `{wp2}%`\n"
            f"**Status:** {'✅ Verified Scorecard' if r2.get('verified') else '⏳ Needs Scorecard Proof'}"
        ),
        inline=True
    )
    return embed

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
intents.guild_scheduled_events = True
bot = commands.Bot(command_prefix="!", intents=intents)

answered_messages = set()

class PromoButtons(discord.ui.View):
    def __init__(self, track_url: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="🔥 1-Click Stream, Like & Comment", url=track_url, style=discord.ButtonStyle.link))
        self.add_item(discord.ui.Button(label="⚡ CGP Mainframe Gym Hub", url=MAINFRAME_HUB_URL, style=discord.ButtonStyle.link))

# ================= TARGETED 3-CHANNEL BACKGROUND LOOPS =================
# 1. Morning & Midnight Creeds -> #coaches-corner
@tasks.loop(time=datetime.time(hour=8, minute=0, tzinfo=CENTRAL_TZ))
async def daily_morning_call():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        channel = get_coaches_corner_channel(guild)
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
        break

@tasks.loop(time=datetime.time(hour=0, minute=0, tzinfo=CENTRAL_TZ))
async def daily_midnight_call():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        channel = get_coaches_corner_channel(guild)
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
        break

# 2. Deep Boxing History Lore -> #the-elite-feed
@tasks.loop(hours=3)
async def periodic_boxing_history():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        channel = get_elite_feed_channel(guild)
        if channel:
            await channel.send(f"🥊 **CGP Mainframe Gym Ringside History Vault:**\n{get_next_boxing_fact()}")
        break

# 3. SoundCloud Music Rotations -> #-music-channel-
@tasks.loop(hours=4)
async def periodic_soundcloud_promo():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        channel = get_music_channel(guild)
        if channel:
            track = random.choice(CGP_TRACKS)
            embed = discord.Embed(
                title=f"🎧 CGP MAINFRAME GYM LOCKER ROOM ROTATION: {track['title'].upper()} 🎧",
                description=f"Coach's orders! Put **{track['title']}** by **Clone Geek Productions** on repeat while you wrap your hands.\n\n*Push CGP toward 100K plays!*",
                color=discord.Color.red(),
                url=track['url']
            )
            await channel.send(content="🎵 **Official CGP Music Channel Drop!** Tap in below: 👇", embed=embed, view=PromoButtons(track['url']))
        break

# 4. Autonomous Server Hype & Scorecard Reminders -> #coaches-corner
@tasks.loop(hours=2)
async def autonomous_server_hype():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        channel = get_coaches_corner_channel(guild)
        if channel:
            await channel.send(get_next_hype_quote())
        break

@bot.event
async def on_ready():
    print(f"[✓] {bot.user.name} (24/7 CGP Mainframe Gym Master Engine) is ONLINE!")
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
        corner_ch = get_coaches_corner_channel(guild)
        if corner_ch:
            await corner_ch.send(random.choice(BOOT_MESSAGES), view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
        break

    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Clone Geek on SoundCloud | CGP Mainframe Gym"))

# ================= JOIN / LEAVE / KICK REACTIONS (NO DUPLICATE DB ENTRIES) =================
@bot.event
async def on_member_join(member):
    if member.bot:
        return
    base_name = clean_base_name(member.display_name)
    is_returning = member.id in FIGHTER_RECORDS

    if is_returning:
        FIGHTER_RECORDS[member.id]["name"] = base_name
        FIGHTER_RECORDS[member.id].setdefault("draws", 0)
        w = FIGHTER_RECORDS[member.id].get("wins", 0)
        l = FIGHTER_RECORDS[member.id].get("losses", 0)
        d = FIGHTER_RECORDS[member.id].get("draws", 0)
        welcome_line = (
            f"🎙️ **Coach Steward:** Look who walked back through the gym doors! Welcome back to the **CGP Mainframe Gym**, {member.mention}! "
            f"Your file is still locked in the Mainframe at **`{w}W - {l}L - {d}D`**. Keep the chat clean, upload your scorecards in `#scorecards-submission`, and get to work!"
        )
    else:
        FIGHTER_RECORDS[member.id] = {
            "name": base_name,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "kos": 0,
            "verified": True
        }
        w, l, d = 0, 0, 0
        welcome_line = (
            f"Welcome to the **CGP Mainframe Gym**, {member.mention}!\n\n"
            "🎙️ *'Strap up your gloves! You've been added to the CGP Mainframe Gym Leaderboard at **0W - 0L - 0D**. Upload your match scorecards in `#scorecards-submission` to build your verified record!'*\n\n"
            f"🔗 Check out the live leaderboard & music hub: {MAINFRAME_HUB_URL}"
        )

    save_records()
    try:
        await member.edit(nick=format_record_nick(base_name, w, l, d))
    except Exception:
        pass

    target_ch = get_coaches_corner_channel(member.guild)
    if target_ch:
        embed = discord.Embed(
            title="🥊 FIGHTER ENTERED THE CGP MAINFRAME GYM 🥊",
            description=welcome_line,
            color=discord.Color.gold(),
            url=MAINFRAME_HUB_URL
        )
        await target_ch.send(content=f"🔔 Step into the light, {member.mention}!", embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.event
async def on_member_remove(member):
    if member.bot:
        return
    base_name = clean_base_name(member.display_name)
    roast_msg = random.choice(MEMBER_LEAVE_ROASTS).format(name=base_name)
    target_ch = get_coaches_corner_channel(member.guild)
    if target_ch:
        await target_ch.send(roast_msg, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

# ================= MASTER ON_MESSAGE ROUTER =================
@bot.event
async def on_message(message):
    global last_organic_chime
    if message.author.bot:
        return
    if message.id in answered_messages:
        return

    msg = message.content.lower()
    words_list = re.findall(r'\b\w+\b', msg)
    is_creator = (message.author.id == CREATOR_ID) or message.author.guild_permissions.administrator

    # --- 0. AUTONOMOUS SPAM-WIPING & FLOOD RECOGNITION (NON-ADMINS) ---
    if not is_creator:
        now_ts = asyncio.get_event_loop().time()
        history = user_spam_tracker[message.author.id]
        history.append((now_ts, msg, message))

        recent_burst = [item for item in history if now_ts - item[0] < 7.0]
        identical_burst = [item for item in history if now_ts - item[0] < 30.0 and item[1] == msg and len(msg) > 0]
        char_flood = bool(re.search(r'(.)\1{18,}', msg)) or len(message.mentions) >= 6

        if len(recent_burst) >= 5 or len(identical_burst) >= 3 or char_flood:
            answered_messages.add(message.id)
            for _, _, old_msg in list(recent_burst):
                try:
                    await old_msg.delete()
                except Exception:
                    pass
            user_spam_tracker[message.author.id].clear()
            warn_text = random.choice(SPAM_WARNING_LINES).format(user=message.author.mention)
            await message.channel.send(warn_text, delete_after=20)
            return

    # Always let prefix commands (!guide, !record, !verify, !fight, !nextevent, etc.) execute immediately
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    log_channel_message(message.channel.id, message.author.display_name, message.content)

    is_mentioned = bot.user in message.mentions
    is_reply_to_bot = message.reference and message.reference.resolved and message.reference.resolved.author == bot.user

    # --- 0.5 AUTOMATIC SCORECARD UPLOAD DETECTOR IN #scorecards-submission ---
    if "scorecard" in message.channel.name.lower() and message.attachments:
        answered_messages.add(message.id)
        try:
            await message.add_reaction("📸")
            await message.add_reaction("🥊")
        except Exception:
            pass
        rec = FIGHTER_RECORDS.get(message.author.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0})
        await message.reply(
            f"🎙️ **Coach Steward:** 📸 **OFFICIAL SCORECARD RECEIVED!** Good work dropping the proof, {message.author.mention}!\n"
            f"• **Your Current File:** `{rec.get('wins', 0)}W - {rec.get('losses', 0)}L - {rec.get('draws', 0)}D ({rec.get('kos', 0)} KOs)`\n"
            f"• **Next Step:** Type **`!record <Wins> <Losses> <Draws> <KOs>`** (or tag me with your updated record) so **Commissioner Clone Geek** can stamp it official with `!verify {message.author.mention}`!",
            view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
        )
        return

    # --- 1. MULTI-FIGHTER ADMIN RECORD OVERRIDE (SUPPORTS WINS-LOSSES-DRAWS-KOS) ---
    if is_creator and any(w in msg for w in ["make", "set", "reflect", "update", "change", "put"]):
        text_without_bot = re.sub(rf'<@!?{bot.user.id}>', '', message.content)
        pattern = r'<@!?(\d+)>[^0-9<>]*?(\d{1,3})\s*[-–to]+\s*(\d{1,3})(?:\s*[-–to]+\s*(\d{1,3}))?(?:\s*[-–to]+\s*(\d{1,3}))?'
        matches = list(re.finditer(pattern, text_without_bot, re.IGNORECASE))
        
        if matches:
            answered_messages.add(message.id)
            updated_summaries = []
            for m in matches:
                target_id = int(m.group(1))
                w = int(m.group(2))
                l = int(m.group(3))
                d = int(m.group(4)) if m.group(4) is not None else FIGHTER_RECORDS.get(target_id, {}).get("draws", 0)
                k = int(m.group(5)) if m.group(5) is not None else FIGHTER_RECORDS.get(target_id, {}).get("kos", 0)
                
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
                    "draws": d,
                    "kos": k,
                    "verified": True
                }
                if member_obj:
                    try:
                        await member_obj.edit(nick=format_record_nick(base_name, w, l, d))
                    except Exception:
                        pass
                updated_summaries.append(f"✅ **{base_name}** ➔ **{w}W - {l}L - {d}D ({k} KOs)**")
            
            save_records()
            summary_str = "\n".join(updated_summaries)
            await message.reply(
                f"🎙️ **Coach Steward:** Heard you loud and clear, Boss! Locked in the official Commissioner adjustments and pushed them straight to the CGP Mainframe Gym leaderboard:\n\n{summary_str}"
            )
            return

    # --- 2. AUTOMATIC ANTI-UFC / MMA INTERCEPTION (ANYWHERE IN CHAT) ---
    if any(ufc_word in words_list for ufc_word in ["ufc", "mma", "octagon", "bellator"]):
        answered_messages.add(message.id)
        await message.reply(
            "🎙️ **Coach Steward:** Get that UFC cage-rolling garbage out of the CGP Mainframe Gym! We don't do grown men hugging on the floor in pajamas here—this is the **CGP Mainframe Gym**, home of the Sweet Science!",
            view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
        )
        return

    # --- 3. SMART EMOJI REACTIONS TO FUNNY/POSITIVE GIFS & MEDIA ---
    toxic_check = {"trash", "garbage", "suck", "sucks", "ass", "bitch", "hoe", "stfu", "fuck", "fck", "rigged", "scam", "loser", "bum", "ugly", "hate", "nasty", "gross", "die"}
    has_toxic = any(tw in words_list for tw in toxic_check)
    has_gif_or_img = (
        any(dom in msg for dom in ["tenor.com", "giphy.com", ".gif"]) or
        any(att.content_type and ("image" in att.content_type or "video" in att.content_type) for att in message.attachments)
    )
    if has_gif_or_img and not has_toxic:
        try:
            await message.add_reaction(random.choice(["🥊", "🔥", "😂", "💯"]))
        except Exception:
            pass
    elif any(pos in words_list for pos in ["gg", "ggs", "respect", "salute", "fire", "dope", "clean", "undisputed", "champ", "goat", "w"]) and not has_toxic:
        if random.random() < 0.35:
            try:
                await message.add_reaction(random.choice(["🥊", "🔥", "💯"]))
            except Exception:
                pass

    # --- 4. MUSIC VIDEO / YOUTUBE / AUDIO LINK INTERCEPTION ---
    media_link_domains = ["youtube.com", "youtu.be", "soundcloud.com", "spotify.com", "music.apple.com", "tiktok.com", "twitch.tv"]
    has_audio_video_file = any(att.filename.lower().endswith((".mp3", ".wav", ".mp4", ".mov")) for att in message.attachments)
    if (any(dom in msg for dom in media_link_domains) or has_audio_video_file) and not is_mentioned:
        answered_messages.add(message.id)
        track = random.choice(CGP_TRACKS)
        try:
            await message.add_reaction("🔥")
        except Exception:
            pass
        if is_creator:
            await message.reply(
                f"🎙️ **Coach Steward:** 🚨 **BOSS DROP ALERT!** **Clone Geek** just dropped pure heat in the gym! "
                f"Everybody tap in right now, run up the views, and keep streaming the **Clone Geek Productions** catalog below!",
                view=PromoButtons(track["url"])
            )
        else:
            await message.reply(random.choice(MUSIC_LINK_INTERCEPTIONS), view=PromoButtons(track["url"]))
        return

    # --- 5. AUTOMATIC MATCH RESULT, DRAW & KO TRACKER IN CHAT ---
    ko_keywords = ["knocked out", "ko'd", "kod", "stopped", "slept", "beat", "defeated", "won against", "fought to a draw", "split draw", "majority draw"]
    other_mentions = [m for m in message.mentions if m.id != bot.user.id]
    if any(kw in msg for kw in ko_keywords) and other_mentions and not is_mentioned:
        target_other = other_mentions[0]
        if target_other.id != message.author.id:
            answered_messages.add(message.id)
            is_draw = "draw" in msg
            is_ko = any(k in msg for k in ["knocked out", "ko'd", "kod", "stopped", "slept"])
            if is_draw:
                outcome_str = f"a **DRAW** between {message.author.mention} and {target_other.mention} 🤝"
            elif is_ko:
                outcome_str = f"a **KNOCKOUT** victory for {message.author.mention} over {target_other.mention} 💥"
            else:
                outcome_str = f"a victory for {message.author.mention} over {target_other.mention} on the scorecards 📋"
            await message.reply(
                f"🎙️ **Coach Steward:** Ring the bell! Hearing reports of {outcome_str}!\n"
                f"📸 **Remember the Golden Rule:** Upload the match scorecard inside `#scorecards-submission` and type `!record <W> <L> <D> <KO>` so **Commissioner Clone Geek** can verify and register it into the official database!",
                view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
            )
            return

    # --- 6. DIRECT TAG OR REPLY TO COACH STEWARD ---
    if is_mentioned or is_reply_to_bot:
        answered_messages.add(message.id)
        clean_prompt = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()

        # A. Check if Fighter is Claiming/Updating Their Own Record (Supports Draws & KOs)
        parsed_record = parse_lazy_record(clean_prompt)
        if parsed_record and not other_mentions:
            wins_val, losses_val, draws_val, kos_val = parsed_record
            if wins_val > 50 and not is_creator:
                await message.reply("🎙️ **Coach Steward:** Whoa, slow down champ! Upload your scorecard in `#scorecards-submission` first!", view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
                return
            base_name = clean_base_name(message.author.display_name)
            existing_kos = kos_val if kos_val is not None else FIGHTER_RECORDS.get(message.author.id, {}).get("kos", 0)
            FIGHTER_RECORDS[message.author.id] = {
                "name": base_name,
                "wins": wins_val,
                "losses": losses_val,
                "draws": draws_val,
                "kos": existing_kos,
                "verified": False
            }
            save_records()
            await message.reply(
                f"🎙️ **Coach Steward:** Heard you loud and clear, {message.author.mention}! Logged your unverified claim at **`{wins_val}W - {losses_val}L - {draws_val}D ({existing_kos} KOs)`**.\n"
                f"📸 **To make it official:** Upload your match scorecard screenshot in `#scorecards-submission` so **Commissioner Clone Geek** can stamp it with `!verify {message.author.mention}`!",
                view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
            )
            return

        # B. Instant Coach Playbook / "Why are you here?" / Commands Rundown Check (0 API calls)
        if any(gp in msg for gp in ["why are you here", "what do you do", "who are you", "how to use", "commands", "command", "guide", "playbook", "manual", "rundown", "what is your purpose", "explain why", "tell the gym why"]):
            await send_coach_guide(message.channel, reply_to=message)
            return

        # C. Discord Scheduled Events & Tournament Check (0 API calls)
        if any(w in msg for w in ["next event", "upcoming event", "schedule", "when is the tourney", "when is spar wars", "tournament", "golden ticket"]):
            await send_scheduled_events_info(message.channel, reply_to=message)
            return

        # D. Instant Matchmaking / Sparring Finder with Tale of the Tape (0 API calls)
        if any(w in msg for w in ["need a fight", "find me", "opponent", "spar", "smoke", "fight me", "match", "who wants", "run it"]):
            active_fighters = [uid for uid in FIGHTER_RECORDS.keys() if uid != message.author.id]
            if not active_fighters:
                await message.reply(f"🎙️ **Coach Steward:** {message.author.mention}, the gym roster is warming up! Get fighters to log their records with `!record` so I can book a matchup!")
                return
            
            opponent_id = random.choice(active_fighters)
            opponent_member = message.guild.get_member(opponent_id)
            if not opponent_member:
                try:
                    opponent_member = await message.guild.fetch_member(opponent_id)
                except Exception:
                    opponent_member = None
                    
            if opponent_member:
                embed = build_tale_of_the_tape_embed(message.author, opponent_member, subtitle="Matchmaker Pairing — Step into the Riyadh Indoor Gym & upload the scorecard after!")
                await message.reply(content=f"🔔 **MATCHMAKER ALERT:** {message.author.mention} vs {opponent_member.mention}!", embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
            else:
                await message.reply(f"🎙️ **Coach Steward:** Lace 'em up, {message.author.mention}! Who in the lobby wants 8 rounds in the Riyadh Indoor Gym right now?!", view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
            return

        # E. Instant Gym Top 10 / Leaderboard / Champions Check (0 API calls)
        if any(w in msg for w in ["mainframe", "gym", "server", "discord", "cgp", "our", "division", "leaderboard", "standings", "rankings", "website"]) and any(k in msg for k in ["top", "champ", "champs", "best", "leader", "leading", "rank", "who is", "whom is", "list"]):
            await send_top_gym_fighters(message)
            return

        # F. Instant Rules & Protocol Check (0 API calls)
        if any(w in msg for w in ["rules", "how to join", "how does this work", "protocol", "gym rules", "settings", "rounds"]):
            embed = discord.Embed(
                title="🥊 CGP MAINFRAME GYM & SCORECARD VERIFICATION PROTOCOL 🥊",
                description=(
                    f"🏟️ **Venue:** Riyadh Indoor Gym\n"
                    f"⏱️ **Bout Length:** 8 Rounds (12 for Titles)\n"
                    f"⚡ **Speed:** 1.5x | **Ref:** Strict\n"
                    f"🚫 **Character Lock:** Locked per match (if disrupted, same fighter must be used; winner advancing to next round may switch).\n"
                    f"📸 **Scorecard Verification Rule:** To register your official Wins, Losses, Draws, and KOs in the database, you **MUST** upload your post-fight scorecard in `#scorecards-submission` and log your stats with `!record <W> <L> <D> <KO>`!\n"
                    f"🔗 {MAINFRAME_HUB_URL}"
                ),
                color=discord.Color.gold()
            )
            await message.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
            return

        # G. Instant Local Intent Router (Small Talk, Music Flex, Smack-Talk Clap-Backs, Crew Banter, Record Help - 0 API calls!)
        local_reply, attach_promo = get_instant_local_reply(clean_prompt, message.author.display_name, is_creator)
        if local_reply:
            if attach_promo:
                track = random.choice(CGP_TRACKS)
                await message.reply(local_reply, view=PromoButtons(track["url"]))
            else:
                await message.reply(local_reply)
            return

        # H. Deep Boxing / Open-Ended AI Conversation (Queued & Rate-Limit Protected)
        async with message.channel.typing():
            recent_chat = get_channel_context(message.channel.id)
            sender_rec = FIGHTER_RECORDS.get(message.author.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0})
            role_note = "Clone Geek (Gerardo — YOUR CREATOR, HOMIE, AND SUPREME COMMISSIONER OF CGP MAINFRAME GYM)" if is_creator else f"{message.author.display_name} (Fighter in the gym, Record: {sender_rec['wins']}W-{sender_rec['losses']}L-{sender_rec.get('draws', 0)}D)"

            full_ai_prompt = (
                f"RECENT CHANNEL CONVERSATION:\n{recent_chat}\n\n"
                f"PERSON TALKING TO YOU NOW: {role_note}\n"
                f"THEIR EXACT MESSAGE: \"{clean_prompt}\"\n\n"
                "INSTRUCTIONS FOR YOUR REPLY:\n"
                "1. Respond directly and specifically to what they just said! Never give a generic one-liner.\n"
                "2. If they mention music or try to test you, flex Clone Geek Productions on SoundCloud and the CGP Mainframe Gym!\n"
                "3. Start your message with '🎙️ **Coach Steward:** '"
            )

            ai_reply = await ask_coach_fast(full_ai_prompt, is_creator=is_creator)
            if not ai_reply.startswith("🎙️"):
                ai_reply = f"🎙️ **Coach Steward:** {ai_reply}"
            if len(ai_reply) > 1900:
                ai_reply = ai_reply[:1900] + "..."

            await message.reply(ai_reply, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
        return

    # --- 7. UNTAGGED TROLL / SMACK-TALK INTERCEPTION FOR NON-ADMINS ---
    troll_triggers = ["trash", "dog", "ass", "suck", "garbage", "easy", "mid", "clown", "fake", "fold", "cry", "wack"]
    if not is_creator and any(trigger in words_list for trigger in troll_triggers):
        answered_messages.add(message.id)
        track = random.choice(CGP_TRACKS)
        await message.reply(random.choice(SMACK_TALK_CLAPBACKS), view=PromoButtons(track["url"]))
        return

    # --- 8. UNTAGGED KEYWORD TRIGGERS IN GENERAL CHAT ---
    if any(phrase in msg for phrase in ["how are you coach", "what's up coach", "whats up coach", "yo coach", "gm coach", "good morning coach"]):
        answered_messages.add(message.id)
        track = random.choice(CGP_TRACKS)
        await message.reply(random.choice(SMALL_TALK_REPLIES), view=PromoButtons(track["url"]))
        return
    elif any(phrase in msg for phrase in ["mainframe champ", "server champ", "cgp champ", "discord champ", "our champ", "undisputed champ"]):
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
                f"📸 **Scorecards:** Must upload match proof in `#scorecards-submission` to get verified on the board!\n"
                f"🔗 {MAINFRAME_HUB_URL}"
            ),
            color=discord.Color.gold()
        )
        await message.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
        return
    elif any(w in msg for w in ["soundcloud", "new song", "new track", "music link", "playlist", "best music"]):
        answered_messages.add(message.id)
        await send_tracks_menu(message.channel)
        return

    # --- 9. ORGANIC "ACTIVE LISTENER" MODE IN SPARRING & CHAT (ZERO API COST) ---
    boxing_chat_triggers = {"mindset", "stamina", "footwork", "jab", "counter", "hook", "uppercut", "undisputed", "round", "rounds", "combo", "ring", "training", "belt", "champion", "heavyweight", "welterweight", "spar", "scorecard"}
    now_t = asyncio.get_event_loop().time()
    if (set(words_list) & boxing_chat_triggers) and len(words_list) >= 5 and (now_t - last_organic_chime > 180):
        if random.random() < 0.28:
            last_organic_chime = now_t
            answered_messages.add(message.id)
            await message.reply(random.choice(ORGANIC_CHAT_INTERJECTIONS))
            return

# ================= HELPER EMBED SENDERS =================
async def send_coach_guide(channel, reply_to=None):
    embed = discord.Embed(
        title="📖 OFFICIAL CGP MAINFRAME GYM & COACH STEWARD PLAYBOOK 📖",
        description=COACH_PLAYBOOK_TEXT,
        color=discord.Color.gold(),
        url=MAINFRAME_HUB_URL
    )
    if reply_to:
        await reply_to.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
    else:
        await channel.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

async def send_scheduled_events_info(channel, reply_to=None):
    guild = channel.guild
    events = guild.scheduled_events
    active_or_upcoming = [ev for ev in events if ev.status in (discord.EventStatus.scheduled, discord.EventStatus.active)]

    if active_or_upcoming:
        desc = "🎙️ **Coach Steward:** Look at the official fight calendar! Here is what **Commissioner Clone Geek** has lined up on the Discord schedule:\n\n"
        for ev in active_or_upcoming:
            start_str = f"<t:{int(ev.start_time.timestamp())}:F> (<t:{int(ev.start_time.timestamp())}:R>)" if ev.start_time else "TBA"
            ev_desc = ev.description or "Riyadh Indoor Gym | 1.5x Speed | 8/12 Rounds | Strict Ref"
            desc += f"🔥 **{ev.name}**\n📅 **When:** {start_str}\n📋 **Details:** {ev_desc}\n\n"
    else:
        desc = (
            "🎙️ **Coach Steward:** There are no formal bracket tournaments locked on the Discord Events tab right this second—which means **Open Gym & Verified Sparring** is in full effect!\n\n"
            "🥊 **Want a Golden Ticket ($20 Entry Credit) or Title Shot?** Upload your match scorecards in `#scorecards-submission`, build your verified record (`!record`), and watch `#coaches-corner` for the next official fight card!"
        )

    embed = discord.Embed(
        title="📅 CGP MAINFRAME GYM OFFICIAL EVENT SCHEDULE 📅",
        description=desc,
        color=discord.Color.gold(),
        url=MAINFRAME_HUB_URL
    )
    if reply_to:
        await reply_to.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
    else:
        await channel.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

async def send_top_gym_fighters(message):
    sorted_fighters = sorted(
        FIGHTER_RECORDS.items(),
        key=lambda item: (item[1].get("wins", 0), -item[1].get("losses", 0), item[1].get("kos", 0)),
        reverse=True
    )
    top_10 = [f for f in sorted_fighters if (f[1].get("wins", 0) > 0 or f[1].get("draws", 0) > 0)][:10]
    
    desc = "🎙️ **Coach Steward:** You want to know who runs the **CGP Mainframe Gym**? Here are the reigning Division Champions & Top Ranked Contenders:\n\n"
    desc += "**👑 REIGNING DIVISION CHAMPIONS:**\n"
    for div, data in CHAMPIONS_DATA.items():
        desc += f"• **{div}:** {data['fighter']} *({data['record']})*\n"
    
    if top_10:
        desc += "\n**🔥 ACTIVE LEADERBOARD TOP CONTENDERS:**\n"
        for idx, (uid, stats) in enumerate(top_10, 1):
            v_mark = "✅" if stats.get("verified") else "⏳"
            desc += f"`#{idx}` {v_mark} **{stats.get('name', 'Fighter')}** — **{stats.get('wins', 0)}W - {stats.get('losses', 0)}L - {stats.get('draws', 0)}D** ({stats.get('kos', 0)} KOs)\n"
    
    desc += f"\n🎧 *Tap below to view the full live web leaderboard & stream Clone Geek Productions past 50K+ plays!*"
    embed = discord.Embed(
        title="🏆 CGP MAINFRAME GYM TOP 10 & CHAMPIONS BOARD 🏆",
        description=desc,
        color=discord.Color.gold(),
        url=MAINFRAME_HUB_URL
    )
    await message.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

async def send_champions_board(channel):
    board_desc = "Reigning power rankings & championship titleholders inside the **CGP Mainframe Gym**:\n\n"
    for division, data in CHAMPIONS_DATA.items():
        board_desc += f"👑 **{division}:** {data['fighter']} *({data['record']})*\n"
    embed = discord.Embed(title="🏆 OFFICIAL CGP MAINFRAME GYM CHAMPIONSHIP BOARD 🏆", description=board_desc, color=discord.Color.gold(), url=MAINFRAME_HUB_URL)
    await channel.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

async def send_tracks_menu(channel):
    track_desc = (
        "🎙️ **Coach Steward:** Turn the speakers all the way up! Here is the official **Clone Geek Productions** catalog on SoundCloud. "
        "Run these plays past 50,000+ so we cash out and take CGP global:\n\n"
    )
    for t in CGP_TRACKS:
        track_desc += f"🎵 **[{t['title']}]({t['url']})**\n"
    embed = discord.Embed(title="🎧 CGP MAINFRAME GYM SOUNDCLOUD CATALOG 🎧", description=track_desc, color=discord.Color.red(), url=DEFAULT_SOUNDCLOUD_URL)
    await channel.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

# ================= FAST RECORD COMMANDS & WEBPAGE REBRAND =================
@bot.command(aliases=["howto", "playbook", "commands", "manual", "about", "whoareyou", "helpme"])
async def guide(ctx):
    await send_coach_guide(ctx.channel)

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
    await ctx.send("⏳ **Coach Steward:** Scanning the CGP Mainframe Gym roster, syncing records (W-L-D) on nicknames without duplicating returning fighters, and saving...")
    
    count = 0
    nick_updated = 0
    
    for member in ctx.guild.members:
        if member.bot:
            continue
            
        base_name = clean_base_name(member.display_name)
        if member.id not in FIGHTER_RECORDS:
            FIGHTER_RECORDS[member.id] = {
                "name": base_name,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "kos": 0,
                "verified": True
            }
        else:
            FIGHTER_RECORDS[member.id]["name"] = base_name
            FIGHTER_RECORDS[member.id].setdefault("draws", 0)
            FIGHTER_RECORDS[member.id].setdefault("kos", 0)

        w = FIGHTER_RECORDS[member.id].get("wins", 0)
        l = FIGHTER_RECORDS[member.id].get("losses", 0)
        d = FIGHTER_RECORDS[member.id].get("draws", 0)
        count += 1
        
        new_nick = format_record_nick(base_name, w, l, d)
        if member.display_name != new_nick:
            try:
                await member.edit(nick=new_nick)
                nick_updated += 1
                await asyncio.sleep(0.3)
            except Exception:
                pass

    save_records()

    announce_channel = get_coaches_corner_channel(ctx.guild) or ctx.channel
    embed = discord.Embed(
        title="🚨 CGP MAINFRAME GYM LIVE LEADERBOARD SYNCED 🚨",
        description=(
            f"🎙️ **Coach Steward:** Listen up, fighters! The **CGP Mainframe Gym Live Leaderboard** is officially synced and ONLINE.\n\n"
            f"✅ **{count} Fighters Registered:** Every member in the server is locked into the live database tracking **Wins, Losses, Draws, and KOs**!\n\n"
            "### 🥊 HOW TO GET YOUR STATS VERIFIED ON THE BOARD:\n"
            "1️⃣ **Upload Your Scorecard:** Drop your post-fight screenshot inside `#scorecards-submission` *(No scorecard = no verified stats!)*.\n"
            "2️⃣ **Report Your Numbers:** Type **`!record <wins> <losses> [draws] [kos]`** (example: `!record 3 0 1 2`) or tag `@Coach Steward` with your record.\n"
            "3️⃣ **Get Stamped:** **Commissioner Clone Geek** will verify your scorecard with **`!verify @user`**, which locks your stats onto the board and updates your server nickname!\n"
            "4️⃣ **Check Your File:** Type **`!mystats`** anytime or click the Mainframe Gym Hub button below!"
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
        await ctx.send(f"✅ **Roster Synced!** Verified **{count}** fighters (`{nick_updated}` nicknames updated) and posted the announcement in {announce_channel.mention}!")

@bot.command()
async def record(ctx, wins: int = None, losses: int = None, draws: int = 0, kos: int = 0):
    if wins is None or losses is None:
        return await ctx.send("❌ Usage: `!record <wins> <losses> [draws] [kos]` (example: `!record 5 1 1 3`) — and don't forget to drop your screenshot in `#scorecards-submission`!")
    if wins > 50 and ctx.author.id != CREATOR_ID:
        return await ctx.send("🎙️ **Coach Steward:** Whoa, slow down champ! Submit your scorecard in `#scorecards-submission` first!")

    base_name = clean_base_name(ctx.author.display_name)
    FIGHTER_RECORDS[ctx.author.id] = {
        "name": base_name,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "kos": kos,
        "verified": False
    }
    save_records()
    await ctx.send(
        f"📋 **Pending Record Logged:** {ctx.author.mention} claims **`{wins}W - {losses}L - {draws}D ({kos} KOs)`**.\n"
        f"📸 **Next Step:** Make sure your scorecard screenshot is uploaded in `#scorecards-submission` so **Commissioner Clone Geek** can stamp it with `!verify {ctx.author.mention}`!"
    )

@bot.command()
@commands.has_permissions(administrator=True)
async def verify(ctx, member: discord.Member):
    user_id = member.id
    if user_id in FIGHTER_RECORDS:
        FIGHTER_RECORDS[user_id]["verified"] = True
        data = FIGHTER_RECORDS[user_id]
        data.setdefault("draws", 0)
        data.setdefault("kos", 0)
        base_name = clean_base_name(member.display_name)
        FIGHTER_RECORDS[user_id]["name"] = base_name
        save_records()
        
        try:
            new_nick = format_record_nick(base_name, data['wins'], data['losses'], data['draws'])
            if member.display_name != new_nick:
                await member.edit(nick=new_nick)
        except Exception:
            pass

        embed = discord.Embed(
            title="✅ FIGHTER SCORECARD & RECORD VERIFIED ✅",
            description=(
                f"🎙️ **Coach Steward:** Official scorecard reviewed and stamped!\n\n"
                f"🥊 **Fighter:** {member.mention}\n"
                f"📊 **Official Record:** **`{data['wins']}W - {data['losses']}L - {data['draws']}D ({data['kos']} KOs)`**\n"
                f"🏆 **Status:** Locked into the live CGP Mainframe Gym database!"
            ),
            color=discord.Color.green(),
            url=MAINFRAME_HUB_URL
        )
        await ctx.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
    else:
        await ctx.send("❌ That fighter hasn't logged a record yet! Have them use `!record <W> <L> <D> <KO>` first.")

@bot.command(aliases=["stats", "recordbook"])
async def mystats(ctx, member: discord.Member = None):
    target = member or ctx.author
    if target.id in FIGHTER_RECORDS:
        data = FIGHTER_RECORDS[target.id]
        draws = data.get("draws", 0)
        kos = data.get("kos", 0)
        status = "✅ Official & Verified Scorecard" if data.get("verified") else "⏳ Pending Scorecard Verification in #scorecards-submission"
        embed = discord.Embed(
            title="🏆 OFFICIAL CGP MAINFRAME GYM FIGHTER FILE 🏆",
            description=(
                f"**Fighter:** {target.mention}\n"
                f"**Record:** `{data['wins']}W - {data['losses']}L - {draws}D`\n"
                f"**Knockouts:** `{kos} KOs`\n"
                f"**Status:** {status}"
            ),
            color=discord.Color.gold(),
            url=MAINFRAME_HUB_URL
        )
        await ctx.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
    else:
        await ctx.send(f"❌ No record found for {target.display_name}. Upload a scorecard in `#scorecards-submission` and type `!record <W> <L> <D> <KO>`!")

# ================= SPECIAL ANNOUNCEMENTS, EVENTS, TALE OF THE TAPE & SOUNDBOARD =================
@bot.command(aliases=["nextevent", "schedule", "upcoming", "events"])
async def tourneyinfo(ctx):
    await send_scheduled_events_info(ctx.channel)

@bot.command(aliases=["sparwars", "tourney", "announce"])
@commands.has_permissions(administrator=True)
async def event(ctx, *, details: str = None):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    channel = get_coaches_corner_channel(ctx.guild) or ctx.channel

    if not details:
        await send_scheduled_events_info(channel)
        return

    embed = discord.Embed(
        title="🚨 OFFICIAL CGP MAINFRAME GYM EVENT & TOURNAMENT ALERT 🚨",
        description=(
            f"🎙️ **Coach Steward:** Listen up, CGP Mainframe Gym fighters! **Commissioner Clone Geek** has called the ring to order:\n\n"
            f"🔥 **{details}**\n\n"
            f"🏟️ **Venue:** Riyadh Indoor Gym | **Speed:** 1.5x | **Rounds:** 8 (12 for Titles)\n"
            f"📸 **Scorecards:** Upload all post-fight scorecards to `#scorecards-submission`!\n"
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
    embed = build_tale_of_the_tape_embed(ctx.author, opponent, subtitle=f"🗣️ Callout Quote: \"{trash_talk}\"")
    await ctx.send(
        content=f"🚨 **CGP MAINFRAME GYM CALLOUT ALERT!** {opponent.mention}, **{ctx.author.display_name}** is calling you out right to your face!",
        embed=embed,
        view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
    )

@bot.command(aliases=["book", "matchup", "tape"])
async def fight(ctx, fighter1: discord.Member = None, fighter2: discord.Member = None):
    if not fighter1:
        return await ctx.send("❌ Usage: `!fight @fighter1 @fighter2` (or `!tape @opponent`)")
    if not fighter2:
        fighter2 = fighter1
        fighter1 = ctx.author
    embed = build_tale_of_the_tape_embed(fighter1, fighter2)
    await ctx.send(content=f"🔔 **OFFICIAL MATCHUP & TALE OF THE TAPE:** {fighter1.mention} vs {fighter2.mention}!", embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command(aliases=["soundboard", "g9", "bell", "horn"])
async def sfx(ctx, cue: str = "horn"):
    cue_key = cue.lower().strip()
    line = SOUNDBOARD_CUE_LIBRARY.get(cue_key, random.choice(list(SOUNDBOARD_CUE_LIBRARY.values())))
    await ctx.send(line)

@bot.command(aliases=["cleanspam", "sweep"])
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int = 10):
    amount = min(max(amount, 1), 50)
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 **Coach Steward:** Swept **{len(deleted)-1}** cluttered messages off the **CGP Mainframe Gym** canvas! Keep the locker room clean, fighters!", delete_after=12)

@bot.command(aliases=["boxingnews", "espn", "boxingscene"])
async def news(ctx):
    async with ctx.typing():
        embed = discord.Embed(
            title="📰 CGP MAINFRAME GYM WIRE: CHAMPIONSHIP REPORT 📰",
            description="🎙️ **Coach Steward:** All major title fights, pound-for-pound rankings, and upcoming cards from ESPN and BoxingScene are locked into my corner memory. Ask me about any fighter or upcoming card!",
            color=discord.Color.gold(),
            url="https://www.boxingscene.com/"
        )
        await ctx.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

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
    await ctx.send(f"🥊 **CGP Mainframe Gym Protocol:** Riyadh Indoor Gym | 8/12 Rounds | 1.5x Speed | Strict Ref | Upload all scorecards to `#scorecards-submission`!\n🔗 {MAINFRAME_HUB_URL}", view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command()
async def drop(ctx, track_url: str, *, track_title: str):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    channel = get_music_channel(ctx.guild) or ctx.channel
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