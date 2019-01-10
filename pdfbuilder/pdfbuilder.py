import pdfrw
import os
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
 
class PDFbuilder(object): 
    def __init__(self,name,dci,decklist,maincount,sidecount,plan):
        self.name = name
        self.dci = dci
        self.decklist = decklist
        self.count = [maincount,sidecount]
        self.plan = plan.split("\n")
        self.tmp = "tmp_overlay.pdf"

    def create_decklist(self):
        """
        Create the data that will be overlayed on top
        of the form that we want to fill
        """
        last_name,first_name = self.name.split(",")
        c = canvas.Canvas(self.tmp)
        c.rotate(90)
        c.drawString(243, -43, first_name)
        c.drawString(67, -43, last_name)
        for i in range(len(self.dci)):
            c.drawString(420+24*i, -43, self.dci[i])
        c.rotate(-90)
        c.drawString(560, 747, last_name[0])


        main = sorted(self.decklist[:self.decklist.index("")],reverse=True)
        side = sorted(self.decklist[self.decklist.index("")+1:],reverse=True)
        for row in range(len(main)):
            num,name = main[row].split(" ",1)
            if row <= 31:
                c.drawString(80, 610-row*18,num+(" "*10)+name)
            else:
                c.drawString(355, 610-(row-32)*18,num+(" "*10)+name)
        for row in range(len(side)):
            num,name = side[row].split(" ",1)
            c.drawString(355, 358-row*18,num+(" "*10)+name)

        c.drawString(271, 29, str(self.count[0]))
        c.drawString(545, 83, str(self.count[1]))
        c.save()

    def create_sideboard(self):
        c = canvas.Canvas(self.tmp)
        mono_font = r"FreeMono.ttf"
        pdfmetrics.registerFont(TTFont("Mono", mono_font))
        c.setFont("Mono", 10.5, leading=None)
        #barcode_string = '<font name="Free 3 of 9 Regular" size="16">%s</font>'
        #barcode_string = barcode_string % "1234567890"



        for row in range(len(self.plan)):
            c.drawString(17, 783-row*10.5,self.plan[row])

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
