
import discord
from discord.ext import commands, tasks
import os
import random
import asyncio  

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

WELCOME_CHANNEL_ID = 1377854642146512979
GOODBYE_CHANNEL_ID = 1377864337481535508
STATIC_CHANNEL_ID = 1381133461758410823
REACTION_ROLE_MESSAGES = []

REACTION_ROLE_SECTIONS = [
    {
        "description": "PRONOUNS:",
        "roles": {
            "1️⃣": (1379207563744252055, "1️⃣ She/Her"),
            "2️⃣": (1379207622590201947, "2️⃣ He/Him"),
            "3️⃣": (1379207671202451497, "3️⃣ They/Them"),
            "4️⃣": (1379207704953753621, "4️⃣ It/Its"),
            "5️⃣": (1379207731327537223, "5️⃣ Any/All"),
            "6️⃣": (1379207767235104920, "6️⃣ Ask"),
        }
    },
    {
        "description": "AGE:",
        "roles": {
            "🔽": (1379463817259384904, "🔽 16+"),
            "🔼": (1379463866077020160, "🔼 18+"),
        }
    },
    {
        "description": "DM AND PING STATUS:",
        "roles": {
            "⏮️": (1378406719058874378, "⏮️ Do Not Ping"),
            "⏭️": (1378406657360662579, "⏭️ Pings OK"),
            "❌": (1378406591996366899, "❌ DMs Closed"),
            "⭕": (1378406509142216764, "⭕ Open DMs"),
            "⛔": (1378406437742710784, "⛔ Ask To DM"),
        }
    }
]

FREQUENCY_CODES = [
    "4912-03-77", "8301-12-65", "1279-56-84", "6203-88-91", "5409-22-11",
    "3392-47-23", "1056-78-55", "7742-19-90", "9183-31-42", "4632-14-36",
    "2180-97-62", "5721-44-19", "8024-33-78", "6549-27-40", "3901-66-12",
    "1178-55-29", "9203-80-04", "3059-42-75", "4810-17-63", "7291-39-50",
    "6682-05-98", "1374-61-20", "8543-18-79", "3910-49-26", "5607-82-41",
    "2483-36-94", "7031-20-87", "4948-13-35", "8210-64-09", "1759-07-32"
]

GOODBYE_VARIANTS = [
    {"last_seen": "Signal terminated mid-transmission", "notes": "Encryption failed. Contents unrecoverable."},
    {"last_seen": "Emergency airlock access triggered", "notes": "We warned them not to open that door."},
    {"last_seen": "Final ping from quarantine zone", "notes": "Exposure protocol enacted too late."},
    {"last_seen": "Security override near the cryo bay", "notes": "Left without triggering thaw sequence."},
    {"last_seen": "Near the experimental core housing", "notes": "Exposure time exceeded safe limits."},
    {"last_seen": "Trail vanished by the reactor vents", "notes": "Nobody volunteers for that route."},
    {"last_seen": "Corridor 13B — off-limits for a reason", "notes": "We really need to start locking doors."},
    {"last_seen": "Purging personal records", "notes": "Who would go looking?"},
    {"last_seen": "Exploding.", "notes": "Thanks for the mess."}
]

def format_blockquote_code(text: str) -> str:
    lines = text.splitlines()
    formatted_lines = [f"> `{line}`" if line.strip() != "" else ">" for line in lines]
    return "\n".join(formatted_lines)

@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    send_static_message.start()

@bot.command()
@commands.has_permissions(administrator=True)
async def setup_reactions(ctx):
    global REACTION_ROLE_MESSAGES
    REACTION_ROLE_MESSAGES.clear()

    for section in REACTION_ROLE_SECTIONS:
        embed = discord.Embed(
            title="SELECT YOUR ROLES",
            description=section["description"],
            color=discord.Color.blue()
        )
        for label in section["roles"].values():
            embed.add_field(name=label[1], value="\u200b", inline=False)

        msg = await ctx.send(embed=embed)
        REACTION_ROLE_MESSAGES.append(msg.id)

        for emoji in section["roles"]:
            await msg.add_reaction(emoji)

@bot.event
async def on_raw_reaction_add(payload):
    if payload.message_id not in REACTION_ROLE_MESSAGES:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member:
        return

    for section in REACTION_ROLE_SECTIONS:
        role_data = section["roles"].get(str(payload.emoji))
        if role_data:
            role_id = role_data[0]
            role = guild.get_role(role_id)
            if role:
                await member.add_roles(role)
                break

@bot.event
async def on_raw_reaction_remove(payload):
    if payload.message_id not in REACTION_ROLE_MESSAGES:
        return

    guild = bot.get_guild(payload.guild_id)
    if not guild:
        return

    member = guild.get_member(payload.user_id)
    if not member:
        return

    for section in REACTION_ROLE_SECTIONS:
        role_data = section["roles"].get(str(payload.emoji))
        if role_data:
            role_id = role_data[0]
            role = guild.get_role(role_id)
            if role:
                await member.remove_roles(role)
                break

async def send_goodbye_message(member):
    channel = bot.get_channel(GOODBYE_CHANNEL_ID)
    if channel:
        variant = random.choice(GOODBYE_VARIANTS)
        embed = discord.Embed(
            title=f"DEPARTURE: {member.display_name or member.name}",
            description=(
                f"**STATUS:** Lost Signal\n"
                f"**LAST SEEN:** {variant['last_seen']}\n\n"
                f"**NOTES:** {variant['notes']}"
            ),
            color=discord.Color.dark_gray()
        )
        await channel.send(embed=embed)

async def send_welcome_message(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        freq_code = random.choice(FREQUENCY_CODES)
        embed = discord.Embed(
            title="REPORT:",
            description=(
                "**STATUS:** New Signal Detected\n"
                "**LOADING. . .**\n\n"
                f"**IDENTIFIED CONTACT:**\n{member.mention}\n\n"
                f"**FREQUENCY CODE**: {freq_code}\n"
                "**NOTES:** Read the handbook, friend"
            ),
            color=discord.Color.red()
        )
        await channel.send(embed=embed)

@tasks.loop(minutes=25)
async def send_static_message():
    channel = bot.get_channel(STATIC_CHANNEL_ID)
    if not channel:
        return

    static_message = "STATIC . . ."

    rare_messages = [
        "SIGNAL . . . NOISE",
        "IDLE. . .",
        "BROADCAST LINK LOST. ATTEMPTING TO RECOVER. . .",
        "UNIDENTIFIED FREQUENCY DETECTED",
        "ERROR 504 — SIGNAL TIMEOUT. REBOOTING. . .",
        "CARRIER WAVE ONLY",
    ]

    super_rare_intro_message = "FOREIGN SIGNAL FOUND"

    super_rare_morse_messages = [
        ".... / ..- / -. / --. .-. / -.-- -.-- -.--",
        "... --- ...",
        "... - ..- -.-. -.-",
        ".... . .-.. .--. / -- .",
        ".. / -.-. .- -. / .... . .- .-. / .. - / -... .-. . .- - .... .. -. --.",
        ".--. .-.. . .- ... .",
        ".-.. / --- / --- / -.- / ..- .--. .--. .--.",
    ]

    roll = random.randint(1, 250) 

    if roll == 1:
        intro = format_blockquote_code(super_rare_intro_message)
        await channel.send(intro)
        await asyncio.sleep(random.uniform(1.0, 2.0))
        morse = random.choice(super_rare_morse_messages)
        morse_formatted = format_blockquote_code(morse)
        await channel.send(morse_formatted)

    elif roll <= 15:
        message = random.choice(rare_messages)
        formatted_message = format_blockquote_code(message)
        await channel.send(formatted_message)

    else:
        formatted_message = format_blockquote_code(static_message)
        await channel.send(formatted_message)

@bot.event
async def on_member_join(member):
    await send_welcome_message(member)

@bot.event
async def on_member_remove(member):
    await send_goodbye_message(member)

@bot.command()
async def testjoin(ctx):
    await send_welcome_message(ctx.author)

@bot.command()
async def testleave(ctx):
    await send_goodbye_message(ctx.author)

bot.run(os.getenv("DISCORD_TOKEN"))
