"""
IN THIS PYTHON FILE NAMED "DATABASE.PY", WE CREATE AND MANAGE THE DATABASE,
INCLUDING THE TICKET ARCHIVE.
WE USE SQLITE3, A LIGHTWEIGHT SQL DATABASE ENGINE THAT CREATES LOCAL DATABASE
FILES (E.G., ticket.db).
SQLITE3 IS SIMPLE TO USE, DOES NOT REQUIRE A SERVER, AND IS PERFECT FOR SMALL
TO MEDIUM PROJECTS LIKE THIS BOT.
FOR MORE INFORMATION ABOUT SQLITE, READ https://sqlite.org/index.html
"""

import os # We use the os library to check whether the database file already exists
import sqlite3 # We use sqlite3 to create the database and its tables/columns/rows
from datetime import datetime # We use this to get the current timestamp
from colorama import Fore, init, Style # We use colorama to apply colors to text output
init() # Initialize colorama

"""
HERE WE DEFINE A FUNCTION THAT INITIALIZES THE DATABASE AND DEFINES ITS STRUCTURE
(TABLES AND COLUMNS). INSIDE THE FUNCTION THERE ARE TWO PARAMETERS: `name` AND `path`.
- `name` IS THE NAME OF THE DATABASE FILE.
- `path` IS THE LOCATION WHERE THE FILE WILL BE CREATED/SAVED.

AFTER DEFINING THE FUNCTION, WE PERFORM A CHECK TO SEE WHETHER THE DATABASE FILE
ALREADY EXISTS. IF IT DOES NOT, WE CREATE IT.
AFTER THE CHECK, WE HAVE TWO IMPORTANT VARIABLES:
- `conn` IS THE CONNECTION OBJECT TO THE DATABASE
- `c` IS THE CURSOR (THE INTERFACE BETWEEN PYTHON AND THE DATABASE)

NEXT, WE CREATE THE DATABASE STRUCTURE USING `c.execute(...)`.
- `c.execute` EXECUTES THE SQL QUERY YOU PROVIDE (SELECT, INSERT, DELETE, UPDATE, ...)
AFTER EXECUTION, WE CALL `conn.commit()` AND `conn.close()`:
- `conn.commit()` APPLIES/SAVES THE CHANGES
- `conn.close()` CLOSES THE CONNECTION TO THE DATABASE

PS: WE USE A FUNCTION HERE SO OTHER INSTRUCTIONS IN THIS FILE DO NOT INTERFERE
WITH THE REST OF THE CODE. IF YOU ONLY NEED THE TICKET DATABASE, YOU CAN CALL THIS
FUNCTION DIRECTLY. NOTE: IT WOULD BE BETTER TO USE `try/except/finally` OR A CONTEXT
MANAGER TO GUARANTEE THE CONNECTION IS ALWAYS CLOSED.
""" 
def create_database_ticket(name="ticket.db", path="data/database/ticket.db"): 
    if os.path.exists(path=path): # Existence check
        # Message printed in the terminal if the database already exists
        print(f"{Fore.LIGHTYELLOW_EX}[WARNING]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}The database already exists at{Style.RESET_ALL} {Fore.CYAN}{os.path.abspath(path=path)}{Style.RESET_ALL}") 
        return # Do nothing if it already exists 
    
    conn = sqlite3.connect(path) # Connection to the database
    c = conn.cursor() # Cursor/interface
    
    # 'IF NOT EXISTS' CHECKS WHETHER THE TABLE ALREADY EXISTS; IF IT DOES, NOTHING IS DONE.
    # BELOW: TABLE NAME, COLUMNS, AND THEIR DATA TYPES.
    c.execute("""CREATE TABLE IF NOT EXISTS ticket( 
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticketname TEXT NOT NULL,
                ticketid INT NOT NULL,
                categoryname TEXT NOT NULL,
                categoryid INT NOT NULL,
                openername TEXT NOT NULL,
                openerid INT NOT NULL,
                closurename TEXT NOT NULL,
                closureid INT NOT NULL,
                dateopened TEXT NOT NULL,
                dateclosure TEXT NOT NULL,
                statusticket TEXT NOT NULL
            
        )""") 
    conn.commit() # Apply changes/creation
    conn.close() # Close the connection to the database
    
    # Message printed in the terminal if the database is created successfully
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} {Fore.LIGHTBLACK_EX}The database was created successfully!{Style.RESET_ALL}\n{Fore.LIGHTBLACK_EX}--> Name:{Style.RESET_ALL} {Fore.CYAN}{name}{Style.RESET_ALL}\n{Fore.LIGHTBLACK_EX}--> Norm Path:{Style.RESET_ALL} {Fore.LIGHTCYAN_EX}{path}{Style.RESET_ALL}\n{Fore.LIGHTBLACK_EX}--> Full Path:{Style.RESET_ALL} {Fore.GREEN}{os.path.abspath(path=path)}{Style.RESET_ALL}\n{Fore.LIGHTBLACK_EX}--> Size:{Style.RESET_ALL} {Fore.LIGHTGREEN_EX}{os.path.getsize(path) / 1000:.2f}kb{Style.RESET_ALL}\n{Fore.LIGHTBLACK_EX}--> Creation Time:{Style.RESET_ALL} {Fore.YELLOW}{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}{Style.RESET_ALL}")
    
if __name__ == "__main__": # Entry point: only runs when executed directly, not on import
    create_database_ticket() # Here we call the function to run it