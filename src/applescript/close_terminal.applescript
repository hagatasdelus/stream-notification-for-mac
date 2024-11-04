tell application "Terminal"
    tell front window       
        set currentTab to selected tab
        do script "cd ${HOME}; clear" in currentTab
        delay 1
        close
    end tell
end tell
