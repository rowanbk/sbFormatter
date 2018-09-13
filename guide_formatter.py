import re

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


f = open("RowanGuide.txt","r")
out = open("printout.txt","w")
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

decks.sort()
max_name_width = 0
for deck in decks:
    deck.shortenNames()
    if (len(deck.name)//2)+1 > max_name_width:
        max_name_width = (len(deck.name)//2)+1
    for card in deck.cardsIn + deck.cardsOut:
        if len(card) > max_name_width:
            max_name_width = len(card)
    deck.sortCards()
    
name_row = ""
max_name_width += 2
card_rows = []
max_block = 0
decklimiter = '|'
name_acc = '-'
row_dev = " "
for i in range(len(decks)):
    curr_block = 0
    deck = decks[i]
    if i%3 == 0 and i>0:
        out.write(name_row[:-1]+'\n')
        for row in card_rows:
            out.write(row[:-1]+'\n')
        out.write(row_dev*max_name_width*2+decklimiter)
        out.write(row_dev*max_name_width*2+decklimiter)
        out.write(row_dev*max_name_width*2+'\n')
        name_row = ""
        card_rows = []
        max_block = 0
    pad_len = max_name_width - (len(deck.name) // 2)
    name_row += name_acc*(pad_len-(len(deck.name)%2))+deck.name+ name_acc*pad_len +decklimiter
    for crn in range(deck.rows()):
        if crn >= len(card_rows):
            card_rows.append("") 
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

f.close()
out.close()
