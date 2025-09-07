"""
THIS IS THE MAIN ENTRY POINT FOR THE DISCORD TICKET BOT.
HERE, ALL CORE FUNCTIONS, EVENTS, COMMANDS, AND LOGIC ARE DEFINED AND ORCHESTRATED.
THE BOT MANAGES A TICKETING SYSTEM FOR DISCORD SERVERS, INCLUDING LOGGING, DATABASE OPERATIONS, AND CUSTOM COMMANDS FOR STAFF AND USERS.
THIS FILE IS RESPONSIBLE FOR INITIALIZING THE BOT, SETTING UP LOGGING, HANDLING DISCORD EVENTS, AND REGISTERING ALL TICKET-RELATED COMMANDS.
"""

import discord # We use the discord library for commands and bot features
import logging # We use the logging library to create bot logs during runtime
import os # We use the os library for checks and filesystem operations
import random # Used to pick a random string from the list in change_activity()
import aiohttp # Asynchronous HTTP client/server for asyncio and Python
import sqlite3 # We use sqlite3 to create/manage the database and its tables/columns/rows

from config import TOKEN, bot_user_avatar_url, bot_user_name # Import configuration values from config.py
from classes import * # Import classes, views and modals from classes.py
from datetime import datetime # Used to get the current date/time
from colorama import Fore, init, Style # We use colorama to colorize terminal output
from discord import app_commands, ui # 'ui' for components; 'app_commands' for slash commands
from discord.ext import commands, tasks # Import commands and background tasks utilities

init() # Initialize colorama
os.makedirs("logs", exist_ok=True) # Create the 'logs' folder if it does not already exist
"""
HERE WE CONFIGURE LOGGING. THE 'level' PARAMETER IS SET TO 'logging.INFO' TO STORE
BASIC INFORMATION. FOR MORE VERBOSE OUTPUT, USE 'logging.DEBUG'. THE 'filename'
PARAMETER SPECIFIES THE OUTPUT LOG FILE PATH.
"""
logging.basicConfig(level=logging.INFO, filename="logs/bot.log") 
"""
HERE WE CREATE THE 'bot' INSTANCE, WHICH IS ESSENTIAL TO RUN THE BOT AND EXECUTE
COMMANDS. IF YOU WANT TO CHANGE THE COMMAND PREFIX, COMMON CHOICES ARE: !, ?, .
IT IS RECOMMENDED NOT TO CHANGE 'intents'. IF YOU NEED TO, READ:
https://discordpy.readthedocs.io/en/stable/intents.html
"""
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.remove_command("help") # Remove Discord.py's default help command

"""
WE CREATE A BACKGROUND TASK (RUNS EVERY 3 SECONDS) THAT CHANGES THE BOT'S PRESENCE
BY RANDOMLY PICKING A STRING FROM THE 'activities' LIST.
FIRST WE GET THE GUILD WITH 'bot.get_guild'. YOU MUST INSERT YOUR SERVER ID.
IF THE GUILD IS NOT FOUND (NONE), WE EXIT EARLY.

IN 'activities' YOU CAN ADD ANY STRINGS YOU WANT.
"""
@tasks.loop(seconds=3) 
async def change_activity():
    """
    BACKGROUND TASK THAT UPDATES THE BOT'S PRESENCE EVERY 3 SECONDS.
    
    RANDOMLY SELECTS A STRING FROM THE 'ACTIVITIES' LIST AND SETS IT AS THE BOT'S CURRENT ACTIVITY (STATUS MESSAGE).
    THIS HELPS KEEP THE BOT'S PRESENCE DYNAMIC AND CAN BE USED FOR ANNOUNCEMENTS OR CREDITS.
    IF THE BOT IS NOT CONNECTED TO A GUILD, THE FUNCTION EXITS EARLY.
    HANDLES CONNECTION RESET ERRORS GRACEFULLY TO AVOID CRASHING THE TASK.
    
    SIDE EFFECTS:
        CHANGES THE BOT'S DISCORD PRESENCE.
    """
    guild = bot.get_guild()
    if guild is None:
        return
    
    activities = [
        "Developed by importsyss",
        "Test"
    ]
    
    try:
        await bot.change_presence(activity=discord.Game(random.choice(activities)))
    except aiohttp.client_exceptions.ClientConnectionResetError:
        pass


"""
THE on_ready EVENT FIRES WHEN THE BOT STARTS.
WE SYNC ALL COMMANDS AND PRINT SOME INFORMATION ABOUT THE BOT AND GUILD.
"""    
@bot.event
async def on_ready():
    """
    EVENT HANDLER THAT IS CALLED WHEN THE BOT HAS SUCCESSFULLY CONNECTED TO DISCORD AND IS READY.
    
    SYNCHRONIZES ALL SLASH COMMANDS WITH DISCORD, STARTS THE BACKGROUND ACTIVITY TASK, AND PRINTS DETAILED INFORMATION ABOUT THE BOT,
    THE SERVER, AND THE CURRENT SESSION TO THE CONSOLE. THIS INCLUDES BOT NAME, ID, SERVER NAME, SERVER ID, LATENCY, AND MORE.
    IF THE GUILD IS NOT FOUND, PRINTS AN ERROR AND EXITS EARLY.
    
    SIDE EFFECTS:
        STARTS BACKGROUND TASKS, PRINTS TO CONSOLE, AND SYNCS COMMANDS.
    """
    comandisincronizzati = await bot.tree.sync()
    guild = bot.get_guild()
    change_activity.start()

    if guild is None:
       print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Unable to find the guild with ID 'Insert the ID'")
       return
    
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}New start!{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Start File Name:{Style.RESET_ALL} {Fore.CYAN}main.py{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Start File Path{Style.RESET_ALL} {Fore.CYAN}{os.path.abspath('src/main.py')}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Bot Name:{Style.RESET_ALL} {Fore.CYAN}{bot.user.name} ({bot_user_name}){Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Bot ID:{Style.RESET_ALL} {Fore.CYAN}{bot.user.id}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Server Name:{Style.RESET_ALL} {Fore.CYAN}{guild.name}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Server ID:{Style.RESET_ALL} {Fore.CYAN}{guild.id}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Ping:{Style.RESET_ALL} {Fore.CYAN}{bot.latency * 1000:.2f}ms{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Synchronized commands:{Style.RESET_ALL} {Fore.CYAN}{len(comandisincronizzati)}{Style.RESET_ALL}")
    print(f"{Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.LIGHTMAGENTA_EX}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}[{Style.RESET_ALL}{Fore.GREEN}INFO{Style.RESET_ALL}{Fore.LIGHTBLACK_EX}]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}Start Date:{Style.RESET_ALL} {Fore.CYAN}{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{Style.RESET_ALL}")
    
@bot.event
async def on_guild_channel_delete(channel):
    """
    EVENT HANDLER TRIGGERED WHEN A CHANNEL IS DELETED IN THE SERVER.
    
    CHECKS IF THE DELETED CHANNEL WAS AN OPEN TICKET BY QUERYING THE DATABASE. IF SO, REMOVES THE TICKET ENTRY FROM THE DATABASE.
    THIS ENSURES THAT ORPHANED TICKET RECORDS DO NOT REMAIN AFTER A CHANNEL IS DELETED.
    HANDLES THE CASE WHERE THE CHANNEL IS NOT A TICKET OR ALREADY CLOSED.
    
    ARGS:
        CHANNEL: THE DISCORD CHANNEL OBJECT THAT WAS DELETED.
    
    SIDE EFFECTS:
        MODIFIES THE DATABASE BY DELETING TICKET RECORDS.
    """
    conn = sqlite3.connect("data/database/ticket.db")
    c = conn.cursor()
    c.execute("""SELECT * FROM ticket WHERE ticketid = ? AND statusticket = 'open'""", (channel.id,))
    result = c.fetchone()
    
    if result is not None:
        c.execute("""DELETE FROM 'ticket' WHERE ticketid = ? AND statusticket = 'open'""", 
                  (channel.id,))
        conn.commit()
        conn.close()
        
    else:
        conn.close()
        return

@bot.event
async def on_member_remove(member):
    """
    EVENT HANDLER TRIGGERED WHEN A MEMBER LEAVES THE SERVER.
    
    CHECKS IF THE DEPARTING MEMBER HAS ANY OPEN TICKETS. IF SO, NOTIFIES THE STAFF IN THE TICKET CHANNEL AND ADDS A CLOSE BUTTON FOR STAFF TO CLOSE THE TICKET.
    HANDLES THE CASE WHERE THE TICKET CHANNEL NO LONGER EXISTS OR THE MEMBER HAS NO OPEN TICKETS.
    
    ARGS:
        MEMBER: THE DISCORD MEMBER OBJECT WHO LEFT THE SERVER.
    
    SIDE EFFECTS:
        SENDS MESSAGES TO TICKET CHANNELS, UPDATES THE UI FOR STAFF.
    """
    guild = bot.get_guild() 
    if guild is None:
        return
    
    conn = sqlite3.connect("data/database/ticket.db")
    c = conn.cursor()
    c.execute("""SELECT * FROM ticket WHERE openername = ? AND openerid = ? AND statusticket = 'open'""", (member.name, member.id))
    result = c.fetchone()
    
    if result is not None:
        channel = bot.get_channel(result[2])
        role = guild.get_role()
        
        if channel is None:
            conn.close()
            return
        
        emb = discord.Embed(description=f"### {member.name} - HA LASCIATO IL SERVER\n> Il membro **{member.name}** ha lasciato il server, ora questo ticket può essere chiuso in qualsiasi momento, usa il pulsante qui sotto per chiudere il ticket.", color=discord.Color.from_rgb(10, 10, 10))
        emb.set_footer(text=bot_user_name, icon_url=bot_user_avatar_url)
        emb.set_thumbnail(url=bot_user_avatar_url)
        
        opening_time = channel.created_at.strftime("%d/%m/%Y %H:%M:%S")
        ticket_owner = result[5]
        view = ui.View(timeout=None)
        view.add_item(CloseTicketButton(ticket_owner, opening_time))
        
        await channel.send(f"{role.mention}", embed=emb, view=view)
        
    else:
        conn.close()
        return

@bot.tree.command(name="ticket-setup", description="Send the ticket setup embed")
@commands.guild_only()
async def dropdown(interaction: discord.Interaction):
    """
    SLASH COMMAND TO SEND THE TICKET SYSTEM SETUP EMBED IN A DESIGNATED CHANNEL.
    
    ONLY USERS WITH AUTHORIZED ROLES CAN USE THIS COMMAND. SENDS AN EMBED WITH INSTRUCTIONS AND A DROPDOWN MENU FOR USERS TO OPEN NEW TICKETS.
    NOTIFIES THE USER IF THE CHANNEL OR REQUIRED ROLES ARE MISSING.
    
    ARGS:
        INTERACTION: THE DISCORD INTERACTION OBJECT FOR THE COMMAND INVOCATION.
    
    SIDE EFFECTS:
        SENDS EMBEDS AND VIEWS TO CHANNELS, SENDS EPHEMERAL ERROR MESSAGES.
    """
    channel = bot.get_channel()
    bitch = interaction.guild.get_role()
    own = interaction.guild.get_role()

    if not any(role in interaction.user.roles for role in [bitch, own]):
        await interaction.response.send_message("You cannot use this command.", ephemeral=True, delete_after=5)
        return
    
    if channel is None:
        await interaction.response.send_message(f"The **channel** was not found. Please contact the developers.", ephemeral=True, delete_after=5)
        return

    emb = discord.Embed(description=f"### {interaction.guild.name} - Ticket System\n\n> Need help? No problem! Use the menu below to create a new ticket where our staff will assist you.", color=discord.Color.from_rgb(10, 10, 10))
    emb.set_footer(text=bot_user_name, icon_url=bot_user_avatar_url)
    emb.set_thumbnail(url=bot_user_avatar_url)
    
    await interaction.response.send_message(f"Ticket embed sent successfully! {channel.mention}", ephemeral=True, delete_after=10)
    await channel.send(embed=emb, view=DropdownView())

@bot.tree.command(name="ticket-add", description="Add a user to a ticket")
@commands.guild_only()
@app_commands.describe(user=f"The user to add to the ticket")
async def add(interaction: discord.Interaction, user: discord.Member):
    """
    SLASH COMMAND TO ADD A USER TO AN EXISTING TICKET CHANNEL.
    
    ONLY STAFF MEMBERS WITH THE REQUIRED ROLE CAN USE THIS COMMAND, AND ONLY IN TICKET CHANNELS.
    CHECKS IF THE USER IS ALREADY IN THE TICKET, IF THE USER EXISTS, AND PREVENTS ADDING ONESELF.
    UPDATES CHANNEL PERMISSIONS TO ALLOW THE ADDED USER TO READ AND SEND MESSAGES IN THE TICKET CHANNEL.
    
    ARGS:
        INTERACTION: THE DISCORD INTERACTION OBJECT FOR THE COMMAND INVOCATION.
        USER: THE DISCORD MEMBER TO ADD TO THE TICKET.
    
    SIDE EFFECTS:
        MODIFIES CHANNEL PERMISSIONS, SENDS CONFIRMATION AND ERROR MESSAGES.
    """
    role = interaction.guild.get_role()
    category = []
    
    if role not in interaction.user.roles:
        await interaction.response.send_message("You cannot use this command.", ephemeral=True, delete_after=5)
        return
    
    if interaction.channel.category_id not in category:
        await interaction.response.send_message(f"This command can only be used in a **ticket category**.", ephemeral=True, delete_after=5)
        return
    
    perms = interaction.channel.permissions_for(user)
    if perms.read_messages and perms.send_messages:
        await interaction.response.send_message(f"{user.mention} is already in the ticket.", ephemeral=True, delete_after=5)
        return
    
    if user is None:
        await interaction.response.send_message(f"The **user** was not found.", ephemeral=True, delete_after=5)
        return
    
    if user == interaction.user:
        await interaction.response.send_message(f"You cannot add **yourself** to the ticket.", ephemeral=True, delete_after=5)
        return
    
    await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
    await interaction.channel.send(f"{interaction.user.mention} added {user.mention} to the ticket.")
    await interaction.response.send_message(f"{user.mention}, {user.mention} was successfully added to {interaction.channel.mention}.", ephemeral=True, delete_after=5)

@bot.tree.command(name="ticket-remove", description="Remove a user from a ticket")
@commands.guild_only()
@app_commands.describe(user="The user to remove from the ticket")
async def remove(interaction: discord.Interaction, user: discord.Member):
    """
    SLASH COMMAND TO REMOVE A USER FROM A TICKET CHANNEL.
    
    ONLY STAFF MEMBERS WITH THE REQUIRED ROLE CAN USE THIS COMMAND, AND ONLY IN TICKET CHANNELS.
    CHECKS IF THE USER IS IN THE TICKET, IF THE USER EXISTS, AND PREVENTS REMOVING ONESELF.
    UPDATES CHANNEL PERMISSIONS TO REVOKE THE USER'S ACCESS TO THE TICKET CHANNEL.
    
    ARGS:
        INTERACTION: THE DISCORD INTERACTION OBJECT FOR THE COMMAND INVOCATION.
        USER: THE DISCORD MEMBER TO REMOVE FROM THE TICKET.
    
    SIDE EFFECTS:
        MODIFIES CHANNEL PERMISSIONS, SENDS CONFIRMATION AND ERROR MESSAGES.
    """
    role = interaction.guild.get_role()
    category = []
    
    if role not in interaction.user.roles:
        await interaction.response.send_message("You cannot use this command.", ephemeral=True, delete_after=5)
        return
    
    if interaction.channel.category_id not in category:
        await interaction.response.send_message(f"This command can only be used in a **ticket category**.", ephemeral=True, delete_after=5)
        return
    
    perms = interaction.channel.permissions_for(user)
    if not (perms.read_messages and perms.send_messages):
        await interaction.response.send_message(f"{user.mention} is not in the ticket.", ephemeral=True, delete_after=5)
        return
    
    if user is None:
        await interaction.response.send_message(f"The **user** was not found.", ephemeral=True, delete_after=5)
        return
    
    if user == interaction.user:
        await interaction.response.send_message(f"You cannot remove **yourself** from the ticket.", ephemeral=True, delete_after=5)
        return
    
    await interaction.channel.set_permissions(user, read_messages=False, send_messages=False)
    await interaction.channel.send(f"{interaction.user.mention} removed {user.mention} from the ticket.")
    await interaction.response.send_message(f"{user.mention}, {user.mention} was successfully removed from {interaction.channel.mention}.", ephemeral=True, delete_after=5)

@bot.tree.command(name="ticket-rename", description="Rename a ticket")
@commands.guild_only()
@app_commands.describe(newname="The new name of the ticket")
async def rename(interaction: discord.Interaction, newname: str):
    """
    SLASH COMMAND TO RENAME A TICKET CHANNEL.
    
    ONLY STAFF MEMBERS WITH THE REQUIRED ROLE CAN USE THIS COMMAND, AND ONLY IN TICKET CHANNELS.
    CHECKS IF THE NEW NAME IS VALID AND NOT ALREADY IN USE, UPDATES THE DATABASE AND CHANNEL NAME ACCORDINGLY.
    HANDLES EDGE CASES WHERE THE CHANNEL NAME IS UNCHANGED OR THE NEW NAME IS INVALID.
    
    ARGS:
        INTERACTION: THE DISCORD INTERACTION OBJECT FOR THE COMMAND INVOCATION.
        NEWNAME: THE NEW NAME FOR THE TICKET CHANNEL.
    
    SIDE EFFECTS:
        UPDATES THE DATABASE, RENAMES THE CHANNEL, SENDS CONFIRMATION AND ERROR MESSAGES.
    """
    role = interaction.guild.get_role()
    category = []
    
    if role not in interaction.user.roles:
        await interaction.response.send_message("You cannot use this command.", ephemeral=True, delete_after=5)
        return

    if interaction.channel.category_id not in category:
        await interaction.response.send_message(f"This command can only be used in a **ticket category**.", ephemeral=True, delete_after=5)
        return
    
    if newname is None:
        await interaction.response.send_message(f"The **new name** is not valid; you must provide a name.", ephemeral=True, delete_after=5)
        return
    
    if interaction.channel.name == f"{newname}":
        await interaction.response.send_message(f"The channel name is already **{interaction.channel.name}**.", ephemeral=True, delete_after=5)
        return

    conn = sqlite3.connect("data/database/ticket.db")
    c = conn.cursor()
    
    c.execute("""UPDATE 'ticket' SET ticketname = ?, ticketid = ? WHERE ticketname = ? AND ticketid = ? AND statusticket = 'open'""", (f"{newname}", interaction.channel.id, interaction.channel.name, interaction.channel.id,))
    conn.commit()
    conn.close()

    await interaction.channel.edit(name=f"{newname}")
    await interaction.channel.send(f"{interaction.user.mention} renamed the ticket to **{newname}**.")
    await interaction.response.send_message(f"{interaction.user.mention}, you successfully renamed the ticket to **{newname}**!", ephemeral=True, delete_after=5)

@bot.tree.command(name="ticket-move", description="Move a ticket to another category")
@commands.guild_only()
@app_commands.describe(category="The category where the ticket will be moved")
async def move(interaction: discord.Interaction, category: discord.CategoryChannel):
    """
    SLASH COMMAND TO MOVE A TICKET CHANNEL TO A DIFFERENT CATEGORY.
    
    ONLY STAFF MEMBERS WITH THE REQUIRED ROLE CAN USE THIS COMMAND, AND ONLY IN TICKET CHANNELS.
    CHECKS IF THE SELECTED CATEGORY IS VALID AND DIFFERENT FROM THE CURRENT ONE, UPDATES THE DATABASE AND MOVES THE CHANNEL.
    HANDLES EDGE CASES WHERE THE CATEGORY IS INVALID OR THE TICKET IS ALREADY IN THE SELECTED CATEGORY.
    
    ARGS:
        INTERACTION: THE DISCORD INTERACTION OBJECT FOR THE COMMAND INVOCATION.
        CATEGORY: THE DISCORD CATEGORY CHANNEL TO MOVE THE TICKET TO.
    
    SIDE EFFECTS:
        UPDATES THE DATABASE, MOVES THE CHANNEL, SENDS CONFIRMATION AND ERROR MESSAGES.
    """
    role = interaction.guild.get_role()
    categorys = []
    
    if role not in interaction.user.roles:
        await interaction.response.send_message("You cannot use this command.", ephemeral=True, delete_after=5)
        return
    
    if interaction.channel.category_id not in categorys:
        await interaction.response.send_message(f"This command can only be used in a **ticket category**.", ephemeral=True, delete_after=5)
        return
    
    if category is None:
        await interaction.response.send_message(f"The **selected category** was not found.", ephemeral=True, delete_after=5)
        return

    if interaction.channel.category_id == category.id:
        await interaction.response.send_message(f"The ticket is already in **{category.name}**.", ephemeral=True, delete_after=5)
        return
    
    if category.id not in categorys:
        await interaction.response.send_message(f"The **selected category** is not a **ticket category**.", ephemeral=True, delete_after=5)
        return

    conn = sqlite3.connect("data/database/ticket.db")
    c = conn.cursor()
    c.execute("""UPDATE 'ticket' SET categoryname = ?, categoryid = ? 
                 WHERE ticketname = ? AND ticketid = ? AND statusticket = 'open'""",
              (category.name, category.id, interaction.channel.name, interaction.channel.id))
    conn.commit()
    conn.close()

    await interaction.channel.edit(category=category)
    await interaction.channel.send(f"{interaction.user.mention} moved the ticket to **{category.name}**.")
    await interaction.response.send_message(f"{interaction.user.mention}, you successfully moved the ticket to **{category.name}**!", ephemeral=True, delete_after=5)
    
@bot.tree.command(name='ticket-close', description='Close the ticket')
@commands.guild_only()
async def closerequest(interaction: discord.Interaction):
    """
    SLASH COMMAND TO INITIATE THE TICKET CLOSURE PROCESS.
    
    ONLY STAFF MEMBERS WITH THE REQUIRED ROLE CAN USE THIS COMMAND, AND ONLY IN TICKET CHANNELS.
    CHECKS IF THE TICKET EXISTS AND IS OPEN, THEN OPENS A MODAL DIALOG TO COLLECT THE REASON FOR CLOSURE.
    HANDLES EDGE CASES WHERE THE TICKET IS NOT FOUND OR ALREADY CLOSED.
    
    ARGS:
        INTERACTION: THE DISCORD INTERACTION OBJECT FOR THE COMMAND INVOCATION.
    
    SIDE EFFECTS:
        OPENS A MODAL, SENDS ERROR MESSAGES, AND MAY UPDATE THE UI.
    """
    role = interaction.guild.get_role()
    category = []
    
    if role not in interaction.user.roles:
        await interaction.response.send_message("You cannot use this command.", ephemeral=True, delete_after=5)
        return
    
    if interaction.channel.category_id not in category:
        await interaction.response.send_message(f"This command can only be used in a **ticket category**.", ephemeral=True, delete_after=5)
        return
    
    conn = sqlite3.connect("data/database/ticket.db")
    c = conn.cursor()
    
    c.execute("""SELECT ticketname, ticketid, statusticket FROM 'ticket' WHERE ticketname = ? AND ticketid = ? AND statusticket = 'open'""", (interaction.channel.name, interaction.channel.id))
    ticket_owner = c.fetchone()
    
    if ticket_owner is None:
        conn.close()
        await interaction.response.send_message("Error: Ticket not found in the **database**.", ephemeral=True)
        return

    opening_time = interaction.channel.created_at.strftime("%d/%m/%Y %H:%M:%S")
    emb = discord.Embed(title='Ticket Closure', description='> Are you sure you want to close this **ticket**? (You have **10** __seconds__ to close it)', color=discord.Color.from_rgb(0, 0, 0))
    emb.set_footer(text=bot_user_name, icon_url=bot_user_avatar_url)
    emb.set_thumbnail(url=bot_user_avatar_url)

    view = ui.View(timeout=None)
    view.add_item(CloseTicketButton(ticket_owner, opening_time))

    await interaction.response.send_message(embed=emb, view=view, ephemeral=True, delete_after=10)
    
if __name__ == "__main__": # Entry point: only runs when executed directly, not on import
    bot.run(token=TOKEN) # Run the bot using the TOKEN
