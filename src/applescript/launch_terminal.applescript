on run argv
    set base_path to item 1 of argv
    tell application "Terminal"
        activate
        do script "cd " & base_path & " && ./stream_notification --no-terminal"
    end tell
end run
