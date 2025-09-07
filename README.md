# Void-Ticket-Bot

A powerful, customizable Discord bot for handling support tickets using buttons, modals, and private channels.  
Designed for Discord communities that need a robust ticketing/helpdesk system with role-based permissions, logging, and a user-friendly interface.

---

## Features

- **Slash Commands**: Modern Discord slash commands for all ticket operations.
- **Ticket Creation**: Users can open tickets via dropdown menus and modals.
- **Role-Based Permissions**: Only authorized staff can manage, close, or move tickets.
- **Ticket Management**: Add/remove users, rename, move, and close tickets with full audit trail.
- **Automatic Logging**: All actions are logged; ticket transcripts (including attachments) are generated and sent to a log channel and the ticket owner.
- **Customizable UI**: Uses Discord's UI components (buttons, dropdowns, modals) for a seamless experience.
- **Database Integration**: Uses SQLite for persistent ticket tracking.
- **Extensive Logging**: Console and file logging for debugging and monitoring.
- **Highly Documented**: All code is thoroughly documented for easy customization and maintenance.

---

## How It Works

1. **Setup**: An admin uses `/ticket-setup` to post the ticket creation embed in a designated channel.
2. **User Interaction**: Users select the type of ticket from a dropdown and fill out a modal with their details.
3. **Ticket Channel**: A private channel is created for the ticket, with permissions set for the user and staff.
4. **Staff Actions**: Staff can add/remove users, rename, move, or close the ticket using slash commands.
5. **Closure**: When closed, a modal collects the reason, a transcript is generated (with all attachments), and the channel is deleted after archiving.

---

## Commands

- `/ticket-setup` — Post the ticket creation embed (admin only).
- `/ticket-add <user>` — Add a user to a ticket (staff only).
- `/ticket-remove <user>` — Remove a user from a ticket (staff only).
- `/ticket-rename <newname>` — Rename the ticket channel (staff only).
- `/ticket-move <category>` — Move the ticket to another category (staff only).
- `/ticket-close` — Initiate the ticket closure process (staff only).

---

## Requirements

- Python 3.9+
- Discord.py 2.x
- colorama
- aiohttp
- sqlite3 (standard library)
- chat_exporter
- python-dotenv
- beautifulsoup4
- (See your `requirements.txt` for exact versions)

---

## Setup

1. **Clone the repository** and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your bot:**
   - Create a `.env` file in `data/private/` with your Discord bot token:
     ```
     TOKEN=your_discord_bot_token
     ```
   - Edit `src/config.py` to set your bot's name and avatar URL if desired.

3. **Run the bot:**
   ```bash
   python src/main.py
   ```

4. **First Run:**
   - The bot will automatically create all required folders, the SQLite database (`data/database/ticket.db`), and the `logs/` directory if they do not exist. No manual setup is needed for the database or logs.

5. **Invite the bot** to your server with the necessary permissions (manage channels, manage roles, read/send messages, etc.).

---

## Notes

- **No manual database or log setup is required.** The bot will create everything it needs on first run.
- **Do not commit your `.env` file or real database to version control.** See `.gitignore` for recommended exclusions.

---

## Customization

- **Roles and Categories**: Edit the role and category IDs in `src/main.py` and `src/classes.py` to match your server's configuration.
- **Embeds and UI**: Modify the embed messages and UI components for your branding.
- **Logging**: Log files are stored in the `logs/` directory.

---

## Important: Setting Up Role and Channel IDs

**You must set your own role and channel IDs in the code for the bot to work properly.**  
The current code uses empty `get_role()` and `get_channel()` calls, which will always return `None` unless you provide the correct IDs.

### Where to Set IDs

- **In `src/main.py` and `src/classes.py`:**  
  - Replace all `get_role()` and `get_channel()` calls with your actual role and channel IDs.
  - Example:  
    ```python
    role = interaction.guild.get_role(123456789012345678)  # Your staff role ID
    channel = bot.get_channel(123456789012345678)         # Your setup/log channel ID
    ```

- **For categories:**  
  - Update the `category` lists in the commands to include your ticket category IDs.

### How to Get IDs

1. Enable Developer Mode in Discord (User Settings > Advanced > Developer Mode).
2. Right-click on the role/channel/category you want to use and select "Copy ID".
3. Paste the ID into the code where needed.

---

## File Structure

- `src/main.py` — Main bot logic, event handlers, and command registration.
- `src/classes.py` — All UI components, modals, and ticket management classes.
- `src/config.py` — Configuration and environment variable loading.
- `data/database/` — SQLite database for ticket tracking (auto-created).
- `logs/` — Log files for bot activity (auto-created).
- `README.md` — This file.

---

## License

This project is provided as-is for educational and community use.  
Please review and adapt the code for your own server's needs.

---

Developed by importsyss.
Uses [discord.py](https://github.com/Rapptz/discord.py) and other open-source libraries.
