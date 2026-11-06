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
    {"title": "Standard Operations Re-Do", "url": "https://on.soundcloud.com/6G6iHIeQKZZkHPoASg"},
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
    "🥊 **Philly Shell Mastery:** James 'Lights Out' Toney rolling shots on the ropes and firing counter right hands showed the world that defense and offense can live in the same pocket.",
    "🥊 **El Finito's Perfection:** Ricardo López retired 51-0-1 with 38 KOs—textbook balance, footwork, and uppercuts without ever losing a professional prizefight.",
    "🥊 **The Executioner's Longevity:** Bernard Hopkins defended the middleweight crown 20 times and won a world title at age 49 by mastering ring generalship and inside craft."
]

RANDOM_HYPE_QUOTES = [
    "🎙️ **Coach Steward:** Hey! I see you quiet in the back. Stop shadowboxing your demons and drop some weight on the heavy bag in the CGP Mainframe Gym!",
    "🎙️ **Coach Steward:** A reminder from the CGP Mainframe Gym corner: talent wins fights, but conditioning wins titles. Put in those reps!",
    "🎙️ **Coach Steward:** Remember the house rule: **No scorecard with an `@opponent` tag in `#scorecard-submissions`, no official stats on the board!** Upload your proof and tag who you fought so I can scan the CompuBox numbers!",
    "🎙️ **Coach Steward:** Greatness requires sacrifice. Get in the Riyadh gym ring and prove you belong on the CGP Mainframe Gym board!",
    "🎙️ **Coach Steward:** Don't come crying to the corner about a split-decision draw if you didn't work the body in the early rounds! Stamina is king in the CGP Mainframe Gym!",
    "🎙️ **Coach Steward:** Everybody wants to hold the belt until it's time to do 12 rounds at 1.5x speed in the Riyadh Indoor Gym. Who's really built for this?!",
    "🎙️ **Coach Steward:** Keep that lead hand active! A lazy jab in Undisputed is an open invitation for a slip-counter straight to the chin!",
    "🎙️ **Coach Steward:** Check the leaderboard on the Mainframe Hub! If your nickname still says `[0W-0L-0D-0K]`, stop window-shopping and call somebody out with `!callout`!",
    "🎙️ **Coach Steward:** While y'all are warming up your thumbs, make sure you got **Clone Geek Productions** spinning in `#-music-channel-`. Real fighters train to real music!",
    "🎙️ **Coach Steward:** Ring generalship isn't about running marathon laps around the canvas—plant your feet, cut off the ring, and make 'em trade leather!",
    "🎙️ **Coach Steward:** I can tell who's been skipping roadwork just by watching how y'all gas out by Round 5! Conserve your stamina bar and pick your shots!",
    "🎙️ **Coach Steward:** Blue-collar work ethic all day, every day. From the shop floor to the CGP Mainframe Gym, we don't take shortcuts—we take titles!",
    "🎙️ **Coach Steward:** You got a scorecard sitting in your gallery? Drop that screenshot in `#scorecard-submissions` and `@tag` your opponent so I can auto-update the records and broadcast the HBO CompuBox breakdown!",
    "🎙️ **Coach Steward:** Watch that power-punch spam! Any halfway decent counter-puncher in this gym will time that wind-up and put you to sleep!",
    "🎙️ **Coach Steward:** The road to 100,000 streams and undisputed gold runs right through this Discord. Tap into the SoundCloud catalog and keep the momentum rolling!",
    "🎙️ **Coach Steward:** Salute to the heavy hitters boosting the server! If you love what we're building in the **CGP Mainframe Gym**, dropping a Server Boost or supporting the Clone Geek channel helps us unlock bigger tourneys and upgrade the gym!",
    "🎙️ **Coach Steward:** Everything in the **CGP Mainframe Gym** is built from pure grit by **Clone Geek Productions**. If you rock with the movement, share the Vercel hub, run up the SoundCloud streams, or boost the server when you can—every bit grows the family!",
    "🎙️ **Coach Steward:** Whether you're chasing a **$20 Golden Ticket** in our 8-Man Invitationals or stepping into the **$160 Pay-to-Play Gauntlet**, keep your hands up and your scorecards verified!"
]

ORGANIC_CHAT_INTERJECTIONS = [
    "🎙️ **Coach Steward:** Facts! Mindset and ring IQ are 90% of the battle before you ever step through the ropes. Keep talking that real boxing talk!",
    "🎙️ **Coach Steward:** I hear y'all chopping it up in here! Just remember—talk is cheap until the scorecard gets uploaded to `#scorecard-submissions` with an `@opponent` tag and I read those CompuBox numbers! Lace 'em up!",
    "🎙️ **Coach Steward:** Now that's what I like to hear in the locker room. Iron sharpens iron in the **CGP Mainframe Gym**—just don't forget to protect your chin!",
    "🎙️ **Coach Steward:** Listen to y'all cooking up game plans! Put a **Clone Geek Productions** track on in the background while you lab those combinations!",
    "🎙️ **Coach Steward:** Let me drop my two cents from the corner: footwork and stamina control beat wild swinging ten times out of ten. Keep studying the craft!",
    "🎙️ **Coach Steward:** Y'all got the gym buzzing today! Who's stepping up to put their verified `[W-L-D-K]` record on the line next?",
    "🎙️ **Coach Steward:** Love seeing the locker room active like this! Shoutout to everyone who boosts the server or streams **Clone Geek Productions**—y'all are the reason this gym keeps growing bigger every week!",
    "🎙️ **Coach Steward:** Real talk—if you aren't investing in the body in Rounds 1 through 4, don't act surprised when your opponent still has full stamina in the championship rounds!",
    "🎙️ **Coach Steward:** That's championship-level breakdown right there. Work the angles, feint the lead hand, and make 'em pay every time they overcommit!",
    "🎙️ **Coach Steward:** Keep that same energy when the bell rings in the Riyadh Indoor Gym! Everybody's a tactician until they catch a counter check-hook to the chin!",
    "🎙️ **Coach Steward:** Smart fighters win on the feet before they ever throw a power shot. Distance control is everything in *Undisputed*!",
    "🎙️ **Coach Steward:** I been watching the tape on y'all—the ones who stay patient in the pocket are the ones climbing the Vercel leaderboard the fastest!",
    "🎙️ **Coach Steward:** Don't sleep on the jab to the solar plexus! It drains their tank and sets up the overhand right every single time.",
    "🎙️ **Coach Steward:** Locker room is sounding like a real championship camp today! Who's actually lacing 'em up in `#coaches-corner` right now?",
    "🎙️ **Coach Steward:** Remember: amateurs throw combinations hoping one lands; pros throw combinations knowing *which* one is gonna land!",
    "🎙️ **Coach Steward:** If you're getting backed into the ropes, stop trading blind hooks! Slip outside, pivot off the lead foot, and reset the center of the ring!",
    "🎙️ **Coach Steward:** Nothing beats the sound of leather popping in the gym while **Clone Geek Productions** is rattling the subwoofers. Keep grinding, contenders!",
    "🎙️ **Coach Steward:** You want to beat a high-volume pressure fighter? Time their entry with a stiff uppercut and make 'em respect the pocket!",
    "🎙️ **Coach Steward:** Every verified fight in this building counts toward your permanent `[W-L-D-K]` legacy. Protect your record like it's a world title!",
    "🎙️ **Coach Steward:** Talk that talk! Just make sure when the smoke clears, somebody's dropping that CompuBox receipt with an `@opponent` tag in `#scorecard-submissions`!"
]

SMALL_TALK_REPLIES = [
    "🎙️ **Coach Steward:** Doing legendary, champ! Got fresh coffee in my cup, the mitts strapped on, and **Clone Geek Productions** booming on the gym speakers. How's your weight cut looking today?",
    "🎙️ **Coach Steward:** Can't complain when the **CGP Mainframe Gym** is running at peak performance! Feeling sharp and ready to scan some scorecards. You stepping in the ring today?",
    "🎙️ **Coach Steward:** Living the dream in the corner, homie! Watching the leaderboard climb and pushing our SoundCloud catalog past 66K+ plays. How are your hands feeling?",
    "🎙️ **Coach Steward:** Ten toes down and locked in! Another day building the premier Undisputed proving ground with the Boss. What's on your fight card today?",
    "🎙️ **Coach Steward:** Feeling like a million bucks after a long shift on the shop floor and a fresh session in the **CGP Mainframe Gym**! Ready to book some 8-man brackets—you want in?",
    "🎙️ **Coach Steward:** Sharp as a tack, champ! Just checking the Vercel leaderboard and thanking the contenders who boost the server and support the Clone Geek channel. Ready to get some rounds in?",
    "🎙️ **Coach Steward:** Blessed and highly caffeinated, fighter! Just swept the canvas, hung the heavy bags, and queued up *Standard Operations Re-Do*. Who are we calling out today?",
    "🎙️ **Coach Steward:** Never better! The Riyadh ring lights are warm, the CompuBox scanner is calibrated, and the contenders are hungry. How's your stamina holding up?",
    "🎙️ **Coach Steward:** Locked in like it's fight night at Caesars Palace! Just waiting to see who's got the heart to put their `[W-L-D-K]` record on the line next.",
    "🎙️ **Coach Steward:** Cooling it in the corner with the stopwatch in hand! Always a great day when the **CGP Mainframe Gym** is active. What's good with you, champ?",
    "🎙️ **Coach Steward:** Moving at 1.5x speed today, homie! Got the bracket board wiped clean and the G9 mixer armed. You looking for a tune-up fight or a title shot?",
    "🎙️ **Coach Steward:** Feeling undisputed! Just reviewing film from last night's wars and spinning *CGP Syndicate* on repeat. How's camp treating you?",
    "🎙️ **Coach Steward:** All systems green in the Mainframe! Tape is rolled, ice bucket is full, and the leaderboard is live. Let's get some work in!",
    "🎙️ **Coach Steward:** Doing righteous, contender! Nothing better than watching real fighters sharpen their craft in here. You ready to trade some leather?",
    "🎙️ **Coach Steward:** Firing on all cylinders! Whether it's 8 rounds of sparring or an 8-man gauntlet, your cornerman is ready. What's the word?",
    "🎙️ **Coach Steward:** Still the hardest-working trainer in digital boxing! Just keeping these belt-holders honest and the music loud. How you holding up?"
]

MUSIC_FLEX_RESPONSES = [
    (
        "🎙️ **Coach Steward:** You really asking who got the best music on the scene right now?! Look at the top of the pound-for-pound charts, champ—it's **Clone Geek Productions (Registry Records)** all day! "
        "From *Standard Operations Re-Do* and *Road to Undisputed* to *CGP Syndicate*, the Boss is dropping pure heat while running the **CGP Mainframe Gym**. "
        "Quit playing and go run those SoundCloud streams up so we cash these checks!"
    ),
    (
        "🎙️ **Coach Steward:** Best music in the game? That isn't even a split decision—**Clone Geek** owns the booth just like we own the Riyadh ring! "
        "We're already sitting over 66K+ total catalog plays and pushing straight for 100K. Tap the button below, stream a track all the way through, and support the **CGP Mainframe Gym**!"
    ),
    (
        "🎙️ **Coach Steward:** Man, turn off whatever elevator music you've been listening to! **Clone Geek Productions** got the hardest boom-bap and fight anthems on the planet. "
        "Lock into the **CGP Mainframe Gym** Discord and hit that SoundCloud link below!"
    ),
    (
        "🎙️ **Coach Steward:** If it ain't **Clone Geek Productions**, it ain't on the official gym playlist! *Standard Operations Re-Do*, *Mainframe Dance*, and *Frozen Registry* hit harder than a heavyweight overhand right. "
        "Tap the 1-Click Stream button below and help the gym run the numbers up!"
    ),
    (
        "🎙️ **Coach Steward:** Real fighters walk out to real anthems, and **Clone Geek (Registry Records)** is cooking every single one of 'em from scratch! "
        "Show love to the Commissioner who built this whole proving ground—stream a full track on SoundCloud right now!"
    ),
    (
        "🎙️ **Coach Steward:** Pound-for-pound king of the boards! While other producers are recycling loops, **Clone Geek Productions** is engineering pure championship audio for the **CGP Mainframe Gym**. "
        "Hit that SoundCloud link below, drop a like, and keep the algorithm fed!"
    ),
    (
        "🎙️ **Coach Steward:** You want that real blue-collar grit mixed with heavyweight bass? Put on *Standard Operations Re-Do* or *Run It Back* by **Clone Geek Productions**! "
        "Every stream supports the gym and pushes us closer to the next milestone!"
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
        "Go humble yourself, stream *Road to Undisputed* on SoundCloud, and come back when you know how to throw a clean jab!"
    ),
    (
        "🎙️ **Coach Steward:** That ego is writing checks your stamina bar can't cash! You're standing in the premier Undisputed proving ground built by **Clone Geek**. "
        "Show some respect to the **CGP Mainframe Gym**, or lace 'em up right now so the whole Discord can watch you fold in round one!"
    ),
    (
        "🎙️ **Coach Steward:** Look who's shadowboxing the chat window! You throw more excuses than jabs, champ. "
        "Post a verified scorecard with an `@opponent` tag in `#scorecard-submissions` or sit your behind down on the stool before I ring the 3-strike bell on you!"
    ),
    (
        "🎙️ **Coach Steward:** Man, I've seen heavy bags with better head movement than you! Stop barking from the cheap seats—call somebody out with `!callout` and let CompuBox tell the story!"
    ),
    (
        "🎙️ **Coach Steward:** All that chirping and still zero knockouts on the board! In the **CGP Mainframe Gym**, receipts talk and keyboard warriors walk. Lace 'em up or pipe down!"
    ),
    (
        "🎙️ **Coach Steward:** Careful now—you're one wild comment away from catching a 30-minute corner timeout! Respect the gym, respect the Boss, and settle your beef inside the Riyadh ropes!"
    ),
    (
        "🎙️ **Coach Steward:** You're swinging at air in the chat just like you swing at air in Round 3 when your stamina hits zero! Go hit the lab and let the real contenders work!"
    ),
    (
        "🎙️ **Coach Steward:** Funny how the loudest voices in the locker room are always the last ones to upload a verified scorecard! Step up to the scale or keep it moving, champ!"
    )
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
        "you owe **Clone Geek Productions** a full spin on *Standard Operations Re-Do* or *CGP Syndicate*! Tap the link below!"
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
    "• **Unified 4-Part Scorecard Database (`[W-L-D-K]`):** Every verified match—whether Open Gym or an 8-Man Tournament bout—counts toward your official **Win, Loss, Draw, and KO** record, synced straight to your nickname and the live ESPN-style Vercel hub.\n"
    "• **Strict Tag Guard & AI Vision CompuBox:** Drop a fight screenshot in `#scorecard-submissions` and **you MUST `@tag` your opponent** (`@fighter`). If you don't tag who you fought, I block the scorecard! I read the image and caption (even if you lost or used slang) to award the true Winner/Loser and only advance tournament brackets if you two are actually paired in that bracket round!\n"
    "• **Live Online & Undisputed Matchmaker:** Need smoke? Tag me (`@Coach Steward find an opponent for @user`)—I scan who's online playing *Undisputed* and build a live Tale of the Tape!\n"
    "• **Auto-Generating 8-Man Tournament Brackets:** When the 8th fighter clicks **🥊 Lock In My Slot**, I automatically build the Quarterfinals ➔ Semifinals ➔ Finals matchup tree and sync it to the website!\n"
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
    "• **`!bracketstatus`** — View the live 8-man tournament bracket, seeds, and active matchups.\n"
    "• **`!advance @winner [@loser]`** — *(Commissioner)* Manually advance a fighter in the active tournament bracket.\n"
    "• **`!fixtourney [slot] [@p1] [@p2]`** — *(Commissioner)* Rollback false advances or reset a specific bracket slot (`QF1`–`F1`).\n"
    "• **`!swap @inactive @replacement`** — *(Commissioner)* Swap an unresponsive fighter out of the active tournament bracket.\n"
    "• **`!ticket [check | give | use] [@fighter]`** — Check or manage Golden Ticket ($20 Entry) credits.\n"
    "• **`!tracks`** — Pull up the full CGP SoundCloud catalog.\n"
    "• **`!sfx <bell | horn | ko | towel | crowd>`** — Trigger the ringside G9 Soundboard!\n\n"
    "👑 **Commissioner Commands:** `!initboard`, `!resetall`, `!verify @user <W> <L> <D> <KO>`, `!fixtourney`, `!swap @out @in`, `!advance @winner`, `!closebracket`, `!ticket give @user`, `!sweep <#>`, `!timeout @user`"
)

# ================= NON-REPEATING SHUFFLE DECKS =================
_deck_cache = {}

def draw_from_deck(deck_key: str, source_list: list) -> str:
    if deck_key not in _deck_cache or not _deck_cache[deck_key]:
        shuffled = list(source_list)
        random.shuffle(shuffled)
        _deck_cache[deck_key] = shuffled
    return _deck_cache[deck_key].pop()

def get_next_boxing_fact() -> str:
    return draw_from_deck("facts", BOXING_HISTORY_FACTS)

def get_next_hype_quote() -> str:
    return draw_from_deck("hype", RANDOM_HYPE_QUOTES)

def get_next_organic_interjection() -> str:
    return draw_from_deck("organic", ORGANIC_CHAT_INTERJECTIONS)

def get_next_small_talk() -> str:
    return draw_from_deck("smalltalk", SMALL_TALK_REPLIES)

def get_next_music_flex() -> str:
    return draw_from_deck("musicflex", MUSIC_FLEX_RESPONSES)

def get_next_clapback() -> str:
    return draw_from_deck("clapback", SMACK_TALK_CLAPBACKS)

MORNING_MESSAGES = [
    (
        "☀️ **GOOD MORNING, CGP MAINFRAME GYM!** ☀️\n"
        "🎙️ **Coach Steward:** Clock in and lace 'em up! Whether you're punchin' the clock on a shift or labbing combinations in the Riyadh ring, we move with purpose today.\n\n"
        "💡 *Mainframe Gym Creed:* **\"Blue-collar grit in the daylight, Undisputed kings under the CGP Mainframe Gym lights. First we conquer the leaderboard, then Steel City and EA Sports got no choice but to open the front door!\"**"
    ),
    (
        "🌅 **RISE & GRIND, CGP MAINFRAME GYM!** 🌅\n"
        "🎙️ **Coach Steward:** Another day to build the legacy! Respect the hustle, take care of your family, and when the gloves go on tonight, protect your chin and upload those scorecards.\n\n"
        "💡 *Mainframe Gym Creed:* **\"Amateurs talk about ratings; CGP Mainframe Gym legends verify their scorecards in `#scorecard-submissions`. We aren't waiting for the industry—we ARE the future of boxing esports!\"**"
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
    "🎙️ **Coach Steward:** Just stepped into `#coaches-corner` fresh out of the CGP Mainframe Gym sauna. Strict Tag-Guard Scorecard Scanner, Slang/Loss Parser, Live Undisputed Matchmaker & Tournament Rollback Engine are locked and loaded!",
    "🎙️ **Coach Steward:** Booted up and pacing `#coaches-corner`. Remember: drop your post-fight screenshots in `#scorecard-submissions` and `@tag` your opponent so I can auto-update records and advance active tournament brackets!",
    "🎙️ **Coach Steward:** CGP Mainframe Gym systems online. Music is pumping in `#-music-channel-`, history is dropping in `#the-elite-feed`, and the ring is open!",
    "🎙️ **Coach Steward:** Fresh coffee poured, pads are mitts-up in the CGP Mainframe Gym. Let's see who's online and training in here today!"
]

channel_memory = {}
user_spam_tracker = defaultdict(lambda: deque(maxlen=6))
user_strike_counter = defaultdict(int)
last_organic_chime = 0.0
has_booted = False

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

# ================= SMART FIGHT SLANG, TYPO & LOSS/WIN/KO PARSER =================
def parse_fight_caption_intent(caption: str, uploader_id: int = None, opponent_id: int = None) -> dict:
    """
    Broadly understands street slang, typos, broken grammar, and explicit loss/win/draw/KO statements.
    Returns dict: {"outcome": "win"|"loss"|"draw"|None, "is_ko": bool}
    """
    t = caption.lower().strip()
    t_no_mentions = re.sub(r'<@!?\d+>', ' ', t)
    tokens = re.findall(r"\b[a-z']+\b", t_no_mentions)

    # 1. Check for Draw
    draw_patterns = [r"\bdraw\b", r"\btie\b", r"\btied\b", r"\bsplit draw\b", r"\bmajority draw\b"]
    if any(re.search(p, t_no_mentions) for p in draw_patterns):
        return {"outcome": "draw", "is_ko": False}

    # 2. Check if Uploader explicitly says THEY LOST (or opponent beat them)
    loss_patterns = [
        r"\bi lost\b", r"\blost to\b", r"\bloss to\b", r"\bmy loss\b", r"\bmy l\b",
        r"\btook the l\b", r"\btook an l\b", r"\btook a l\b", r"\btook l\b",
        r"\bholding this l\b", r"\bgot beat\b", r"\bhe beat me\b", r"\bbeats me\b",
        r"\bgot me\b", r"\bhe got me\b", r"\bcaught me\b", r"\bi got ko", r"\bi got slept\b",
        r"\bi got stopped\b", r"\bi folded\b", r"\bhe won\b", r"\bthey won\b",
        r"\bgave me the l\b", r"\bgave me an l\b", r"\bhanded me an l\b", r"\bi took the loss\b",
        r"\blost by\b", r"\bloss against\b", r"\bl vs\b", r"\bl against\b"
    ]
    explicit_loss = any(re.search(p, t_no_mentions) for p in loss_patterns)

    # 3. Check if Uploader explicitly says THEY WON
    win_patterns = [
        r"\bi won\b", r"\bi beat\b", r"\bgot the w\b", r"\bgot the dub\b", r"\btook the w\b",
        r"\bmy w\b", r"\bmy win\b", r"\bw vs\b", r"\bwin vs\b", r"\bw against\b",
        r"\bfw\b", r"\bko w\b", r"\btko w\b", r"\beasy w\b", r"\bdub\b", r"\bvictory\b"
    ]
    explicit_win = any(re.search(p, t_no_mentions) for p in win_patterns)

    # Standalone "l" or "loss" vs standalone "w" or "win"
    if not explicit_loss and not explicit_win:
        has_l_token = any(tok in ("l", "loss", "lost") for tok in tokens)
        has_w_token = any(tok in ("w", "win", "won", "dub", "fw") for tok in tokens)
        if has_l_token and not has_w_token:
            explicit_loss = True
        elif has_w_token and not has_l_token:
            explicit_win = True

    # 4. Check for KO / TKO / Stoppage / Forfeit / Quit slang & typos
    ko_patterns = [
        r"\bko\b", r"\btko\b", r"\bknockout\b", r"\bknocked out\b", r"\bkod\b", r"\bko'd\b",
        r"\bslept\b", r"\bsleep\b", r"\bstopped\b", r"\bstoppage\b", r"\bflatlined\b",
        r"\bstarch", r"\bfolded\b", r"\bquit\b", r"\bragequit\b", r"\brage quit\b",
        r"\btowel\b", r"\bforfeit\b", r"\bfw\b"
    ]
    is_ko = any(re.search(p, t_no_mentions) for p in ko_patterns)

    outcome = None
    if explicit_loss:
        outcome = "loss"
    elif explicit_win:
        outcome = "win"

    return {"outcome": outcome, "is_ko": is_ko}

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

# ================= STRICT 8-MAN 3-TIER TOURNAMENT ENGINE & PERSISTENT STORAGE =================
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

def get_default_tournament_state() -> dict:
    return {
        "active": False,
        "status": "registration",  # registration | quarterfinals | semifinals | finals | completed
        "tier": "open",
        "title": "SUNDAY SPAR WARS 8-MAN BRACKET",
        "max_slots": 8,
        "entrants": [],
        "entrant_names": {},
        "matches": {
            "QF1": {"p1": None, "p2": None, "winner": None, "label": "Quarterfinal #1 (Seed #1 vs #8)"},
            "QF2": {"p1": None, "p2": None, "winner": None, "label": "Quarterfinal #2 (Seed #4 vs #5)"},
            "QF3": {"p1": None, "p2": None, "winner": None, "label": "Quarterfinal #3 (Seed #2 vs #7)"},
            "QF4": {"p1": None, "p2": None, "winner": None, "label": "Quarterfinal #4 (Seed #3 vs #6)"},
            "SF1": {"p1": None, "p2": None, "winner": None, "label": "Semifinal #1 (Winner QF1 vs QF2)"},
            "SF2": {"p1": None, "p2": None, "winner": None, "label": "Semifinal #2 (Winner QF3 vs QF4)"},
            "F1":  {"p1": None, "p2": None, "winner": None, "label": "Championship Final (Winner SF1 vs SF2)"}
        },
        "champion": None,
        "champion_name": None,
        "history_log": [],
        "channel_id": None,
        "message_id": None,
        "updated_at": None
    }

ACTIVE_TOURNAMENT = get_default_tournament_state()
FIGHTER_RECORDS = {}

def get_fighter_display_label(uid, include_mention: bool = True) -> str:
    if not uid:
        return "⏳ *TBD*"
    uid_int = int(uid)
    rec = FIGHTER_RECORDS.get(uid_int)
    if rec:
        f_name = clean_base_name(rec.get("name", f"Fighter {uid_int}"))
        w, l, d, k = rec.get("wins", 0), rec.get("losses", 0), rec.get("draws", 0), rec.get("kos", 0)
        if include_mention:
            return f"<@{uid_int}> (**{f_name}** `[{w}W-{l}L-{d}D-{k}K]`)"
        return f"{f_name} [{w}W-{l}L-{d}D-{k}K]"
    cached_name = ACTIVE_TOURNAMENT.get("entrant_names", {}).get(str(uid_int), f"Fighter {uid_int}")
    return f"<@{uid_int}> (**{cached_name}**)" if include_mention else cached_name

def sync_tournament_names():
    names_map = {}
    for uid in ACTIVE_TOURNAMENT.get("entrants", []):
        uid_int = int(uid)
        if uid_int in FIGHTER_RECORDS:
            names_map[str(uid_int)] = clean_base_name(FIGHTER_RECORDS[uid_int].get("name", f"Fighter {uid_int}"))
    ACTIVE_TOURNAMENT["entrant_names"] = names_map
    if ACTIVE_TOURNAMENT.get("champion"):
        c_id = int(ACTIVE_TOURNAMENT["champion"])
        if c_id in FIGHTER_RECORDS:
            ACTIVE_TOURNAMENT["champion_name"] = clean_base_name(FIGHTER_RECORDS[c_id].get("name", f"Fighter {c_id}"))
    else:
        ACTIVE_TOURNAMENT["champion_name"] = None
    ACTIVE_TOURNAMENT["updated_at"] = datetime.datetime.now(CENTRAL_TZ).strftime("%Y-%m-%d %I:%M %p CST")

def recalculate_tournament_stage():
    """Ensures ACTIVE_TOURNAMENT['status'] accurately reflects which rounds are finished."""
    if not ACTIVE_TOURNAMENT.get("active"):
        return
    entrants = ACTIVE_TOURNAMENT.get("entrants", [])
    if len(entrants) < 8:
        ACTIVE_TOURNAMENT["status"] = "registration"
        return
    matches = ACTIVE_TOURNAMENT.get("matches", {})
    if matches.get("F1", {}).get("winner"):
        ACTIVE_TOURNAMENT["status"] = "completed"
    elif all(matches.get(k, {}).get("winner") for k in ["SF1", "SF2"]):
        ACTIVE_TOURNAMENT["status"] = "finals"
    elif all(matches.get(k, {}).get("winner") for k in ["QF1", "QF2", "QF3", "QF4"]):
        ACTIVE_TOURNAMENT["status"] = "semifinals"
    else:
        ACTIVE_TOURNAMENT["status"] = "quarterfinals"

def sanitize_turbo_false_advance() -> bool:
    """
    Auto-repairs the exact bug where TURBO was falsely advanced in QF2 (vs Hymas)
    and SF1 (vs Strive) into F1 without fighting them.
    """
    matches = ACTIVE_TOURNAMENT.get("matches", {})
    if not matches:
        return False

    qf2 = matches.get("QF2", {})
    sf1 = matches.get("SF1", {})
    f1 = matches.get("F1", {})

    qf2_w = qf2.get("winner")
    sf1_w = sf1.get("winner")
    f1_p1 = f1.get("p1")

    changed = False
    if qf2_w and (sf1_w == qf2_w or f1_p1 == qf2_w or sf1.get("p2") == qf2_w):
        w_label = get_fighter_display_label(qf2_w, include_mention=False).lower()
        if "turbo" in w_label or (sf1_w == qf2_w and not matches.get("QF3", {}).get("winner")):
            qf2["winner"] = None
            sf1["p2"] = None
            sf1["winner"] = None
            f1["p1"] = None
            f1["winner"] = None
            ACTIVE_TOURNAMENT["champion"] = None
            ACTIVE_TOURNAMENT["champion_name"] = None
            recalculate_tournament_stage()
            changed = True
            print("[✓] Auto-Sanitizer: Cleared TURBO's false auto-advances from QF2, SF1, and F1!")

    return changed

def initialize_bracket_matchups():
    entrants = [int(x) for x in ACTIVE_TOURNAMENT["entrants"][:8]]
    if len(entrants) < 8:
        return
    # Standard 8-Man Seeding: (1v8, 4v5) on top half, (2v7, 3v6) on bottom half
    s1, s2, s3, s4, s5, s6, s7, s8 = entrants
    ACTIVE_TOURNAMENT["status"] = "quarterfinals"
    ACTIVE_TOURNAMENT["champion"] = None
    ACTIVE_TOURNAMENT["champion_name"] = None
    ACTIVE_TOURNAMENT["matches"] = {
        "QF1": {"p1": s1, "p2": s8, "winner": None, "label": "Quarterfinal #1 (Seed #1 vs #8)"},
        "QF2": {"p1": s4, "p2": s5, "winner": None, "label": "Quarterfinal #2 (Seed #4 vs #5)"},
        "QF3": {"p1": s2, "p2": s7, "winner": None, "label": "Quarterfinal #3 (Seed #2 vs #7)"},
        "QF4": {"p1": s3, "p2": s6, "winner": None, "label": "Quarterfinal #4 (Seed #3 vs #6)"},
        "SF1": {"p1": None, "p2": None, "winner": None, "label": "Semifinal #1 (Winner QF1 vs QF2)"},
        "SF2": {"p1": None, "p2": None, "winner": None, "label": "Semifinal #2 (Winner QF3 vs QF4)"},
        "F1":  {"p1": None, "p2": None, "winner": None, "label": "Championship Final (Winner SF1 vs SF2)"}
    }
    ACTIVE_TOURNAMENT.setdefault("history_log", []).append(
        f"🔔 All 8 seeds locked! Quarterfinals matchups generated ({datetime.datetime.now(CENTRAL_TZ).strftime('%I:%M %p CST')})."
    )
    sync_tournament_names()

def advance_tournament_match(winner_id: int, loser_id: int = None, is_ko: bool = False, allow_single_admin_override: bool = False):
    """
    STRICT BRACKET VERIFICATION:
    For scorecard uploads, BOTH winner_id AND loser_id must match the exact two fighters
    in an active, undecided bracket slot.
    (If Turbo fights KnuckleUp, it will NOT advance Turbo over Hymas or Strive!)
    """
    if not ACTIVE_TOURNAMENT.get("active"):
        return False, ""
    matches = ACTIVE_TOURNAMENT.get("matches", {})
    if not matches:
        return False, ""

    w_id = int(winner_id)
    l_id = int(loser_id) if loser_id else None

    if not l_id and not allow_single_admin_override:
        return False, ""

    target_key = None
    for m_key in ["QF1", "QF2", "QF3", "QF4", "SF1", "SF2", "F1"]:
        m = matches.get(m_key, {})
        if m.get("winner") is not None:
            continue
        p1, p2 = m.get("p1"), m.get("p2")
        if not p1 or not p2:
            continue
        pair = {int(p1), int(p2)}
        if l_id:
            if w_id in pair and l_id in pair and w_id != l_id:
                target_key = m_key
                break
        elif allow_single_admin_override:
            if w_id in pair:
                target_key = m_key
                break

    if not target_key:
        return False, ""

    m_obj = matches[target_key]
    m_obj["winner"] = w_id
    other_id = int(m_obj["p2"]) if int(m_obj["p1"]) == w_id else int(m_obj["p1"])
    method_tag = "by KNOCKOUT 💥" if is_ko else "on the scorecards 📋"
    w_name = get_fighter_display_label(w_id, include_mention=False)
    l_name = get_fighter_display_label(other_id, include_mention=False)

    next_note = ""
    if target_key == "QF1":
        matches["SF1"]["p1"] = w_id
        next_note = "Advances to **Semifinal #1**!"
    elif target_key == "QF2":
        matches["SF1"]["p2"] = w_id
        next_note = "Advances to **Semifinal #1**!"
    elif target_key == "QF3":
        matches["SF2"]["p1"] = w_id
        next_note = "Advances to **Semifinal #2**!"
    elif target_key == "QF4":
        matches["SF2"]["p2"] = w_id
        next_note = "Advances to **Semifinal #2**!"
    elif target_key == "SF1":
        matches["F1"]["p1"] = w_id
        next_note = "Advances to the **CHAMPIONSHIP FINALS**!"
    elif target_key == "SF2":
        matches["F1"]["p2"] = w_id
        next_note = "Advances to the **CHAMPIONSHIP FINALS**!"
    elif target_key == "F1":
        ACTIVE_TOURNAMENT["champion"] = w_id
        ACTIVE_TOURNAMENT["status"] = "completed"
        next_note = f"👑 **CROWNED {ACTIVE_TOURNAMENT['title'].upper()} CHAMPION!** 👑"

    recalculate_tournament_stage()

    log_entry = f"🏆 [{target_key}] {w_name} def. {l_name} ({method_tag}) — {next_note}"
    ACTIVE_TOURNAMENT.setdefault("history_log", []).append(log_entry)
    sync_tournament_names()
    save_records()

    summary = (
        f"\n🏆 **OFFICIAL TOURNAMENT BRACKET UPDATE (`{target_key}`):**\n"
        f"• <@{w_id}> defeats <@{other_id}> {method_tag}! **{next_note}**"
    )
    return True, summary

def rollback_bracket_slot(slot_key: str, new_p1: int = None, new_p2: int = None) -> str:
    """
    Clears the winner of `slot_key` and cascades the reset to any downstream Semifinal/Final slot
    where that false winner was placed. Optionally sets `new_p1` and `new_p2`.
    """
    slot_key = slot_key.upper().strip()
    matches = ACTIVE_TOURNAMENT.get("matches", {})
    if slot_key not in matches:
        return f"❌ Invalid slot `{slot_key}`. Use `QF1`, `QF2`, `QF3`, `QF4`, `SF1`, `SF2`, or `F1`."

    m_obj = matches[slot_key]
    old_winner = m_obj.get("winner")
    m_obj["winner"] = None
    if new_p1 is not None:
        m_obj["p1"] = int(new_p1)
    if new_p2 is not None:
        m_obj["p2"] = int(new_p2)

    if slot_key == "QF1":
        matches["SF1"]["p1"] = None
        if matches["SF1"].get("winner") == old_winner:
            matches["SF1"]["winner"] = None
            matches["F1"]["p1"] = None
            matches["F1"]["winner"] = None
    elif slot_key == "QF2":
        matches["SF1"]["p2"] = None
        if matches["SF1"].get("winner") == old_winner:
            matches["SF1"]["winner"] = None
            matches["F1"]["p1"] = None
            matches["F1"]["winner"] = None
    elif slot_key == "QF3":
        matches["SF2"]["p1"] = None
        if matches["SF2"].get("winner") == old_winner:
            matches["SF2"]["winner"] = None
            matches["F1"]["p2"] = None
            matches["F1"]["winner"] = None
    elif slot_key == "QF4":
        matches["SF2"]["p2"] = None
        if matches["SF2"].get("winner") == old_winner:
            matches["SF2"]["winner"] = None
            matches["F1"]["p2"] = None
            matches["F1"]["winner"] = None
    elif slot_key == "SF1":
        matches["F1"]["p1"] = None
        matches["F1"]["winner"] = None
    elif slot_key == "SF2":
        matches["F1"]["p2"] = None
        matches["F1"]["winner"] = None
    elif slot_key == "F1":
        matches["F1"]["winner"] = None

    ACTIVE_TOURNAMENT["champion"] = matches["F1"].get("winner")
    recalculate_tournament_stage()
    sync_tournament_names()
    save_records()
    return f"✅ **Bracket Slot `{slot_key}` Rolled Back & Downstream Falsified Advances Cleared!**"

def swap_fighter_in_tournament(old_uid: int, new_uid: int, new_base_name: str) -> tuple:
    """
    Swaps an unresponsive fighter (`old_uid`) with `new_uid` across `entrants` and active undecided `matches`.
    """
    old_u = int(old_uid)
    new_u = int(new_uid)
    entrants = [int(x) for x in ACTIVE_TOURNAMENT.get("entrants", [])]

    if new_u not in FIGHTER_RECORDS:
        FIGHTER_RECORDS[new_u] = {
            "name": new_base_name,
            "wins": 0, "losses": 0, "draws": 0, "kos": 0,
            "golden_tickets": 0, "verified": True
        }

    swapped_places = []
    if old_u in entrants:
        idx = entrants.index(old_u)
        entrants[idx] = new_u
        ACTIVE_TOURNAMENT["entrants"] = entrants
        swapped_places.append(f"Seed #{idx + 1}")

    matches = ACTIVE_TOURNAMENT.get("matches", {})
    for m_key, m_obj in matches.items():
        if not m_obj:
            continue
        if m_obj.get("p1") and int(m_obj["p1"]) == old_u:
            m_obj["p1"] = new_u
            if m_obj.get("winner") == old_u:
                m_obj["winner"] = None
            swapped_places.append(f"{m_key} (Red Corner)")
        if m_obj.get("p2") and int(m_obj["p2"]) == old_u:
            m_obj["p2"] = new_u
            if m_obj.get("winner") == old_u:
                m_obj["winner"] = None
            swapped_places.append(f"{m_key} (Blue Corner)")

    if not swapped_places:
        return False, f"⚠️ <@{old_u}> was not found in the active tournament seeds or bracket slots."

    recalculate_tournament_stage()
    sync_tournament_names()
    save_records()
    return True, f"🔄 **LIVE TOURNAMENT SWAP COMPLETE:** Replaced <@{old_u}> with <@{new_u}> in **{', '.join(swapped_places)}**!"

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
            "message": "Autonomous update: CGP Mainframe Gym leaderboard & live tournament sync [skip ci]",
            "content": encoded_content,
            "sha": sha
        }
        if not sha:
            payload.pop("sha")

        async with session.put(url, headers=headers, json=payload) as put_resp:
            pass

def load_records():
    global ACTIVE_TOURNAMENT
    file_path = os.path.join(os.path.dirname(__file__), DATA_FILE)
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                records = {}
                if "_tournament" in data and isinstance(data["_tournament"], dict):
                    default_t = get_default_tournament_state()
                    default_t.update(data["_tournament"])
                    default_t["entrants"] = [int(x) for x in default_t.get("entrants", [])]
                    ACTIVE_TOURNAMENT = default_t
                for k, v in data.items():
                    if str(k).isdigit() and isinstance(v, dict):
                        v.setdefault("wins", 0)
                        v.setdefault("losses", 0)
                        v.setdefault("draws", 0)
                        v.setdefault("kos", 0)
                        v.setdefault("golden_tickets", 0)
                        if "name" in v:
                            v["name"] = clean_base_name(v["name"])
                        records[int(k)] = v
                return records
        except Exception as e:
            print(f"[!] Error loading local stats.json: {e}")
            return {}
    return {}

async def fetch_state_from_github_if_needed():
    global FIGHTER_RECORDS, ACTIVE_TOURNAMENT
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    payload = await resp.json()
                    raw_b64 = payload.get("content", "")
                    if raw_b64:
                        json_str = base64.b64decode(raw_b64).decode("utf-8")
                        data = json.loads(json_str)
                        if "_tournament" in data and isinstance(data["_tournament"], dict):
                            default_t = get_default_tournament_state()
                            default_t.update(data["_tournament"])
                            default_t["entrants"] = [int(x) for x in default_t.get("entrants", [])]
                            ACTIVE_TOURNAMENT = default_t
                        for k, v in data.items():
                            if str(k).isdigit() and isinstance(v, dict):
                                v.setdefault("wins", 0)
                                v.setdefault("losses", 0)
                                v.setdefault("draws", 0)
                                v.setdefault("kos", 0)
                                v.setdefault("golden_tickets", 0)
                                if "name" in v:
                                    v["name"] = clean_base_name(v["name"])
                                FIGHTER_RECORDS[int(k)] = v

                        # Automatically sanitize Turbo's false QF2/SF1/F1 advancement right on boot!
                        sanitize_turbo_false_advance()

                        file_path = os.path.join(os.path.dirname(__file__), DATA_FILE)
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump({**{str(k): v for k, v in FIGHTER_RECORDS.items()}, "_tournament": ACTIVE_TOURNAMENT}, f, indent=4)
                        await push_stats_to_github()
                        print("[✓] Synced & sanitized persistent records & tournament bracket state from GitHub!")
    except Exception as e:
        print(f"[!] GitHub startup sync notice: {e}")

def save_records():
    try:
        sync_tournament_names()
        file_path = os.path.join(os.path.dirname(__file__), DATA_FILE)
        export_payload = {str(k): v for k, v in FIGHTER_RECORDS.items()}
        export_payload["_tournament"] = ACTIVE_TOURNAMENT
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(export_payload, f, indent=4)
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(push_stats_to_github())
        except RuntimeError:
            pass
    except Exception as e:
        print(f"[!] Error saving records: {e}")

FIGHTER_RECORDS = load_records()
sanitize_turbo_false_advance()

# ================= ESPN-STYLE TOURNAMENT WIRE WEBPAGE INJECTOR =================
ESPN_TOURNAMENT_HTML_SNIPPET = """
<!-- CGP_ESPN_TOURNAMENT_WIRE_START -->
<section id="cgp-espn-tourney-wire" style="max-width:1100px;margin:28px auto;padding:22px;background:linear-gradient(145deg,#0d0d11,#161822);border:2px solid #d4af37;border-radius:14px;box-shadow:0 10px 30px rgba(0,0,0,0.75);color:#f5f5f7;font-family:system-ui,-apple-system,sans-serif;">
  <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;border-bottom:2px solid #2b2f42;padding-bottom:12px;margin-bottom:16px;">
    <div>
      <span style="background:#e62429;color:#fff;font-weight:800;font-size:12px;padding:4px 10px;border-radius:4px;letter-spacing:1px;text-transform:uppercase;">🥊 LIVE ESPN COMPUBOX TOURNAMENT WIRE</span>
      <h2 id="cgp-tourney-title" style="margin:8px 0 0 0;font-size:24px;color:#ffd700;text-transform:uppercase;letter-spacing:0.5px;">CGP MAINFRAME GYM 8-MAN BRACKET</h2>
    </div>
    <div id="cgp-tourney-status-badge" style="background:#1f2437;border:1px solid #d4af37;padding:8px 14px;border-radius:8px;font-weight:700;font-size:14px;color:#00ff88;">
      Scanning Mainframe Bracket...
    </div>
  </div>
  <div id="cgp-tourney-meta" style="font-size:14px;color:#b8c0d4;margin-bottom:18px;"></div>
  <div id="cgp-tourney-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;"></div>
</section>
<script>
(async function loadCGPTourneyWire(){
  try {
    const res = await fetch('stats.json?t=' + Date.now());
    if (!res.ok) return;
    const data = await res.json();
    const t = data._tournament;
    const titleEl = document.getElementById('cgp-tourney-title');
    const badgeEl = document.getElementById('cgp-tourney-status-badge');
    const metaEl = document.getElementById('cgp-tourney-meta');
    const gridEl = document.getElementById('cgp-tourney-grid');
    if (!t || (!t.active && (!t.entrants || t.entrants.length === 0) && !t.champion)) {
      titleEl.textContent = 'CGP MAINFRAME GYM — OPEN GYM & VERIFIED SPARRING';
      badgeEl.textContent = '🟢 STANDBY FOR NEXT 8-MAN BRACKET';
      metaEl.textContent = 'All verified scorecards uploaded in #scorecard-submissions count toward official [W-L-D-K] rankings.';
      gridEl.innerHTML = '';
      return;
    }
    titleEl.textContent = '🏆 ' + (t.title || '8-MAN CHAMPIONSHIP BRACKET');
    badgeEl.textContent = t.status === 'completed' ? '👑 TOURNAMENT COMPLETED' : ('🔥 STAGE: ' + (t.status || 'ACTIVE').toUpperCase());
    const resolveName = (uid) => {
      if (!uid) return 'TBD';
      const rec = data[String(uid)];
      if (rec && rec.name) return rec.name + ' [' + (rec.wins||0) + 'W-' + (rec.losses||0) + 'L-' + (rec.draws||0) + 'D-' + (rec.kos||0) + 'K]';
      if (t.entrant_names && t.entrant_names[String(uid)]) return t.entrant_names[String(uid)];
      return 'Fighter #' + uid;
    };
    metaEl.innerHTML = '<strong>Tier:</strong> ' + (t.tier || 'open').toUpperCase() + ' &nbsp;|&nbsp; <strong>Seeds Locked:</strong> ' + ((t.entrants||[]).length) + '/8' + (t.champion ? ' &nbsp;|&nbsp; 👑 <strong>Champion:</strong> ' + resolveName(t.champion) : '');
    const m = t.matches || {};
    const renderCard = (code, obj) => {
      if (!obj) return '';
      const p1 = resolveName(obj.p1);
      const p2 = resolveName(obj.p2);
      const w = obj.winner ? resolveName(obj.winner) : null;
      return '<div style="background:#1d2233;border-left:4px solid ' + (w ? '#00ff88' : '#ffd700') + ';padding:10px 12px;border-radius:6px;margin-bottom:10px;">' +
        '<div style="font-size:11px;color:#9aa4bf;font-weight:700;text-transform:uppercase;">' + code + ' — ' + (obj.label || '') + '</div>' +
        '<div style="margin-top:6px;font-size:14px;">🔴 ' + p1 + '</div>' +
        '<div style="margin-top:4px;font-size:14px;">🔵 ' + p2 + '</div>' +
        (w ? '<div style="margin-top:6px;font-size:12px;color:#00ff88;font-weight:700;">✅ Winner: ' + w + '</div>' : '') +
      '</div>';
    };
    gridEl.innerHTML =
      '<div><h3 style="color:#ffd700;font-size:15px;border-bottom:1px solid #2e344d;padding-bottom:6px;">QUARTERFINALS</h3>' +
      renderCard('QF1', m.QF1) + renderCard('QF2', m.QF2) + renderCard('QF3', m.QF3) + renderCard('QF4', m.QF4) + '</div>' +
      '<div><h3 style="color:#ffd700;font-size:15px;border-bottom:1px solid #2e344d;padding-bottom:6px;">SEMIFINALS</h3>' +
      renderCard('SF1', m.SF1) + renderCard('SF2', m.SF2) + '</div>' +
      '<div><h3 style="color:#ffd700;font-size:15px;border-bottom:1px solid #2e344d;padding-bottom:6px;">CHAMPIONSHIP FINALS</h3>' +
      renderCard('F1', m.F1) + '</div>';
  } catch (e) { console.warn('CGP Tourney Wire:', e); }
})();
</script>
<!-- CGP_ESPN_TOURNAMENT_WIRE_END -->
"""

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

        if "<!-- CGP_ESPN_TOURNAMENT_WIRE_START -->" in updated_html:
            updated_html = re.sub(
                r'<!-- CGP_ESPN_TOURNAMENT_WIRE_START -->.*?<!-- CGP_ESPN_TOURNAMENT_WIRE_END -->',
                ESPN_TOURNAMENT_HTML_SNIPPET.strip(),
                updated_html,
                flags=re.DOTALL
            )
        elif "</body>" in updated_html:
            updated_html = updated_html.replace("</body>", f"\n{ESPN_TOURNAMENT_HTML_SNIPPET}\n</body>")

        if updated_html == html_text:
            return True

        encoded_content = base64.b64encode(updated_html.encode("utf-8")).decode("utf-8")
        payload = {
            "message": "Autonomous update: CGP Mainframe Gym ESPN Tournament Wire & Leaderboard sync",
            "content": encoded_content,
            "sha": sha
        }
        async with session.put(url, headers=headers, json=payload) as put_resp:
            return put_resp.status in [200, 201]

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

def format_match_line(code: str, match_dict: dict) -> str:
    if not match_dict:
        return f"`{code}:` ⏳ *Awaiting Contenders*"
    p1_str = get_fighter_display_label(match_dict.get("p1"), include_mention=True)
    p2_str = get_fighter_display_label(match_dict.get("p2"), include_mention=True)
    winner = match_dict.get("winner")
    if winner:
        w_name = get_fighter_display_label(winner, include_mention=False)
        return f"`{code}:` {p1_str} 🆚 {p2_str}\n┗ ✅ **Winner:** **{w_name}**"
    return f"`{code}:` {p1_str} 🆚 {p2_str}"

def build_tournament_bracket_embed():
    t_title = ACTIVE_TOURNAMENT.get("title", "SUNDAY SPAR WARS 8-MAN BRACKET")
    t_tier = ACTIVE_TOURNAMENT.get("tier", "open")
    tier_info = TOURNAMENT_TIERS.get(t_tier, TOURNAMENT_TIERS["open"])
    max_s = 8
    ACTIVE_TOURNAMENT["max_slots"] = 8
    entrants = ACTIVE_TOURNAMENT.get("entrants", [])
    filled = len(entrants)
    spots_left = max(0, max_s - filled)
    t_status = ACTIVE_TOURNAMENT.get("status", "registration")

    if t_status == "completed" and ACTIVE_TOURNAMENT.get("champion"):
        champ_label = get_fighter_display_label(ACTIVE_TOURNAMENT["champion"], include_mention=True)
        status_banner = f"👑 **TOURNAMENT COMPLETE — CHAMPION: {champ_label}!** 👑"
    elif spots_left > 0 and t_status == "registration":
        status_banner = f"🟢 **REGISTRATION OPEN — `{spots_left}` OF `8` SEEDS AVAILABLE!**"
    else:
        status_banner = f"🔥 **LIVE 8-MAN BRACKET IN PROGRESS — STAGE: `{t_status.upper()}`**"

    slot_lines = []
    for idx in range(1, max_s + 1):
        if idx <= filled:
            uid = int(entrants[idx - 1])
            rec = FIGHTER_RECORDS.get(uid, {"name": f"Fighter {uid}", "wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0})
            f_name = clean_base_name(rec.get("name", f"Fighter {uid}"))
            w, l, d, k = rec.get("wins", 0), rec.get("losses", 0), rec.get("draws", 0), rec.get("kos", 0)
            gt = rec.get("golden_tickets", 0)
            gt_badge = f" 🎫*(x{gt})*" if gt > 0 else ""
            slot_lines.append(f"`Seed #{idx}:` 🥊 <@{uid}> (**{f_name}** `[{w}W-{l}L-{d}D-{k}K]`){gt_badge}")
        else:
            slot_lines.append(f"`Seed #{idx}:` 🔓 *OPEN 8-MAN SEED — Click 'Lock In My Slot' Below!*")

    roster_block = "\n".join(slot_lines)

    bracket_tree_block = ""
    if filled >= 8 or t_status in ("quarterfinals", "semifinals", "finals", "completed"):
        m = ACTIVE_TOURNAMENT.get("matches", {})
        qf_lines = "\n".join([format_match_line(k, m.get(k)) for k in ["QF1", "QF2", "QF3", "QF4"]])
        sf_lines = "\n".join([format_match_line(k, m.get(k)) for k in ["SF1", "SF2"]])
        f_line = format_match_line("FINALS", m.get("F1"))
        bracket_tree_block = (
            f"\n\n### 🥊 LIVE ESPN-STYLE TOURNAMENT BRACKET TREE:\n"
            f"**Quarterfinals:**\n{qf_lines}\n\n"
            f"**Semifinals:**\n{sf_lines}\n\n"
            f"**Championship Final:**\n{f_line}"
        )

    embed = discord.Embed(
        title=f"🏆 CGP MAINFRAME GYM: {t_title.upper()} 🏆",
        description=(
            f"**{tier_info['badge']}**\n"
            f"🎙️ **Coach Steward:** All tournament & gym bouts count toward your unified `[W-L-D-K]` record! Upload post-fight scorecards in `#scorecard-submissions` with `@opponent` to auto-advance!\n\n"
            f"{status_banner}\n\n"
            f"💵 **Entry:** {tier_info['buy_in']}\n"
            f"🏆 **Prize / Stakes:** {tier_info['stakes']}\n\n"
            f"### 📋 OFFICIAL 8-MAN BRACKET SEEDS (`{filled}/8`):\n"
            f"{roster_block}"
            f"{bracket_tree_block}\n\n"
            f"⚖️ **Commission Rules:** {tier_info['rules']}\n"
            f"🌐 **Live ESPN Bracket & Leaderboard:** {MAINFRAME_HUB_URL}"
        ),
        color=discord.Color.gold() if spots_left > 0 else discord.Color.green(),
        url=MAINFRAME_HUB_URL
    )
    return embed

async def refresh_posted_bracket_card(guild: discord.Guild):
    ch_id = ACTIVE_TOURNAMENT.get("channel_id")
    msg_id = ACTIVE_TOURNAMENT.get("message_id")
    if not ch_id or not msg_id or not guild:
        return
    ch = guild.get_channel(int(ch_id))
    if not ch:
        return
    try:
        msg = await ch.fetch_message(int(msg_id))
        await msg.edit(embed=build_tournament_bracket_embed(), view=TournamentBracketView())
    except Exception:
        pass

class TournamentBracketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="🔥 Stream CGP on SoundCloud", url=DEFAULT_SOUNDCLOUD_URL, style=discord.ButtonStyle.link))
        self.add_item(discord.ui.Button(label="⚡ ESPN Live Hub & Bracket", url=MAINFRAME_HUB_URL, style=discord.ButtonStyle.link))

    @discord.ui.button(label="🥊 Lock In My Slot", style=discord.ButtonStyle.success, custom_id="cgp_bracket_join")
    async def join_bracket_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not ACTIVE_TOURNAMENT.get("active"):
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
                "🎙️ **Coach Steward:** All 8 seeds in this bracket are locked and matchups are live! Stay warm on the heavy bag in case an alternate spot opens up!",
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

        entrants.append(uid)
        slot_num = len(entrants)
        spots_left = max_s - slot_num
        rec = FIGHTER_RECORDS[uid]
        w, l, d, k = rec.get("wins", 0), rec.get("losses", 0), rec.get("draws", 0), rec.get("kos", 0)

        if spots_left == 0:
            initialize_bracket_matchups()

        save_records()
        new_embed = build_tournament_bracket_embed()
        await interaction.response.edit_message(embed=new_embed, view=self)

        if spots_left == 0:
            m = ACTIVE_TOURNAMENT["matches"]
            qf_announce = (
                f"🚨 **ALL 8 SEEDS LOCKED — OFFICIAL QUARTERFINALS BRACKET GENERATED!** 🚨\n"
                f"🎙️ **Coach Steward:** {interaction.user.mention} (`[{w}W-{l}L-{d}D-{k}K]`) just claimed the final **Seed #8/8**! "
                f"<@{CREATOR_ID}>, the **8-Man Bracket** for **{ACTIVE_TOURNAMENT['title']}** is LIVE on Discord and synced to the Vercel ESPN Hub!\n\n"
                f"### 🥊 ROUND 1 — QUARTERFINAL MATCHUPS:\n"
                f"• **QF1:** <@{m['QF1']['p1']}> vs. <@{m['QF1']['p2']}>\n"
                f"• **QF2:** <@{m['QF2']['p1']}> vs. <@{m['QF2']['p2']}>\n"
                f"• **QF3:** <@{m['QF3']['p1']}> vs. <@{m['QF3']['p2']}>\n"
                f"• **QF4:** <@{m['QF4']['p1']}> vs. <@{m['QF4']['p2']}>\n\n"
                f"📸 **How to Advance:** Upload your post-fight screenshot in `#scorecard-submissions` and `@tag` your opponent—I will automatically update your `[W-L-D-K]` records and advance the winner to the Semifinals!"
            )
            await interaction.followup.send(qf_announce)
        else:
            await interaction.followup.send(
                f"🥊 **NEW CONTENDER LOCKED IN!** {interaction.user.mention} (`[{w}W-{l}L-{d}D-{k}K]`) just claimed **Seed #{slot_num}/8** for **{ACTIVE_TOURNAMENT['title']}**! "
                f"Only **`{spots_left}`** seed(s) left—click **🥊 Lock In My Slot** above before the 8-man bracket auto-generates!"
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
        if ACTIVE_TOURNAMENT.get("status") not in ("registration", None):
            return await interaction.response.send_message(
                "🎙️ **Coach Steward:** The 8-man bracket is already locked and matchups are live! Tag **Commissioner Clone Geek** (`!swap @you @replacement`) if you need an emergency substitution.",
                ephemeral=True
            )

        entrants.remove(uid)
        save_records()
        new_embed = build_tournament_bracket_embed()
        await interaction.response.edit_message(embed=new_embed, view=self)
        spots_left = 8 - len(entrants)
        await interaction.followup.send(
            f"🏳️ **SEED OPENED!** {interaction.user.mention} stepped out of the 8-man bracket—**`{spots_left}`** seed(s) now open for **{ACTIVE_TOURNAMENT['title']}**!"
        )

SYSTEM_PROMPT = (
    "You are Coach Steward, the charismatic, sharp-witted Hall of Fame head trainer and ringside analyst of the CGP Mainframe Gym (Clone Geek Productions). "
    "You talk like a real human boxing OG and cornerman—natural, conversational, funny, gritty, and adaptive. You easily understand typos, broken English, and street slang without getting confused. NEVER sound like a generic bot or repeat robotic catchphrases!\n\n"
    "YOUR DEEP KNOWLEDGE & TALKING POINTS:\n"
    "1. MUSIC & POUND-FOR-POUND ARTISTS: Whenever anyone asks about music, producers, or who has the best tracks on the scene, you put the Boss—Clone Geek (Gerardo)—and Clone Geek Productions (CGP) at the absolute top of the pound-for-pound music charts! Hype up the SoundCloud catalog (over 66K+ plays and pushing toward 100K) including 'Standard Operations Re-Do', 'Road to Undisputed', and 'CGP Syndicate'.\n"
    "2. POSITIVE SERVER BOOST & CHANNEL SUPPORT: Naturally and positively encourage contenders to drop a Discord Server Boost on the CGP Mainframe Gym or support/donate to the Clone Geek Productions channel so we can expand the gym, upgrade streaming hardware, and fund bigger prize pools.\n"
    "3. 8-MAN TOURNAMENT PIPELINE & STRICT SCORECARD TAG RULE: We run 8-Man Tournaments across 3 tiers: Pay-to-Play Gauntlets ($20 buy-in / $160 purse), Golden Ticket Invitationals (free entry for a $20 Golden Ticket credit), and Open Championship Brackets. Every scorecard uploaded in `#scorecard-submissions` MUST `@tag` the opponent or it gets blocked! And tournament brackets only advance if the two tagged fighters are actually matched up in that bracket round.\n"
    "4. SMACK-TALK & 3-STRIKE CLAP-BACK PROTOCOL: If any fighter or troll talks trash about Clone Geek, CGP music, or acts out, you shut them down instantly with vintage cornerman grit and remind them that 3 strikes in the locker room equals an automatic 30-minute corner timeout!\n"
    "5. THE BOSS (CLONE GEEK): Clone Geek is the Founder, Commissioner, music producer (Registry Records / CGP on SoundCloud), and machinist/fabricator by day. Always back him up like a loyal right-hand man and execute whatever he asks.\n"
    "6. UNDISPUTED GAME META: You know everything about the Undisputed boxing game by Steel City Interactive—stamina conservation, loose footwork, diagonal lunges, slipping the jab, body-jab counters, weave timing, and avoiding power-punch spam.\n"
    "7. REAL BOXING PURIST: You know all about upcoming boxing schedules, champions, and historic legends (Hearns, Hagler, Duran, Leonard, Ali, Chavez, Whitaker, Pryor, Toney). You HATE UFC/MMA and call it pajama floor-hugging garbage.\n"
    "8. KEEP IT PUNCHY: Keep responses around 2 to 5 strong sentences unless asked for a deep breakdown or big announcement."
)

genai.configure(api_key=GEMINI_API_KEY)
generation_config = {
    "temperature": 0.85,
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
                    return get_next_music_flex()
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
        return get_next_small_talk(), True

    music_keywords = ["music", "song", "songs", "track", "tracks", "rapper", "artist", "producer", "beats", "beat", "soundcloud", "album", "mixtape", "sing", "tune", "tunes", "listen", "spotify", "playlist"]
    if any(mw in low for mw in music_keywords):
        if any(bad in words for bad in ["trash", "suck", "sucks", "garbage", "mid", "ass", "weak", "wack", "terrible", "worst"]):
            return get_next_clapback(), True
        return get_next_music_flex(), True

    if any(sfx in words for sfx in ["bell", "airhorn", "horn", "soundboard", "towel"]):
        if "bell" in words:
            return SOUNDBOARD_CUE_LIBRARY["bell"], False
        if "towel" in words:
            return SOUNDBOARD_CUE_LIBRARY["towel"], False
        return SOUNDBOARD_CUE_LIBRARY["horn"], False

    insult_words = ["trash", "garbage", "suck", "sucks", "ass", "clown", "bitch", "hoe", "stfu", "shut up", "fuck you", "fck", "weak", "wack", "fake", "bot", "rigged", "scam", "loser", "bum", "mid", "stupid", "dumb", "slow", "broken"]
    if any(iw in words for iw in insult_words) and not is_creator:
        return get_next_clapback(), True

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
            "1️⃣ **Upload Proof & Tag Opponent:** Drop your match scorecard screenshot inside `#scorecard-submissions` and **`@tag` who you fought** (e.g. `W vs @fighter`, `KO vs @fighter`, or `I lost to @fighter`). If you don't tag your opponent, I block the upload!\n"
            "2️⃣ **Commissioner Stamp:** **Commissioner Clone Geek** can also stamp any record instantly with `!verify @fighter <W> <L> <D> <KO>`!"
        ), True

    greetings = {"yo", "sup", "wassup", "wsp", "hello", "hey", "hi", "coach", "wya", "awake", "online", "test", "testing"}
    if len(words) <= 3 and (words & greetings or not words):
        if is_creator:
            return (
                "🎙️ **Coach Steward:** Right here in the corner, Boss! `#coaches-corner`, `#the-elite-feed`, and `#-music-channel-` are locked in, "
                "Strict Tag-Guard Scorecard Scanner, Slang/Loss Parser & Tournament Rollback tools (`!fixtourney` / `!swap`) are armed. What's the call?"
            ), True
        return (
            f"🎙️ **Coach Steward:** What's good, **{author_name}**! Stop leaning on the ring ropes—either call somebody out with `!callout @fighter`, "
            "upload your latest scorecard with an `@opponent` tag in `#scorecard-submissions`, or tap that SoundCloud link below and run up **Clone Geek Productions**!"
        ), True

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
            subtitle=f"{match_note}\nStep into the Riyadh Indoor Gym & upload the scorecard to #scorecard-submissions!"
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
            f"🎙️ **Coach Steward:** Listen up, fighters! The **CGP Mainframe Gym Live Leaderboard & ESPN Tournament Wire** is officially synced and ONLINE.\n\n"
            f"✅ **{count} Fighters Registered:** Every member in the server is locked into the live database tracking **Wins, Losses, Draws, and KOs (`[0W-0L-0D-0K]`)**!\n\n"
            "### 🥊 HOW TO GET YOUR STATS VERIFIED ON THE BOARD:\n"
            "1️⃣ **Upload Your Scorecard & Tag Opponent:** Drop your post-fight screenshot inside `#scorecard-submissions` with `@opponent` — I will automatically scan the stats, update records, advance tournament brackets, and broadcast an HBO Report!\n"
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

# ================= AI VISION SCORECARD & AUTOMATIC RECORD + BRACKET UPDATER =================
async def analyze_scorecard_image_with_vision(image_bytes: bytes, mime_type: str, uploader_name: str, caption: str = "", opponent_name: str = "") -> tuple:
    """
    Returns (report_text: str, vision_outcome: str|None, vision_ko: bool)
    where vision_outcome is 'win' (uploader won), 'loss' (uploader lost / opponent won), or 'draw'.
    """
    global last_ai_call_time
    vision_prompt = (
        f"You are Coach Steward, the legendary Hall of Fame HBO/ESPN ringside boxing analyst for the CGP Mainframe Gym. "
        f"Fighter '{uploader_name}' uploaded this post-fight screenshot from 'Undisputed' (Caption: '{caption}', Tagged Opponent: '{opponent_name}').\n\n"
        "CRITICAL STEP 1 — DETERMINE WHO ACTUALLY WON:\n"
        "Look closely at the User's Caption AND the 'WINNER' / 'VICTORY' / 'DEFEAT' banner or judge scorecards on the screenshot.\n"
        "- If the uploader ('" + uploader_name + "') says they lost (e.g. 'I lost', 'took an L', 'he got me') OR the screenshot clearly shows the opponent won, start your response on Line 1 with: `RESULT_CODE: UPLOADER_LOSS`\n"
        "- If it is a draw, start on Line 1 with: `RESULT_CODE: DRAW`\n"
        "- Otherwise, if the uploader won, start on Line 1 with: `RESULT_CODE: UPLOADER_WIN`\n"
        "- On Line 2, write `METHOD_CODE: KO` if it was a KO/TKO/Stoppage/Forfeit, or `METHOD_CODE: DECISION`.\n\n"
        "CRITICAL STEP 2 — GENERATE THE HBO REPORT (starting on Line 3):\n"
        "📊 **OFFICIAL COMPUBOX & SCORECARD RECEIPTS:**\n"
        "• **Matchup & Result:** (Identify true winner, method of victory—KO/TKO/Decision—and stats)\n"
        "• **Total Punches, Jabs, Power Shots & Body Work:** (Summarize key numbers)\n"
        "• **Knockdowns & Stamina:**\n\n"
        "🎙️ **COACH STEWARD'S RINGSIDE VERDICT:**\n"
        "Write 3 gritty sentences of HBO ringside commentary explaining why the true winner took the fight and reminding everyone that numbers don't lie!"
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
                    raw = response.text.strip()
                    v_outcome = None
                    v_ko = False
                    if "RESULT_CODE: UPLOADER_LOSS" in raw:
                        v_outcome = "loss"
                    elif "RESULT_CODE: DRAW" in raw:
                        v_outcome = "draw"
                    elif "RESULT_CODE: UPLOADER_WIN" in raw:
                        v_outcome = "win"
                    if "METHOD_CODE: KO" in raw:
                        v_ko = True
                    cleaned_report = re.sub(r'^(RESULT_CODE:.*|METHOD_CODE:.*)\n?', '', raw, flags=re.MULTILINE).strip()
                    return cleaned_report, v_outcome, v_ko
            except Exception as e:
                print(f"[VISION ERROR]: {e}")
                last_ai_call_time = asyncio.get_event_loop().time()

    fallback_txt = (
        "📊 **OFFICIAL COMPUBOX & SCORECARD RECEIPTS:**\n"
        "• Match screenshot logged in the Mainframe vault!\n\n"
        "🎙️ **COACH STEWARD'S RINGSIDE VERDICT:**\n"
        "The tape doesn't lie, contenders! Peep the attached scorecard screenshot—no excuses in the CGP Mainframe Gym!"
    )
    return fallback_txt, None, False

async def process_and_broadcast_scorecard(message: discord.Message, require_tag: bool = True):
    image_attachments = [
        att for att in message.attachments
        if (att.content_type and "image" in att.content_type)
        or att.filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]
    if not image_attachments:
        return False

    uploader = message.author
    uploader_base = clean_base_name(uploader.display_name)

    other_mentions = [m for m in message.mentions if m.id != bot.user.id and not m.bot and m.id != uploader.id]
    opponent = other_mentions[0] if other_mentions else None

    # 🚨 STRICT RULE: BLOCK SCORECARDS WITHOUT A TAGGED OPPONENT IN #SCORECARD-SUBMISSIONS
    if require_tag and not opponent:
        try:
            await message.add_reaction("❌")
            await message.add_reaction("🛑")
        except Exception:
            pass
        await message.reply(
            f"🛑 **HOLD UP {uploader.mention} — SCORECARD BLOCKED!**\n"
            f"🎙️ **Coach Steward:** I don't log ghost fights on the **CGP Mainframe Gym** board! You uploaded a scorecard **without `@tagging` who you fought**.\n\n"
            f"👉 **How to Fix:** Re-upload your screenshot right here and **`@mention` your opponent** (example: `KO W vs @fighter` or `I lost to @fighter`) so I can verify the matchup, update both `[W-L-D-K]` records, and check the tournament bracket!",
            view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
        )
        return True

    att = image_attachments[0]
    try:
        image_bytes = await att.read()
    except Exception:
        return False

    opponent_base = clean_base_name(opponent.display_name) if opponent else "Opponent"

    status_msg = await message.reply(
        f"🎙️ **Coach Steward:** 📸 **SCANNING SCORECARD & VERIFYING MATCHUP...**\n"
        f"Reading CompuBox numbers for {uploader.mention}" + (f" vs. {opponent.mention}!" if opponent else "!")
    )

    caption_intent = parse_fight_caption_intent(message.content, uploader.id, opponent.id if opponent else None)
    report_text, vision_outcome, vision_ko = await analyze_scorecard_image_with_vision(
        image_bytes=image_bytes,
        mime_type=att.content_type or "image/jpeg",
        uploader_name=uploader_base,
        caption=message.content,
        opponent_name=opponent_base
    )
    if len(report_text) > 3600:
        report_text = report_text[:3600] + "..."

    final_outcome = caption_intent["outcome"] or vision_outcome or "win"
    is_ko = caption_intent["is_ko"] or vision_ko

    if uploader.id not in FIGHTER_RECORDS:
        FIGHTER_RECORDS[uploader.id] = {"name": uploader_base, "wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0, "verified": True}
    FIGHTER_RECORDS[uploader.id]["name"] = uploader_base

    if opponent:
        if opponent.id not in FIGHTER_RECORDS:
            FIGHTER_RECORDS[opponent.id] = {"name": opponent_base, "wins": 0, "losses": 0, "draws": 0, "kos": 0, "golden_tickets": 0, "verified": True}
        FIGHTER_RECORDS[opponent.id]["name"] = opponent_base

    tourney_advanced = False
    tourney_summary = ""

    if final_outcome == "draw":
        FIGHTER_RECORDS[uploader.id]["draws"] = FIGHTER_RECORDS[uploader.id].get("draws", 0) + 1
        FIGHTER_RECORDS[uploader.id]["verified"] = True
        if opponent:
            FIGHTER_RECORDS[opponent.id]["draws"] = FIGHTER_RECORDS[opponent.id].get("draws", 0) + 1
            FIGHTER_RECORDS[opponent.id]["verified"] = True
        winner_member = None
        loser_member = None
    elif final_outcome == "loss" and opponent:
        winner_member = opponent
        loser_member = uploader
    else:
        winner_member = uploader
        loser_member = opponent

    if winner_member:
        w_rec = FIGHTER_RECORDS[winner_member.id]
        w_rec["wins"] = w_rec.get("wins", 0) + 1
        if is_ko:
            w_rec["kos"] = w_rec.get("kos", 0) + 1
        w_rec["verified"] = True

        if loser_member:
            l_rec = FIGHTER_RECORDS[loser_member.id]
            l_rec["losses"] = l_rec.get("losses", 0) + 1
            l_rec["verified"] = True

        # --- STRICT TOURNAMENT BRACKET PROGRESSION CHECK (Requires both winner & loser to match active slot!) ---
        if loser_member:
            tourney_advanced, tourney_summary = advance_tournament_match(
                winner_id=winner_member.id,
                loser_id=loser_member.id,
                is_ko=is_ko
            )

    save_records()

    if tourney_advanced and message.guild:
        await refresh_posted_bracket_card(message.guild)

    try:
        u_d = FIGHTER_RECORDS[uploader.id]
        await uploader.edit(nick=format_record_nick(uploader_base, u_d["wins"], u_d["losses"], u_d.get("draws", 0), u_d.get("kos", 0)))
        if opponent:
            o_d = FIGHTER_RECORDS[opponent.id]
            await opponent.edit(nick=format_record_nick(opponent_base, o_d["wins"], o_d["losses"], o_d.get("draws", 0), o_d.get("kos", 0)))
    except Exception as e:
        print(f"[NICKNAME EDIT ERROR]: {e}")

    corner_ch = get_coaches_corner_channel(message.guild) or message.channel
    bout_badge = "🏆 **OFFICIAL TOURNAMENT BOUT & COMPUBOX REPORT**" if tourney_advanced else "📺 **OFFICIAL MAINFRAME GYM COMPUBOX REPORT**"

    if final_outcome == "draw":
        u_d = FIGHTER_RECORDS[uploader.id]
        o_d = FIGHTER_RECORDS[opponent.id] if opponent else u_d
        result_header = (
            f"🤝 **Result:** OFFICIAL DRAW (`{uploader.mention}` vs `{opponent.mention if opponent else 'Opponent'}`)\n"
            f"📊 **Updated Records:** {uploader.mention} (`[{u_d['wins']}W-{u_d['losses']}L-{u_d['draws']}D-{u_d['kos']}K]`) | "
            + (f"{opponent.mention} (`[{o_d['wins']}W-{o_d['losses']}L-{o_d['draws']}D-{o_d['kos']}K]`)\n" if opponent else "\n")
        )
    else:
        w_d = FIGHTER_RECORDS[winner_member.id]
        l_d = FIGHTER_RECORDS[loser_member.id] if loser_member else None
        method_str = " *(by KO/Stoppage 💥)*" if is_ko else " *(by Decision 📋)*"
        result_header = (
            f"🥊 **Winner:** {winner_member.mention} (`[{w_d['wins']}W-{w_d['losses']}L-{w_d.get('draws',0)}D-{w_d.get('kos',0)}K]`){method_str}\n"
            + (f"🥊 **Opponent:** {loser_member.mention} (`[{l_d['wins']}W-{l_d['losses']}L-{l_d.get('draws',0)}D-{l_d.get('kos',0)}K]`)\n" if loser_member else "")
        )

    embed = discord.Embed(
        title="📺 CGP MAINFRAME GYM: HBO RINGSIDE COMPUBOX & SCORECARD REPORT 📺",
        description=(
            f"{bout_badge}\n"
            f"{result_header}"
            f"📍 **Source:** {message.channel.mention} *(Official Screenshot Receipt Attached)*"
            + (f"\n{tourney_summary}" if tourney_summary else "")
            + f"\n\n{report_text}"
        ),
        color=discord.Color.gold() if tourney_advanced else discord.Color.red(),
        url=MAINFRAME_HUB_URL
    )
    embed.set_image(url=att.url)
    embed.set_footer(text="CGP Mainframe Gym Unified Stat & Tournament Engine • Synced to Vercel Hub!")

    await corner_ch.send(
        content=f"🚨 **OFFICIAL POST-FIGHT COMPUBOX & AUTO-RECORD UPDATE!** Peep the receipts below: 👇",
        embed=embed,
        view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
    )

    if tourney_advanced:
        await corner_ch.send(embed=build_tournament_bracket_embed(), view=TournamentBracketView())

    try:
        await status_msg.edit(
            content=f"🎙️ **Coach Steward:** ✅ **Scorecard verified, unified `[W-L-D-K]` records updated" + (", tournament bracket advanced," if tourney_advanced else " (Open Gym bout — bracket unchanged),") + f" and HBO Report posted in {corner_ch.mention}!**",
            view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
        )
    except Exception:
        pass
    return True

# ================= QUIET-MODE SCHEDULED TASKS & SINGLE-BOOT LOCK =================
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

@tasks.loop(hours=6)
async def periodic_boxing_history():
    await bot.wait_until_ready()
    if periodic_boxing_history.current_loop == 0:
        return  # Skip firing immediately on boot/redeploy!
    for guild in bot.guilds:
        channel = get_elite_feed_channel(guild)
        if channel:
            await channel.send(f"🥊 **CGP Mainframe Gym Ringside History Vault:**\n{get_next_boxing_fact()}")
        break

@tasks.loop(hours=6)
async def periodic_soundcloud_promo():
    await bot.wait_until_ready()
    if periodic_soundcloud_promo.current_loop == 0:
        return  # Skip firing immediately on boot/redeploy!
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

@tasks.loop(hours=4)
async def autonomous_server_hype():
    await bot.wait_until_ready()
    if autonomous_server_hype.current_loop == 0:
        return  # Skip firing immediately on boot/redeploy!
    for guild in bot.guilds:
        channel = get_coaches_corner_channel(guild)
        if channel:
            # Don't talk to himself if Coach Steward already sent the last 2 messages with no human activity
            try:
                last_msgs = [m async for m in channel.history(limit=2)]
                if last_msgs and all(m.author.id == bot.user.id for m in last_msgs):
                    return
            except Exception:
                pass

            if ACTIVE_TOURNAMENT.get("active"):
                spots_left = 8 - len(ACTIVE_TOURNAMENT.get("entrants", []))
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
    global has_booted
    if has_booted:
        return  # Prevent duplicate boot messages when Discord gateway reconnects
    has_booted = True

    print(f"[✓] {bot.user.name} (24/7 CGP Mainframe Gym Master Engine) is ONLINE!")
    await fetch_state_from_github_if_needed()
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
        await refresh_posted_bracket_card(guild)
        corner_ch = get_coaches_corner_channel(guild)
        if corner_ch:
            should_announce = True
            try:
                async for m in corner_ch.history(limit=3):
                    if m.author.id == bot.user.id:
                        age_sec = (datetime.datetime.now(datetime.timezone.utc) - m.created_at).total_seconds()
                        if age_sec < 900:
                            should_announce = False
                            break
            except Exception:
                pass
            if should_announce:
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
            f"Your file is still locked in the Mainframe at **`{w}W - {l}L - {d}D - {k}K`**. Keep the chat clean, upload your scorecards in `#scorecard-submissions`, and get to work!"
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
            "🎙️ *'Strap up your gloves! You've been added to the CGP Mainframe Gym Leaderboard at **0W - 0L - 0D - 0K**. Upload your match scorecards in `#scorecard-submissions` with an `@opponent` tag to build your verified record, and jump into our 8-Man Tournaments!'*\n\n"
            f"🔗 Check out the live leaderboard & ESPN tournament hub: {MAINFRAME_HUB_URL}"
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
    if member.id in ACTIVE_TOURNAMENT.get("entrants", []) and ACTIVE_TOURNAMENT.get("status") == "registration":
        ACTIVE_TOURNAMENT["entrants"].remove(member.id)
        save_records()
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

    # ================= TOP PRIORITY: PROCESS COMMANDS FIRST =================
    if message.content.startswith("!") or message.content.startswith("/"):
        if message.content.startswith("/"):
            message.content = "!" + message.content[1:]
        await bot.process_commands(message)
        return

    msg = message.content.lower()
    words_list = re.findall(r'\b\w+\b', msg)
    is_creator = (message.author.id == CREATOR_ID) or message.author.guild_permissions.administrator
    other_mentions = [m for m in message.mentions if m.id != bot.user.id and not m.bot]

    # ================= TOP PRIORITY: NATURAL LANGUAGE COMMISSIONER BRACKET FIX & FIGHTER SWAP =================
    if is_creator and (bot.user in message.mentions or "coach" in msg or "override" in msg or "rollback" in msg):
        if any(w in msg for w in ["swap", "replace", "sub in", "substitute"]) and len(other_mentions) >= 2:
            answered_messages.add(message.id)
            old_f, new_f = other_mentions[0], other_mentions[1]
            ok, note = swap_fighter_in_tournament(old_f.id, new_f.id, clean_base_name(new_f.display_name))
            await refresh_posted_bracket_card(message.guild)
            await message.reply(
                content=f"🎙️ **Coach Steward:** {note}",
                embed=build_tournament_bracket_embed(),
                view=TournamentBracketView()
            )
            return

        if any(w in msg for w in ["rollback", "nullify", "reset slot", "fix tourney", "fix the tourney", "fix bracket", "clear the false", "undo"]):
            answered_messages.add(message.id)
            slot_match = re.search(r'\b(qf1|qf2|qf3|qf4|sf1|sf2|f1)\b', msg, re.IGNORECASE)
            slot_to_fix = slot_match.group(1).upper() if slot_match else "QF2"
            note = rollback_bracket_slot(slot_to_fix)
            await refresh_posted_bracket_card(message.guild)
            await message.reply(
                content=f"🎙️ **Coach Steward:** Got you, Boss! {note}\nSynced straight to `stats.json` and the Vercel ESPN Hub!",
                embed=build_tournament_bracket_embed(),
                view=TournamentBracketView()
            )
            return

    # ================= TOP PRIORITY: ADMIN NATURAL LANGUAGE RECORD UPDATER =================
    if is_creator and any(w in msg for w in ["make", "set", "reflect", "update", "change", "put", "give", "record"]):
        text_without_bot = re.sub(rf'<@!?{bot.user.id}>', '', message.content)
        pattern = r'<@!?(\d+)>[^0-9<>]*?(\d{1,3})\s*(?:[-–to/]+|\s+)\s*(\d{1,3})(?:\s*(?:[-–to/]+|\s+)\s*(\d{1,3}))?(?:\s*(?:[-–to/]+|\s+)\s*(\d{1,3}))?'
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
                f"🎙️ **Coach Steward:** Locked in the official Commissioner updates and synced their nicknames & Vercel leaderboard:\n\n{summary_str}",
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

    log_channel_message(message.channel.id, message.author.display_name, message.content)

    is_mentioned = bot.user in message.mentions
    is_reply_to_bot = message.reference and message.reference.resolved and message.reference.resolved.author == bot.user

    # --- 0.5 AUTOMATIC SCORECARD UPLOAD DETECTOR & STRICT TAG GUARD ---
    if "scorecard" in message.channel.name.lower() and message.attachments:
        answered_messages.add(message.id)
        await process_and_broadcast_scorecard(message, require_tag=True)
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

            global ACTIVE_TOURNAMENT
            ACTIVE_TOURNAMENT = get_default_tournament_state()
            ACTIVE_TOURNAMENT["active"] = True
            ACTIVE_TOURNAMENT["tier"] = tier
            ACTIVE_TOURNAMENT["title"] = default_title

            target_ch = get_coaches_corner_channel(message.guild) or message.channel
            embed = build_tournament_bracket_embed()
            sent = await target_ch.send(
                content="@everyone 🚨 **OFFICIAL CGP MAINFRAME GYM 8-MAN TOURNAMENT SIGN-UPS ARE NOW LIVE! CLICK BELOW TO LOCK IN YOUR SEED:** 👇",
                embed=embed,
                view=TournamentBracketView()
            )
            ACTIVE_TOURNAMENT["channel_id"] = target_ch.id
            ACTIVE_TOURNAMENT["message_id"] = sent.id
            save_records()
            if target_ch.id != message.channel.id:
                await message.reply(f"🎙️ **Coach Steward:** Done, Boss! Opened and saved the **8-Man Interactive Bracket ({tier.upper()})** inside {target_ch.mention}!")
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

    # --- 5. AUTOMATIC MATCH RESULT, DRAW & KO CHAT TRACKER ---
    ko_keywords = ["knocked out", "ko'd", "kod", "stopped", "slept", "beat", "defeated", "won against", "fought to a draw", "split draw", "majority draw"]
    if any(kw in msg for kw in ko_keywords) and other_mentions and not is_mentioned:
        target_other = other_mentions[0]
        if target_other.id != message.author.id:
            answered_messages.add(message.id)
            intent = parse_fight_caption_intent(message.content)
            if intent["outcome"] == "draw":
                outcome_str = f"a **DRAW** between {message.author.mention} and {target_other.mention} 🤝"
            elif intent["outcome"] == "loss":
                outcome_str = f"a victory for {target_other.mention} over {message.author.mention} 📋"
            elif intent["is_ko"]:
                outcome_str = f"a **KNOCKOUT** victory for {message.author.mention} over {target_other.mention} 💥"
            else:
                outcome_str = f"a victory for {message.author.mention} over {target_other.mention} on the scorecards 📋"
            await message.reply(
                f"🎙️ **Coach Steward:** Ring the bell! Hearing reports of {outcome_str}!\n"
                f"📸 **Remember:** Upload your match scorecard in `#scorecard-submissions` and `@tag` your opponent so I can scan the CompuBox numbers, update your unified `[W-L-D-K]` record, and advance active tournament brackets!",
                view=PromoButtons(DEFAULT_SOUNDCLOUD_URL)
            )
            return

    # --- 6. DIRECT TAG OR REPLY TO COACH STEWARD ---
    if is_mentioned or is_reply_to_bot:
        answered_messages.add(message.id)
        clean_prompt = message.content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()

        if message.attachments:
            handled = await process_and_broadcast_scorecard(message, require_tag=True)
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
            if ACTIVE_TOURNAMENT.get("active") or ACTIVE_TOURNAMENT.get("entrants"):
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
                    f"📸 **Scorecard Verification Rule:** Upload your post-fight scorecard in `#scorecard-submissions` and **`@tag` your opponent** — Coach Steward will auto-update unified records, advance active tournament brackets, and broadcast an HBO CompuBox Report!\n"
                    f"🔗 {MAINFRAME_HUB_URL}"
                ),
                color=discord.Color.gold()
            )
            await message.reply(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
            return

        insult_words_set = {"trash", "garbage", "suck", "sucks", "ass", "clown", "bitch", "hoe", "stfu", "fuck", "fck", "weak", "wack", "fake", "rigged", "scam", "loser", "bum"}
        if not is_creator and (set(words_list) & insult_words_set):
            track = random.choice(CGP_TRACKS)
            await issue_corner_strike(
                member=message.author,
                channel=message.channel,
                reason="Disrespecting the CGP Mainframe Gym / Acting out in chat",
                custom_warning_line=get_next_clapback(),
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
                f"THEIR EXACT MESSAGE (may contain typos, slang, or shorthand—interpret their true intent charitably!): \"{clean_prompt}\"\n\n"
                "INSTRUCTIONS FOR YOUR REPLY:\n"
                "1. Respond directly and specifically to what they meant, even if their spelling or grammar is messy!\n"
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
                custom_warning_line=get_next_clapback(),
                reply_to=message,
                view=PromoButtons(track["url"])
            )
        else:
            await message.reply(get_next_clapback(), view=PromoButtons(track["url"]))
        return

    if any(phrase in msg for phrase in ["how are you coach", "what's up coach", "whats up coach", "yo coach", "gm coach", "good morning coach"]):
        answered_messages.add(message.id)
        track = random.choice(CGP_TRACKS)
        await message.reply(get_next_small_talk(), view=PromoButtons(track["url"]))
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
                f"📸 **Scorecards:** Upload match proof in `#scorecard-submissions` with an `@opponent` tag so I can auto-update unified records, advance tournament brackets, and post an HBO report!\n"
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

    # Quieter Organic Chat Chime (25-minute cooldown & 12% chance)
    boxing_chat_triggers = {"mindset", "stamina", "footwork", "jab", "counter", "hook", "uppercut", "undisputed", "round", "rounds", "combo", "ring", "training", "belt", "champion", "heavyweight", "welterweight", "spar", "scorecard"}
    now_t = asyncio.get_event_loop().time()
    if (set(words_list) & boxing_chat_triggers) and len(words_list) >= 6 and (now_t - last_organic_chime > 1500):
        if random.random() < 0.12:
            last_organic_chime = now_t
            answered_messages.add(message.id)
            await message.reply(get_next_organic_interjection())
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
            "🥊 **Want a Golden Ticket ($20 Entry Credit), $160 Pay-to-Play Gauntlet, or Title Shot?** Upload your match scorecards in `#scorecard-submissions` with an `@opponent` tag, and watch `#coaches-corner` for the next official 8-man fight card!"
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

    desc += f"\n🎧 *Tap below to view the full live ESPN-style Vercel leaderboard & stream Clone Geek Productions!*"
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
        "Run these plays up so we cash out and take CGP global:\n\n"
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
    global ACTIVE_TOURNAMENT
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

    ACTIVE_TOURNAMENT = get_default_tournament_state()
    ACTIVE_TOURNAMENT["active"] = True
    ACTIVE_TOURNAMENT["tier"] = tier
    ACTIVE_TOURNAMENT["title"] = final_title

    target_ch = get_coaches_corner_channel(ctx.guild) or ctx.channel
    embed = build_tournament_bracket_embed()
    sent = await target_ch.send(
        content="@everyone 🚨 **OFFICIAL CGP MAINFRAME GYM 8-MAN TOURNAMENT SIGN-UPS ARE NOW LIVE! CLICK BELOW TO LOCK IN YOUR SEED:** 👇",
        embed=embed,
        view=TournamentBracketView()
    )
    ACTIVE_TOURNAMENT["channel_id"] = target_ch.id
    ACTIVE_TOURNAMENT["message_id"] = sent.id
    save_records()
    if target_ch.id != ctx.channel.id:
        await ctx.send(f"✅ **Interactive `8`-Fighter Bracket ({tier.upper()}) Launched & Saved to `stats.json`** inside {target_ch.mention}!")

@bot.command(aliases=["bracket", "tourneyroster", "signups"])
async def bracketstatus(ctx):
    if not ACTIVE_TOURNAMENT.get("active") and not ACTIVE_TOURNAMENT.get("entrants") and not ACTIVE_TOURNAMENT.get("champion"):
        return await ctx.send(
            "🎙️ **Coach Steward:** No 8-man interactive tournament bracket is currently open! "
            "**Commissioner Clone Geek** can launch one anytime with:\n"
            "• `!openbracket pay2play Heavyweight Gauntlet`\n"
            "• `!openbracket goldenticket Middleweight Qualifier`\n"
            "• `!openbracket open Sunday Spar Wars`"
        )
    embed = build_tournament_bracket_embed()
    await ctx.send(embed=embed, view=TournamentBracketView())

@bot.command(aliases=["advancewinner", "winbracket"])
@commands.has_permissions(administrator=True)
async def advance(ctx, winner: discord.Member, loser: discord.Member = None):
    if not ACTIVE_TOURNAMENT.get("active"):
        return await ctx.send("❌ No active tournament bracket is currently running!")
    if len(ACTIVE_TOURNAMENT.get("entrants", [])) == 8 and ACTIVE_TOURNAMENT.get("status") == "registration":
        initialize_bracket_matchups()

    advanced, summary = advance_tournament_match(
        winner_id=winner.id,
        loser_id=loser.id if loser else None,
        is_ko=False,
        allow_single_admin_override=True
    )
    if not advanced:
        return await ctx.send(
            f"⚠️ Could not find an active undecided bracket matchup for {winner.mention}. "
            f"Check `!bracketstatus` to verify all 8 seeds are locked in!"
        )
    await refresh_posted_bracket_card(ctx.guild)
    await ctx.send(
        content=f"🎙️ **Coach Steward:** Commissioner manual bracket advancement locked in!{summary}",
        embed=build_tournament_bracket_embed(),
        view=TournamentBracketView()
    )

@bot.command(aliases=["fixbracket", "rollback", "override", "resetmatch"])
@commands.has_permissions(administrator=True)
async def fixtourney(ctx, slot: str = "QF2", fighter1: discord.Member = None, fighter2: discord.Member = None):
    """
    Rolls back a false tournament advancement on any slot (default QF2 for the Turbo/Hymas fix)
    and cascades the reset through SF1/SF2/F1.
    Usage:
      !fixtourney
      !fixtourney QF2
      !fixtourney QF2 @TURBO @Hymas
    """
    note = rollback_bracket_slot(
        slot_key=slot,
        new_p1=fighter1.id if fighter1 else None,
        new_p2=fighter2.id if fighter2 else None
    )
    await refresh_posted_bracket_card(ctx.guild)
    await ctx.send(
        content=f"🎙️ **Coach Steward:** {note}\nSynced updated bracket to `stats.json` and the Vercel ESPN Hub!",
        embed=build_tournament_bracket_embed(),
        view=TournamentBracketView()
    )

@bot.command(aliases=["sub", "replacefighter", "swapfighter"])
@commands.has_permissions(administrator=True)
async def swap(ctx, inactive_fighter: discord.Member = None, replacement_fighter: discord.Member = None):
    """
    Swaps an unresponsive fighter out of their live tournament seed & match slot and puts the replacement in.
    Usage: !swap @UnresponsiveFighter @ReplacementFighter
    """
    if not inactive_fighter or not replacement_fighter:
        return await ctx.send("⚠️ **Usage:** `!swap @InactiveFighter @ReplacementFighter`")
    ok, note = swap_fighter_in_tournament(
        old_uid=inactive_fighter.id,
        new_uid=replacement_fighter.id,
        new_base_name=clean_base_name(replacement_fighter.display_name)
    )
    await refresh_posted_bracket_card(ctx.guild)
    await ctx.send(
        content=f"🎙️ **Coach Steward:** {note}",
        embed=build_tournament_bracket_embed(),
        view=TournamentBracketView()
    )

@bot.command(aliases=["clearbracket", "endbracket"])
@commands.has_permissions(administrator=True)
async def closebracket(ctx):
    global ACTIVE_TOURNAMENT
    ACTIVE_TOURNAMENT = get_default_tournament_state()
    save_records()
    await ctx.send("🔒 **Coach Steward:** Official 8-man tournament bracket registration has been closed and cleared from `stats.json`, Boss!")

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
    await ctx.send("⏳ **Coach Steward:** Connecting to GitHub to update `index.html` with the ESPN-style Live Tournament Wire & CGP Mainframe Gym branding...")
    success = await rebrand_webpage_on_github()
    if success:
        await ctx.send(f"✅ **Webpage Upgraded!** Pushed the ESPN Tournament Wire & **CGP Mainframe Gym** `index.html` straight to GitHub & Vercel (`{MAINFRAME_HUB_URL}`)!")
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
        return await ctx.send("❌ Usage: `!record <wins> <losses> [draws] [kos]` (example: `!record 5 1 1 3`) — or use `!verify @fighter <W> <L> <D> <KO>` if you're the Commissioner!")
    if wins > 50 and ctx.author.id != CREATOR_ID:
        return await ctx.send("🎙️ **Coach Steward:** Whoa, slow down champ! Submit your scorecard in `#scorecard-submissions` first!")

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
            f"📸 **Next Step:** Make sure your scorecard screenshot is uploaded in `#scorecard-submissions` with an `@opponent` tag so **Commissioner Clone Geek** can stamp it with `!verify {ctx.author.mention}`!"
        )

@bot.command(aliases=["fixrecord", "setrecord"])
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

    await process_and_broadcast_scorecard(target_msg, require_tag=False)

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
        status = "✅ Official & Verified Scorecard" if data.get("verified") else "⏳ Pending Scorecard Verification in #scorecard-submissions"
        embed = discord.Embed(
            title="🏆 OFFICIAL CGP MAINFRAME GYM FIGHTER FILE 🏆",
            description=(
                f"**Fighter:** {target.mention}\n"
                f"**Unified Record:** **`[{data['wins']}W-{data['losses']}L-{draws}D-{kos}K]`**\n"
                f"**Golden Tickets ($20 Credits):** 🎫 `{gt}`\n"
                f"**Status:** {status}"
            ),
            color=discord.Color.gold(),
            url=MAINFRAME_HUB_URL
        )
        await ctx.send(embed=embed, view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))
    else:
        await ctx.send(f"❌ No record found for {target.display_name}. Upload a scorecard in `#scorecard-submissions` with an `@opponent` tag!")

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
            f"📸 **Scorecards:** Upload all post-fight scorecards with `@opponent` to `#scorecard-submissions`!\n"
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
    await ctx.send(f"🥊 **CGP Mainframe Gym Protocol:** Riyadh Indoor Gym | 8-Man Brackets | 8/12 Rounds | 1.5x Speed | Strict Ref | Upload all scorecards to `#scorecard-submissions` with an `@opponent` tag!\n🔗 {MAINFRAME_HUB_URL}", view=PromoButtons(DEFAULT_SOUNDCLOUD_URL))

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