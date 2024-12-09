tell application "Terminal"
    tell front window       
        set currentTab to selected tab
        do script "cd ~; clear" in currentTab
        delay 1
        close
    end tell
end tell
