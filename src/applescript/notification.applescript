(*
Author: Hagata
Version: 0.0.1
Date: 2024/12/23 (Created: 2024/10/20)
*)

on run argv
	set message to item 1 of argv
	set title to item 2 of argv
	display notification message with title title sound name "Submarine"
end run
