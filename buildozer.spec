[app]

# 應用程式名稱
title = My Application

# 套件名稱（只能小寫）
package.name = myapp

# 套件網域（反向網域）
package.domain = org.test

# 主程式所在資料夾（main.py 在這）
source.dir = .

# 包含的檔案類型
source.include_exts = py,png,jpg,kv,atlas

# 版本號
version = 0.1

# Python / Kivy 需求
requirements = python3,kivy

# Kivy 使用 SDL2（正確）
bootstrap = sdl2


# ======================
# Android 設定
# ======================

# 目標 API（Android 13）
android.api = 33

# 最低支援版本（保守穩定）
android.minapi = 21

# 權限
android.permissions = INTERNET

# 🔑 關鍵：支援手機 + 模擬器
android.arch = arm64-v8a, armeabi-v7a, x86_64

# 使用 AndroidX（避免相容問題）
android.enable_androidx = True

# logcat 除錯（可選但推薦）
android.logcat_filters = *:S python:D


# ======================
# Buildozer 本身設定
# ======================

# Android NDK / SDK 版本（穩定）
android.ndk = 25b
android.sdk = 33

# 不用自訂 icon / presplash 先註解
# icon.filename = %(source.dir)s/icon.png
# presplash.filename = %(source.dir)s/presplash.png

# 全螢幕（Kivy 預設）
fullscreen = 1
