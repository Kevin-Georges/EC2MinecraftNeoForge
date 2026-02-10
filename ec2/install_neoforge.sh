#!/usr/bin/env bash
set -euo pipefail

# === CONFIG ===
MC_USER="minecraft"
MC_DIR="/opt/minecraft"
NEOFORGE_VERSION="21.1.0"          # Change to your desired NeoForge build for MC 1.21.1
INSTALLER_URL="https://maven.neoforged.net/releases/net/neoforged/neoforge/${NEOFORGE_VERSION}/neoforge-${NEOFORGE_VERSION}-installer.jar"

# === PACKAGES ===
sudo apt-get update
sudo apt-get install -y \
  curl wget unzip screen jq \
  python3 python3-venv \
  openjdk-21-jre-headless

# === USER + DIR ===
if ! id -u "${MC_USER}" >/dev/null 2>&1; then
  sudo adduser --disabled-password --gecos "" "${MC_USER}"
fi

sudo mkdir -p "${MC_DIR}"
sudo chown -R "${MC_USER}:${MC_USER}" "${MC_DIR}"

# === DOWNLOAD + INSTALL NEOFORGE ===
sudo -u "${MC_USER}" bash -lc "
  cd '${MC_DIR}'
  wget -O neoforge-installer.jar '${INSTALLER_URL}'
  java -jar neoforge-installer.jar --installServer
"

# Copy repo scripts (assumes you scp/rsync this repo to the box)
# Place start.sh, user_jvm_args.txt, systemd units afterward.

echo "NeoForge installed into ${MC_DIR}."
echo "Next: copy ec2/server/* into ${MC_DIR}, then install systemd units from ec2/systemd/."
