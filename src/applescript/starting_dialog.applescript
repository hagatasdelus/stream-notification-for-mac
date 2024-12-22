(*
Author: Hagata
Version: 0.0.1
Date: 2024/12/21 (Created: 2024/12/21)
*)

on run argv
    set message to item 1 of argv
    set title to item 2 of argv
    set iconPath to item 3 of argv
    display dialog message with title title with icon POSIX file iconPath buttons {"OK"} default button "OK" giving up after 30
end run
