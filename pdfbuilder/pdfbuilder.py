import pdfrw
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
 
class PDFbuilder(object):
    def __init__(self):

        self.tmp = "pdfbuilder/tmp_overlay.pdf"
        mono_font = r"FreeMono.ttf"
        pdfmetrics.registerFont(TTFont("Mono", mono_font))

    def decklist(self,attrs,deckfile,decklist):
        self.create_decklist(attrs,decklist)
        self.merge_pdfs('pdfbuilder/empty_decklist.pdf',deckfile)

    def sideboard(self,sidefile,sideplan):
        self.create_sideboard(sideplan)
        self.merge_pdfs('pdfbuilder/empty_sideboard.pdf',sidefile)

    def create_decklist(self,attrs,decklist):
        """
        Create the data that will be overlayed on top
        of the form that we want to fill
        """
        c = canvas.Canvas(self.tmp)
        c.rotate(90)
        #first name
        c.drawString(246, -43, attrs[2])
        #last name
        c.drawString(67, -43, attrs[1])
        for i in range(len(attrs[0])):
            #DCI
            c.drawString(420+24*i, -43, attrs[0][i])
        c.rotate(-90)


        #first letter last name
        c.drawString(560, 747, attrs[1][0])

        #date
        c.drawString(195, 722, attrs[3])

        #location
        c.drawString(195, 698, attrs[5])

        #event name
        c.drawString(415, 722, attrs[4])

        #deck name
        c.drawString(415, 698, attrs[6])

        #deck designer
        c.drawString(415, 674, attrs[7])


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

        c.drawString(271, 29, attrs[8])
        c.drawString(545, 83, attrs[9])
        c.save()

    def create_sideboard(self,plan):
        c = canvas.Canvas(self.tmp)
        c.setFont("Mono", 10.5, leading=None)
        #barcode_string = '<font name="Free 3 of 9 Regular" size="16">%s</font>'
        #barcode_string = barcode_string % "1234567890"



        for row in range(len(plan)):
            c.drawString(17, 803-row*10.5,plan[row])

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
