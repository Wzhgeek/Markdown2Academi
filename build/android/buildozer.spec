[app]
title = Markdown2Academia
package.name = markdown2academia
package.domain = com.markdown2academia
source.dir = .
source.include_exts = py,kv,md,txt,csv,yaml,yml
data = ../../src:src,../../assets:assets,../../templates:templates
version = 0.1.0

requirements = python3,kivy==2.2.1,requests,pyyaml,markdown,openpyxl,pandas,pillow,charset-normalizer

orientation = portrait
fullscreen = 0

android.permissions = INTERNET,READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.arch = arm64-v8a

# 指定构建输出目录
android.build_dir = ./build
android.bin_dir = ./bin

[buildozer]
log_level = 2
warn_on_root = 0
