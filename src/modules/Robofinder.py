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
    subprocess.run(["python3", "robofinder/robofinder.py", "-u", url])

# مثال على استخدام الدالة
if __name__ == "__main__":
    run_tool("https://example.com")