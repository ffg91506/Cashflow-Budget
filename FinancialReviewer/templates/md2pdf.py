import re, sys
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
pdfmetrics.registerFont(TTFont("Sans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("SansB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
for b in (0, 1):
    for i in (0, 1): addMapping("Sans", b, i, "SansB" if b else "Sans")
A = colors.HexColor("#1d4e89"); INK = colors.HexColor("#1f2933")
st = lambda **k: ParagraphStyle("x", **{**dict(fontName="Sans", fontSize=8.6, leading=11.2, textColor=INK), **k})
T, H2, H3, B, LI = st(fontName="SansB", fontSize=14, leading=18, textColor=A), st(fontName="SansB", fontSize=11, leading=14, textColor=A, spaceBefore=8, spaceAfter=3), st(fontName="SansB", fontSize=9.4, leading=12, spaceBefore=5, spaceAfter=2), st(spaceAfter=2), st(leftIndent=10, firstLineIndent=-8, spaceAfter=1.5)
out = []
for line in open(sys.argv[1], encoding="utf-8").read().splitlines():
    t = line.rstrip()
    t2 = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    if not t: continue
    if t.startswith("# "): out.append(Paragraph(t2[2:], T))
    elif t.startswith("## "): out.append(Paragraph(t2[3:], H2))
    elif t.startswith("### "): out.append(Paragraph(t2[4:], H3))
    elif t.startswith("- "): out.append(Paragraph("•&nbsp;&nbsp;" + t2[2:], LI))
    elif t == "---": out.append(Spacer(1, 4))
    else: out.append(Paragraph(t2, B))
SimpleDocTemplate(sys.argv[2], pagesize=letter, leftMargin=0.6*inch, rightMargin=0.6*inch, topMargin=0.5*inch, bottomMargin=0.5*inch).build(out)
