import pdfrw
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
 
class PDFbuilder(object):
    def __init__(self,dci,last_name,first_name,date,event,location,deck_name,deck_dev,deckfile,decklist,maincount,sidecount,sidefile,plan):

        self.tmp = "tmp_overlay.pdf"
        mono_font = r"FreeMono.ttf"
        pdfmetrics.registerFont(TTFont("Mono", mono_font))

        self.create_decklist(dci,last_name,first_name,date,event,location,deck_name,deck_dev,maincount,sidecount,decklist)
        self.merge_pdfs('pdfbuilder/empty_decklist.pdf',deckfile)
        self.create_sideboard(plan)
        self.merge_pdfs('pdfbuilder/empty_sideboard.pdf',sidefile)

    def create_decklist(self,dci,last_name,first_name,date,event,location,deck_name,deck_dev,maincount,sidecount,decklist):
        """
        Create the data that will be overlayed on top
        of the form that we want to fill
        """
        c = canvas.Canvas(self.tmp)
        c.rotate(90)
        c.drawString(246, -43, first_name)
        c.drawString(67, -43, last_name)
        for i in range(len(dci)):
            c.drawString(420+24*i, -43, dci[i])
        c.rotate(-90)

        c.drawString(560, 747, last_name[0])

        c.drawString(195, 722, date)
        c.drawString(195, 698, location)

        c.drawString(415, 722, event)
        c.drawString(415, 698, deck_name)
        c.drawString(415, 674, deck_dev)


        main = sorted(decklist[:decklist.index("")],reverse=True)
        side = sorted(decklist[decklist.index("")+1:],reverse=True)
        for row in range(len(main)):
            num,name = main[row].split(" ",1)
            if row <= 31:
                c.drawString(80, 610-row*18,num+(" "*10)+name)
            else:
                c.drawString(355, 610-(row-32)*18,num+(" "*10)+name)
        for row in range(len(side)):
            num,name = side[row].split(" ",1)
            c.drawString(355, 358-row*18,num+(" "*10)+name)

        c.drawString(271, 29, str(maincount))
        c.drawString(545, 83, str(sidecount))
        c.save()

    def create_sideboard(self,plan):
        c = canvas.Canvas(self.tmp)
        c.setFont("Mono", 10.5, leading=None)
        #barcode_string = '<font name="Free 3 of 9 Regular" size="16">%s</font>'
        #barcode_string = barcode_string % "1234567890"



        for row in range(len(plan)):
            c.drawString(17, 783-row*10.5,plan[row])

        c.save()

    def merge_pdfs(self,form_pdf, output):
        """
        Merge the specified fillable form PDF with the 
        overlay PDF and save the output
        """
        form = pdfrw.PdfReader(form_pdf)
        olay = pdfrw.PdfReader(self.tmp)
        for form_page, overlay_page in zip(form.pages, olay.pages):
            merge_obj = pdfrw.PageMerge()
            overlay = merge_obj.add(overlay_page)[0]
            pdfrw.PageMerge(form_page).add(overlay).render()
        writer = pdfrw.PdfWriter()
        writer.write(output,form)
