tell application "Terminal"
    tell front window
        do script "exit" in selected tab
        delay 1 -- 少し待ってからウィンドウを閉じる
        close
    end tell
end tell
