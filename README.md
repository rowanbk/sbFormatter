# sbFormatter
Turn sideboard documents in printable SB maps

# Requirements:
install the python library "argparser" with "pip install argparse" or a package manager of your choice


# CyrusCG
Using CyrusCG's sideboard plan formatting from google docs this will create a more readable printer friendly version. Make sure to always use full card names (eg. Empty the Warrens not ETW). If you do want to abbreviate a card name add it to the abbrs.txt file in the format: Proper Name/Short. Eg:
Empty the Warrens/ETW

Input:

~ Deck Name
+1 Card1 +2 Card2
-3 Card3

Output:

|--------Deck Name--------|
| -3 Card3       +2 Card2 |
|	 	 +1 Card1 |

# Caleb
To use Caleb's formatting from his website "adventuringgear.wordpress.com" the following steps are needed:
Input:

~ Deck Name
In: 1 Card1 2 Card2
Out: 3 Card3

Output:

|--------Deck Name--------|
| -3 Card3       +2 Card2 |
|	 	 +1 Card1 |

1. copy his sideboard plan to a .txt document
2. copy your decklist to the top of that document eg.
	4 Spirebluff Canal
	4 ...
	SIDEBOARD
	2 Empty the Warrens
	1 ...
3. call the program with the -c argument "python sbFormatter.py -c CalebsGuide.txt"

#Options
-c : use Caleb formatting instead of Cyrus formatting
-s : add spaces where the page should be folded
-f N : alternate format where the guide shows the 15 cards that should be removed instead of ins and outs. N is the number of columns to print with
	eg. python sbFormatter.py -f 3 CyrusGuide.txt
	output:
	...
	|~Elves~            |~RB Reanimator~    |~Grixis Control~   |
	|Decay              |Decay              |Decay              |
	|Decay              |Decay              |Decay              |
	|Xantid             |Xantid             |Xantid             |
	|Xantid             |Xantid             |Xantid             |
	|Hurkyl's           |Hurkyl's           |Hurkyl's           |
	|Hurkyl's           |Hurkyl's           |Hurkyl's           |
	|Truth              |Truth              |Truth              |
	|Truth              |Truth              |Truth              |
	|Truth              |Truth              |Truth              |
	|Massacre           |Massacre           |CoV                |
	|Empty              |Empty              |CoV                |
	|Duress             |Seize              |Massacre           |
	|Duress             |Seize              |Empty              |
	|Swamp              |Swamp              |Petal              |
	|PiF                |Preordain          |Cabal              |
	etc...

-i : do not abbreviate card names
	eg. python sbFormatter.py -i CyrusGuide.txt
	output:
	...
	|-----------------Stoneblade-----------------|
	| -1 Rain of Filth      +2 Xantid Swarm      |
	| -1 Past in Flames     +2 Abrupt Decay      |
	| -1 Lotus Petal        +1 Massacre          |
	| -1 Dark Petition                           |
	| -1 Cabal Ritual                            |
	|                                            |
	etc...

-o : save to a file other than "printout.txt"
	eg. python sbFormatter.py -o saveme.txt

-m : print out interesting metrics about the sideboard plan

-p : save in text form as well as pdf

-d : print decklist as well as sideboard plan
