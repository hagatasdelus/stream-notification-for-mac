tell application "Terminal"
    tell front window       
        set currentTab to selected tab
        do script "printf \"\\033c\\033[3J\"" in currentTab
        close
    end tell
end tell
