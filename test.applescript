on run argv
    set script_path to POSIX path of (path to me)
    set parent_dir to do shell script "dirname " & quoted form of script_path
    display dialog "Hello" with icon (parent_dir & "/AppIcon.icns")
end run
