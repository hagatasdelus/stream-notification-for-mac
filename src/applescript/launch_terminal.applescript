on run argv
    set base_path to item 1 of argv
    tell application "Terminal"
        activate
        do script "\"" & base_path & "/setup\" --no-terminal"
    end tell
end run
