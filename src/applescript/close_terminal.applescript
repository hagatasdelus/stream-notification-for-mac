tell application "Terminal"
    tell front window       
        set currentTab to selected tab
        do script "cd ${HOME}; clear" in currentTab
        delay 1
        close saving no
    end tell
end tell
