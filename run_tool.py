import subprocess
import sys

# تحديد مسار السكريبت الذي تريد تشغيله
script_name = './src/core/main.py'

# تمرير جميع المعاملات التي تم تمريرها للسكريبت الرئيسي
subprocess.run(['python', script_name] + sys.argv[1:])
