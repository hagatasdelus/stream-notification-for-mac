(*
Author: Hagata
Version: 0.0.1
Date: 2024/12/23 (Created: 2024/10/20)
*)

on run argv
    set message to item 1 of argv
    set title to item 2 of argv
    set a_url to item 3 of argv
    set iconPath to item 4 of argv
    display dialog message with title title with icon POSIX file iconPath buttons {"Watch stream", "OK"} default button "Watch stream" cancel button "OK" giving up after 60
    set the button_pressed to the button returned of the result
    if the button_pressed is "Watch stream" then
        open location a_url
    end if
end run
