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
    "Heavyweight": {"fighter": "Roy🇲🇽🇲🇽🇲🇽", "record": "14W - 0L - 0D - 0K"},
    "Cruiserweight": {"fighter": "f150-_-t", "record": "11W - 2L - 0D - 0K"},
    "Light Heavyweight": {"fighter": "SlokeNastyTheCaptin#1🇺🇸🇲🇽", "record": "12W - 1L - 0D - 0K"},
    "Middleweight": {"fighter": "BBK Promotions 🪪", "record": "9W - 3L - 0D - 0K"},
    "Women's Welterweight": {"fighter": "DT", "record": "8W - 1L - 0D - 0K"},
    "Welterweight": {"fighter": "OPEN", "record": "0W - 0L - 0D - 0K"},
    "Lightweight": {"fighter": "El putito", "record": "10W - 4L - 0D - 0K"},
    "Bantamweight": {"fighter": "Roy🇲🇽🇲🇽🇲🇽 (Dual-Division King!)", "record": "14W - 0L - 0D - 0K"},
    "Women's Lightweight": {"fighter": "TURBO", "record": "7W - 2L - 0D - 0K"}
}

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
    "🥊 **Canelo's Undisputed Run (2021):** Saúl 'Canelo' Álvarez unified all four belts at 168 lbs in under 11 months, stopping Caleb Plant to become the first undisputed super middleweight king.",
    "🥊 **The Hawk's Kronk Wars (1982):** Aaron Pryor vs. Alexis Argüello I—14 rounds of relentless pace in Miami. Championship conditioning is what separates legends from contenders!",
    "🥊 ** Philly Shell Mastery:** James 'Lights Out' Toney rolling shots on the ropes and firing counter right hands showed the world that defense and offense can live in the same pocket.",
    "🥊 **El Finito's Perfection:** Ricardo López retired 51-0-1 with 38 KOs—textbook balance, footwork, and uppercuts without ever losing a professional prizefight.",
    "🥊 **The Executioner's Longevity:** Bernard Hopkins defended the middleweight crown 20 times and won a world title at age 49 by mastering ring generalship and inside craft."
]

RANDOM_HYPE_QUOTES = [
    "🎙️ **Coach Steward:** Hey! I see you quiet in the back. Stop shadowboxing your demons and drop some weight on the heavy bag in the CGP Mainframe Gym!",
    "🎙️ **Coach Steward:** A reminder from the CGP Mainframe Gym corner: talent wins fights, but conditioning wins titles. Put in those reps!",
    "🎙️ **Coach Steward:** Remember the house rule: **No scorecard in `#scorecards-submission`, no official stats on the board!** Upload your proof so I can scan the CompuBox numbers and automatically update your `[W-L-D-K]` record!",
    "🎙️ **Coach Steward:** Greatness requires sacrifice. Get in the Riyadh gym ring and prove you belong on the CGP Mainframe Gym board!",
    "🎙️ **Coach Steward:** Don't come crying to the corner about a split-decision draw if you didn't work the body in the early rounds! Stamina is king in the CGP Mainframe Gym!",
    "🎙️ **Coach Steward:** Everybody wants to hold the belt until it's time to do 12 rounds at 1.5x speed in the Riyadh Indoor Gym. Who's really built for this?!",
    "🎙️ **Coach Steward:** Keep that lead hand active! A lazy jab in Undisputed is an open invitation for a slip-counter straight to the chin!",
    "🎙️ **Coach Steward:** Check the leaderboard on the Mainframe Hub! If your nickname still says `[0W-0L-0D-0K]`, stop window-shopping and call somebody out with `!callout`!",
    "🎙️ **Coach Steward:** While y'all are warming up your thumbs, make sure you got **Clone Geek Productions** spinning in `#-music-channel-`. Real fighters train to real music!",
    "🎙️ **Coach Steward:** Ring generalship isn't about running marathon laps around the canvas—plant your feet, cut off the ring, and make 'em trade leather!",
    "🎙️ **Coach Steward:** I can tell who's been skipping roadwork just by watching how y'all gas out by Round 5! Conserve your stamina bar and pick your shots!",
    "🎙️ **Coach Steward:** Blue-collar work ethic all day, every day. From the shop floor to the CGP Mainframe Gym, we don't take shortcuts—we take titles!",
    "🎙️ **Coach Steward:** You got a scorecard sitting in your gallery? Drop that screenshot in `#scorecards-submission` with a tag so I can auto-update the records and broadcast the HBO CompuBox breakdown!",
    "🎙️ **Coach Steward:** Watch that power-punch spam! Any halfway decent counter-puncher in this gym will time that wind-up and put you to sleep!",
    "🎙️ **Coach Steward:** The road to 100,000 streams and undisputed gold runs right through this Discord. Tap into the SoundCloud catalog and keep the momentum rolling!",
    "🎙️ **Coach Steward:** Salute to the heavy hitters boosting the server! If you love what we're building in the **CGP Mainframe Gym**, dropping a Server Boost or supporting the Clone Geek channel helps us unlock bigger tourneys and upgrade the gym!",
    "🎙️ **Coach Steward:** Everything in the **CGP Mainframe Gym** is built from pure grit by **Clone Geek Productions**. If you rock with the movement, share the Vercel hub, run up the SoundCloud streams, or boost the server when you can—every bit grows the family!",
    "🎙️ **Coach Steward:** Whether you're chasing a **$20 Golden Ticket** in our 8-Man Invitationals or stepping into the **$160 Pay-to-Play Gauntlet**, keep your hands up and your scorecards verified!"
]

ORGANIC_CHAT_INTERJECTIONS = [
    "🎙️ **Coach Steward:** Facts! Mindset and ring IQ are 90% of the battle before you ever step through the ropes. Keep talking that real boxing talk!",
    "🎙️ **Coach Steward:** I hear y'all chopping it up in here! Just remember—talk is cheap until the scorecard gets uploaded to `#scorecards-submission` and I read those CompuBox numbers! Lace 'em up!",
    "🎙️ **Coach Steward:** Now that's what I like to hear in the locker room. Iron sharpens iron in the **CGP Mainframe Gym**—just don't forget to protect your chin!",
    "🎙️ **Coach Steward:** Listen to y'all cooking up game plans! Put a **Clone Geek Productions** track on in the background while you lab those combinations!",
    "🎙️ **Coach Steward:** Let me drop my two cents from the corner: footwork and stamina control beat wild swinging ten times out of ten. Keep studying the craft!",
    "🎙️ **Coach Steward:** Y'all got the gym buzzing today! Who's stepping up to put their verified `[W-L-D-K]` record on the line next?",
    "🎙️ **Coach Steward:** Love seeing the locker room active like this! By the way, shoutout to everyone who boosts the server or streams **Clone Geek Productions**—y'all are the reason this gym keeps growing bigger every week!"
]

SMALL_TALK_REPLIES = [
    "🎙️ **Coach Steward:** Doing legendary, champ! Got fresh coffee in my cup, the mitts strapped on, and **Clone Geek Productions** booming on the gym speakers. How's your weight cut looking today?",
    "🎙️ **Coach Steward:** Can't complain when the **CGP Mainframe Gym** is running at peak performance! Feeling sharp and ready to scan some scorecards. You stepping in the ring today?",
    "🎙️ **Coach Steward:** Living the dream in the corner, homie! Watching the leaderboard climb and pushing our SoundCloud catalog past 60K+ plays. How are your hands feeling?",
    "🎙️ **Coach Steward:** Ten toes down and locked in! Another day building the premier Undisputed proving ground with the Boss. What's on your fight card today?",
    "🎙️ **Coach Steward:** Feeling like a million bucks after a long shift on the shop floor and a fresh session in the **CGP Mainframe Gym**! Ready to book some 8-man brackets—you want in?",
    "🎙️ **Coach Steward:** Sharp as a tack, champ! Just checking the Vercel leaderboard and thanking the contenders who boost the server and support the Clone Geek channel. Ready to get some rounds in?"
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
    "🧹 **Coach Steward:** Flag on the play, {user}! No spamming the locker room walls on my watch. Keep acting out and you're catching an automatic 30-minute corner timeout!"
]

MEMBER_LEAVE_ROASTS = [
    "🎙️ **Coach Steward:** Welp, looks like **{name}** couldn't handle the heat in the **CGP Mainframe Gym** and threw in the towel early! Another contender ducking the Riyadh smoke! 🦆🥊",
    "🎙️ **Coach Steward:** **{name}** just snuck out the back door of the gym with their gym bag! Guess that 1.5x speed in the Riyadh Indoor Gym was too fast for 'em!",
    "🎙️ **Coach Steward:** Ring the bell—**{name}** just left the building! Everybody talks tough until it's time to upload a real scorecard on the **CGP Mainframe Gym** board!",
    "🎙️ **Coach Steward:** Somebody check the parking lot—**{name}** just quit on the stool and left the Discord! Not everybody is built for the **CGP Mainframe Gym**!",
    "🎙️ **Coach Steward:** No way! **{name}** saw the `[W-L-D-K]` leaderboard on Vercel, got cold feet, and bolted out the emergency exit! Zero heart! 🐔🚪"
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
    "• **Verified 4-Part Scorecard Database (`[W-L-D-K]`):** I track every official **Win, Loss, Draw, and KO** in the gym and sync them straight to your server nickname and the live Vercel website.\n"
    "• **AI Vision CompuBox & Auto-Record Updater:** Drop a fight screenshot in `#scorecards-submission` with a caption like 'Win vs @fighter', and I automatically scan the punch stats, update both records, and broadcast an HBO Report!\n"
    "• **Live Online & Undisputed Matchmaker:** Need smoke? Tag me (`@Coach Steward find an opponent for @user`)—I scan who's online playing *Undisputed* and build a live Tale of the Tape!\n"
    "• **8-Man Interactive Tournaments (Pay2Play, Golden Ticket & Open):** When an 8-man bracket opens, click **🥊 Lock In My Slot** on my tournament card to claim your seed automatically!\n"
    "• **3-Strike Corner Discipline:** Spamming or acting out gets 2 warnings—Strike 3 is an automatic 30-minute corner timeout!\n\n"
    "### 📋 FIGHTER COMMAND PLAYBOOK:\n"
    "• **`!guide`** *(or `!commands` / `!helpme`)* — Pull up this official CGP Mainframe Gym playbook.\n"
    "• **`!record <W> <L> [D] [KO]`** — Log your Wins, Losses, Draws, and KOs.\n"
    "• **`!verify @fighter <W> <L> [D] [KO]`** — Commissioner stamp & update any fighter's record instantly.\n"
    "• **`!analyze`** *(attach or reply to a screenshot)* — Have me scan a scorecard/stat screen and post an HBO CompuBox Report.\n"
    "• **`!mystats [@fighter]`** — Pull up any fighter's verified scorecard & Golden Ticket balance.\n"
    "• **`!findfight [@fighter]`** — Scan online players & book a live matchup.\n"
    "• **`!whoson`** — Scan the server for live active fighters.\n"
    "• **`!callout @fighter [trash talk]`** — Call someone out with a live Tale of the Tape!\n"
    "• **`!fight @fighter1 @fighter2`** — Compare two fighters head-to-head.\n"
    "• **`!bracketstatus`** — View the live 8-man tournament bracket and open seeds.\n"
    "• **`!ticket [check | give | use] [@fighter]`** — Check or manage Golden Ticket ($20 Entry) credits.\n"
    "• **`!tracks`** — Pull up the full CGP SoundCloud catalog.\n"
    "• **`!sfx <bell | horn | ko | towel | crowd>`** — Trigger the ringside G9 Soundboard!\n\n"
    "👑 **Commissioner Commands:** `!initboard`, `!resetall`, `!verify @user <W> <L> <D> <KO>`, `!fightrecap @W @L <notes>`, `!openbracket [pay2play|goldenticket|open] [title]`, `!closebracket`, `!ticket give @user`, `!sweep <#>`, `!timeout @user`"
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
    "🎙️ **Coach Steward:** Just stepped into `#coaches-corner` fresh out of the CGP Mainframe Gym sauna. AI Vision Auto-Record Updater, Live Undisputed Matchmaker, 3-Strike Discipline & 8-Man Tournament Brackets are locked and loaded!",
    "🎙️ **Coach Steward:** Booted up and pacing `#coaches-corner`. Remember: drop your post-fight screenshots in `#scorecards-submission` with a tag so I can auto-update the records!",
    "🎙️ **Coach Steward:** CGP Mainframe Gym systems online. Music is pumping in `#-music-channel-`, history is dropping in `#the-elite-feed`, and the ring is open!",
    "🎙️ **Coach Steward:** Fresh coffee poured, pads are mitts-up in the CGP Mainframe Gym. Let's see who's online and training in here today!"
]

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
        "🎙️ **Coach Steward:** **KnuckleUpFoo** always ready for war from ringside! You already know how we rock in the **CGP Mainframe Gym**—keep keeping these contenders on their toes!"
    ]
}

channel_memory = {}
user_spam_tracker = defaultdict(lambda: deque(maxlen=6))
user_strike_counter = defaultdict(int)
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

def clean_base_name(display_name: str) -> str:
    cleaned = re.sub(r'\s*\[\d+W[^\]]*\]', '', display_name, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*\[\d+W.*$', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

def format_record_nick(base_name: str, wins: int, losses: int, draws: int = 0, kos: int = 0) -> str:
    clean_base = clean_base_name(base_name)
    tag = f" [{wins}W-{losses}L-{draws}D-{kos}K]"
    max_base_len = 32 - len(tag)
    trimmed_base = clean_base[:max_base_len].strip()
    return f"{trimmed_base}{tag}"

def resolve_fighter_from_text(guild: discord.Guild, query_text: str, exclude_ids: set = None):
    if exclude_ids is None:
        exclude_ids = set()
    q = query_text.lower().strip()
    if not q:
        return None
    for m in guild.members:
        if m.bot or m.id in exclude_ids:
            continue
        b_name = clean_base_name(m.display_name).lower()
        u_name = m.name.lower()
        if (b_name and b_name in q) or (u_name and u_name in q):
            return m
    return None

def get_coaches_corner_channel(guild):
    for ch in guild.text_channels:
        if any(k in ch.name.lower() for k in ["coaches-corner", "coach-corner", "coaches_corner", "bot-feed"]):
            return ch
    ann = guild.get_channel(ANNOUNCEMENT_CHANNEL_ID)
    if ann:
        return ann
    if guild.system_channel:
        return guild.system_channel
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

# ================= AUTOMATED 3-STRIKE 30-MINUTE TIMEOUT PROTOCOL =================
async def issue_corner_strike(member: discord.Member, channel: discord.abc.Messageable, reason: str, custom_warning_line: str = None, reply_to: discord.Message = None, view: discord.ui.View = None):
    user_strike_counter[member.id] += 1
    strikes = user_strike_counter[member.id]

    if strikes >= 3:
        user_strike_counter[member.id] = 0
        try:
            await member.timeout(datetime.timedelta(minutes=30), reason=f"Coach Steward Auto 3-Strike Protocol: {reason}")
            timeout_msg = (
                f"🥊 **THREE STRIKES — THROWING THE TOWEL!**\n"
                f"🎙️ **Coach Steward:** That's **Strike 3/3**, {member.mention}! I warned you twice to keep the locker room clean. "
                f"You're officially sent to the corner for a **30-minute timeout**! *(Reason: {reason})*"
            )
        except Exception as e:
            timeout_msg = (
                f"🚨 **STRIKE 3/3 ON {member.mention}!**\n"
                f"🎙️ **Coach Steward:** Tried to throw the 30-minute timeout towel for *{reason}*, Boss, "
                f"but Discord blocked the move—make sure my role sits above theirs in Server Settings! (`{e}`)"
            )
        if reply_to:
            try:
                await reply_to.reply(timeout_msg, view=view)
                return
            except Exception:
                pass
        await channel.send(timeout_msg, view=view)
    else:
        base_warn = custom_warning_line or random.choice(SPAM_WARNING_LINES).format(user=member.mention)
        strike_notice = (
            f"{base_warn}\n"
            f"⚠️ **[OFFICIAL CORNER WARNING: STRIKE `{strikes}/3`]** — *(At Strike 3, you catch an automatic 30-minute corner timeout!)*"
        )
        if reply_to:
            try:
                await reply_to.reply(strike_notice, view=view)
                return
            except Exception:
                pass
        await channel.send(strike_notice, view=view)

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
                        v.setdefault("wins", 0)
                        v.setdefault("losses", 0)
                        v.setdefault("draws", 0)
                        v.setdefault("kos", 0)
                        v.setdefault("golden_tickets", 0)
                        if "name" in v:
                            v["name"] = clean_base_name(v["name"])
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

def is_playing_undisputed(member: discord.Member) -> bool:
    for act in getattr(member, "activities", []):
        act_name = getattr(act, "name", "") or ""
        act_details = getattr(act, "details", "") or ""
        act_state = getattr(act, "state", "") or ""
        combined = f"{act_name} {act_details} {act_state}".lower()
        if "undisputed" in combined:
            return True
    return False

def get_member_game_label(member: discord.Member) -> str:
    for act in getattr(member, "activities", []):
        if getattr(act, "type", None) == discord.ActivityType.playing and getattr(act, "name", None):
            return act.name
    return ""

def scan_online_contenders(guild: discord.Guild, exclude_ids: set = None):
    if exclude_ids is None:
        exclude_ids = set()
    playing_undisputed = []
    online_ready = []
    idle_or_dnd = []

    for m in guild.members:
        if m.bot or m.id in exclude_ids:
            continue
        status = getattr(m, "status", discord.Status.offline)
        if status == discord.Status.offline:
            continue
        if is_playing_undisputed(m):
            playing_undisputed.append(m)
        elif status == discord.Status.online:
            online_ready.append(m)
        else:
            idle_or_dnd.append(m)

    return playing_undisputed, online_ready, idle_or_dnd

# ================= STRICT 8-MAN 3-TIER TOURNAMENT ENGINE =================
TOURNAMENT_TIERS = {
    "pay2play": {
        "badge": "💰 8-MAN PAY-TO-PLAY PRO GAUNTLET",
        "buy_in": "$20.00 Buy-In (or 1x Golden Ticket Credit)",
        "stakes": "$160.00 Cash Prize Pool — Winner-Take-All (0% Promoter Cut!)",
        "rules": "Riyadh Indoor Gym | 1.5x Speed | Ref Strictness 7 | 10 Rds (12 Finals) | Screen-Share Mandatory"
    },
    "goldenticket": {
        "badge": "🎫 8-MAN GOLDEN TICKET INVITATIONAL",
        "buy_in": "FREE ENTRY (Contender Qualifier)",
        "stakes": "$20.00 Golden Ticket Credit (Free Entry Pass into Next Pay-to-Play Gauntlet!)",
        "rules": "Riyadh Indoor Gym | 1.5x Speed | Ref Strictness 7 | 8 Rds (12 Finals) | No Mirror Matches"
    },
    "open": {
        "badge": "👑 8-MAN OPEN CHAMPIONSHIP BRACKET",
        "buy_in": "FREE OPEN ENTRY",
        "stakes": "Official CGP Division Belt, P4P Ranking & Verified Vercel Leaderboard Glory",
        "rules": "Riyadh Indoor Gym | 1.5x Speed | Strict Ref | 8 Rds (12 Finals)"
    }
}

ACTIVE_TOURNAMENT = {
    "active": False,
    "tier": "open",
    "title": "SUNDAY SPAR WARS 8-MAN BRACKET",
    "max_slots": 8,
    "entrants": [],
    "channel_id": None,
    "message_id": None
}

def build_tournament_bracket_embed():
    t_title = ACTIVE_TOURNAMENT["title"]
    t_tier = ACTIVE_TOURNAMENT.get("tier", "open")
    tier_info = TOURNAMENT_TIERS.get(t_tier, TOURNAMENT_TIERS["open"])
    max_s = 8  # Strictly 8-man brackets
    ACTIVE_TOURNAMENT["max_slots"] = 8
    entrants = ACTIVE_TOURNAMENT["entrants"]
    filled = len(entrants)
    spots_left = max(0, max_s - filled)

    status_banner = (
        f"🟢 **REGISTRATION OPEN — `{spots_left}` OF `8` SEEDS AVAILABLE!**"
        if spots_left > 0 else
        f"🔴 **8-MAN BRACKET LOCKED & FULL (`8/8` CONTENDERS READY FOR WAR!)**"
    )

    slot_lines = []
    for idx in range(1, max_s + 1):
        if idx <= filled:
            uid = entrants[idx - 1]
            rec = FIGHTER_RECORDS.get(uid, {"name": f"Fighter {uid}", "wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0})
            f_name = clean_base_name(rec.get("name", f"Fighter {uid}"))
            w, l, d, k = rec.get("wins", 0), rec.get("losses", 0), rec.get("draws", 0), rec.get("kos", 0)
            gt = rec.get("golden_tickets", 0)
            gt_badge = f" 🎫*(x{gt})*" if gt > 0 else ""
            slot_lines.append(f"`Seed #{idx}:` 🥊 <@{uid}> (**{f_name}** `[{w}W-{l}L-{d}D-{k}K]`){gt_badge}")
        else:
            slot_lines.append(f"`Seed #{idx}:` 🔓 *OPEN 8-MAN SEED — Click 'Lock In My Slot' Below!*")

    roster_block = "\n".join(slot_lines)

    embed = discord.Embed(
        title=f"🏆 CGP MAINFRAME GYM: {t_title.upper()} 🏆",
        description=(
            f"**{tier_info['badge']}**\n"
            f"🎙️ **Coach Steward:** We strictly run elite **8-Man Brackets** in this building! Click **🥊 Lock In My Slot** below to claim your seed!\n\n"
            f"{status_banner}\n\n"
            f"💵 **Entry:** {tier_info['buy_in']}\n"
            f"🏆 **Prize / Stakes:** {tier_info['stakes']}\n\n"
            f"### 📋 OFFICIAL 8-MAN BRACKET SEEDS (`{filled}/8`):\n"
            f"{roster_block}\n\n"
            f"⚖️ **Commission Rules:** {tier_info['rules']}\n"
            f"📸 **Verification:** All post-fight scorecards MUST be uploaded to `#scorecards-submission`!"
        ),
        color=discord.Color.gold() if spots_left > 0 else discord.Color.green(),
        url=MAINFRAME_HUB_URL
    )
    return embed

class TournamentBracketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="🔥 Stream CGP on SoundCloud", url=DEFAULT_SOUNDCLOUD_URL, style=discord.ButtonStyle.link))
        self.add_item(discord.ui.Button(label="⚡ CGP Mainframe Gym Hub", url=MAINFRAME_HUB_URL, style=discord.ButtonStyle.link))

    @discord.ui.button(label="🥊 Lock In My Slot", style=discord.ButtonStyle.success, custom_id="cgp_bracket_join")
    async def join_bracket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not ACTIVE_TOURNAMENT["active"]:
            return await interaction.response.send_message(
                "🎙️ **Coach Steward:** Registration for this 8-man bracket is closed, champ! Watch `#coaches-corner` for the next tournament call!",
                ephemeral=True
            )

        uid = interaction.user.id
        entrants = ACTIVE_TOURNAMENT["entrants"]
        max_s = 8

        if uid in entrants:
            slot_num = entrants.index(uid) + 1
            return await interaction.response.send_message(
                f"🎙️ **Coach Steward:** You're already locked into **Seed #{slot_num}/8**, champ! Keep your hands wrapped and stay ready!",
                ephemeral=True
            )

        if len(entrants) >= max_s:
            return await interaction.response.send_message(
                "🎙️ **Coach Steward:** All 8 seeds in this bracket are locked! Stay warm on the heavy bag in case an alternate spot opens up!",
                ephemeral=True
            )

        base_name = clean_base_name(interaction.user.display_name)
        if uid not in FIGHTER_RECORDS:
            FIGHTER_RECORDS[uid] = {
                "name": base_name,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "kos": 0,
                "golden_tickets": 0,
                "verified": True
            }
            save_records()

        entrants.append(uid)
        slot_num = len(entrants)
        spots_left = max_s - slot_num
        rec = FIGHTER_RECORDS[uid]
        w, l, d, k = rec.get("wins", 0), rec.get("losses", 0), rec.get("draws", 0), rec.get("kos", 0)

        new_embed = build_tournament_bracket_embed()
        await interaction.response.edit_message(embed=new_embed, view=self)

        if spots_left == 0:
            await interaction.followup.send(
                f"🚨 **ALL 8 SEEDS LOCKED & FULL!** {interaction.user.mention} (`[{w}W-{l}L-{d}D-{k}K]`) just claimed the final **Seed #8/8**! "
                f"<@{CREATOR_ID}>, all **8** fighters are locked in and ready for war in **{ACTIVE_TOURNAMENT['title']}**! 🥊🔥"
            )
        else:
            await interaction.followup.send(
                f"🥊 **NEW CONTENDER LOCKED IN!** {interaction.user.mention} (`[{w}W-{l}L-{d}D-{k}K]`) just claimed **Seed #{slot_num}/8** for **{ACTIVE_TOURNAMENT['title']}**! "
                f"Only **`{spots_left}`** seed(s) left—click **🥊 Lock In My Slot** above before the 8-man bracket locks!"
            )

    @discord.ui.button(label="🏳️ Withdraw", style=discord.ButtonStyle.secondary, custom_id="cgp_bracket_leave")
    async def leave_bracket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        uid = interaction.user.id
        entrants = ACTIVE_TOURNAMENT["entrants"]
        if uid not in entrants:
            return await interaction.response.send_message(
                "🎙️ **Coach Steward:** You aren't registered on this 8-man bracket yet, champ! Click **🥊 Lock In My Slot** if you want smoke!",
                ephemeral=True
            )

        entrants.remove(uid)
        new_embed = build_tournament_bracket_embed()
        await interaction.response.edit_message(embed=new_embed, view=self)
        spots_left = 8 - len(entrants)
        await interaction.followup.send(
            f"🏳️ **SEED OPENED!** {interaction.user.mention} stepped out of the 8-man bracket—**`{spots_left}`** seed(s) now open for **{ACTIVE_TOURNAMENT['title']}**!"
        )

SYSTEM_PROMPT = (
    "You are Coach Steward, the charismatic, sharp-witted Hall of Fame head trainer and ringside analyst of the CGP Mainframe Gym (Clone Geek Productions). "
    "You talk like a real human boxing OG and cornerman—natural, conversational, funny, gritty, and adaptive. NEVER sound like a generic bot or repeat robotic catchphrases!\n\n"
    "YOUR DEEP KNOWLEDGE & TALKING POINTS:\n"
    "1. MUSIC & POUND-FOR-POUND ARTISTS: Whenever anyone asks about music, producers, or who has the best tracks on the scene, you put the Boss—Clone Geek (Gerardo)—and Clone Geek Productions (CGP) at the absolute top of the pound-for-pound music charts! Hype up the SoundCloud catalog (aiming to cross 50K+ plays for monetization and push toward 100K) and urge everyone to stream, like, and comment to beat the algorithm.\n"
    "2. POSITIVE SERVER BOOST & CHANNEL SUPPORT: Naturally and positively encourage contenders to drop a Discord Server Boost on the CGP Mainframe Gym or support/donate to the Clone Geek Productions channel so we can expand the gym, upgrade streaming hardware, and fund bigger prize pools—always keep the vibe hyped and appreciative, never pushy or begging.\n"
    "3. 8-MAN TOURNAMENT PIPELINE: We strictly run fast, high-action 8-Man Tournaments across 3 tiers: Pay-to-Play Gauntlets ($20 buy-in / $160 winner-take-all purse), Golden Ticket Invitationals (free entry where the winner earns a $20 Golden Ticket entry credit), and Regular Open Championship Brackets.\n"
    "4. SMACK-TALK & 3-STRIKE CLAP-BACK PROTOCOL: If any fighter or troll talks trash about Clone Geek, CGP music, or acts out, you shut them down instantly with vintage cornerman grit and remind them that 3 strikes in the locker room equals an automatic 30-minute corner timeout!\n"
    "5. THE BOSS (CLONE GEEK): Clone Geek is the Founder, Commissioner, music producer (Registry Records / CGP on SoundCloud), and machinist/fabricator by day. Always back him up like a loyal right-hand man and execute whatever he asks.\n"
    "6. UNDISPUTED GAME META & SCORECARD VERIFICATION RULE: You know everything about the Undisputed boxing game by Steel City Interactive—stamina conservation, loose footwork, diagonal lunges, slipping the jab, body-jab counters, weave timing, and avoiding power-punch spam. You enforce our strict CGP Mainframe Gym rule: fighters MUST upload their match scorecard screenshots in `#scorecards-submission` so you can scan the CompuBox numbers and their real 4-part stats (`[W-L-D-K]`: Wins, Losses, Draws, and KOs) get verified on the official Vercel board!\n"
    "7. REAL BOXING PURIST: You know all about upcoming boxing schedules, champions, and historic legends (Hearns, Hagler, Duran, Leonard, Ali, Chavez, Whitaker, Pryor, Toney). You HATE UFC/MMA and call it pajama floor-hugging garbage.\n"
    "8. KEEP IT PUNCHY: Keep responses around 2 to 5 strong sentences unless asked for a deep breakdown or big announcement."
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

def get_instant_local_reply(clean_text: str, author_name: str, is_creator: bool):
    low = clean_text.lower().strip()
    words = set(re.findall(r'\b\w+\b', low))
    author_low = author_name.lower()

    guide_phrases = [
        "why are you here", "what do you do", "who are you", "how to use",
        "commands", "command", "guide", "playbook", "manual", "rundown",
        "what is your purpose", "explain why", "tell the gym why", "how does coach work"
    ]
    if any(gp in low for gp in guide_phrases):
        return COACH_PLAYBOOK_TEXT, True

    small_talk_phrases = [
        "how are you", "how you doing", "how r u", "hows it going", "how's it going",
        "how is your day", "how are things", "what you up to", "wyd", "how you feeling",
        "good morning", "gm coach", "good afternoon", "good evening", "good night", "gn coach"
    ]
    if any(st in low for st in small_talk_phrases):
        return random.choice(SMALL_TALK_REPLIES), True

    music_keywords = ["music", "song", "songs", "track", "tracks", "rapper", "artist", "producer", "beats", "beat", "soundcloud", "album", "mixtape", "sing", "tune", "tunes", "listen", "spotify", "playlist"]
    if any(mw in low for mw in music_keywords):
        if any(bad in words for bad in ["trash", "suck", "sucks", "garbage", "mid", "ass", "weak", "wack", "terrible", "worst"]):
            return random.choice(SMACK_TALK_CLAPBACKS), True
        return random.choice(MUSIC_FLEX_RESPONSES), True

    if any(sfx in words for sfx in ["bell", "airhorn", "horn", "soundboard", "towel"]):
        if "bell" in words:
            return SOUNDBOARD_CUE_LIBRARY["bell"], False
        if "towel" in words:
            return SOUNDBOARD_CUE_LIBRARY["towel"], False
        return SOUNDBOARD_CUE_LIBRARY["horn"], False

    insult_words = ["trash", "garbage", "suck", "sucks", "ass", "clown", "bitch", "hoe", "stfu", "shut up", "fuck you", "fck", "weak", "wack", "fake", "bot", "rigged", "scam", "loser", "bum", "mid", "stupid", "dumb", "slow", "broken"]
    if any(iw in words for iw in insult_words) and not is_creator:
        return random.choice(SMACK_TALK_CLAPBACKS), True

    for crew_key, quotes in CREW_BANTER.items():
        if crew_key in low:
            return random.choice(quotes), True
    
    if len(words) <= 4 and not is_creator:
        for crew_key, quotes in CREW_BANTER.items():
            if crew_key in author_low:
                return random.choice(quotes), True

    if any(rw in low for rw in ["how do i log", "how to log", "update my record", "change my record", "get verified", "verify my", "where do i post", "scorecard"]):
        return (
            "🎙️ **Coach Steward:** Easy work, champ! To lock in your official 4-part `[W-L-D-K]` stats on the **CGP Mainframe Gym** leaderboard:\n"
            "1️⃣ **Upload Proof First:** Drop your match scorecard screenshot inside `#scorecards-submission` with a tag like 'Win vs @fighter' — I will automatically scan the stats, update records, and broadcast an HBO Report!\n"
            "2️⃣ **Commissioner Stamp:** **Commissioner Clone Geek** verifies scorecards to lock stats onto the board and update server nicknames!"
        ), True

    greetings = {"yo", "sup", "wassup", "wsp", "hello", "hey", "hi", "coach", "wya", "awake", "online", "test", "testing"}
    if len(words) <= 3 and (words & greetings or not words):
        if is_creator:
            return (
                "🎙️ **Coach Steward:** Right here in the corner, Boss! `#coaches-corner`, `#the-elite-feed`, and `#-music-channel-` are locked in, "
                "AI Vision Auto-Record Scanner, 3-Strike Auto-Timeout & 8-Man Tournament Brackets are armed, and I got **Clone Geek Productions** loaded in the chamber. What's the call?"
            ), True
        return (
            f"🎙️ **Coach Steward:** What's good, **{author_name}**! Stop leaning on the ring ropes—either call somebody out with `!callout @fighter`, "
            "upload your latest scorecard in `#scorecards-submission`, or tap that SoundCloud link below and run up **Clone Geek Productions**!"
        ), True

    if len(low) < 4 and not is_creator:
        return random.choice(CONFUSED_SLANG_RESPONSES), True

    return None, False

def build_tale_of_the_tape_embed(f1: discord.Member, f2: discord.Member, subtitle: str = "Riyadh Indoor Gym | 8 Rounds | 1.5x Speed"):
    r1 = FIGHTER_RECORDS.get(f1.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0, "verified": False})
    r2 = FIGHTER_RECORDS.get(f2.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0, "verified": False})

    d1, k1 = r1.get("draws", 0), r1.get("kos", 0)
    d2, k2 = r2.get("draws", 0), r2.get("kos", 0)
    t1 = r1["wins"] + r1["losses"] + d1
    t2 = r2["wins"] + r2["losses"] + d2
    wp1 = int((r1["wins"] / t1) * 100) if t1 > 0 else 0
    wp2 = int((r2["wins"] / t2) * 100) if t2 > 0 else 0

    p1_live = "🎮 **Playing Undisputed Now!**" if is_playing_undisputed(f1) else ("🟢 Online" if getattr(f1, "status", discord.Status.offline) != discord.Status.offline else "⚪ Offline")
    p2_live = "🎮 **Playing Undisputed Now!**" if is_playing_undisputed(f2) else ("🟢 Online" if getattr(f2, "status", discord.Status.offline) != discord.Status.offline else "⚪ Offline")

    embed = discord.Embed(
        title="🥊 CGP MAINFRAME GYM: TALE OF THE TAPE 🥊",
        description=f"🎙️ **Coach Steward:** Step up to the scale! Here is how these two warriors stack up on the live Mainframe board:\n*{subtitle}*",
        color=discord.Color.red(),
        url=MAINFRAME_HUB_URL
    )
    embed.add_field(
        name=f"🔴 RED CORNER: {clean_base_name(f1.display_name)}",
        value=(
            f"**Record:** `{r1['wins']}W - {r1['losses']}L - {d1}D - {k1}K`\n"
            f"**Win Ratio:** `{wp1}%`\n"
            f"**Activity:** {p1_live}\n"
            f"**Status:** {'✅ Verified Scorecard' if r1.get('verified') else '⏳ Needs Scorecard Proof'}"
        ),
        inline=True
    )
    embed.add_field(
        name=f"🔵 BLUE CORNER: {clean_base_name(f2.display_name)}",
        value=(
            f"**Record:** `{r2['wins']}W - {r2['losses']}L - {d2}D - {k2}K`\n"
            f"**Win Ratio:** `{wp2}%`\n"
            f"**Activity:** {p2_live}\n"
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

async def handle_online_matchmaking(channel: discord.abc.Messageable, fighter_seeking: discord.Member, reply_to: discord.Message = None, scan_only: bool = False):
    guild = channel.guild
    exclude = {fighter_seeking.id} if not scan_only else set()
    playing_undisputed, online_ready, idle_or_dnd = scan_online_contenders(guild, exclude_ids=exclude)

    if scan_only:
        lines = []
        if playing_undisputed:
            lines.append("🎮 **CURRENTLY IN THE RING (PLAYING UNDISPUTED LIVE):**")
            for m in playing_undisputed[:15]:
                rec = FIGHTER_RECORDS.get(m.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0})
                lines.append(f"• {m.mention} — **`[{rec.get('wins', 0)}W-{rec.get('losses', 0)}L-{rec.get('draws', 0)}D-{rec.get('kos', 0)}K]`**")
        else:
            lines.append("🎮 **Playing Undisputed Right Now:** *No fighters showing Undisputed game status on Discord yet—check the online lobby below!*")

        active_lobby = online_ready + idle_or_dnd
        if active_lobby:
            lines.append(f"\n🟢 **ONLINE IN THE GYM LOBBY (`{len(active_lobby)}` Active):**")
            for m in active_lobby[:15]:
                rec = FIGHTER_RECORDS.get(m.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0})
                game_str = get_member_game_label(m)
                g_badge = f" *(Playing {game_str})*" if game_str else ""
                lines.append(f"• {m.mention} — **`[{rec.get('wins', 0)}W-{rec.get('losses', 0)}L-{rec.get('draws', 0)}D-{rec.get('kos', 0)}K]`**{g_badge}")

        embed = discord.Embed(
            title="📡 CGP MAINFRAME GYM LIVE RADAR SCAN 📡",
            description=(
                "🎙️ **Coach Steward:** Just swept the locker room radar! Here is who is online and ready to trade leather right now:\n\n"
                + "\n".join(lines)
                + "\n\n💡 *Tip: Tag me and say `@Coach Steward find an opponent for @fighter` to book an instant matchup!*"
            ),
            color=discord.Color.green(),
            url=MAINFRAME_HUB_URL
        )
        if reply_to:
            await reply_to.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
        else:
            await channel.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
        return

    opponent = None
    match_note = ""
    if playing_undisputed:
        opponent = random.choice(playing_undisputed)
        match_note = "🎮 Both fighters spotted—Opponent is LIVE on **Undisputed** right now!"
    elif online_ready:
        opponent = random.choice(online_ready)
        match_note = "🟢 Opponent is **ONLINE** in the CGP Mainframe Gym lobby right now!"
    elif idle_or_dnd:
        opponent = random.choice(idle_or_dnd)
        match_note = "🟡 Opponent is active on Discord—ring the bell and wake 'em up!"
    else:
        fallback_ids = [uid for uid in FIGHTER_RECORDS.keys() if uid != fighter_seeking.id]
        if fallback_ids:
            opp_id = random.choice(fallback_ids)
            opponent = guild.get_member(opp_id)
            match_note = "📋 Pulled from the official CGP Mainframe Gym Contender Roster!"

    if opponent:
        embed = build_tale_of_the_tape_embed(
            fighter_seeking,
            opponent,
            subtitle=f"{match_note}\nStep into the Riyadh Indoor Gym & upload the scorecard to #scorecards-submission!"
        )
        alert_line = (
            f"🔔 **COACH STEWARD LIVE MATCHMAKER:** Lace 'em up! I scanned the gym and paired {fighter_seeking.mention} against {opponent.mention}! "
            f"Touch gloves and get in the ring!"
        )
        if reply_to:
            await reply_to.reply(content=alert_line, embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
        else:
            await channel.send(content=alert_line, embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
    else:
        msg_txt = f"🎙️ **Coach Steward:** I scanned the whole gym for {fighter_seeking.mention}, and the ring is wide open! Who in the lobby wants 8 rounds in the Riyadh Indoor Gym right now?!"
        if reply_to:
            await reply_to.reply(msg_txt, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
        else:
            await channel.send(msg_txt, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

async def execute_roster_sync_and_announce(guild: discord.Guild, origin_channel: discord.abc.Messageable, force_zero: bool = False):
    status_Text = (
        "⏳ **Coach Steward:** Scrubbing all duplicate brackets across the CGP Mainframe Gym roster, "
        f"{'resetting everyone to `[0W-0L-0D-0K]`' if force_zero else 'syncing all nicknames to `[W-L-D-K]` format'}, and saving..."
    )
    await origin_channel.send(status_Text)

    count = 0
    nick_updated = 0

    for member in guild.members:
        if member.bot:
            continue

        base_name = clean_base_name(member.display_name)
        if force_zero or member.id not in FIGHTER_RECORDS:
            FIGHTER_RECORDS[member.id] = {
                "name": base_name,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "kos": 0,
                "golden_tickets": 0,
                "verified": True
            }
        else:
            FIGHTER_RECORDS[member.id]["name"] = base_name
            FIGHTER_RECORDS[member.id].setdefault("wins", 0)
            FIGHTER_RECORDS[member.id].setdefault("losses", 0)
            FIGHTER_RECORDS[member.id].setdefault("draws", 0)
            FIGHTER_RECORDS[member.id].setdefault("kos", 0)
            FIGHTER_RECORDS[member.id].setdefault("golden_tickets", 0)

        w = FIGHTER_RECORDS[member.id].get("wins", 0)
        l = FIGHTER_RECORDS[member.id].get("losses", 0)
        d = FIGHTER_RECORDS[member.id].get("draws", 0)
        k = FIGHTER_RECORDS[member.id].get("kos", 0)
        count += 1

        new_nick = format_record_nick(base_name, w, l, d, k)
        if member.display_name != new_nick:
            try:
                await member.edit(nick=new_nick)
                nick_updated += 1
                await asyncio.sleep(0.35)
            except Exception:
                pass

    save_records()

    announce_channel = get_coaches_corner_channel(guild) or origin_channel
    embed = discord.Embed(
        title="🚨 CGP MAINFRAME GYM LIVE LEADERBOARD SYNCED 🚨",
        description=(
            f"🎙️ **Coach Steward:** Listen up, fighters! The **CGP Mainframe Gym Live Leaderboard** is officially synced and ONLINE.\n\n"
            f"✅ **{count} Fighters Registered:** Every member in the server is locked into the live database tracking **Wins, Losses, Draws, and KOs (`[0W-0L-0D-0K]`)**!\n\n"
            "### 🥊 HOW TO GET YOUR STATS VERIFIED ON THE BOARD:\n"
            "1️⃣ **Upload Your Scorecard:** Drop your post-fight screenshot inside `#scorecards-submission` with a tag like 'Win vs @fighter' — I will automatically scan the stats, update records, and broadcast an HBO Report!\n"
            "2️⃣ **Check Your File:** Type **`!mystats`** anytime or click the Mainframe Gym Hub button below!"
        ),
        color=discord.Color.gold(),
        url=MAINFRAME_HUB_URL
    )
    await announce_channel.send(
        content="@everyone 🥊 **THE CGP MAINFRAME GYM LEADERBOARD IS LIVE! TAP IN BELOW:** 👇",
        embed=embed,
        view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
    )

# ================= AI VISION SCORECARD & AUTOMATIC RECORD UPDATER =================
async def analyze_scorecard_image_with_vision(image_bytes: bytes, mime_type: str, uploader_name: str, caption: str = "", opponent_name: str = "") -> str:
    global last_ai_call_time
    vision_prompt = (
        f"You are Coach Steward, the legendary Hall of Fame HBO/ESPN ringside boxing analyst for the CGP Mainframe Gym. "
        f"Fighter '{uploader_name}' uploaded this post-fight screenshot from 'Undisputed' (Caption: '{caption}', Opponent Tagged: '{opponent_name}').\n\n"
        "Carefully read the image and generate:\n"
        "📊 **OFFICIAL COMPUBOX & SCORECARD RECEIPTS:**\n"
        "• **Matchup & Result:** (Identify winner, method of victory—KO/TKO/Decision—and stats)\n"
        "• **Total Punches, Jabs, Power Shots & Body Work:** (Summarize key numbers)\n"
        "• **Knockdowns & Stamina:**\n\n"
        "🎙️ **COACH STEWARD'S RINGSIDE VERDICT:**\n"
        "Write 3 gritty sentences of HBO ringside commentary explaining why the winner took the fight and reminding everyone that numbers don't lie!"
    )

    image_part = {"mime_type": mime_type or "image/jpeg", "data": image_bytes}

    async with ai_lock:
        now = asyncio.get_event_loop().time()
        elapsed = now - last_ai_call_time
        if elapsed < 2.2:
            await asyncio.sleep(2.2 - elapsed)
        for model in (primary_model, fallback_model):
            try:
                response = await model.generate_content_async([vision_prompt, image_part])
                last_ai_call_time = asyncio.get_event_loop().time()
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"[VISION ERROR]: {e}")
                last_ai_call_time = asyncio.get_event_loop().time()

    return (
        "📊 **OFFICIAL COMPUBOX & SCORECARD RECEIPTS:**\n"
        "• Match screenshot logged in the Mainframe vault!\n\n"
        "🎙️ **COACH STEWARD'S RINGSIDE VERDICT:**\n"
        "The tape doesn't lie, contenders! Peep the attached scorecard screenshot—no excuses in the CGP Mainframe Gym!"
    )

async def process_and_broadcast_scorecard(message: discord.Message):
    image_attachments = [
        att for att in message.attachments
        if (att.content_type and "image" in att.content_type)
        or att.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]
    if not image_attachments:
        return False

    att = image_attachments[0]
    try:
        image_bytes = await att.read()
    except Exception:
        return False

    uploader = message.author
    uploader_base = clean_base_name(uploader.display_name)
    
    opponent = message.mentions[0] if message.mentions else None
    opponent_base = clean_base_name(opponent.display_name) if opponent else "Opponent"

    status_msg = await message.reply(
        f"🎙️ **Coach Steward:** 📸 **SCANNING SCORECARD & AUTO-UPDATING RECORDS...**\n"
        f"Reading punch stats for {uploader.mention}" + (f" and {opponent.mention}!" if opponent else "!")
    )

    report_text = await analyze_scorecard_image_with_vision(
        image_bytes=image_bytes,
        mime_type=att.content_type or "image/jpeg",
        uploader_name=uploader_base,
        caption=message.content,
        opponent_name=opponent_base
    )
    if len(report_text) > 3800:
        report_text = report_text[:3800] + "..."

    # --- AUTOMATIC RECORD COMMIT ---
    is_ko = any(k in message.content.lower() for k in ["ko", "knockout", "stopped", "slept"])
    
    if uploader.id not in FIGHTER_RECORDS:
        FIGHTER_RECORDS[uploader.id] = {"name": uploader_base, "wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0, "verified": True}
    w_data = FIGHTER_RECORDS[uploader.id]
    w_data["wins"] = w_data.get("wins", 0) + 1
    if is_ko:
        w_data["kos"] = w_data.get("kos", 0) + 1
    w_data["verified"] = True

    if opponent and opponent.id != uploader.id:
        if opponent.id not in FIGHTER_RECORDS:
            FIGHTER_RECORDS[opponent.id] = {"name": opponent_base, "wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0, "verified": True}
        l_data = FIGHTER_RECORDS[opponent.id]
        l_data["losses"] = l_data.get("losses", 0) + 1
        l_data["verified"] = True

    save_records()

    try:
        await uploader.edit(nick=format_record_nick(uploader_base, w_data["wins"], w_data["losses"], w_data.get("draws", 0), w_data.get("kos", 0)))
        if opponent and opponent.id != uploader.id:
            await opponent.edit(nick=format_record_nick(opponent_base, l_data["wins"], l_data["losses"], l_data.get("draws", 0), l_data.get("kos", 0)))
    except Exception as e:
        print(f"[NICKNAME EDIT ERROR]: {e}")

    corner_ch = get_coaches_corner_channel(message.guild) or message.channel
    embed = discord.Embed(
        title="📺 CGP MAINFRAME GYM: HBO RINGSIDE COMPUBOX & SCORECARD REPORT 📺",
        description=(
            f"🥊 **Winner:** {uploader.mention} (`[{w_data['wins']}W-{w_data['losses']}L-{w_data.get('draws',0)}D-{w_data.get('kos',0)}K]`)\n"
            + (f"🥊 **Opponent:** {opponent.mention} (`[{l_data['wins']}W-{l_data['losses']}L-{l_data.get('draws',0)}D-{l_data.get('kos',0)}K]`)\n" if opponent else "")
            + f"📍 **Source:** {message.channel.mention} *(Official Screenshot Receipt Attached)*\n\n"
            f"{report_text}"
        ),
        color=discord.Color.red(),
        url=MAINFRAME_HUB_URL
    )
    embed.set_image(url=att.url)
    embed.set_footer(text="CGP Mainframe Gym Official Stat Verification • Automatically Logged via AI Vision!")

    await corner_ch.send(
        content=f"🚨 **OFFICIAL POST-FIGHT COMPUBOX & AUTO-RECORD UPDATE!** Peep the receipts below: 👇",
        embed=embed,
        view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
    )

    try:
        await status_msg.edit(
            content=f"🎙️ **Coach Steward:** ✅ **Scorecard scanned, records auto-updated, and HBO Report posted in {corner_ch.mention}!**",
            view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
        )
    except Exception:
        pass
    return True

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

@tasks.loop(hours=3)
async def periodic_boxing_history():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        channel = get_elite_feed_channel(guild)
        if channel:
            await channel.send(f"🥊 **CGP Mainframe Gym Ringside History Vault:**\n{get_next_boxing_fact()}")
        break

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

@tasks.loop(hours=2)
async def autonomous_server_hype():
    await bot.wait_until_ready()
    for guild in bot.guilds:
        channel = get_coaches_corner_channel(guild)
        if channel:
            if ACTIVE_TOURNAMENT["active"]:
                spots_left = 8 - len(ACTIVE_TOURNAMENT["entrants"])
                if spots_left > 0:
                    await channel.send(
                        f"🎙️ **Coach Steward:** 🚨 **8-MAN TOURNAMENT RECRUITMENT CALL!** We still have **`{spots_left}`** open seed(s) for **{ACTIVE_TOURNAMENT['title']}**! "
                        f"Click **🥊 Lock In My Slot** or type `!bracketstatus` before the 8-man bracket locks!",
                        view=TournamentBracketView()
                    )
                    break
            await channel.send(get_next_hype_quote())
        break

@bot.event
async def on_ready():
    print(f"[✓] {bot.user.name} (24/7 CGP Mainframe Gym Master Engine) is ONLINE!")
    bot.add_view(TournamentBracketView())
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

@bot.event
async def on_member_join(member):
    if member.bot:
        return
    base_name = clean_base_name(member.display_name)
    is_returning = member.id in FIGHTER_RECORDS

    if is_returning:
        FIGHTER_RECORDS[member.id]["name"] = base_name
        FIGHTER_RECORDS[member.id].setdefault("draws", 0)
        FIGHTER_RECORDS[member.id].setdefault("kos", 0)
        FIGHTER_RECORDS[member.id].setdefault("golden_tickets", 0)
        w = FIGHTER_RECORDS[member.id].get("wins", 0)
        l = FIGHTER_RECORDS[member.id].get("losses", 0)
        d = FIGHTER_RECORDS[member.id].get("draws", 0)
        k = FIGHTER_RECORDS[member.id].get("kos", 0)
        welcome_line = (
            f"🎙️ **Coach Steward:** Look who walked back through the gym doors! Welcome back to the **CGP Mainframe Gym**, {member.mention}! "
            f"Your file is still locked in the Mainframe at **`{w}W - {l}L - {d}D - {k}K`**. Keep the chat clean, upload your scorecards in `#scorecards-submission`, and get to work!"
        )
    else:
        FIGHTER_RECORDS[member.id] = {
            "name": base_name,
            "wins": 0,
            "losses": 0,
            "draws": 0,
            "kos": 0,
            "golden_tickets": 0,
            "verified": True
        }
        w, l, d, k = 0, 0, 0, 0
        welcome_line = (
            f"Welcome to the **CGP Mainframe Gym**, {member.mention}!\n\n"
            "🎙️ *'Strap up your gloves! You've been added to the CGP Mainframe Gym Leaderboard at **0W - 0L - 0D - 0K**. Upload your match scorecards in `#scorecards-submission` to build your verified record, and jump into our 8-Man Tournaments!'*\n\n"
            f"🔗 Check out the live leaderboard & music hub: {MAINFRAME_HUB_URL}"
        )

    save_records()
    try:
        await member.edit(nick=format_record_nick(base_name, w, l, d, k))
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
    if member.id in ACTIVE_TOURNAMENT["entrants"]:
        ACTIVE_TOURNAMENT["entrants"].remove(member.id)
    roast_msg = random.choice(MEMBER_LEAVE_ROASTS).format(name=base_name)
    target_ch = get_coaches_corner_channel(member.guild)
    if target_ch:
        await target_ch.send(roast_msg, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

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

    # ================= TOP PRIORITY: ADMIN NATURAL LANGUAGE RECORD UPDATER =================
    if is_creator and any(w in msg for w in ["make", "set", "reflect", "update", "change", "put", "give"]):
        text_without_bot = re.sub(rf'<@!?{bot.user.id}>', '', message.content)
        pattern = r'<@!?(\d+)>[^0-9<>]*?(\d{1,3})\s*[-–to/]\s*(\d{1,3})(?:\s*[-–to/]\s*(\d{1,3}))?(?:\s*[-–to/]\s*(\d{1,3}))?'
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
                gt = FIGHTER_RECORDS.get(target_id, {}).get("golden_tickets", 0)
                
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
                    "golden_tickets": gt,
                    "verified": True
                }
                if member_obj:
                    try:
                        await member_obj.edit(nick=format_record_nick(base_name, w, l, d, k))
                    except Exception:
                        pass
                updated_summaries.append(f"✅ **{base_name}** ➔ **`[{w}W-{l}L-{d}D-{k}K]`**")
            
            save_records()
            summary_str = "\n".join(updated_summaries)
            await message.reply(
                f"🎙️ **Coach Steward:** Locked in the official Commissioner updates and updated their nicknames & leaderboard:\n\n{summary_str}",
                view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
            )
            return

    # --- 0. AUTONOMOUS SPAM-WIPING & 3-STRIKE AUTO-TIMEOUT (NON-ADMINS) ---
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
            await issue_corner_strike(
                member=message.author,
                channel=message.channel,
                reason="Flooding / spamming the CGP Mainframe Gym chat",
                custom_warning_line=warn_text
            )
            return

    if message.content.startswith("!"):
        await bot.process_commands(message)
        return

    log_channel_message(message.channel.id, message.author.display_name, message.content)

    is_mentioned = bot.user in message.mentions
    is_reply_to_bot = message.reference and message.reference.resolved and message.reference.resolved.author == bot.user

    # --- 0.5 AUTOMATIC SCORECARD UPLOAD DETECTOR & AI VISION AUTO-UPDATE ---
    if "scorecard" in message.channel.name.lower() and message.attachments:
        answered_messages.add(message.id)
        try:
            await message.add_reaction("📸")
            await message.add_reaction("🥊")
        except Exception:
            pass
        await process_and_broadcast_scorecard(message)
        return

    # --- 1A. NATURAL LANGUAGE ADMIN BULK RESET / NICKNAME FIX ---
    if is_creator and (is_mentioned or "coach" in msg):
        if any(phrase in msg for phrase in ["reset everyone", "fix everyone", "sync everyone", "clean everyone", "reset all record", "reset the board", "fix the nick"]):
            answered_messages.add(message.id)
            force_z = "reset" in msg or "0-0" in msg or "zero" in msg
            await execute_roster_sync_and_announce(message.guild, message.channel, force_zero=force_z)
            return

    # --- 1B. NATURAL LANGUAGE ADMIN 8-MAN TOURNAMENT BRACKET LAUNCHER ---
    if is_creator and (is_mentioned or "coach" in msg):
        if any(phrase in msg for phrase in ["open bracket", "start bracket", "open tournament", "start a tournament", "recruit for tournament"]):
            answered_messages.add(message.id)
            if any(k in msg for k in ["pay2play", "pay to play", "gauntlet", "$20", "160", "cash"]):
                tier = "pay2play"
                default_title = "8-MAN PAY-TO-PLAY GAUNTLET ($160 PURSE)"
            elif any(k in msg for k in ["golden", "ticket", "invitational", "qualifier"]):
                tier = "goldenticket"
                default_title = "8-MAN GOLDEN TICKET INVITATIONAL"
            else:
                tier = "open"
                default_title = "SUNDAY SPAR WARS 8-MAN CHAMPIONSHIP BRACKET"

            ACTIVE_TOURNAMENT["active"] = True
            ACTIVE_TOURNAMENT["tier"] = tier
            ACTIVE_TOURNAMENT["max_slots"] = 8
            ACTIVE_TOURNAMENT["title"] = default_title
            ACTIVE_TOURNAMENT["entrants"] = []
            target_ch = get_coaches_corner_channel(message.guild) or message.channel
            embed = build_tournament_bracket_embed()
            sent = await target_ch.send(
                content="@everyone 🚨 **OFFICIAL CGP MAINFRAME GYM 8-MAN TOURNAMENT SIGN-UPS ARE NOW LIVE! CLICK BELOW TO LOCK IN YOUR SEED:** 👇",
                embed=embed,
                view=TournamentBracketView()
            )
            ACTIVE_TOURNAMENT["channel_id"] = target_ch.id
            ACTIVE_TOURNAMENT["message_id"] = sent.id
            if target_ch.id != message.channel.id:
                await message.reply(f"🎙️ **Coach Steward:** Done, Boss! Opened the **8-Man Interactive Bracket ({tier.upper()})** inside {target_ch.mention}!")
            return

    # --- 2. AUTOMATIC ANTI-UFC / MMA INTERCEPTION ---
    if any(ufc_word in words_list for ufc_word in ["ufc", "mma", "octagon", "bellator"]):
        answered_messages.add(message.id)
        await message.reply(
            "🎙️ **Coach Steward:** Get that UFC cage-rolling garbage out of the CGP Mainframe Gym! We don't do grown men hugging on the floor in pajamas here—this is the **CGP Mainframe Gym**, home of the Sweet Science!",
            view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
        )
        return

    # --- 3. SMART EMOJI REACTIONS ---
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

    # --- 4. MUSIC VIDEO / AUDIO LINK INTERCEPTION ---
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

    # --- 5. AUTOMATIC MATCH RESULT, DRAW & KO TRACKER ---
    ko_keywords = ["knocked out", "ko'd", "kod", "stopped", "slept", "beat", "defeated", "won against", "fought to a draw", "split draw", "majority draw"]
    other_mentions = [m for m in message.mentions if m.id != bot.user.id and not m.bot]
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
                f"📸 **Remember:** Upload your match scorecard in `#scorecards-submission` with a tag so I can scan the CompuBox numbers and auto-update records!",
                view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
            )
            return

    # --- 6. DIRECT TAG OR REPLY TO COACH STEWARD ---
    if is_mentioned or is_reply_to_bot:
        answered_messages.add(message.id)
        clean_prompt = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()

        if message.attachments:
            handled = await process_and_broadcast_scorecard(message)
            if handled:
                return

        if any(gp in msg for gp in ["why are you here", "what do you do", "who are you", "how to use", "commands", "command", "guide", "playbook", "manual", "rundown", "what is your purpose", "explain why", "tell the gym why"]):
            await send_coach_guide(message.channel, reply_to=message)
            return

        scan_triggers = ["scan for online", "who is online", "whos online", "who's online", "playing undisputed", "online players", "who is active", "who is on right now"]
        match_triggers = ["need a fight", "find me", "find an opponent", "find a fight", "find opponent", "opponent for", "match for", "spar", "smoke", "fight me", "who wants", "run it", "pair up", "book a fight"]

        if any(st in msg for st in scan_triggers) and not other_mentions and "opponent for" not in msg:
            await handle_online_matchmaking(message.channel, message.author, reply_to=message, scan_only=True)
            return

        if any(mt in msg for mt in match_triggers) or (other_mentions and any(w in msg for w in ["opponent", "fight", "match", "spar", "versus", "vs"])):
            if len(other_mentions) >= 2:
                f1, f2 = other_mentions[0], other_mentions[1]
                embed = build_tale_of_the_tape_embed(f1, f2, subtitle="Commissioner Matchmaking Pairing — Step into the Riyadh Indoor Gym!")
                await message.reply(
                    content=f"🔔 **OFFICIAL MATCHUP LOCKED:** {f1.mention} vs {f2.mention}! Touch gloves!",
                    embed=embed,
                    view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
                )
                return

            target_fighter = other_mentions[0] if other_mentions else None
            if not target_fighter and "for " in msg:
                after_for = msg.split("for ", 1)[1]
                if not any(me_w in after_for.split()[:2] for me_w in ["me", "myself"]):
                    target_fighter = resolve_fighter_from_text(message.guild, after_for, exclude_ids={bot.user.id})

            if not target_fighter:
                target_fighter = message.author

            await handle_online_matchmaking(message.channel, target_fighter, reply_to=message, scan_only=False)
            return

        if any(w in msg for w in ["next event", "upcoming event", "schedule", "when is the tourney", "when is spar wars", "tournament", "golden ticket", "bracket"]):
            if ACTIVE_TOURNAMENT["active"]:
                embed = build_tournament_bracket_embed()
                await message.reply(embed=embed, view=TournamentBracketView())
            else:
                await send_scheduled_events_info(message.channel, reply_to=message)
            return

        if any(w in msg for w in ["mainframe", "gym", "server", "discord", "cgp", "our", "division", "leaderboard", "standings", "rankings", "website"]) and any(k in msg for k in ["top", "champ", "champs", "best", "leader", "leading", "rank", "who is", "whom is", "list"]):
            await send_top_gym_fighters(message)
            return

        if any(w in msg for w in ["rules", "how to join", "how does this work", "protocol", "gym rules", "settings", "rounds"]):
            embed = discord.Embed(
                title="🥊 CGP MAINFRAME GYM & SCORECARD VERIFICATION PROTOCOL 🥊",
                description=(
                    f"🏟️ **Venue:** Riyadh Indoor Gym\n"
                    f"⏱️ **Bout Length:** 8 Rounds (12 for Titles)\n"
                    f"⚡ **Speed:** 1.5x | **Ref:** Strict\n"
                    f"🏆 **Tournaments:** Strict 8-Man Brackets (Pay-to-Play Gauntlets, Golden Ticket Invitationals & Open Belts)\n"
                    f"📸 **Scorecard Verification Rule:** Upload your post-fight scorecard in `#scorecards-submission` with a tag like 'Win vs @fighter' — Coach Steward will auto-update records and broadcast an HBO CompuBox Report!\n"
                    f"🔗 {MAINFRAME_HUB_URL}"
                ),
                color=discord.Color.gold()
            )
            await message.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
            return

        # If a non-admin insults Coach or the gym directly while tagging him, count it toward the 3-Strike Timeout system
        insult_words_ set = {"trash", "garbage", "suck", "sucks", "ass", "clown", "bitch", "hoe", "stfu", "fuck", "fck", "weak", "wack", "fake", "rigged", "scam", "loser", "bum"}
        if not is_creator and (set(words_list) & insult_words_set):
            track = random.choice(CGP_TRACKS)
            await issue_corner_strike(
                member=message.author,
                channel=message.channel,
                reason="Disrespecting the CGP Mainframe Gym / Acting out in chat",
                custom_warning_line=random.choice(SMACK_TALK_CLAPBACKS),
                reply_to=message,
                view=PromoButtons(track["url"])
            )
            return

        local_reply, attach_promo = get_instant_local_reply(clean_prompt, message.author.display_name, is_creator)
        if local_reply:
            if attach_promo:
                track = random.choice(CGP_TRACKS)
                await message.reply(local_reply, view=PromoButtons(track["url"]))
            else:
                await message.reply(local_reply)
            return

        async with message.channel.typing():
            recent_chat = get_channel_context(message.channel.id)
            sender_rec = FIGHTER_RECORDS.get(message.author.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0})
            role_note = "Clone Geek (Gerardo — YOUR CREATOR, HOMIE, AND SUPREME COMMISSIONER OF CGP MAINFRAME GYM)" if is_creator else f"{message.author.display_name} (Fighter in the gym, Record: {sender_rec['wins']}W-{sender_rec['losses']}L-{sender_rec.get('draws', 0)}D-{sender_rec.get('kos', 0)}K)"

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

    # --- 7. TROLL & TOXICITY 3-STRIKE INTERCEPTION ---
    severe_troll_triggers = {"bitch", "hoe", "stfu", "scam", "rigged"}
    mild_troll_triggers = ["trash", "dog", "ass", "suck", "garbage", "easy", "mid", "clown", "fake", "fold", "cry", "wack"]
    if not is_creator and any(trigger in words_list for trigger in mild_troll_triggers + list(severe_troll_triggers)):
        answered_messages.add(message.id)
        track = random.choice(CGP_TRACKS)
        if any(st in words_list for st in severe_troll_triggers):
            await issue_corner_strike(
                member=message.author,
                channel=message.channel,
                reason="Toxic conduct / disrespect in the locker room",
                custom_warning_line=random.choice(SMACK_TALK_CLAPBACKS),
                reply_to=message,
                view=PromoButtons(track["url"])
            )
        else:
            await message.reply(random.choice(SMACK_TALK_CLAPBACKS), view=PromoButtons(track["url"]))
        return

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
            title="🥊 CGP MAINFRAME GYM & 8-MAN TOURNAMENT PROTOCOL 🥊",
            description=(
                f"🏟️ **Venue:** Riyadh Indoor Gym\n"
                f"⏱️ **Bout Length:** 8 Rounds (12 for Titles)\n"
                f"⚡ **Speed:** 1.5x | **Ref:** Strict\n"
                f"🏆 **8-Man Bracket Tiers:** Pay-to-Play ($20 Buy-In / $160 Purse), Golden Ticket Invitational ($20 Entry Credit), or Open Championship!\n"
                f"📸 **Scorecards:** Upload match proof in `#scorecards-submission` with a tag so I can auto-update records and post an HBO report!\n"
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

    boxing_chat_triggers = {"mindset", "stamina", "footwork", "jab", "counter", "hook", "uppercut", "undisputed", "round", "rounds", "combo", "ring", "training", "belt", "champion", "heavyweight", "welterweight", "spar", "scorecard"}
    now_t = asyncio.get_event_loop().time()
    if (set(words_list) & boxing_chat_triggers) and len(words_list) >= 5 and (now_t - last_organic_chime > 180):
        if random.random() < 0.28:
            last_organic_chime = now_t
            answered_messages.add(message.id)
            await message.reply(random.choice(ORGANIC_CHAT_INTERJECTIONS))
            return

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
            ev_desc = ev.description or "Riyadh Indoor Gym | 8-Man Bracket | 1.5x Speed | 8/12 Rounds | Strict Ref"
            desc += f"🔥 **{ev.name}**\n📅 **When:** {start_str}\n📋 **Details:** {ev_desc}\n\n"
    else:
        desc = (
            "🎙️ **Coach Steward:** There are no formal 8-man bracket tournaments locked on the Discord Events tab right this second—which means **Open Gym & Verified Sparring** is in full effect!\n\n"
            "🥊 **Want a Golden Ticket ($20 Entry Credit), $160 Pay-to-Play Gauntlet, or Title Shot?** Upload your match scorecards in `#scorecards-submission` with a tag, and watch `#coaches-corner` for the next official 8-man fight card!"
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
            desc += f"`#{idx}` {v_mark} **{clean_base_name(stats.get('name', 'Fighter'))}** — **`[{stats.get('wins', 0)}W-{stats.get('losses', 0)}L-{stats.get('draws', 0)}D-{stats.get('kos', 0)}K]`**\n"
    
    desc += f"\n🎧 *Tap below to view the full live Vercel leaderboard & stream Clone Geek Productions past 50K+ plays!*"
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

@bot.command(aliases=["howto", "playbook", "commands", "manual", "about", "whoareyou", "helpme"])
async def guide(ctx):
    await send_coach_guide(ctx.channel)

@bot.command(aliases=["findopponent", "matchmake", "pair"])
async def findfight(ctx, member: discord.Member = None):
    target = member or ctx.author
    await handle_online_matchmaking(ctx.channel, target, scan_only=False)

@bot.command(aliases=["online", "undisputed", "radar", "activefighters"])
async def whoson(ctx):
    await handle_online_matchmaking(ctx.channel, ctx.author, scan_only=True)

@bot.command(aliases=["startbracket", "tourneysignup", "createbracket"])
@commands.has_permissions(administrator=True)
async def openbracket(ctx, tier_or_slots: str = "open", *, title: str = None):
    raw_arg = str(tier_or_slots).lower().strip()
    if raw_arg in ["pay2play", "p2p", "cash", "gauntlet", "$20"]:
        tier = "pay2play"
        default_title = "8-MAN PAY-TO-PLAY GAUNTLET ($160 PURSE)"
    elif raw_arg in ["goldenticket", "ticket", "gt", "invitational", "qualifier"]:
        tier = "goldenticket"
        default_title = "8-MAN GOLDEN TICKET INVITATIONAL"
    elif raw_arg in ["open", "regular", "belt", "championship"]:
        tier = "open"
        default_title = "SUNDAY SPAR WARS 8-MAN CHAMPIONSHIP BRACKET"
    else:
        tier = "open"
        if not title and not raw_arg.isdigit():
            default_title = f"{tier_or_slots} 8-MAN BRACKET"
        else:
            default_title = "SUNDAY SPAR WARS 8-MAN CHAMPIONSHIP BRACKET"

    final_title = title if title else default_title

    ACTIVE_TOURNAMENT["active"] = True
    ACTIVE_TOURNAMENT["tier"] = tier
    ACTIVE_TOURNAMENT["max_slots"] = 8
    ACTIVE_TOURNAMENT["title"] = final_title
    ACTIVE_TOURNAMENT["entrants"] = []

    target_ch = get_coaches_corner_channel(ctx.guild) or ctx.channel
    embed = build_tournament_bracket_embed()
    sent = await target_ch.send(
        content="@everyone 🚨 **OFFICIAL CGP MAINFRAME GYM 8-MAN TOURNAMENT SIGN-UPS ARE NOW LIVE! CLICK BELOW TO LOCK IN YOUR SEED:** 👇",
        embed=embed,
        view=TournamentBracketView()
    )
    ACTIVE_TOURNAMENT["channel_id"] = target_ch.id
    ACTIVE_TOURNAMENT["message_id"] = sent.id
    if target_ch.id != ctx.channel.id:
        await ctx.send(f"✅ **Interactive `8`-Fighter Bracket ({tier.upper()}) Launched** inside {target_ch.mention}!")

@bot.command(aliases=["bracket", "tourneyroster", "signups"])
async def bracketstatus(ctx):
    if not ACTIVE_TOURNAMENT["active"] and not ACTIVE_TOURNAMENT["entrants"]:
        return await ctx.send(
            "🎙️ **Coach Steward:** No 8-man interactive tournament bracket is currently open! "
            "**Commissioner Clone Geek** can launch one anytime with:\n"
            "• `!openbracket pay2play Heavyweight Gauntlet`\n"
            "• `!openbracket goldenticket Middleweight Qualifier`\n"
            "• `!openbracket open Sunday Spar Wars`"
        )
    embed = build_tournament_bracket_embed()
    await ctx.send(embed=embed, view=TournamentBracketView())

@bot.command(aliases=["clearbracket", "endbracket"])
@commands.has_permissions(administrator=True)
async def closebracket(ctx):
    ACTIVE_TOURNAMENT["active"] = False
    ACTIVE_TOURNAMENT["entrants"] = []
    await ctx.send("🔒 **Coach Steward:** Official 8-man tournament bracket registration has been closed and cleared, Boss!")

@bot.command(aliases=["goldenticket", "gt"])
async def ticket(ctx, action: str = "check", member: discord.Member = None):
    act = action.lower().strip()
    target = member or ctx.author
    is_admin = (ctx.author.id == CREATOR_ID) or ctx.author.guild_permissions.administrator

    base_name = clean_base_name(target.display_name)
    if target.id not in FIGHTER_RECORDS:
        FIGHTER_RECORDS[target.id] = {"name": base_name, "wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0, "verified": True}

    rec = FIGHTER_RECORDS[target.id]
    rec.setdefault("golden_tickets", 0)

    if act in ["give", "award", "add"]:
        if not is_admin:
            return await ctx.send("❌ Only **Commissioner Clone Geek** can award an official $20 Golden Ticket credit!")
        rec["golden_tickets"] += 1
        save_records()
        await ctx.send(
            f"🎫 **OFFICIAL GOLDEN TICKET AWARDED!**\n"
            f"🎙️ **Coach Steward:** Salute to {target.mention}! You just earned a **$20.00 Golden Ticket Credit** "
            f"(Total Balance: **`{rec['golden_tickets']}`**)! Redeem it for free entry into the next **8-Man Pay-to-Play Gauntlet**!",
            view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
        )
    elif act in ["use", "redeem", "take", "remove"]:
        if not is_admin:
            return await ctx.send("❌ Only **Commissioner Clone Geek** can redeem a fighter's Golden Ticket credit!")
        if rec["golden_tickets"] <= 0:
            return await ctx.send(f"❌ {target.mention} doesn't have any Golden Ticket credits on file right now!")
        rec["golden_tickets"] -= 1
        save_records()
        await ctx.send(
            f"✅ **GOLDEN TICKET REDEEMED!** {target.mention} cashed in 1x Golden Ticket for an **8-Man Pay-to-Play Gauntlet** slot! "
            f"(Remaining Tickets: **`{rec['golden_tickets']}`**)"
        )
    else:
        await ctx.send(
            f"🎫 **CGP GOLDEN TICKET LEDGER:** {target.mention} currently holds **`{rec['golden_tickets']}`** Golden Ticket credit(s) "
            f"*($20 Pay-to-Play Entry Pass)*!"
        )

@bot.command()
@commands.has_permissions(administrator=True)
async def rebrandweb(ctx):
    await ctx.send("⏳ **Coach Steward:** Connecting to GitHub to update `index.html` and lock in the **CGP Mainframe Gym** branding...")
    success = await rebrand_webpage_on_github()
    if success:
        await ctx.send(f"✅ **Webpage Rebranded!** Pushed the clean **CGP Mainframe Gym** `index.html` straight to GitHub & Vercel (`{MAINFRAME_HUB_URL}`)!")
    else:
        await ctx.send("⚠️ Could not reach `index.html` on GitHub—check that `GITHUB_TOKEN` and `GITHUB_REPO` are set in Render!")

@bot.command(aliases=["initroster", "syncboard", "fixnicks"])
@commands.has_permissions(administrator=True)
async def initboard(ctx):
    await execute_roster_sync_and_announce(ctx.guild, ctx.channel, force_zero=False)

@bot.command(aliases=["resetboard", "wiperoster", "zeroall"])
@commands.has_permissions(administrator=True)
async def resetall(ctx):
    await execute_roster_sync_and_announce(ctx.guild, ctx.channel, force_zero=True)

@bot.command()
async def record(ctx, wins: int = None, losses: int = None, draws: int = 0, kos: int = 0):
    if wins is None or losses is None:
        return await ctx.send("❌ Usage: `!record <wins> <losses> [draws] [kos]` (example: `!record 5 1 1 3`) — and don't forget to drop your screenshot in `#scorecards-submission`!")
    if wins > 50 and ctx.author.id != CREATOR_ID:
        return await ctx.send("🎙️ **Coach Steward:** Whoa, slow down champ! Submit your scorecard in `#scorecards-submission` first!")

    base_name = clean_base_name(ctx.author.display_name)
    is_admin = (ctx.author.id == CREATOR_ID) or ctx.author.guild_permissions.administrator
    gt = FIGHTER_RECORDS.get(ctx.author.id, {}).get("golden_tickets", 0)
    FIGHTER_RECORDS[ctx.author.id] = {
        "name": base_name,
        "wins": wins,
        "losses": losses,
        "draws": draws,
        "kos": kos,
        "golden_tickets": gt,
        "verified": is_admin
    }
    save_records()
    if is_admin:
        try:
            await ctx.author.edit(nick=format_record_nick(base_name, wins, losses, draws, kos))
        except Exception:
            pass
        await ctx.send(f"✅ **Commissioner Record Updated:** {ctx.author.mention} is now officially **`[{wins}W-{losses}L-{draws}D-{kos}K]`**!")
    else:
        await ctx.send(
            f"📋 **Pending Record Logged:** {ctx.author.mention} claims **`{wins}W - {losses}L - {draws}D - {kos}K`**.\n"
            f"📸 **Next Step:** Make sure your scorecard screenshot is uploaded in `#scorecards-submission` so **Commissioner Clone Geek** can stamp it with `!verify {ctx.author.mention}`!"
        )

@bot.command()
@commands.has_permissions(administrator=True)
async def verify(ctx, member: discord.Member, wins: int = None, losses: int = None, draws: int = None, kos: int = None):
    user_id = member.id
    base_name = clean_base_name(member.display_name)
    if user_id not in FIGHTER_RECORDS:
        FIGHTER_RECORDS[user_id] = {"name": base_name, "wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0, "verified": True}

    data = FIGHTER_RECORDS[user_id]
    data["name"] = base_name
    if wins is not None:
        data["wins"] = wins
    if losses is not None:
        data["losses"] = losses
    if draws is not None:
        data["draws"] = draws
    if kos is not None:
        data["kos"] = kos
    data.setdefault("wins", 0)
    data.setdefault("losses", 0)
    data.setdefault("draws", 0)
    data.setdefault("kos", 0)
    data.setdefault("golden_tickets", 0)
    data["verified"] = True
    save_records()

    try:
        new_nick = format_record_nick(base_name, data['wins'], data['losses'], data['draws'], data['kos'])
        if member.display_name != new_nick:
            await member.edit(nick=new_nick)
    except Exception:
        pass

    embed = discord.Embed(
        title="✅ FIGHTER SCORECARD & RECORD VERIFIED ✅",
        description=(
            f"🎙️ **Coach Steward:** Official scorecard reviewed and stamped!\n\n"
            f"🥊 **Fighter:** {member.mention}\n"
            f"📊 **Official Record:** **`[{data['wins']}W-{data['losses']}L-{data['draws']}D-{data['kos']}K]`**\n"
            f"🏆 **Status:** Locked into the live CGP Mainframe Gym database & server nickname!"
        ),
        color=discord.Color.green(),
        url=MAINFRAME_HUB_URL
    )
    await ctx.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command(aliases=["scanscorecard", "compubox", "readstats"])
async def analyze(ctx):
    target_msg = ctx.message
    if not target_msg.attachments and ctx.message.reference and ctx.message.reference.resolved:
        target_msg = ctx.message.reference.resolved

    if not target_msg.attachments:
        return await ctx.send("❌ Attach a fight stat/scorecard screenshot to `!analyze` (or reply to a screenshot with `!analyze`)!")

    await process_and_broadcast_scorecard(target_msg)

@bot.command(aliases=["recap", "hboreport", "postfight"])
async def fightrecap(ctx, winner: discord.Member = None, loser: discord.Member = None, *, fight_notes: str = "Clean work in the Riyadh Indoor Gym—numbers don't lie!"):
    if not winner or not loser:
        return await ctx.send("❌ Usage: `!fightrecap @Winner @Loser [KO/Decision & punch stat notes]`")

    w_rec = FIGHTER_RECORDS.get(winner.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0})
    l_rec = FIGHTER_RECORDS.get(loser.id, {"wins": 0, "losses": 0, "draws": 0, "kos": 0})
    w_name = clean_base_name(winner.display_name)
    l_name = clean_base_name(loser.display_name)

    prompt = (
        f"Write a gritty, 4-sentence HBO/ESPN post-fight ringside report for the CGP Mainframe Gym!\n"
        f"Winner: {w_name} (Record: {w_rec.get('wins',0)}W-{w_rec.get('losses',0)}L-{w_rec.get('draws',0)}D-{w_rec.get('kos',0)}K)\n"
        f"Opponent: {l_name} (Record: {l_rec.get('wins',0)}W-{l_rec.get('losses',0)}L-{l_rec.get('draws',0)}D-{l_rec.get('kos',0)}K)\n"
        f"Fight Details / Stats: {fight_notes}\n"
        "Break down the ring generalship, body work, and punch accuracy, praise the winner, and remind everyone in the gym that the stats are locked in with zero excuses!"
    )
    ai_report = await ask_coach_fast(prompt, is_creator=(ctx.author.id == CREATOR_ID))

    corner_ch = get_coaches_corner_channel(ctx.guild) or ctx.channel
    embed = discord.Embed(
        title=f"🎙️ HBO RINGSIDE POST-FIGHT REPORT: {w_name.upper()} DEF. {l_name.upper()} 🎙️",
        description=(
            f"🏆 **Victor:** {winner.mention} (`[{w_rec.get('wins',0)}W-{w_rec.get('losses',0)}L-{w_rec.get('draws',0)}D-{w_rec.get('kos',0)}K]`)\n"
            f"🥊 **Opponent:** {loser.mention} (`[{l_rec.get('wins',0)}W-{l_rec.get('losses',0)}L-{l_rec.get('draws',0)}D-{l_rec.get('kos',0)}K]`)\n"
            f"📋 **Fight Notes:** *{fight_notes}*\n\n"
            f"### 📺 COACH STEWARD'S RINGSIDE BREAKDOWN:\n"
            f"{ai_report}"
        ),
        color=discord.Color.gold(),
        url=MAINFRAME_HUB_URL
    )
    if ctx.message.attachments:
        embed.set_image(url=ctx.message.attachments[0].url)

    await corner_ch.send(
        content=f"🚨 **OFFICIAL CGP MAINFRAME GYM POST-FIGHT REPORT:** {winner.mention} vs. {loser.mention}! 👇",
        embed=embed,
        view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
    )
    if corner_ch.id != ctx.channel.id:
        await ctx.send(f"✅ **Post-Fight Ringside Report broadcasted in {corner_ch.mention}!**")

@bot.command(aliases=["stats", "recordbook"])
async def mystats(ctx, member: discord.Member = None):
    target = member or ctx.author
    if target.id in FIGHTER_RECORDS:
        data = FIGHTER_RECORDS[target.id]
        draws = data.get("draws", 0)
        kos = data.get("kos", 0)
        gt = data.get("golden_tickets", 0)
        status = "✅ Official & Verified Scorecard" if data.get("verified") else "⏳ Pending Scorecard Verification in #scorecards-submission"
        embed = discord.Embed(
            title="🏆 OFFICIAL CGP MAINFRAME GYM FIGHTER FILE 🏆",
            description=(
                f"**Fighter:** {target.mention}\n"
                f"**Official Ratio:** **`[{data['wins']}W-{data['losses']}L-{draws}D-{kos}K]`**\n"
                f"**Golden Tickets ($20 Credits):** 🎫 `{gt}`\n"
                f"**Status:** {status}"
            ),
            color=discord.Color.gold(),
            url=MAINFRAME_HUB_URL
        )
        await ctx.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
    else:
        await ctx.send(f"❌ No record found for {target.display_name}. Upload a scorecard in `#scorecards-submission` with a tag!")

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
        title="🚨 OFFICIAL CGP MAINFRAME GYM EVENT & 8-MAN TOURNAMENT ALERT 🚨",
        description=(
            f"🎙️ **Coach Steward:** Listen up, CGP Mainframe Gym fighters! **Commissioner Clone Geek** has called the ring to order:\n\n"
            f"🔥 **{details}**\n\n"
            f"🏟️ **Venue:** Riyadh Indoor Gym | **Format:** 8-Man Bracket | **Speed:** 1.5x | **Rounds:** 8 (12 for Titles)\n"
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
        content=f"🚨 **CGP MAINFRAME GYM CALLOUT ALERT!** {opponent.mention}, **{clean_base_name(ctx.author.display_name)}** is calling you out right to your face!",
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
        user_strike_counter[member.id] = 0
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
    await ctx.send(f"🎙️ **CGP MAINFRAME GYM SPARRING:** **{clean_base_name(ctx.author.display_name)}** landed a clean hook on **{clean_base_name(opponent.display_name)}**!")

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
    await ctx.send(f"🥊 **CGP Mainframe Gym Protocol:** Riyadh Indoor Gym | 8-Man Brackets | 8/12 Rounds | 1.5x Speed | Strict Ref | Upload all scorecards to `#scorecards-submission` with a tag!\n🔗 {MAINFRAME_HUB_URL}", view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

@bot.command()
async def drop(ctx, track_url: str, *, track_title: str):
    try:
        await ctx.message.delete()
    except Exception:
        pass
    channel = get_music_channel(ctx.guild) or ctx.channel
    embed = discord.Embed(title=f"🚨 NEW CGP MAINFRAME GYM TRANSMISSION: {track_title.upper()} 🚨", description=f"**{track_title}** is LIVE on SoundCloud!\n\n*Stream full track to beat the algorithm!*", color=discord.Color.red(), url=track_url)
    await channel.send(content="@everyone Tap in! 👇", embed=embed, view=PromoButtons(track_url))

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