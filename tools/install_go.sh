#!/bin/bash
# Script: install_go_latest.sh
# Description: This script downloads and installs the latest version of Go on a Linux system.
# It is recommended to run it as a regular user; it will prompt for sudo privileges when needed.
# The script requires curl and tar to be installed.

set -e  # Exit immediately if a command exits with a non-zero status

# Check if curl and tar are installed
if ! command -v curl >/dev/null 2>&1; then
    echo "curl is not installed. Please install curl first."
    exit 1
fi

if ! command -v tar >/dev/null 2>&1; then
    echo "tar is not installed. Please install tar first."
    exit 1
fi

# Check if Go is already installed
if command -v go >/dev/null 2>&1; then
    echo "Go is already installed: $(go version)"
    exit 0
fi

echo "Go is not installed, proceeding with the installation of the latest version..."

# Retrieve the latest version of Go from the official website
latest_version=$(curl -s https://go.dev/VERSION?m=text)
if [ -z "$latest_version" ]; then
    echo "Failed to fetch the latest Go version."
    exit 1
fi
echo "Latest available version: $latest_version"

# Build the download URL (for Linux amd64)
go_tarball="${latest_version}.linux-amd64.tar.gz"
download_url="https://go.dev/dl/${go_tarball}"
echo "Downloading from $download_url ..."

# Download the tarball to a temporary directory
tmp_dir=$(mktemp -d)
curl -o "$tmp_dir/$go_tarball" -L "$download_url"

# Remove any previous installation of Go at /usr/local/go (if it exists)
if [ -d "/usr/local/go" ]; then
    echo "Found a previous installation of Go, removing it..."
    sudo rm -rf /usr/local/go
fi

echo "Extracting files to /usr/local ..."
sudo tar -C /usr/local -xzf "$tmp_dir/$go_tarball"

# Clean up temporary directory
rm -rf "$tmp_dir"

# Update PATH if /usr/local/go/bin is not already in PATH
if ! echo "$PATH" | grep -q "/usr/local/go/bin"; then
    echo "Adding /usr/local/go/bin to PATH in ~/.profile"
    echo "export PATH=\$PATH:/usr/local/go/bin" >> ~/.profile
    # Load the changes immediately
    export PATH=$PATH:/usr/local/go/bin
fi

echo "Go has been installed successfully."
echo "Installed version: $(/usr/local/go/bin/go version)"
echo "Please log out and log back in, or run 'source ~/.profile' to update your PATH."
