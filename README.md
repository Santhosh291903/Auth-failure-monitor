# 🔒 Auth Failure Monitor

This project monitors Linux authentication logs (`/var/log/auth.log`) for login failures. When an authentication failure is detected, the script captures an image using the system webcam, uploads it to Google Drive, and sends an alert with the photo link to a Google Chat space via webhook.

---

## ✅ Features

- 📸 Captures a photo using the webcam upon each login failure
- ☁️ Uploads the captured image to a shared Google Drive folder
- 💬 Sends a formatted alert message to Google Chat with Drive link
- 🔁 Runs as a background service using `systemd`
- 🔐 Designed for Ubuntu/Debian systems using `/var/log/auth.log`

---

## 🧰 Requirements

- Python 3
- `fswebcam` installed
- Google Cloud Service Account (with Drive API enabled)
- Shared Google Drive folder
- Google Chat Webhook URL
- Linux OS (Ubuntu/Debian)

---

## 📦 Installation

### 1. Clone this Repository


git clone https://github.com/YOUR_USERNAME/auth-failure-monitor.git
cd auth-failure-monitor

2. Install Dependencies

sudo apt update
sudo apt install -y fswebcam
pip3 install -r requirements.txt

3. Setup Google Drive
Go to Google Cloud Console

Create a project → Enable Google Drive API

Create a Service Account → Generate and download a JSON key

Share a Google Drive folder with the service account's email

Copy the Folder ID from the Drive folder URL

4. Set Up Google Chat Webhook
Go to Google Chat

Open/create a Space → Manage Webhooks → Create Webhook

Copy the webhook URL

⚙️ Configuration
Edit auth_monitor.py and update the following:

python

drive_folder_id = 'YOUR_GOOGLE_DRIVE_FOLDER_ID'
chat_webhook_url = 'YOUR_GOOGLE_CHAT_WEBHOOK_URL'
json_key_path = 'service_account.json'  # Path to your JSON key

Move your credentials:

cp ~/Downloads/YOUR_JSON_KEY.json service_account.json

🧪 Manual Test

sudo python3 auth_monitor.py
Then trigger a login failure:

sudo -k
sudo ls  # Enter wrong password
You should receive a message in Google Chat with the image link.

⚙️ Run as a Service (systemd)

1. Move Files
sudo mkdir -p /opt/auth_monitor
sudo cp auth_monitor.py service_account.json /opt/auth_monitor/

2. Create Service File

sudo nano /etc/systemd/system/auth-monitor.service

Paste:

[Unit]
Description=Authentication Failure Monitor
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/auth_monitor/auth_monitor.py
WorkingDirectory=/opt/auth_monitor
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target

3. Enable & Start

sudo systemctl daemon-reload
sudo systemctl enable auth-monitor.service
sudo systemctl start auth-monitor.service

4. Logs

journalctl -u auth-monitor.service -f
