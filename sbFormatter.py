import re
import argparse
from math import *

class Deck(object):

    def __init__(self, name):
        self.name = name
        self.cardsIn = []
        self.cardsOut = []
        self.maybeIn = []
        self.maybeOut = []

    def __lt__(self,other):
        return self.rows() > other.rows()

    def rows(self):
       return max(len(self.cardsIn)+len(self.maybeIn),len(self.cardsOut)+len(self.maybeOut))

    def sortCards(self):
       self.cardsIn.sort(reverse=True)
       self.cardsOut.sort(reverse=True)

    def checkNums(self):
        count = 0
        for card in self.cardsIn:
            count += int(card[1])
        for card in self.cardsOut:
            count -= int(card[1])
        if len(self.maybeOut) == 0 and count > 0:
            print(self.name,count,"more in than out")
        if len(self.maybeIn) == 0 and count < 0:
            print(self.name,-1*count,"more out than in")

    def shortenNames(self,noshorten):
        for s in [self.cardsIn,self.cardsOut,self.maybeIn,self.maybeOut]:
            for i in range(len(s)):
                name = s[i][3:].lower()
                if name in shortNames and not noshorten:
                    s[i] = s[i][:3]+shortNames[name]
                elif not name in listed and not noshorten:
                    print("No abbr for:",name,self.name)
                    listed.append(name)

def CWStoCyrus(f):
    lines = [""]
    for line in f:
        curr = ""
        line = line.rstrip('\n')
        beginning = line.split(' ',1)[0].lower()
        if "in:" in beginning or "out:" in beginning:
            if "in" in beginning:
                add_char = "+"
            else:
                add_char = "-"
            first = True
            for sec in line.split()[1:]:
                if len(curr) > 0 and sec.isdigit():
                    if not first:
                        lines[-1] += ", "+curr
                    else:
                        first = False
                        lines[-1] += curr
                    curr = add_char+sec
                elif sec.isdigit():
                    curr += add_char+sec.rstrip(',')
                else:
                    curr += " "+sec.rstrip(',')
            lines[-1] += ", "+curr
            lines.append("")
        elif beginning.isdigit() or beginning == "sideboard":
            lines.append(line)
        elif len(beginning) > 0:
            lines.append("~"+line+"\n")
            lines.append("")

    return lines


def groupByPlan(decks):
    groupedDecks = []
    groupedDecks.append(decks.pop())
    while len(decks) > 0:
        maxSim = 0
        maxInd = 0
        for i in range(len(decks)):
            if decks[i].rows() == groupedDecks[-1].rows():
                cardsIn1 = set(map(lambda x:x[3:],decks[i].cardsIn))
                cardsIn2 = set(map(lambda x:x[3:],groupedDecks[-1].cardsIn))
                overlap = len(list(cardsIn1 & cardsIn2))
                if overlap > maxSim:
                    maxSim = overlap
                    maxInd = i
        groupedDecks.append(decks[maxInd])
        del decks[maxInd]

    return groupedDecks



parser = argparse.ArgumentParser()
parser.add_argument('path',nargs='?')
parser.add_argument('-o',nargs='?', default="printout.txt")
parser.add_argument('-i',action='store_true')
parser.add_argument('-f',nargs='?', default=False)
parser.add_argument('-c',action='store_true')
args = parser.parse_args()

out = open(vars(args)['o'],"w")
noshorten = vars(args)['i']
cws = vars(args)['c']
allout = vars(args)['f']
nms = open("abbrs.txt","r")
shortNames = {}
with open(vars(args)['path'],"r") as f:
    if cws:
        file_lines = CWStoCyrus(f)
    else:
        file_lines = [line for line in f]
for line in nms:
    splitLine = line.split('/')
    shortNames[splitLine[0].lower()] = splitLine[1].rstrip()
pline = ""
decks = []
cards = []
duplicate = False
maindeck = 1
sidestart = 0
for line in file_lines:
    if re.search(r'[-+] [1-4]',line):
        line = re.sub(r'(?<=[-+]) (?=[1-4])','', line)
    if "sideboard" in line.lower():
        maindeck = 0
    elif re.search(r'^[1-4] [A-Z][A-Za-z ]',line):
        line = line.lower().rstrip('\n')
        if not "sideboard" in line:
            num,name = line.split(" ",1)
            cards += int(num)*[name]
        sidestart += int(num)*maindeck
    elif '~' in line:
        line = line[:line.find(':')]
        line = line.lstrip("~ ")
        for deck in decks:
            if deck.name == line:
                duplicate = True
                break
        if not duplicate:
            decks.append(Deck(line))
    elif not duplicate and re.search(r'[-+][1-4]',line):
        words = re.split('[, ]',line)
        change = ""
        name = ""
        optional = False
        option = False
        for word in words:
            word = word.rstrip(',./:\n ')
            if word == "OPTION":
                optional = True
            elif re.search(r'^[-+][1-4]$',word):
                if re.search(r'^[-][1-4]',change):
                    if option:
                        decks[-1].maybeOut.append(change+name)
                    else:
                        decks[-1].cardsOut.append(change+name)
                        if optional:
                            option = True
                elif re.search(r'^[+][1-4]',change):
                    if option:
                        decks[-1].maybeIn.append(change+name)
                    else:
                        decks[-1].cardsIn.append(change+name)
                        if optional:
                            option = True
                name = ""
                change = word
            elif name.lstrip() in cards:
                continue
            elif len(word)> 1:
                name+=' '+word

        if re.search(r'^[-][1-4]',change):
            if optional:
                decks[-1].maybeOut.append(change+name)
            else:
                decks[-1].cardsOut.append(change+name)
        elif re.search(r'^[+][1-4]',change):
            if optional:
                decks[-1].maybeIn.append(change+name)
            else:
                decks[-1].cardsIn.append(change+name)

    if duplicate:
        break

decks.sort()
#decks = groupByPlan(decks.copy())
if len(decks) == 0 or len(cards) == 0:
    print("Decklist or argument error")
    exit(1)

max_name_width = 0
listed = []
for deck in decks:
    deck.shortenNames(noshorten != False)
    if (len(deck.name)//2)+1 > max_name_width:
        max_name_width = (len(deck.name)//2)+1
    for card in deck.cardsIn + deck.cardsOut:
        if len(card) > max_name_width:
            max_name_width = len(card)
    deck.sortCards()
    deck.checkNums()

name_row = ""
max_name_width += 2
card_rows = []
max_block = 0
decklimiter = '|'
foldSpace = ' '
name_acc = '-'
bolden = '~'
optional = '*'
rowCount = 6
maxRowCount = 20
colwidth = max([len(shortNames[card]) for card in shortNames]+[len(deck.name)+3 for deck in decks])
cols = int(allout)

if allout != False:
    for r in range(ceil(len(decks)/cols)):
        decks = groupByPlan(decks)
        totalout = []
        for c in range(cols):
            i = (cols*r)+c
            if i < len(decks):
                out.write((decklimiter+bolden+decks[i].name+bolden).ljust(colwidth))
                totalin = []
                totalout.append([])
                for line in decks[i].cardsIn:
                    totalin += int(line[1])*[line[3:].lower()]
                for card in cards[sidestart:]:
                    if not noshorten:
                        card = shortNames[card]
                    if card.lower() in totalin:
                        totalin.remove(card.lower())
                    else:
                        totalout[c].append(card)
                for line in decks[i].cardsOut:
                    totalout[c] += int(line[1])*[line[3:]]
            else:
                out.write((decklimiter).ljust(colwidth))
        out.write(decklimiter+'\n')
        for num in range(15):
            for c in range(cols):
                if c < len(totalout):
                    out.write((decklimiter+totalout[c][num]).ljust(colwidth))
                else:
                    out.write(decklimiter.ljust(colwidth))
            out.write(decklimiter+'\n')
        out.write(decklimiter+(((cols*colwidth)-1)*name_acc)+decklimiter+'\n')

else:
    for i in range(0,len(decks),3):
        j = i+1
        k = j+1
        maxRows = decks[i].rows()
        printString = ""

        if rowCount >= maxRowCount:
            for r in range(max(1,(25 - rowCount))):
                out.write((foldSpace*((6*max_name_width)+5))+'\n')
            rowCount = 0

        if(j<len(decks)):
            maxRows = max(maxRows,decks[j].rows())
        if(k<len(decks)):
            maxRows = max(maxRows,decks[k].rows())
        pad_len = max_name_width - (len(decks[i].name) // 2)
        printString += (decklimiter
                        + name_acc*(pad_len-(len(decks[i].name)%2))
                        + decks[i].name
                        + name_acc*(pad_len))
        if(j<len(decks)):
            pad_len = max_name_width - (len(decks[j].name) // 2)
            printString += (decklimiter
                            + name_acc*(pad_len)
                            + decks[j].name
                            + name_acc*(pad_len+(1+len(decks[j].name))%2))
        else:
            printString+=decklimiter+(1+2*max_name_width)*' '
        if(k<len(decks)):
            pad_len = max_name_width - (len(decks[k].name) // 2)
            printString += (decklimiter
                            + name_acc*(pad_len-(len(decks[k].name)%2))
                            + decks[k].name
                            + name_acc*(pad_len)
                            +decklimiter)
        else:
            printString+=decklimiter+2*max_name_width*' '+decklimiter

        out.write(printString+'\n')
        rowCount+=1
        for r in range(maxRows+1):
            printString = decklimiter+" "
            if len(decks[i].cardsOut) > r:
                printString += decks[i].cardsOut[r]+ ' '*(max_name_width-len(decks[i].cardsOut[r]))
            elif len(decks[i].cardsOut)+len(decks[i].maybeOut) > r:
                maybeR = r-len(decks[i].cardsOut)
                printString += decks[i].maybeOut[maybeR]+optional+' '*(max_name_width-1-len(decks[i].maybeOut[maybeR]))
            else:
                printString+=(max_name_width)*' '
            if len(decks[i].cardsIn) > r:
                printString += decks[i].cardsIn[r]+ ' '*(max_name_width-1-len(decks[i].cardsIn[r]))
            elif len(decks[i].cardsIn)+len(decks[i].maybeIn) > r:
                maybeR = r-len(decks[i].cardsIn)
                printString += decks[i].maybeIn[maybeR]+optional+' '*(max_name_width-2-len(decks[i].maybeIn[maybeR]))
            else:
                printString+= (max_name_width-1)*' '

            printString+=decklimiter+' '
            if j<len(decks) and len(decks[j].cardsOut) > r:
                printString += decks[j].cardsOut[r]+ ' '*(max_name_width-len(decks[j].cardsOut[r]))
            elif j<len(decks) and len(decks[j].cardsOut)+len(decks[j].maybeOut) > r:
                maybeR = r-len(decks[j].cardsOut)
                printString += decks[j].maybeOut[maybeR]+optional+' '*(max_name_width-1-len(decks[j].maybeOut[maybeR]))
            else:
                printString+=(max_name_width)*' '
            if j<len(decks) and len(decks[j].cardsIn) > r:
                printString += decks[j].cardsIn[r]+ ' '*(max_name_width-len(decks[j].cardsIn[r]))
            elif j<len(decks) and len(decks[j].cardsIn)+len(decks[j].maybeIn) > r:
                maybeR = r-len(decks[j].cardsIn)
                printString += decks[j].maybeIn[maybeR]+optional+' '*(max_name_width-1-len(decks[j].maybeIn[maybeR]))
            else:
                printString+= (max_name_width)*' '

            printString+=decklimiter+' '
            if k<len(decks) and len(decks[k].cardsOut) > r:
                printString += decks[k].cardsOut[r]+ ' '*(max_name_width-len(decks[k].cardsOut[r]))
            elif k<len(decks) and len(decks[k].cardsOut)+len(decks[k].maybeOut) > r:
                maybeR = r-len(decks[k].cardsOut)
                printString += decks[k].maybeOut[maybeR]+optional+' '*(max_name_width-1-len(decks[k].maybeOut[maybeR]))
            else:
                printString+=(max_name_width)*' '
            if k<len(decks) and len(decks[k].cardsIn) > r:
                printString += decks[k].cardsIn[r]+ ' '*(max_name_width-1-len(decks[k].cardsIn[r]))
            elif k<len(decks) and len(decks[k].cardsIn)+len(decks[k].maybeIn) > r:
                maybeR = r-len(decks[k].cardsIn)
                printString += decks[k].maybeIn[maybeR]+optional+' '*(max_name_width-2-len(decks[k].maybeIn[maybeR]))
            else:
                printString+= (max_name_width-1)*' '
            printString+=decklimiter
            out.write(printString+'\n')
            rowCount+=1
    out.write((name_acc*((6*max_name_width)+5))+'\n')
