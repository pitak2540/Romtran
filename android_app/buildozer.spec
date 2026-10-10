[app]
title = Romtran GBA Edition
package.name = romtran
package.domain = org.pbkcenter
source.dir = .
source.include_exts = py,kv,png,jpg,atlas,txt,json
version = 0.1.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE
android.api = 35
android.minapi = 23
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
