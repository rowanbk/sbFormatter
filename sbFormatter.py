import re
import argparse

class Deck(object):

    def __init__(self, name):
        self.name = name
        self.cardsIn = []
        self.cardsOut = []

    def __lt__(self,other):
        return self.rows() > other.rows()

    def rows(self):
       return max(len(self.cardsIn),len(self.cardsOut))

    def sortCards(self):
       self.cardsIn.sort(reverse=True)
       self.cardsOut.sort(reverse=True)

    def checkNums(self):
        count = 0
        for card in self.cardsIn:
            count += int(card[1])
        for card in self.cardsOut:
            count -= int(card[1])
        if count > 0:
            print(self.name,count,"more in than out")
        if count < 0:
            print(self.name,-1*count,"more out than in")


    def shortenNames(self):
        nms = open("abbrs.txt","r")
        shortNames = {}
        for line in nms:
            splitLine = line.split('/')
            shortNames[splitLine[0]] = splitLine[1].rstrip()
        for i in range(len(self.cardsIn)):
            if self.cardsIn[i][3:] in shortNames:
                self.cardsIn[i] = self.cardsIn[i][:3]+shortNames[self.cardsIn[i][3:]]
        for i in range(len(self.cardsOut)):
            if self.cardsOut[i][3:] in shortNames:
                self.cardsOut[i] = self.cardsOut[i][:3]+shortNames[self.cardsOut[i][3:]]

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
args = parser.parse_args()

f = open(vars(args)['path'],"r")
out = open(vars(args)['o'],"w")
pline = ""
decks = []
cards = []
duplicate = False
for line in f:
    if re.search(r'[-+] [1-4]',line):
        line = re.sub(r'(?<=[-+]) (?=[1-4])','', line)
    if re.search(r'^[1-4] [A-Z][A-Za-z ]',line):
        line = line[2:]
        line = line.rstrip('\n')
        cards.append(line)
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
        for word in words:
            word = word.rstrip(',./\n ')
            if re.search(r'^[-+][1-4]$',word):
                if re.search(r'^[-][1-4]',change):
                    decks[-1].cardsOut.append(change+name)
                elif re.search(r'^[+][1-4]',change):
                    decks[-1].cardsIn.append(change+name)
                name = ""
                change = word
            elif name.lstrip() in cards:
                continue
            elif len(word)> 1:
                name+=' '+word


        if re.search(r'^[-][1-4]',change):
            decks[-1].cardsOut.append(change+name)
        elif re.search(r'^[+][1-4]',change):
            decks[-1].cardsIn.append(change+name)

    if duplicate:
        break

f.close()

decks.sort()
#decks = groupByPlan(decks.copy())

max_name_width = 0
for deck in decks:
    deck.shortenNames()
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
boarder = '.'
name_acc = '-'
row_dev = " "


for i in range(0,len(decks),3):
    j = i+1
    k = j+1
    maxRows = decks[i].rows()
    printString = ""
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
    for r in range(maxRows+1):
        printString = decklimiter+' '
        if len(decks[i].cardsOut) > r:
            printString += decks[i].cardsOut[r]+ ' '*(max_name_width-len(decks[i].cardsOut[r]))
        else:
            printString+=max_name_width*' '
        if len(decks[i].cardsIn) > r:
            printString += decks[i].cardsIn[r]+ ' '*(max_name_width-1-len(decks[i].cardsIn[r]))
        else:
            printString+= (max_name_width-1)*' '

        printString+=decklimiter+' '
        if j<len(decks) and len(decks[j].cardsOut) > r:
            printString += decks[j].cardsOut[r]+ ' '*(max_name_width-len(decks[j].cardsOut[r]))
        else:
            printString+=max_name_width*' '
        if j<len(decks) and len(decks[j].cardsIn) > r:
            printString += decks[j].cardsIn[r]+ ' '*(max_name_width-len(decks[j].cardsIn[r]))
        else:
            printString+= (max_name_width)*' '

        printString+=decklimiter+' '
        if k<len(decks) and len(decks[k].cardsOut) > r:
            printString += decks[k].cardsOut[r]+ ' '*(max_name_width-len(decks[k].cardsOut[r]))
        else:
            printString+=max_name_width*' '
        if k<len(decks) and len(decks[k].cardsIn) > r:
            printString += decks[k].cardsIn[r]+ ' '*(max_name_width-1-len(decks[k].cardsIn[r]))
        else:
            printString+= (max_name_width-1)*' '
        printString+=decklimiter
        out.write(printString+'\n')







exit(0)
for i in range(len(decks)):
    curr_block = 0
    deck = decks[i]
    if i%3 == 0 and i>0:
        out.write(boarder+name_row[:-1]+boarder+'\n')
        for row in card_rows:
            out.write(boarder+row[:-1]+boarder+'\n')
        out.write(boarder+row_dev*max_name_width*2+decklimiter)
        out.write(row_dev*max_name_width*2+decklimiter)
        out.write(row_dev*max_name_width*2+boarder+'\n')
        name_row = ""
        card_rows = []
        max_block = 0
    pad_len = max_name_width - (len(deck.name) // 2)
    name_row += name_acc*(pad_len-(len(deck.name)%2))+deck.name+ name_acc*pad_len +decklimiter
    for crn in range(deck.rows()):
        if crn >= len(card_rows):
            card_rows.append("") 
            for j in range(i%3):
                card_rows[crn] += ' '*(max_name_width*2) + decklimiter
        if crn < len(deck.cardsOut):
            card_rows[crn] += ' '+deck.cardsOut[crn]
            card_rows[crn] += ' '*(max_name_width-1-len(deck.cardsOut[crn]))
        else:
            card_rows[crn] += ' '*(max_name_width)
        if crn < len(deck.cardsIn):
            card_rows[crn] += deck.cardsIn[crn]
            card_rows[crn] += ' '*(max_name_width-len(deck.cardsIn[crn]))+decklimiter
        else:
            card_rows[crn] += ' '*(max_name_width)+decklimiter
        curr_block = crn
    if curr_block >= max_block:
        max_block = curr_block
    else:
        card_rows[max_block] += ' '*(max_name_width*2)+decklimiter
out.close()
