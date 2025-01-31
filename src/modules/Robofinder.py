import os
import shutil
import subprocess
import requests
from pathlib import Path

# مسار المجلد الذي سيتم تنزيل الأداة فيه
TOOL_DIR = Path("src/modules/tools_file/robofinder")

def download_tool():
    # حذف المجلد إذا كان موجودًا لتحديث الأداة
    if TOOL_DIR.exists():
        shutil.rmtree(TOOL_DIR)
    
    # تنزيل الأداة من GitHub
    subprocess.run(["git", "clone", "https://github.com/Spix0r/robofinder.git", str(TOOL_DIR)])
    
    # تثبيت المتطلبات
    subprocess.run(["pip", "install", "-r", str(TOOL_DIR / "requirements.txt")])

def run_tool(url):
    # إذا لم يكن المجلد موجودًا، نقوم بتنزيل الأداة أولًا
    if not TOOL_DIR.exists():
        print("الأداة غير موجودة، يتم التنزيل الآن...")
        download_tool()
    
    # الانتقال إلى مجلد الأداة
    os.chdir(TOOL_DIR)
    
    # تشغيل الأداة
    subprocess.run(
    ["python3", "robofinder/robofinder.py", "-u", url, "-o", "Rebofider_output.txt"],
    stdout=subprocess.DEVNULL,  # إخفاء الإخراج العادي
  #  stderr=subprocess.DEVNULL   # إخفاء الأخطاء أيضًا
    )

    # ارجاع النتائج
    with open("Rebofider_output.txt", "r") as file:
        output = file.read()
    return output
# مثال على استخدام الدالة

#run_tool("https://companyhub.com")


Github_URL_Clone = ""

