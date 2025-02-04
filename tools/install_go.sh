#!/bin/bash
# Script: install_go.sh
# الوصف: يقوم هذا السكريبت بتثبيت لغة Go على نظام لينكس.
# يُفضل تشغيله بصلاحيات المستخدم العادي، حيث سيطلب sudo عند الحاجة.
# يدعم السكريبت أنظمة ديبيان/أوبنتو (apt-get) وأنظمة RHEL/CentOS (yum).

set -e  # إيقاف السكريبت في حال حدوث خطأ

# التحقق من وجود لغة Go
if command -v go >/dev/null 2>&1; then
    echo "Go already installed: $(go version)"
    exit 0
fi

echo "Go not installed so installing..."

# التحقق من مدير الحزم واستخدامه لتثبيت Go
if command -v apt-get >/dev/null 2>&1; then
    echo "installing Go... apt-get."
    sudo apt update
    sudo apt install -y golang
elif command -v yum >/dev/null 2>&1; then
    echo "downloading and installing Go.. yum."
    sudo yum install -y golang
else
    echo "not supported package manager"
    echo "https://golang.org/dl/"
    exit 1
fi

# التحقق من نجاح التثبيت
echo "checking Go installation.."
if command -v go >/dev/null 2>&1; then
    echo "successfully installed Go: $(go version)"
else
    echo "Error installing Go."
    exit 1
fi
