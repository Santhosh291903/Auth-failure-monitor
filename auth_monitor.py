import subprocess
import time
import os
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import requests

# CONFIG - UPDATE THESE
drive_folder_id = 'YOUR_DRIVE_FOLDER_ID'
chat_webhook_url = 'YOUR_GOOGLE_CHAT_WEBHOOK_URL'
json_key_path = 'service_account.json'

# Google Authentication
credentials = service_account.Credentials.from_service_account_file(json_key_path)
drive_service = build('drive', 'v3', credentials=credentials)

# Image storage
PHOTO_DIR = "/tmp/auth_photos"
os.makedirs(PHOTO_DIR, exist_ok=True)

def upload_file_to_drive(file_path):
    file_name = os.path.basename(file_path)
    file_metadata = {'name': file_name, 'parents': [drive_folder_id]}
    media = MediaFileUpload(file_path, mimetype='image/jpeg')
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
    return file['webViewLink']

def send_message_to_chat(message):
    data = {"text": message}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(chat_webhook_url, json=data, headers=headers)
    print("Message sent:", response.status_code, response.text)

def take_photo():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    photo_path = os.path.join(PHOTO_DIR, f"auth_fail_{timestamp}.jpg")
    try:
        subprocess.run(["fswebcam", "--no-banner", photo_path], check=True)
        print(f"Photo taken: {photo_path}")
        return photo_path
    except subprocess.CalledProcessError:
        print("Camera error.")
        return None

def monitor_auth_log():
    auth_log = "/var/log/auth.log"
    with open(auth_log, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            line = f.readline()
            if not line:
                time.sleep(1)
                continue
            if "authentication failure" in line:
                print(f"Failure: {line.strip()}")
                photo = take_photo()
                if photo:
                    drive_link = upload_file_to_drive(photo)
                    msg = f"🔒 Authentication Failure:\n{line.strip()}\n📸 Photo: {drive_link}"
                    send_message_to_chat(msg)
                    os.remove(photo)

if __name__ == "__main__":
    print("🔍 Monitoring /var/log/auth.log for authentication failures...")
    monitor_auth_log()
