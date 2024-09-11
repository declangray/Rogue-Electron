# Rogue Electron 😈
A C2 server designed to run within Electron applications.
## Backstory
### The Electron Problem
#### ASAR Archives
Rogue Electron C2 exploits a flaw in Electron ASAR archives. ASAR archives contain the entire source for an Electron application, they are largely made up of JavaScript files, with a file `package.json` pointing to the "main" script which will be executed when the Electron application's executable is launched. ASAR files can be easily modified to include arbitrary JavaScript, which will be executed as the application process. As of Electron version 30.0.0, ASAR integrity checking has been introduced, however it is considered an "experimental feature" and is not enabled by default (source: [literally electron themselves](https://www.electronjs.org/docs/latest/tutorial/asar-integrity)). 
#### Crappy Applications First, Security... Last
Even if developers wanted to implement ASAR integrity checking, a lot of them can't. The latest version of Discord, 1.0.9162 (as of 11/09/2024), uses Electron 28.2.10 notably 2 major versions behind the required version 30.0.0 for ASAR integrity checking. Even the Electron-based Microsoft Teams (Classic) (*not the new one*), at its most up-to-date version (*before Microsoft Teams (New) (with Copilot) (Office 365) (For work and school) (~~Bedrock edition with RTX raytracing~~) completely replaced it*) used Electron 22.3.27.

Because of this oversight, Electron applications will not complain if you completely replace their entire source code, and *in the case of Microsoft Teams (**Not New**)™, run code as a *~~perfectly safe~~* Microsoft signed and approved executable. This is where the idea for a stealthy C2 came about.
### Exploiting Integrity Checking (or lack thereof...)
So you can change any code within essentially any Electron application, great (*if you're an attacker, not so great for users*). To exploit this, I created a JavaScript C2 client which reaches out to a server (written in Python using [FastAPI](https://fastapi.tiangolo.com/) and [Uvicorn](https://www.uvicorn.org/)) and executes commands using node (*which is not necessarily available in all Electron applications, but I've tested it in Discord and Teams (Classic) and it works so...*). I then chucked this script into an ASAR archive and replaced the ASAR file of an Electron application with my new malicious ASAR archive. Because most Electron applications do not have integrity checking, the application will run just fine and execute my JavaScript C2 client.
## Features
### Current
- Execute commands remotely through an Electron app (with Node JS enabled).
- Inject C2 into legitimate ASAR archive.
- TLS encryption.
- Request randomisation.
### Planned
- [x] Modify existing ASAR file, injecting C2 client into it (eg. supply MS Teams ASAR archive and receive back modified archive with embedded C2).
- [ ] File upload/download.
- [ ] Client killing
- [ ] Multiple sessions/session handling.
## Usage
### Getting Started
1. Most Electron apps store their ASAR archive in `%LOCALAPPDATA%\[application name]\[version]\resources\app.asar`, make a copy of this and keep somewhere safe.

2. Run the server script with `python server.py`. 

*Note: if you run into issues you may need to specify python version 3, eg. `python3 server.py`*

3. You'll be prompted if you want to create an ASAR archive, enter `y`.
4. Next provide the server's IP address.
5. Now provide to the ASAR file you ~~stole~~ copied and it will do all the work for you. The archive created will be called `app.asar`.

![Screenshot of asar creation](screenshot.png)

6. All you need to do now is replace the *legitimate* ASAR file of your target application. eg. if you want to backdoor Discord, overwrite the current ASAR archive in `%LOCALAPPDATA%\Discord\app-[versionnumber]\resources\`.
7. Launch the application and you'll have a C2 connection.

### Commanding and Controlling
Right now, the C2 is very simple. You can run any command that is supported by the OS the application is installed on (*most likely Windows*). There are a few extra commands:

- `history` will show your previous commands.
- `banner`  will display the really cool nice looking logo.
- `help` will tell you what I'm telling you right now.
- `exit` will exit the program ***note:** this will not kill the client, which will still be trying to ping the server!*

## Detection
Because Rogue Electron runs within trusted applications, it is unlikely to be detected by signature-based AV detections. I've been testing this on Windows 11 with Windows Defender fully enabled and it has not even batted an eye. Online scanners like VirusTotal can't give an accurate detection from the ASAR file because it can't actually execute it.

Detection is most likely going to come from the network. Seeing Discord or Teams constantly reaching out to a random IP address is suspicious to say the least. I tried my best to disguise the traffic, using randomised requests that *should* blend in with normal traffic, and TLS to encrypt everything (and also make it look somewhat legit), however C2 traffic will always look like C2 traffic. Plus avoiding detection **at all costs** was not the goal of this project.

