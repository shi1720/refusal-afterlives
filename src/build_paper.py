#!/usr/bin/env python3
"""Build the article from editable JSON; all tables consume measured results."""
from pathlib import Path
import json
import re
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, KeepTogether

ROOT=Path(__file__).resolve().parents[1]
M=json.loads((ROOT/'paper/manuscript.json').read_text())
S=json.loads((ROOT/'results/summary.json').read_text())
fontdir=Path('/System/Library/Fonts/Supplemental')
for name,file in [('Article','Georgia.ttf'),('ArticleBold','Georgia Bold.ttf'),
                  ('ArticleItalic','Georgia Italic.ttf'),('UI','Arial.ttf'),('UIBold','Arial Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,str(fontdir/file)))
pdfmetrics.registerFontFamily('Article',normal='Article',bold='ArticleBold',italic='ArticleItalic',boldItalic='ArticleBold')
ink=colors.HexColor('#142c42'); gray=colors.HexColor('#53606a'); teal=colors.HexColor('#157b83')
W,H=A4
styles={
    'body':ParagraphStyle('body',fontName='Article',fontSize=10.5,leading=15,alignment=TA_JUSTIFY,spaceAfter=7.5,
                          allowWidows=0,allowOrphans=0),
    'heading':ParagraphStyle('heading',fontName='UIBold',fontSize=11.5,leading=16,textColor=ink,spaceBefore=13,spaceAfter=7,keepWithNext=True),
    'abstract':ParagraphStyle('abstract',fontName='Article',fontSize=9.4,leading=13.6,alignment=TA_JUSTIFY,spaceAfter=8),
    'caption':ParagraphStyle('caption',fontName='Article',fontSize=8.4,leading=11.7,textColor=gray,spaceAfter=12),
    'reference':ParagraphStyle('reference',fontName='Article',fontSize=8.6,leading=12,spaceAfter=7,leftIndent=13,firstLineIndent=-13),
    'cell':ParagraphStyle('cell',fontName='UI',fontSize=8.3,leading=11),
    'cellhead':ParagraphStyle('cellhead',fontName='UIBold',fontSize=8.3,leading=11,textColor=colors.white),
}
def safe(t):
    t=t.replace('\u2011','-').replace('\u2013','-').replace('\u2014','-')
    t=escape(t)
    t=re.sub(r'(https?://[^\s]+)',lambda m:'<link color="#157b83" href="'+m[1]+'">'+m[1]+'</link>',t)
    return t
def p(t,style='body'):return Paragraph(safe(t),styles[style])

class PageCountCanvas(canvas.Canvas):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.pages=[]
    def showPage(self):self.pages.append(dict(self.__dict__));self._startPage()
    def save(self):
        n=len(self.pages)
        for state in self.pages:
            self.__dict__.update(state)
            self.setStrokeColor(colors.HexColor('#d7dfe5'));self.setLineWidth(.4)
            self.line(58,H-39,W-58,H-39)
            self.setFont('UI',7.3);self.setFillColor(gray)
            self.drawString(58,H-30,'GUPTA  |  THE AFTERLIFE OF NO')
            self.drawRightString(W-58,28,f'{self._pageNumber} / {n}')
            self.drawString(58,28,'Research manuscript  |  16 October 2026')
            super().showPage()
        super().save()

def table(which):
    if which=='verification':
        data=[['Check','Scope','Result'],
          ['Source identity','Two poem branch bodies','Identical after whitespace normalization'],
          ['Baseline replay','10,000 plays; seeds 0-9,999',f"{S['poem_arrivals']:,} reached the poem menu"],
          ['Paired intervention',f"{S['paired_runs']:,} reached-state pairs",f"{S['paired_mismatches']} downstream mismatches"],
          ['Local enumeration','43 sequences x 4 profiles x 101 scores',f"{S['local_executions']:,} executions"],
          ['Independent model','Destinations + 4 checked values',f"{S['local_model_disagreements']} disagreements"]]
        widths=[101,180, W-116-281]
    else:
        data=[['Terminal category','Executions','Scope of classification']]
        descriptions={'serial boundary':'Reached Episode2 before purchase', 'Torres closure':'WrapUp with marriedTorres true',
                      'Mendosa closure':'WrapUp with marriedMendosa true','death closure':'WrapUp with alive false',
                      'other closure':'Remaining WrapUp cases'}
        for k in ['serial boundary','Torres closure','Mendosa closure','death closure','other closure']:
            data.append([k.capitalize(),f"{S['baseline_terminal_categories'][k]:,}",descriptions[k]])
        data.append(['Total','10,000','All baseline plays'])
        widths=[123,80,W-116-203]
    rows=[[p(c,'cellhead' if i==0 else 'cell') for c in row] for i,row in enumerate(data)]
    t=Table(rows,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),ink),('VALIGN',(0,0),(-1,-1),'TOP'),
                           ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
                           ('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),8),
                           ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#f0f4f6'),colors.white]),
                           ('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#b8c7d0'))]))
    return t

story=[]
story.append(Paragraph(M['title'],ParagraphStyle('title',fontName='ArticleBold',fontSize=26,leading=31,textColor=ink,spaceBefore=9,spaceAfter=5)))
story.append(Paragraph(M['subtitle'],ParagraphStyle('subtitle',fontName='Article',fontSize=15.2,leading=20,textColor=ink,spaceAfter=17)))
story.append(Paragraph(M['author'],ParagraphStyle('author',fontName='UIBold',fontSize=11,leading=15,spaceAfter=3)))
story.append(Paragraph(M['affiliation']+'<br/>'+M['email'],ParagraphStyle('affiliation',fontName='UI',fontSize=9,leading=13,textColor=gray,spaceAfter=15)))
story.append(p('Abstract','heading'));story.append(p(M['abstract'],'abstract'))
story.append(Paragraph('<b>Keywords:</b> '+safe(M['keywords']),ParagraphStyle('keywords',fontName='Article',fontSize=8.5,leading=12,spaceAfter=11)))
for sec in M['sections']:
    if 'heading' in sec:
        story.append(p(sec['heading'],'heading'))
        story.extend(p(x) for x in sec['paragraphs'])
    elif 'figure' in sec:
        f=ROOT/'figures'/(sec['figure']+'.png')
        im=Image(str(f)); im.drawHeight=(W-116)*im.imageHeight/im.imageWidth;im.drawWidth=W-116
        story.append(KeepTogether([Spacer(1,6),im,Spacer(1,6),p(sec['caption'],'caption')]))
    elif 'table' in sec:
        story.append(KeepTogether([Spacer(1,7),table(sec['table']),Spacer(1,7),p(sec['caption'],'caption')]))
story.append(p('Works cited','heading'))
story.extend(p(x,'reference') for x in M['references'])
out=ROOT/'paper/The_Afterlife_of_No_Shivam_Gupta.pdf'
doc=SimpleDocTemplate(str(out),pagesize=A4,rightMargin=58,leftMargin=58,topMargin=54,bottomMargin=49,
                      title=M['title']+': '+M['subtitle'],author=M['author'],subject='Popular romance studies and interactive fiction')
doc.build(story,canvasmaker=PageCountCanvas)
print(out)
