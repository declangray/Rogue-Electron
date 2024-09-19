#!/bin/bash

install_packages() {
    echo "Installing npm..."
    if command -v apt-get > /dev/null; then
        sudo apt-get update
        sudo apt-get install -y npm
    elif command -v yum > /dev/null; then
        sudo yum install -y npm
    elif command -v dnf > /dev/null; then
        sudo dnf install -y npm
    elif command -v pacman > /dev/null; then
        sudo pacman -Sy --noconfirm npm
    elif command -v zypper > /dev/null; then
        sudo zypper install -y npm
    elif command -v brew > /dev/null; then
        brew install npm
    else
        echo "Unsupported OS."
        exit 1
    fi

    npm install -y asar
}

generate_cert() {
    echo "Generating TLS/SSL certificate..."
    openssl req -x509 -newkey rsa:4096 -keyout ./Server/TLS/key.pem -out ./Server/TLS/cert.pem -days 365 -nodes -subj "/CN="
}

install_python_req() {
    sudo pip install -r requirements.txt
}

echo "Running setup..."
install_packages
generate_cert
install_python_req
echo "Setup Complete!"
