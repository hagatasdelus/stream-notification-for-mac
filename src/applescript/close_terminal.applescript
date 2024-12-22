(*
Author: Hagata
Version: 0.0.1
Date: 2024/12/23 (Created: 2024/10/20)
*)

tell application "Terminal"
    tell front window       
        set currentTab to selected tab
        do script "cd ~; clear" in currentTab
        delay 1
        close
    end tell
end tell
