import requests
import shutil
import os

TOKEN = "8067500091:AAGc9efhwdEP3X9S09vJt6IXN0BpxolSYg0"  # ضع التوكن الصحيح
CHAT_ID = "6705812641"  # ضع الـ CHAT_ID الصحيح

FOLDER_PATH = "outputs"
ZIP_FILE_NAME = "outputs.zip"
ZIP_FILE_PATH = os.path.join(os.getcwd(), ZIP_FILE_NAME)  # حفظ الملف المضغوط في نفس مجلد الكود


def send_file_to_bot():
    # ضغط المجلد
    shutil.make_archive(ZIP_FILE_NAME.replace(".zip", ""), 'zip', FOLDER_PATH)
    print(f"File {ZIP_FILE_NAME} created at {ZIP_FILE_PATH}")

    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    
    with open(ZIP_FILE_PATH, 'rb') as file:
        response = requests.post(url, data={"chat_id": CHAT_ID}, files={"document": file})

    if response.status_code == 200:
        print("✅ File sent successfully")
    else:
        print("❌ File sending failed", response.text)

