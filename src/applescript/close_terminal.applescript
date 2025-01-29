(*
Author: Hagata
Version: 0.0.1
Date: 2025/1/30 (Created: 2024/10/20)
*)

tell application "Terminal"
    tell front window       
        set currentTab to selected tab
        do script "printf \"\\033c\\033[3J\"" in currentTab
        close
    end tell
end tell
