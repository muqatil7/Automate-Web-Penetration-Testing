import requests
import shutil
import os

TOKEN = "8067500091:AAGc9efhwdEP3X9S09vJt6IXN0BpxolSYg0"  # ضع التوكن الصحيح
CHAT_ID = "6705812641"  # ضع الـ CHAT_ID الصحيح

FOLDER_PATH = "outputs"  # المجلد الذي سيتم ضغطه

def send_file_to_bot(filename_without_extension):
    """ تضغط المجلد وترسله إلى تيليجرام """
    
    # إنشاء اسم الملف المضغوط
    zip_filename = f"{filename_without_extension}.zip"

    # نقل ملف السجل إلى المجلد الناتج
    shutil.move('cyber_toolkit.log', 'outputs')
    
    # تحديد المسار الكامل للملف المضغوط داخل نفس مجلد السكريبت
    script_dir = os.path.dirname(os.path.abspath(__file__))
    zip_file_path = os.path.join(script_dir, zip_filename)

    # ضغط المجلد (سيتم حفظه بنفس مسار السكريبت)
    shutil.make_archive(zip_file_path.replace('.zip', ''), 'zip', FOLDER_PATH)
    print(f"✅ File '{zip_filename}' created at {zip_file_path}")

    # رابط API الخاص بتليجرام لإرسال الملفات
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    
    # إرسال الملف إلى تيليجرام
    with open(zip_file_path, 'rb') as file:
        try:
            response = requests.post(url, data={"chat_id": CHAT_ID}, files={"document": file})
            response.raise_for_status()
            print("✅ File sent successfully!")
        except requests.exceptions.RequestException as e:
            print("❌ File sending failed:", e)
