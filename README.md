# Twitch Notification App

このアプリケーションは、TwitchAPI、Python、およびAppleScriptを用いてMac内に指定したストリーマーの配信通知を行うものです。

## インストールと実行
1. `poetry install`
2. `.env`と`AppIcon.icns`をルートに配置し、`.env`にTwitchAPIの`Client_ID`と`Client_Secret`を記述

3. `
python -m nuitka --standalone --follow-imports --macos-create-app-bundle --macos-app-name="StreamNotification" --output-dir=../build --include-data-dir=./applesc
ript=applescript --include-data-files=.env=../.env --macos-app-icon=../AppIcon.icns main.py
`
