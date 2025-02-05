#!/bin/bash

# التأكد من تشغيل السكريبت بصلاحيات الجذر
if [ "$EUID" -ne 0 ]; then 
    echo "يرجى تشغيل السكريبت بصلاحيات الجذر (root)"
    exit 1
fi

# تحميل أحدث إصدار من Go
echo "جاري البحث عن أحدث إصدار من Go..."
LATEST_VERSION=$(curl -s https://golang.org/VERSION?m=text)
DOWNLOAD_URL="https://golang.org/dl/${LATEST_VERSION}.linux-amd64.tar.gz"

echo "جاري تحميل ${LATEST_VERSION}..."
wget -q $DOWNLOAD_URL -O /tmp/go.tar.gz

# إزالة النسخة القديمة إذا وجدت
if [ -d "/usr/local/go" ]; then
    echo "إزالة النسخة القديمة من Go..."
    rm -rf /usr/local/go
fi

# فك ضغط الملف وتثبيته
echo "جاري تثبيت Go..."
tar -C /usr/local -xzf /tmp/go.tar.gz

# إضافة مسار Go إلى ملف النظام
if ! grep -q "/usr/local/go/bin" /etc/profile; then
    echo 'export PATH=$PATH:/usr/local/go/bin' >> /etc/profile
fi

# تنظيف الملفات المؤقتة
rm /tmp/go.tar.gz

# التحقق من التثبيت
source /etc/profile
GO_VERSION=$(go version)
echo "تم تثبيت Go بنجاح!"
echo "إصدار Go المثبت: ${GO_VERSION}"
echo "يرجى تسجيل الخروج وإعادة تسجيل الدخول لتطبيق التغييرات على متغيرات البيئة"