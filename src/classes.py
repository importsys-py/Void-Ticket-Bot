"""
THIS FILE CONTAINS ALL THE CLASSES, VIEWS, AND MODALS USED BY THE DISCORD TICKET BOT.
EACH CLASS ENCAPSULATES A SPECIFIC PART OF THE TICKETING SYSTEM, SUCH AS UI COMPONENTS, MODAL DIALOGS, AND TICKET MANAGEMENT LOGIC.
THE CLASSES HERE ARE DESIGNED TO BE USED AS PART OF THE DISCORD UI AND EVENT SYSTEM, AND INTERACT WITH THE DATABASE AND DISCORD API.
"""
import discord
import asyncio
import base64
import asyncio
import sqlite3
import io
import chat_exporter
import pytz

from bs4 import BeautifulSoup
from discord import ui
from datetime import datetime
from config import bot_user_avatar_url, bot_user_name

# ──────────────────────────────────────────────────────────────────────────────────────────────────────

class CloseTicketButton(ui.Button):
    """
    A DISCORD UI BUTTON THAT ALLOWS AUTHORIZED USERS TO CLOSE A TICKET CHANNEL.
    
    THIS BUTTON IS ADDED TO THE TICKET EMBED MESSAGE. WHEN CLICKED, IT CHECKS IF THE USER HAS THE REQUIRED ROLE TO CLOSE TICKETS.
    IF AUTHORIZED, IT OPENS A MODAL DIALOG TO COLLECT THE REASON FOR CLOSING THE TICKET. OTHERWISE, IT SENDS AN ERROR MESSAGE.
    THE BUTTON IS STYLED AS A RED 'DANGER' BUTTON WITH A LOCK EMOJI TO CLEARLY INDICATE ITS PURPOSE.
    
    ATTRIBUTES:
        TICKET_OWNER: THE USER WHO OPENED THE TICKET (CAN BE A USER ID OR OBJECT, DEPENDING ON CONTEXT).
        OPENING_TIME: THE TIMESTAMP WHEN THE TICKET WAS CREATED, USED FOR LOGGING AND TRANSCRIPT PURPOSES.
    
    USAGE:
        ADD THIS BUTTON TO A DISCORD.UI.VIEW AND SEND IT WITH A MESSAGE IN THE TICKET CHANNEL.
    """
    def __init__(self, ticket_owner, opening_time):
        """
        INITIALIZE THE CLOSETICKETBUTTON WITH THE TICKET OWNER AND OPENING TIME.
        SETS UP THE BUTTON'S LABEL, EMOJI, AND STYLE FOR DISCORD UI.
        
        ARGS:
            TICKET_OWNER: THE USER WHO OWNS THE TICKET (ID OR OBJECT).
            OPENING_TIME: THE DATETIME STRING WHEN THE TICKET WAS OPENED.
        """
        super().__init__(
            label="Close Ticket",
            emoji="🔒",
            style=discord.ButtonStyle.danger,
        )
        self.ticket_owner = ticket_owner
        self.opening_time = opening_time

    async def callback(self, interaction: discord.Interaction):
        """
        HANDLES THE BUTTON CLICK EVENT.
        
        CHECKS IF THE USER WHO CLICKED HAS THE REQUIRED ROLE TO CLOSE TICKETS. IF NOT, SENDS AN EPHEMERAL ERROR MESSAGE.
        IF AUTHORIZED, OPENS A MODAL DIALOG (CLOSETICKETBUTTONMODAL) TO COLLECT THE REASON FOR CLOSING THE TICKET.
        CLOSES THE DATABASE CONNECTION AFTER THE CHECK.
        
        ARGS:
            INTERACTION: THE DISCORD INTERACTION OBJECT REPRESENTING THE BUTTON CLICK EVENT.
        
        SIDE EFFECTS:
            MAY SEND ERROR MESSAGES, OPEN A MODAL, OR DO NOTHING IF UNAUTHORIZED.
        """
        conn = sqlite3.connect("data/database/ticket.db")
        c = conn.cursor()

        c.execute(
            """SELECT ticketname, ticketid, statusticket FROM 'ticket' WHERE ticketname = ? AND ticketid = ? AND statusticket = 'open'""",
            (interaction.channel.name, interaction.channel.id))
        ticket_owner = c.fetchone()
        
        """
        IN THE VARIABLE 'role', INSERT THE ID OF THE ROLE THAT CAN CLOSE TICKETS.
        IF YOU WANT TO ALLOW MULTIPLE ROLES, WRITE IT LIKE THIS:
        role1 = interaction.guild.get_role(ID_1)
        role2 = interaction.guild.get_role(ID_2)
        if not any(role in interaction.user.roles for role in [role1, role2]):
        """
        role = interaction.guild.get_role() 
        opening_time = interaction.channel.created_at.strftime("%d/%m/%Y %H:%M:%S")

        if role not in interaction.user.roles:
            conn.close()
            await interaction.response.send_message(f"{interaction.user.mention}, you don't have sufficient permissions to close this ticket.", ephemeral=True, delete_after=10)
            return

        else:
            modal = CloseTicketButtonModal(ticket_owner, opening_time)
            await interaction.response.send_modal(modal)
            conn.close()

# ──────────────────────────────────────────────────────────────────────────────────────────────────────

class DropdownView(ui.View):
    """
    A DISCORD UI VIEW CONTAINING A DROPDOWN MENU FOR TICKET TYPE SELECTION.
    
    THIS VIEW IS USED TO LET USERS CHOOSE THE TYPE OF TICKET THEY WANT TO OPEN (E.G., ASSISTANCE, SUPPORT, ETC.).
    EACH DROPDOWN OPTION IS MAPPED TO A SPECIFIC CATEGORY ID, WHICH DETERMINES WHERE THE TICKET CHANNEL WILL BE CREATED.
    THE VIEW IS PERSISTENT (TIMEOUT=NONE) SO IT REMAINS ACTIVE UNTIL MANUALLY REMOVED.
    
    ATTRIBUTES:
        CATEGORY_IDS: A DICTIONARY MAPPING DROPDOWN VALUES TO DISCORD CATEGORY IDS.
    
    USAGE:
        SEND THIS VIEW WITH A MESSAGE IN THE SETUP CHANNEL TO ALLOW USERS TO OPEN TICKETS.
    """
    def __init__(self):
        """
        INITIALIZES THE DROPDOWNVIEW WITH PREDEFINED TICKET CATEGORIES AND OPTIONS.
        SETS UP THE DROPDOWN MENU WITH PLACEHOLDER TEXT AND AVAILABLE OPTIONS.
        THE CALLBACK FOR THE DROPDOWN IS SET TO HANDLE USER SELECTIONS.
        """
        super().__init__(timeout=None)

        """
        INSERT THE CATEGORY ID FOR EACH VALUE.
        IF YOU HAVE MORE OPTIONS, WRITE THEM LIKE THIS:
        "1": CATEGORY_ID, # Category name
        "2": CATEGORY_ID  # Category name
        """
        self.category_ids = {
            "1": 123,  # Assistance
        }
        
        """
        THE 'placeholder' PARAMETER IS THE TEXT THAT APPEARS IN THE MENU.
        THE 'options' PARAMETER DEFINES THE BUTTONS THAT WILL APPEAR
        IN THE MENU.
        """
        select = discord.ui.Select(
            placeholder="🎫〢Select an option to open a ticket",
            options=[
                discord.SelectOption(emoji="⭐", label="Assistance", description="Select this option if you need assistance from our staff.", value="1"),
            ]
        )

        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        """
        HANDLES THE EVENT WHEN A USER SELECTS AN OPTION FROM THE DROPDOWN MENU.
        
        DEPENDING ON THE SELECTED VALUE, OPENS THE CORRESPONDING MODAL DIALOG (E.G., ASSISTANCE MODAL).
        IF THE VALUE IS INVALID OR AN ERROR OCCURS, SENDS AN EPHEMERAL ERROR MESSAGE TO THE USER.
        
        ARGS:
            INTERACTION: THE DISCORD INTERACTION OBJECT REPRESENTING THE DROPDOWN SELECTION EVENT.
        
        SIDE EFFECTS:
            MAY OPEN A MODAL, SEND ERROR MESSAGES, OR DO NOTHING IF THE SELECTION IS INVALID.
        """
        selected_value = interaction.data["values"][0]
        category_id = self.category_ids.get(selected_value)

        try:
            match selected_value:
                case "1":
                    modal = Assistance(category_id)
                case _:
                    await interaction.response.send_message(f"{interaction.user.mention}, the selected value is not a valid option. Please try again.", ephemeral=True, delete_after=10)
                    return

            await interaction.response.send_modal(modal)

        except Exception as e:
            await interaction.response.send_message(f"{interaction.user.mention}, an error occurred while opening your ticket. Please contact the developer.\n\nError: {e}", ephemeral=True)
            return
                   
# ──────────────────────────────────────────────────────────────────────────────────────────────────────

class Assistance(ui.Modal, title="🚨 | Ticket Assistance (Part: Modal)"):
    """
    A DISCORD MODAL DIALOG FOR COLLECTING INFORMATION FROM USERS WHO WANT TO OPEN A NEW TICKET.
    
    THIS MODAL ASKS THE USER FOR THEIR NICKNAME AND A DESCRIPTION OF THEIR PROBLEM. WHEN SUBMITTED, IT CHECKS IF THE USER ALREADY HAS AN OPEN TICKET.
    IF NOT, IT CREATES A NEW TICKET CHANNEL IN THE APPROPRIATE CATEGORY, SETS PERMISSIONS, SAVES TICKET DATA TO THE DATABASE, AND SENDS A WELCOME EMBED.
    ALSO ADDS A CLOSETICKETBUTTON TO THE NEW TICKET CHANNEL FOR FUTURE CLOSURE.
    
    ATTRIBUTES:
        CATEGORY_ID: THE DISCORD CATEGORY ID WHERE THE TICKET CHANNEL WILL BE CREATED.
        OPENING_TIME: THE TIMESTAMP WHEN THE MODAL WAS OPENED (FOR LOGGING/TRANSCRIPT).
        TICKET_OWNER: THE USER WHO IS OPENING THE TICKET (SET ON SUBMIT).
    
    USAGE:
        INSTANTIATED AND SHOWN TO THE USER WHEN THEY SELECT A TICKET TYPE FROM THE DROPDOWN.
    """
    def __init__(self, category_id):
        """
        INITIALIZES THE ASSISTANCE MODAL WITH INPUT FIELDS FOR NICKNAME AND PROBLEM DESCRIPTION.
        SETS THE CATEGORY WHERE THE TICKET WILL BE CREATED.
        
        ARGS:
            CATEGORY_ID: THE DISCORD CATEGORY ID FOR THE NEW TICKET CHANNEL.
        """
        super().__init__(timeout=None)
        self.category_id = category_id
        self.opening_time = datetime.now(pytz.timezone("Europe/Rome")).strftime("%d/%m/%Y %H:%M:%S (DD/MM/YYYY Italian Timezone)")
        self.ticket_owner = None
    
        self.add_item(ui.TextInput(label="Nickname", placeholder="Your Discord nickname", style=discord.TextStyle.short))
        self.add_item(ui.TextInput(label="What's your problem?", placeholder="Describe your problem", style=discord.TextStyle.paragraph))
        
    async def on_submit(self, interaction: discord.Interaction):
        """
        HANDLES THE EVENT WHEN THE USER SUBMITS THE ASSISTANCE MODAL.
        
        CHECKS IF THE USER ALREADY HAS AN OPEN TICKET (BOTH IN THE DATABASE AND ON THE SERVER).
        IF NOT, CREATES A NEW TICKET CHANNEL, SETS PERMISSIONS, SAVES TICKET INFO TO THE DATABASE, AND SENDS A WELCOME EMBED AND CLOSE BUTTON.
        PINS THE WELCOME MESSAGE FOR VISIBILITY. HANDLES EDGE CASES WHERE THE TICKET EXISTS IN THE DB BUT NOT ON THE SERVER.
        
        ARGS:
            INTERACTION: THE DISCORD INTERACTION OBJECT REPRESENTING THE MODAL SUBMISSION.
        
        SIDE EFFECTS:
            MAY CREATE CHANNELS, SEND MESSAGES, UPDATE THE DATABASE, AND PIN MESSAGES.
        """
        await interaction.response.defer(ephemeral=True)

        conn = sqlite3.connect("data/database/ticket.db")
        c = conn.cursor()

        self.ticket_owner = interaction.user
        nickname = self.children[0].value # The first answer from the modal
        description = self.children[1].value # The second answer from the modal
        role = interaction.guild.get_role() # The role that can see the ticket
        category = discord.utils.get(interaction.guild.categories, id=self.category_id) # Do not change this

        """
        THIS 'if' IS A CHECK THAT CONTROLS WHETHER THE USER ALREADY HAS
        AN OPEN TICKET AND WHETHER THE TICKET EXISTS IN THE DATABASE
        BUT NOT ON THE SERVER.
        """
        c.execute("SELECT ticketname FROM ticket WHERE openername = ? AND openerid = ? AND statusticket = 'open'", (interaction.user.name, interaction.user.id,))
        existing_ticket = c.fetchone()

        if existing_ticket:
            ticket_name = existing_ticket[0]
            ticket_channel = discord.utils.get(interaction.guild.text_channels, name=ticket_name)

            if ticket_channel:
                await interaction.followup.send(f'You already have an open ticket: {ticket_channel.mention}', ephemeral=True)
                return
            else:
                await interaction.followup.send(f'You already have an open ticket named **{ticket_name}**, but the channel was not found. Please contact the staff.', ephemeral=True)
                return
        
        """
        THIS IS THE TICKET CREATION WITH PERMISSIONS,
        NAME, CATEGORY, ETC.
        """
        ticket_channel = await interaction.guild.create_text_channel(
            name=f'ticket-{interaction.user.name}',
            category=category,
            overwrites={
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                role: discord.PermissionOverwrite(read_messages=True),
                interaction.user: discord.PermissionOverwrite(read_messages=True)
            }
        )

        dateopened = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        c.execute("""INSERT INTO 'ticket' (ticketname, ticketid, categoryname, categoryid, openername, openerid, closurename, closureid, dateopened, dateclosure, statusticket) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (ticket_channel.name, ticket_channel.id, category.name, category.id, interaction.user.name, interaction.user.id, '', '', f"{dateopened}", '', 'open'))
        conn.commit()
        conn.close()

        # The embed that will be sent in the ticket when it is opened
        emb = discord.Embed(
            description=f"Hello, {interaction.user.mention}\nA staff member will assist you shortly.\n\nThank you for opening a ticket! We are working to respond as quickly as possible.\nWe are a bit behind, but we will do our best to help you.\n\n**Note: current wait times may be high (up to 24h), so please do not tag staff members.**\n\n**Details:**\n> **Nickname**: **``{nickname}``**\n> **Problem**: **``{description}``**",
            color=discord.Color.from_rgb(10, 10, 10)
        )
        emb.set_author(name=f'✅ How can we help you?', icon_url=f'{interaction.user.avatar.url}' if interaction.user.avatar else "https://discord.com/assets/a0180771ce23344c2a95.png?size=1024&format=webp&quality=lossless&width=0&height=256")
        emb.set_footer(text=bot_user_name, icon_url=bot_user_avatar_url)
        emb.set_thumbnail(url=bot_user_avatar_url)

        await ticket_channel.send(f"{interaction.user.mention}{role.mention}")

        message = await ticket_channel.send(embed=emb)

        if interaction.response.is_done():
            await interaction.followup.send(f'Your ticket has been created: {ticket_channel.mention}', ephemeral=True)
        else:
            await interaction.response.send_message(f'Your ticket has been created: {ticket_channel.mention}', ephemeral=True)

        view = ui.View(timeout=None)
        close_button = CloseTicketButton(self.ticket_owner, self.opening_time)

        view.add_item(close_button)
        await ticket_channel.send(view=view)
        await message.pin()

# ──────────────────────────────────────────────────────────────────────────────────────────────────────

class CloseTicketButtonModal(ui.Modal, title="🧩 | Close Ticket"):
    """
    A DISCORD MODAL DIALOG FOR COLLECTING THE REASON FOR CLOSING A TICKET.
    
    THIS MODAL IS SHOWN WHEN AN AUTHORIZED USER CLICKS THE CLOSETICKETBUTTON IN A TICKET CHANNEL.
    IT ASKS FOR THE REASON FOR CLOSURE, THEN UPDATES THE TICKET STATUS IN THE DATABASE, GENERATES A TRANSCRIPT (INCLUDING ATTACHMENTS),
    SENDS THE TRANSCRIPT TO A LOG CHANNEL AND THE TICKET OWNER, AND FINALLY DELETES THE TICKET CHANNEL AFTER A SHORT DELAY.
    HANDLES VARIOUS ERROR CASES, SUCH AS MISSING PERMISSIONS OR DM FAILURES.
    
    ATTRIBUTES:
        TICKET_OWNER: THE USER WHO OPENED THE TICKET.
        OPENING_TIME: THE TIMESTAMP WHEN THE TICKET WAS OPENED.
    
    USAGE:
        INSTANTIATED AND SHOWN TO THE USER WHEN THEY ATTEMPT TO CLOSE A TICKET VIA THE CLOSETICKETBUTTON.
    """
    def __init__(self, ticket_owner, opening_time):
        """
        INITIALIZES THE CLOSETICKETBUTTONMODAL WITH A REQUIRED TEXT FIELD FOR THE CLOSURE REASON.
        
        ARGS:
            TICKET_OWNER: THE USER WHO OPENED THE TICKET.
            OPENING_TIME: THE DATETIME STRING WHEN THE TICKET WAS OPENED.
        """
        super().__init__(timeout=None)
        self.ticket_owner = ticket_owner
        self.opening_time = opening_time
        self.add_item(ui.TextInput(label="Reason for closing ticket", placeholder="Enter the reason for closing the ticket, e.g.: Ticket Resolved...", style=discord.TextStyle.paragraph, required=True))
    
    async def on_submit(self, interaction: discord.Interaction):
        """
        HANDLES THE EVENT WHEN THE USER SUBMITS THE CLOSE TICKET MODAL.
        
        CHECKS IF THE USER HAS THE REQUIRED ROLE TO CLOSE TICKETS. IF AUTHORIZED, UPDATES THE TICKET STATUS IN THE DATABASE,
        GENERATES A TRANSCRIPT (INCLUDING ALL MESSAGES AND ATTACHMENTS), SENDS THE TRANSCRIPT TO A LOG CHANNEL AND THE TICKET OWNER VIA DM,
        AND DELETES THE TICKET CHANNEL AFTER A SHORT DELAY. HANDLES ERRORS SUCH AS MISSING PERMISSIONS OR DM FAILURES GRACEFULLY.
        
        ARGS:
            INTERACTION: THE DISCORD INTERACTION OBJECT REPRESENTING THE MODAL SUBMISSION.
        
        SIDE EFFECTS:
            UPDATES THE DATABASE, SENDS FILES AND MESSAGES, AND DELETES THE CHANNEL.
        """
        conn = sqlite3.connect("data/database/ticket.db")
        c = conn.cursor()
        reason = str(self.children[0].value)
        transcriptchannel = interaction.guild.get_channel()
        role = interaction.guild.get_role()
        
        if role not in interaction.user.roles:
            await interaction.response.send_message("You do not have the required permissions to close this ticket.", ephemeral=True)
            return
        
        await interaction.response.send_message(f"The ticket will be closed in a few seconds... (Transcript: {transcriptchannel.mention})", ephemeral=True)
        ticket = interaction.channel
        await ticket.send(f"The ticket was closed by {interaction.user.mention}... (This ticket will be closed in a few seconds)")
        overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
        overwrite.send_messages = False
        await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        
        dateclosed = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        c.execute("SELECT statusticket FROM ticket WHERE ticketid = ?", (interaction.channel.id,))
        status = c.fetchone()
        
        if status and status[0] == 'open':
            c.execute("UPDATE ticket SET closurename = ?, closureid = ?, dateclosure = ?, statusticket = 'closed' WHERE ticketid = ?", (interaction.user.name, interaction.user.id, dateclosed, interaction.channel.id))
            conn.commit()
            transcript = await chat_exporter.export(ticket, limit=None)
        
        try:
            transcript = await chat_exporter.export(ticket, limit=None)
            if transcript:
                modified_transcript = await self.modify_transcript_with_attachments(ticket, transcript)
                transcript_bytes = modified_transcript.encode("utf-8")
                byte_io = io.BytesIO(transcript_bytes)
                transcript_file = discord.File(byte_io, filename=f"transcript-{ticket.name}.html")
                
                c.execute("SELECT * FROM ticket WHERE ticketid = ? ORDER BY dateclosure DESC LIMIT 1", (interaction.channel.id,))
                embed_data = c.fetchone()
                
                emb = discord.Embed(title="📄 | New Transcript Generated", color=discord.Color.blue())
                emb.add_field(name="🆔 Ticket ID", value=f"`{embed_data[2]}`", inline=True)
                emb.add_field(name="📁 Category", value=f"`{embed_data[3]}`", inline=True)
                emb.add_field(name="🔒 Closed by", value=f"<@{embed_data[7]}>", inline=True)
                emb.add_field(name="👤 Opened by", value=f"<@{embed_data[5]}>", inline=True)
                emb.add_field(name="📅 Opened on", value=f"`{embed_data[9]}`", inline=True)
                emb.add_field(name="📅 Closed on", value=f"`{embed_data[10]}`", inline=True)
                emb.add_field(name="📝 Reason for closing", value=f"```{reason}```", inline=True)
                
                await transcriptchannel.send(embed=emb, file=transcript_file)
                byte_io.seek(0)
                user = interaction.guild.get_member(embed_data[6])
                if user:
                    await user.send(embed=emb, file=discord.File(byte_io, filename=f"transcript-{ticket.name}.html"))
        
        except discord.errors.Forbidden:
            print(f"Unable to send a DM to {self.ticket_owner}.")
        except discord.Forbidden:
            print(f"Unable to send a DM to {self.ticket_owner}")    
        except Exception as e:
            print(f"Error sending the transcript or DM: {e}")
        
        await asyncio.sleep(5)
        await ticket.delete()
        conn.close()
    
    """
    THIS IS THE FUNCTION THAT WILL CREATE THE TRANSCRIPT, 
    DO NOT TOUCH ANYTHING
    """
    async def modify_transcript_with_attachments(self, channel, transcript):
        """
        MODIFIES THE HTML TRANSCRIPT TO INCLUDE ALL ATTACHMENTS (IMAGES, VIDEOS, FILES) AS BASE64-ENCODED DATA.
        
        ITERATES THROUGH ALL MESSAGES IN THE CHANNEL, FINDS ATTACHMENTS, AND EMBEDS THEM DIRECTLY INTO THE TRANSCRIPT HTML.
        THIS ENSURES THAT THE TRANSCRIPT IS SELF-CONTAINED AND CAN BE VIEWED OFFLINE WITH ALL MEDIA INCLUDED.
        HANDLES ERRORS FOR UNSUPPORTED OR PROBLEMATIC ATTACHMENTS GRACEFULLY.
        
        ARGS:
            CHANNEL: THE DISCORD CHANNEL OBJECT FOR THE TICKET.
            TRANSCRIPT: THE HTML TRANSCRIPT STRING GENERATED BY CHAT_EXPORTER.
        
        RETURNS:
            STR: THE MODIFIED HTML TRANSCRIPT WITH EMBEDDED ATTACHMENTS.
        """
        soup = BeautifulSoup(transcript, 'html.parser')
        
        async for message in channel.history(limit=None, oldest_first=True):
            message_div = soup.find('div', {'data-message-id': str(message.id)})
            if not message_div or not message.attachments:
                continue
            
            attachments_div = message_div.find('div', class_='chatlog__attachments')
            if not attachments_div:
                attachments_div = soup.new_tag('div', class_='chatlog__attachments')
                message_div.append(attachments_div)
            
            attachment_tags = []
            for attachment in message.attachments:
                try:
                    file_data = await attachment.read()
                    base64_file = base64.b64encode(file_data).decode('utf-8')
                    file_type = attachment.content_type.split('/')[0]
                    
                    if file_type == 'image':
                        tag = soup.new_tag('img', src=f"data:{attachment.content_type};base64,{base64_file}", alt=attachment.filename, style="max-width:100%; display:block; margin-top:10px; border-radius:5px;")
                    elif file_type == 'video':
                        tag = soup.new_tag('video', controls=True, style="max-width:100%; display:block; margin-top:10px; border-radius:5px;")
                        source_tag = soup.new_tag('source', src=f"data:{attachment.content_type};base64,{base64_file}", type=attachment.content_type)
                        tag.append(source_tag)
                    else:
                        tag = soup.new_tag('a', href=f"data:{attachment.content_type};base64,{base64_file}", download=attachment.filename, style="display:block; margin-top:10px; font-weight:bold; color:#00b0f4;")
                        tag.string = f"📂 {attachment.filename} (Download)"
                    
                    attachment_tags.append(tag)
                except Exception as e:
                    print(f"Error processing attachment {attachment.filename}: {e}")
            
            attachments_div.extend(attachment_tags)
        
        return str(soup)

# ──────────────────────────────────────────────────────────────────────────────────────────────────────
