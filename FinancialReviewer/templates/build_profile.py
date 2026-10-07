"""Client Profile: a one-page fillable PDF uploaded with each set of financials."""
import sys, textwrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("Sans", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("SansB", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"))
ACCENT = colors.HexColor("#1d4e89"); INK = colors.HexColor("#1f2933"); MUTED = colors.HexColor("#5f6b7a")
BOX = colors.HexColor("#f2f5f9"); LINE = colors.HexColor("#c9d1dc")

W, H = letter; L = 40; R = W - 40

SECTIONS = [
    ("1. Client basics", [
        [("Client name", "name"), ("Tier (Monthly / Quarterly / Business Mgmt)", "tier")],
        [("Primary contact + email", "contact"), ("Industry", "industry")],
        [("Books in (QBO / Google Sheets)", "system"), ("Basis (Cash / Accrual)", "basis")],
        [("Entity type (S-corp, LLC, etc.)", "entity"), ("State", "state")],
        [("Owners + ownership %", "owners"), ("How owners get paid (W-2, draw, entity)", "ownerpay")],
    ]),
    ("2. Goals + targets (what we score against)", [
        [("Monthly revenue goal", "revgoal"), ("Cash collected goal (% of billed)", "collgoal")],
        [("Overhead target (% of revenue)", "ohtarget"), ("Ops / job cost target (% of revenue)", "opstarget")],
        [("Profit target (% of revenue)", "profittarget"), ("Owner pay target per month", "ownertarget")],
        [("Tax set-aside % (company / owners)", "taxpct"), ("Next goal the owner is chasing", "nextgoal")],
        [("Current 90-day constraint (Leads / Conversions / Capacity / Cash / Leakage)", "constraint")],
        [("Focus metric for this quarter + target", "focus")],
    ]),
    ("3. Recurring money out (so Surplus is right)", [
        [("Loans: lender, payment, due date", "loans")],
        [("Big fixed bills (rent, insurance, software)", "fixed")],
        [("Known money leaks to watch", "leaks")],
    ]),
    ("4. This review", [
        [("Period reviewed", "period"), ("Books final? (Yes / No)", "final")],
        [("Reports included (P&L, BS, AR, AP, GL, by Class, bank recs)", "reports")],
        [("What changed this month (hires, big buys, new loans, big jobs)", "changes")],
        [("Open REVIEW items from last review + status", "openreview")],
        [("Notes / special instructions", "notes")],
    ]),
]

def build(path, values):
    c = canvas.Canvas(path, pagesize=letter)
    c.setTitle("Client Profile")
    c.setFillColor(ACCENT); c.setFont("SansB", 16); c.drawString(L, H - 48, "Client Profile")
    c.setFillColor(MUTED); c.setFont("Sans", 8.2)
    c.drawString(L, H - 62, "Upload this with the financials every review. Update only what changed. Blank = not known yet.")
    y = H - 82
    form = c.acroForm
    for title, rows in SECTIONS:
        c.setFillColor(ACCENT); c.setFont("SansB", 9.8); c.drawString(L, y, title)
        c.setStrokeColor(ACCENT); c.setLineWidth(0.8); c.line(L, y - 3, R, y - 3)
        y -= 16
        for row in rows:
            n = len(row); gap = 12
            colw = (R - L - gap * (n - 1)) / n
            tall = n == 1 and row[0][1] in ("loans", "fixed", "openreview", "changes", "notes", "leaks")
            fh = 25 if tall else 15
            for i, (label, key) in enumerate(row):
                x = L + i * (colw + gap)
                c.setFillColor(INK); c.setFont("Sans", 7.2); c.drawString(x, y, label)
                form.textfield(name=key, x=x, y=y - 3 - fh, width=colw, height=fh,
                               value=(textwrap.fill(values.get(key, ""), int(colw / 3.6)) if tall else values.get(key, "")).replace("\u2212", "-"), fontName="Helvetica", fontSize=8 if not tall else 7.5,
                               borderColor=LINE, fillColor=BOX, textColor=INK, borderWidth=0.6,
                               fieldFlags="multiline" if tall else "", forceBorder=True)
            y -= fh + 13
        y -= 4
    c.setFillColor(MUTED); c.setFont("Sans", 6.8)
    c.drawString(L, 18, "Financial Reviewer reads this first. It sets the tier, the targets, and the REVIEW items to carry forward.")
    c.save()

JVP = {
    "name": "Johnston Vidal Projects", "tier": "Business Management", "industry": "Construction + design (job-based)",
    "system": "QuickBooks Online (class = job address)", "basis": "Accrual", "entity": "S-corp? (confirm)", "state": "California",
    "owners": "Johnston ___% / Vidal ___%", "ownerpay": "W-2 $5,000/mo + comp paid to DMCS and JLI",
    "constraint": "Money Leakage (Q3 2026 review)",
    "focus": "Job profit back to 37¢ per $1 by Dec · 0 losing jobs · $0 unbilled job costs · 90%+ collected",
    "loans": "Rivian R1T (bal $12,516) · Tahoe (bal $48,234) · Transit Van (bal $37,680) · Ford F350 x2 ($1,237.10 ea) · Bobcat E35 ($1,549.55). Fill in lenders, payments, and due dates.",
    "fixed": "Office rent $4,455 · health insurance $7,371 · workers comp about $21,600 avg · monthly software about $2,400",
    "leaks": "Already tracked in the 'Leaks' class: card interest, bank fees, extra travel",
    "period": "September 2026", "final": "No", "reports": "P&L by Month, P&L by Class, Balance Sheet by Month, AR Aging, GL",
    "openreview": "Undeposited Funds $119,830 · BOA-4089 −$1,755 · unapplied $26,557 deposit · D.W. Johnston −$139,430 credit · 3 loan payments missing · payroll liabilities · petty cash $26,220 · escrow $288,140 · DMCS / Johnston Landscape balances",
}

if __name__ == "__main__":
    out = sys.argv[1]
    build(f"{out}/Client_Profile_TEMPLATE.pdf", {})
    build(f"{out}/JVP_Client_Profile.pdf", JVP)
    print("ok")
