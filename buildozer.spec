[app]

title = MY AI 3.2
package.name = myai
package.domain = org.myai

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,html,css,js
source.exclude_dirs = .github,bin,.buildozer,java

version = 3.2

requirements = python3,kivy==2.3.0,pyjnius

orientation = portrait+landscape
fullscreen = 0

android.permissions = INTERNET,RECORD_AUDIO

android.api = 33
android.minapi = 24
android.ndk = 25b
android.add_src = java

android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True

p4a.branch = v2024.01.21

[buildozer]

log_level = 2
warn_on_root = 1
