"""
IN THIS PYTHON FILE WE WILL GET THE TOKEN FROM THE .ENV 
AND CREATE TWO VARIABLES THAT WE WILL USE IN THE CODE
"""
import os # We will use the library os to get the TOKEN
import dotenv # We will use the library dotenv to load the .env
from datetime import datetime # We will use the library datetime to get the date

dotenv.load_dotenv(dotenv_path="data/private/.env") # Here we load the .env 
TOKEN=os.getenv('TOKEN') # Here we fetch the token with os.getenv

bot_user_name = f"Ticket Bot | {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}" # Insert the name of the bot or what do you want
# Insert the link of the image of the bot (.png)
bot_user_avatar_url = r"https://cdn.discordapp.com/avatars/1106645819811184754/fe158876f71fefd32543a846c8ca69ce.webp?size=1024" 