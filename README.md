# Twitch Notification App

このアプリケーションは、TwitchAPI、Python、およびAppleScriptを用いてMac内に指定したストリーマーの配信通知を行うものである。

## インストールと実行
1. `poetry install`
2. `.env`と`AppIcon.icns`, `AppIcon.png`をルートに配置し、`.env`にTwitchAPIの`Client_ID`と`Client_Secret`を記述

4. `
nuitka --standalone --follow-imports --macos-create-app-bundle --macos-app-name="StreamNotification" --output-dir=build --include-data-dir=src/applescript=applescript --include-data-files=.env=.env --include-data-file=AppIcon.png=AppIcon.png --macos-app-icon=AppIcon.icns setup.py
`
を実行
