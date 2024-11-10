on run argv
    set message to item 1 of argv
    set title to item 2 of argv
    set iconPath to POSIX file (item 3 of argv)
    display dialog message with title title with icon iconPath buttons {"OK"} default button "OK" giving up after 30
end run
