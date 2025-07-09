from urllib import request
import subprocess
import os
import shutil

def grab_discord_asar():
    discord_installer_url = "https://discord.com/api/downloads/distributions/app/installers/latest?channel=stable&platform=win&arch=x64"

    print("Creating temp directory...")
    os.makedirs("./temp", exist_ok=True)

    filename = "temp/DiscordSetup.exe"

    opener = request.build_opener(request.HTTPHandler())

    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')]

    request.install_opener(opener)

    print("Downloading Discord installer...")
    
    request.urlretrieve(discord_installer_url, filename)

    print("Extracting ASAR archive from installer...")

    subprocess.run(f'7z e {filename} -otemp/', shell=True)

    for file in os.listdir(f"{os.getcwd()}/temp"):
        if "nupkg" in file:
            nupkgfile = f"temp/{file}"

    subprocess.run(f'7z e {nupkgfile} -otemp/nupkg/', shell=True)

    for file in os.listdir(f"{os.getcwd()}/temp/nupkg/"):
        if file == "app.asar":
            asarfile = f"{os.getcwd()}/temp/nupkg/{file}"
            shutil.move(asarfile, f"{os.getcwd()}/discord.asar")

    print("Cleaning up...")

    shutil.rmtree(f"{os.getcwd()}/temp")

    print(f"Downloaded {os.getcwd()}/discord.asar successfully!")

    return f"{os.getcwd()}/discord.asar"