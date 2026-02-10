#!/usr/bin/env python3
import os
import time
import json
import socket
import subprocess
from datetime import datetime, timezone

import urllib.request

MC_HOST = os.getenv("MC_HOST", "127.0.0.1")
MC_PORT = int(os.getenv("MC_PORT", "25565"))

EMPTY_MINUTES = int(os.getenv("EMPTY_MINUTES", "10"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
BOOT_GRACE_SECONDS = int(os.getenv("BOOT_GRACE_SECONDS", "600"))

AWS_REGION = os.getenv("AWS_REGION", "eu-west-2")
INSTANCE_ID = os.getenv("INSTANCE_ID")  # required

# Uses IMDSv2 to stop itself via AWS CLI OR instance profile.
# Easiest path: install awscli + instance role with ec2:StopInstances on itself.
STOP_CMD = os.getenv("STOP_CMD", "aws ec2 stop-instances --region {} --instance-ids {}".format(AWS_REGION, INSTANCE_ID))

def uptime_seconds() -> int:
    with open("/proc/uptime", "r", encoding="utf-8") as f:
        return int(float(f.read().split()[0]))

def players_online() -> int:
    """
    Minimal check using TCP connect + server query is modpack-dependent.
    Safer: parse latest.log for joined/left is messy.
    Best practical: use rcon or a query mod/plugin.
    Here we do a simple port-open check and assume "unknown players" -> don't stop.
    """
    try:
        with socket.create_connection((MC_HOST, MC_PORT), timeout=3):
            # Port open: server is up but we can't read player count without query protocol.
            # Return -1 meaning "unknown; don't stop"
            return -1
    except OSError:
        # Server not listening -> treat as empty
        return 0

def stop_instance():
    print("Stopping instance via:", STOP_CMD)
    subprocess.run(STOP_CMD, shell=True, check=False)

def main():
    if not INSTANCE_ID:
        raise SystemExit("INSTANCE_ID env var is required")

    empty_streak = 0

    while True:
        up = uptime_seconds()
        if up < BOOT_GRACE_SECONDS:
            print(f"Boot grace period: {up}/{BOOT_GRACE_SECONDS}s")
            time.sleep(CHECK_INTERVAL)
            continue

        p = players_online()
        print("players_online:", p)

        if p == 0:
            empty_streak += 1
        else:
            empty_streak = 0

        if empty_streak * CHECK_INTERVAL >= EMPTY_MINUTES * 60:
            print(f"Empty for {EMPTY_MINUTES} minutes -> stopping instance")
            stop_instance()
            time.sleep(300)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
