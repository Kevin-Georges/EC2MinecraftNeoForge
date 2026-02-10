This repo provisions an EC2 instance for a NeoForge server and exposes a tiny controller API via API Gateway + Lambda + Discord slash-commands via Discord Interactions (requires signature verification).

What is included
- EC2 Ubuntu host
- systemd service starts NeoForge on boot
- Optional auto-stop: stop EC2 when no players online
- API endpoints:
  - POST /       (Discord verification ping)
  - POST /start  (start EC2 if stopped)
  - POST /status (return EC2 state)

Security
- Do NOT commit Discord bot token or private keys
- Discord Interactions uses the Application PUBLIC KEY for signature verification (safe to store as env var)

Setup
1) Provision infra (Terraform): `infra/terraform`
2) SSH into EC2 and run `ec2/install_neoforge.sh`
3) Enable systemd service `neoforge.service`
4) Deploy Lambda from `lambda/discord_ec2_controller.py`
5) Configure API Gateway routes: ANY /, ANY /start, ANY /status -> same Lambda
6) Set Discord Interactions Endpoint URL to `https://.../default/` (your stage root)

Notes
- Discord Interactions requires request signature verification.
  This repo includes a PyNaCl Lambda layer build script (see lambda/layer).
