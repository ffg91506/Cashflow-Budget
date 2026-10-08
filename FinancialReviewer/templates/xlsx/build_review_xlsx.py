"""Financial Reviewer: monthly review workbook (Google Sheets friendly).

Tabs: Corrections · Monthly Summary · YTD Summary · Quarterly Summary · Job Profit (Month) ·
Open Jobs · Client Requests · Budget · Data · Internal Notes
Inputs (blue) live on Budget, Data, Job Profit, Open Jobs. Everything else is formulas.
"""
import json, sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import FormulaRule
from openpyxl.comments import Comment

S, OUT = sys.argv[1], sys.argv[2]
plm = json.load(open(f'{S}/plm.json')); jobs = json.load(open(f'{S}/jobs.json')); aging = json.load(open(f'{S}/aging.json'))
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
MC = {m: chr(ord('C') + i) for i, m in enumerate(MONTHS)}  # Data/YTD month columns C..K
CLIENT, PERIOD = 'Johnston Vidal Projects', 'September 2026'

# ---------- styles ----------
F = 'Arial'
ACC = '1D4E89'
f_title = Font(name=F, size=15, bold=True, color=ACC); f_sub = Font(name=F, size=9, italic=True, color='5F6B7A')
f_h = Font(name=F, size=11, bold=True, color=ACC); f_th = Font(name=F, size=9, bold=True, color='FFFFFF')
f_b = Font(name=F, size=9); f_bb = Font(name=F, size=9, bold=True)
f_in = Font(name=F, size=9, color='0000FF'); f_link = Font(name=F, size=9, color='008000')
fill_th = PatternFill('solid', fgColor=ACC); fill_band = PatternFill('solid', fgColor='EEF2F7')
fill_in = PatternFill('solid', fgColor='FFF2CC'); fill_red = PatternFill('solid', fgColor='FDE2E1')
fill_green = PatternFill('solid', fgColor='E3F4E8'); fill_amber = PatternFill('solid', fgColor='FFF0D6')
thin = Side(style='thin', color='C9D1DC'); bot = Border(bottom=thin)
CUR = '$#,##0;($#,##0);-'; PCT = '0.0%;(0.0%);-'; CENT = '0.0%'
wrap = Alignment(wrap_text=True, vertical='top')

wb = Workbook()
def sheet(name, first=False):
    ws = wb.active if first else wb.create_sheet(name)
    ws.title = name; ws.sheet_view.showGridLines = False
    return ws
def title(ws, t, sub):
    ws['A1'] = t; ws['A1'].font = f_title
    ws['A2'] = sub; ws['A2'].font = f_sub
def header(ws, r, cols, start=1):
    for i, c in enumerate(cols):
        x = ws.cell(r, start + i, c); x.font = f_th; x.fill = fill_th; x.alignment = Alignment(wrap_text=True, vertical='center')
def put(ws, r, c, v, font=f_b, fmt=None, fill=None, al=None):
    x = ws.cell(r, c, v); x.font = font
    if fmt: x.number_format = fmt
    if fill: x.fill = fill
    if al: x.alignment = al
    x.border = bot
    return x
def widths(ws, w):
    for k, v in w.items(): ws.column_dimensions[k].width = v
def status_colors(ws, rng):
    a = rng.split(':')[0]
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("over",{a}))'], fill=fill_red))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("short",{a}))'], fill=fill_red))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("under",{a}))'], fill=fill_green))
    ws.conditional_formatting.add(rng, FormulaRule(formula=[f'ISNUMBER(SEARCH("on ",{a}))'], fill=fill_green))

# =====================================================================
# Tab order per Ayrica: Corrections, Monthly, YTD, Quarterly, Job Profit, Open Jobs (+ support tabs)
wsC = sheet('Corrections', first=True)
wsM = sheet('Monthly Summary'); wsS = sheet('YTD Snapshot'); wsY = sheet('YTD Summary'); wsQ = sheet('Quarterly Summary')
wsJ = sheet('Job Profit (Month)'); wsO = sheet('Open Jobs'); wsR = sheet('Client Requests')
wsB = sheet('Budget'); wsD = sheet('Data'); wsN = sheet('Internal Notes')

# =====================================================================
# BUDGET (inputs)
title(wsB, f'{CLIENT}: Budget + Assumptions', 'Blue = input. Yellow = check or update each month. Source: JVP_ROOTS_Budget_2025.xlsx (2025 cash-basis actuals used as 2026 targets) unless noted.')
B = {}  # name -> absolute ref
rows = [
    ('Monthly cash collected goal', 728348.4533, CUR, 'cash_goal', 'Budget tab, "Expected cash collected"'),
    ('Overhead budget per month (2025 base)', 275702.4392, CUR, 'oh_base', 'Budget tab, Total Overhead (includes all crew labor)'),
    ('New-hire overhead add-on per month', 10477.62, CUR, 'oh_add', 'Team payroll Sept 2026 vs 2025 budget (Office & Admin, PM, Design). Confirm hires, start dates, pay.'),
    ('New-hire add-on starts in month #', 9, '0', 'oh_start', '9 = September'),
    ('Debt payments per month', 10000, CUR, 'debt', 'Per Ayrica: $10,000/month principal + interest'),
    ('Entity taxes per month', 2576.56, CUR, 'tax_m', 'Franchise + city tax, 2025 average'),
    ('Project costs (% of cash collected)', 0.40, CENT, 'p_cogs', 'Per Ayrica 10/08: 40% (COGS excl. crew labor)'),
    ('Operations (% of cash collected)', 0.02, CENT, 'p_ops', 'Per Ayrica 10/08: 2% (fuel, truck repairs, legal)'),
    ('Debt (% of cash collected)', 0.01, CENT, 'p_debt', 'Per Ayrica 10/08: 1%. The fixed $10,000/month is still tracked.'),
    ('Reinvested (% of cash collected)', 0.018, CENT, 'p_reinv', 'Per Ayrica 10/08: 1.8% (marketing, travel, meals, brand: discretionary)'),
    ('Owner pay (% of cash collected)', 0.135, CENT, 'p_owner', 'Per Ayrica 10/08: 13.5% (wages + DMCS + Johnston Landscapes + draws)'),
    ('Cash kept target (% of cash collected)', 250642.35 / 8740181.44, CENT, 'p_kept', 'Net cash kept in business, 2025'),
    ('Leakage target', 0, CUR, 'leak', 'Penalties, bad debt, fraud'),
    ('Target job profit (kept per $1 billed)', 0.43, CENT, 'job_tgt', '2026 YTD gross margin (P&L by Month)'),
    ('Months in review (YTD)', 9, '0', 'months', 'Jan–Sep'),
    ('CA S-corp entity tax rate', 0.015, CENT, 'ca_corp', 'CA franchise tax on S-corp net income'),
    ('Federal standard deduction (single, 2026)', 16100, CUR, 'fed_std', '2026 IRS figure'),
    ('CA standard deduction (single)', 5706, CUR, 'ca_std', '2025 CA figure (2026 not yet published)'),
    ('Cash-basis Net Operating Income YTD (reference)', 649907.85, CUR, 'cash_ni', 'QBO P&L Jan–Sep 2026, cash basis (from Ayrica). Taxable Net Income comes from the Data tab.'),
    ('Ownership % Johnston', 0.5, CENT, 'own_j', 'Confirmed by Ayrica 10/08: 50/50'),
    ('Ownership % Vidal', 0.5, CENT, 'own_v', 'Confirmed by Ayrica 10/08: 50/50'),
]
header(wsB, 4, ['Assumption', 'Value', 'Source / note'])
for i, (lab, val, fmt, key, note) in enumerate(rows):
    r = 5 + i
    put(wsB, r, 1, lab); c = put(wsB, r, 2, val, f_in, fmt, fill_in if key in ('oh_add', 'oh_start', 'months', 'own_j', 'own_v', 'cash_ni') else None); put(wsB, r, 3, note, f_sub)
    B[key] = f"Budget!$B${r}"
r0 = 5 + len(rows) + 2
put(wsB, r0, 1, 'Breakeven: cash needed per month (with new hires)', f_bb)
put(wsB, r0, 2, f"=({B['oh_base']}+{B['oh_add']}+{B['debt']})/(1-{B['p_cogs']}-{B['p_ops']})", f_bb, CUR)
put(wsB, r0, 3, 'Covers overhead + debt after project costs and operations take their %. Does not cover owner pay.', f_sub)
B['breakeven_now'] = f'Budget!$B${r0}'
# tax brackets
def brackets(r, name, rows_):
    put(wsB, r, 1, name, f_h)
    header(wsB, r + 1, ['Income over', 'Rate', 'Rate step'])
    for i, (lo, rate) in enumerate(rows_):
        rr = r + 2 + i
        put(wsB, rr, 1, lo, f_in, CUR); put(wsB, rr, 2, rate, f_in, CENT)
        put(wsB, rr, 3, f'=B{rr}' if i == 0 else f'=B{rr}-B{rr-1}', f_b, CENT)
    return f'Budget!$A${r+2}:$A${r+1+len(rows_)}', f'Budget!$C${r+2}:$C${r+1+len(rows_)}'
FED = [(0, .10), (12400, .12), (50400, .22), (105700, .24), (201775, .32), (256225, .35), (640600, .37)]
CA = [(0, .01), (11079, .02), (26264, .04), (41452, .06), (57542, .08), (72724, .093), (371479, .103), (445771, .113), (742953, .123)]
fed_lo, fed_step = brackets(r0 + 3, 'Federal brackets (single, 2026)', FED)
ca_lo, ca_step = brackets(r0 + 3 + len(FED) + 3, 'California brackets (single, 2025)', CA)
widths(wsB, {'A': 46, 'B': 16, 'C': 90})

# =====================================================================
# DATA: cash-basis P&L by month mapped to ROOTS (inputs)
plc = json.load(open(f'{S}/plc.json'))
title(wsD, f'{CLIENT}: Monthly P&L (cash basis) mapped to ROOTS', 'Blue = pulled from QBO (P&L by Month, cash basis; Balance Sheet by Month). Change a ROOTS label in column B and every summary updates.')
MAP = [
  ('Cash Income', ['Billable Expense Income', 'Construction Income', 'Design Income', 'Discounts/Refunds Given', 'Unapplied Cash Payment Income']),
  ('Overhead', ['Non-Payroll', 'Payroll', '6010 Office Rent', '6020 Office Utilities', '6030 Office Repair & Maintenance', '6040 Office Supplies', '6050 Telephone & Communications', '6060 Postage & Shipping', '6150 Auto Registration', '6160 Auto Fees', '6240 Workers Compensation', '6241 Health Insurance', '6242 D&O Insurance', '6243 Property Insurance', '6310 Monthly Subscriptions', '6320 Annual Subscriptions', '6410 Project Manager', '6430 Office & Admin', '6440 Design & Drafting Staff', '6463 Payroll Fees', '6464 Payroll Taxes', '6810 Software & Apps', '6830 Computer Maintenance', '6911 Professional Fees', '6940 Tax Prep & Tax Filing', '6960 Bookkeeping & Accounting']),
  ('Project Costs', ['5100 Materials & Supplies', '5200 Merchant Fees', '5201 Blueprints and Reproduction', '5400 Subcontractor Costs', '5600 Freight & Shipping', '5700 Equipment Rental - Job Site', '5800 Permits & Inspection Fees - Project', '5801 Sanitation and Waste Disposal', '5900 Travel & Lodging', 'Fence', 'Hardscape', 'Landscape', 'Pool', '6601 Bank & Credit Card Fees', '6610 Bank Fees', '6640 Credit Card Fees', '6751 Parking']),
  ('Operations', ['6120 Gas & Fuel', '6140 Auto Repair & Maintenance', '6910 Legal Fees']),
  ('Debt', ['6620 Interest Fees']),
  ('Taxes', ['6952 State Franchise Tax', '6953 State Filing Fees', '6954 City Tax']),
  ('Reinvested', ['6530 Client Acquisition', '6710 Airfare', '6720 Hotel', '6750 Travel Transportation', '6861 Website Redesign & Development', '6852 Research & Development', '6853 Photoshoot & Advertising', 'Meals and Entertainment']),
  ('Owner Pay', ['DMCS', 'JLI', "6462 Owner's Wages & Salaries"]),
  ('Leakage', ['Bad Debt Expense']),
  ('Timing', ['Unapplied Cash Bill Payment Expense']),
  ('Other Income', ['Cashback & Rewards', 'Interest Income', 'Merchant Surcharge Income']),
]
bs_ltl = [264850.12, 260852.33, 251729.12, 243348.44, 236609.23, 227700.30, 220032.74, 208302.81, 204279.06]
bs_draw = [4077.27, 8520.77, 11759.55, 17922.78, 28421.17, 32524.86, 36079.82, 40416.51, 46399.73]
diff = lambda a: [None] + [round(a[i] - a[i-1], 2) for i in range(1, len(a))]
charity = [plc['Charitable Contributions'][m] for m in MONTHS]
personal = [0] * 8 + [3500]
accr_billed = [plm['Total for Income'].get(m, 0) for m in MONTHS]
EXTRA = [
  ('Owner Pay', 'Owner draws (Balance Sheet change)', [bs_draw[0]] + diff(bs_draw)[1:], 'Jan assumes the draw account started 2026 at $0.'),
  ('Owner Pay', 'Personal donation reclass (9/1 JE)', personal, '$3,500 "donation to my son\'s school" is personal. Moved from Charitable Contributions.'),
  ('Reinvested', 'Charitable Contributions (business)', [c - p for c, p in zip(charity, personal)], 'Charitable Contributions less the personal donation.'),
  ('Debt', 'Loan principal paid (Balance Sheet change)', [0] + [-x for x in diff(bs_ltl)[1:]], 'Jan unknown: need the Dec 2025 balance sheet. Sept is missing 3 payments (REVIEW).'),
  ('Billed (accrual)', 'Invoices billed (accrual P&L, info only)', accr_billed, 'From the accrual P&L by Month. Not part of the cash math.'),
]
header(wsD, 4, ['Account', 'ROOTS label'] + MONTHS + ['YTD', 'Note'])
r = 5
for cat, accts in MAP:
    for a in accts:
        vals = plc[a]
        put(wsD, r, 1, a); put(wsD, r, 2, cat, f_in)
        for m in MONTHS: put(wsD, r, ord(MC[m]) - 64, vals[m], f_in, CUR)
        put(wsD, r, 12, f'=SUM(C{r}:K{r})', f_bb, CUR)
        if cat == 'Timing': put(wsD, r, 13, 'REVIEW: bill payments not applied to bills. They lower cash-basis expenses (Sept −$94,602).', f_sub)
        if a == 'Unapplied Cash Payment Income': put(wsD, r, 13, 'REVIEW: customer payments not applied to invoices.', f_sub)
        r += 1
for cat, name, vals, note in EXTRA:
    put(wsD, r, 1, name); put(wsD, r, 2, cat, f_in)
    for i, m in enumerate(MONTHS): put(wsD, r, 3 + i, vals[i] if vals[i] is not None else 0, f_in, CUR)
    put(wsD, r, 12, f'=SUM(C{r}:K{r})', f_bb, CUR); put(wsD, r, 13, note, f_sub); r += 1
DATA_LAST = r - 1
r += 1
put(wsD, r, 1, 'QBO Net Income, cash basis (check)', f_bb); put(wsD, r, 2, 'Check', f_in)
for m in MONTHS: put(wsD, r, ord(MC[m]) - 64, plc['Net Income'][m], f_in, CUR)
put(wsD, r, 12, f'=SUM(C{r}:K{r})', f_bb, CUR); put(wsD, r, 13, 'Cash-basis Net Operating Income YTD is $649,907.85. Net Income after other income/expenses is this row.', f_sub); NI_ROW = r; r += 1
put(wsD, r, 1, 'Mapped Net Income (should match)', f_bb)
for i, m in enumerate(MONTHS):
    col = MC[m]; rng = lambda lab: f'SUMIFS({col}$5:{col}${DATA_LAST},$B$5:$B${DATA_LAST},"{lab}")'
    excl = f'SUMIFS({col}$5:{col}${DATA_LAST},$A$5:$A${DATA_LAST},"Owner draws (Balance Sheet change)")+SUMIFS({col}$5:{col}${DATA_LAST},$A$5:$A${DATA_LAST},"Loan principal paid (Balance Sheet change)")'
    f = (f'={rng("Cash Income")}+{rng("Other Income")}-({rng("Overhead")}+{rng("Project Costs")}+{rng("Operations")}+{rng("Debt")}+{rng("Taxes")}+{rng("Reinvested")}+{rng("Owner Pay")}+{rng("Leakage")}+{rng("Timing")})+({excl})')
    put(wsD, r, 3 + i, f, f_b, CUR)
put(wsD, r, 12, f'=SUM(C{r}:K{r})', f_bb, CUR); put(wsD, r, 13, 'Difference row below must be 0.', f_sub); r += 1
put(wsD, r, 1, 'Difference', f_bb)
for i in range(10): put(wsD, r, 3 + i, f'={chr(67+i)}{r-2}-{chr(67+i)}{r-1}', f_bb, CUR)
r += 2
put(wsD, r, 1, 'QBO Net Income, accrual basis (info)', f_bb); put(wsD, r, 2, 'Info', f_in)
for m in MONTHS: put(wsD, r, ord(MC[m]) - 64, plm['Net Income'].get(m, 0), f_in, CUR)
put(wsD, r, 12, f'=SUM(C{r}:K{r})', f_bb, CUR); put(wsD, r, 13, 'Used for the balance sheet bridge (YTD Snapshot).', f_sub); ACC_NI_ROW = r
widths(wsD, {'A': 40, 'B': 14, 'L': 13, 'M': 80, **{MC[m]: 12 for m in MONTHS}})
wsD.freeze_panes = 'C5'
DR = f'$B$5:$B${DATA_LAST}'
def dsum(col, lab): return f'SUMIFS(Data!{col}$5:{col}${DATA_LAST},Data!{DR},"{lab}")'

# =====================================================================
# YTD SUMMARY
title(wsY, f'{CLIENT}: YTD Summary vs. Goal (Jan – Sep 2026, cash basis)', 'Fixed lines (overhead, taxes) are compared in dollars. Flex lines (project costs, operations, debt, reinvested, owner pay, cash kept) are compared as a % of cash collected that month.')
header(wsY, 4, ['Line', 'Rule'] + MONTHS + ['YTD actual', 'YTD goal / allowed', 'Over / (under)', 'Status'])
put(wsY, 5, 1, 'Month #', f_sub); [put(wsY, 5, 3 + i, i + 1, f_sub) for i in range(9)]
Y = {}
def yrow(r, label, rule, fn, bold=False, fmt=CUR):
    put(wsY, r, 1, label, f_bb if bold else f_b); put(wsY, r, 2, rule, f_sub)
    for i, m in enumerate(MONTHS): put(wsY, r, 3 + i, fn(MC[m]), f_bb if bold else f_b, fmt)
    put(wsY, r, 12, f'=SUM(C{r}:K{r})', f_bb, fmt)
    Y[label] = r
r = 7; put(wsY, r - 1, 1, 'ACTUAL', f_h)
yrow(r, 'Billed', 'Invoices (accrual, info)', lambda c: '=' + dsum(c, 'Billed (accrual)')); r += 1
yrow(r, 'Change in A/R', 'Billed − collected (info)', lambda c: f'={c}{Y["Billed"]}-{c}{r+1}'); r += 1
yrow(r, 'Cash collected', 'Cash-basis income', lambda c: '=' + dsum(c, 'Cash Income'), True); r += 1
for lab, key in [('Overhead', 'Overhead'), ('Project costs', 'Project Costs'), ('Operations', 'Operations'), ('Debt', 'Debt'), ('Taxes', 'Taxes'), ('Reinvested', 'Reinvested'), ('Owner pay', 'Owner Pay'), ('Leakage', 'Leakage'), ('Timing', 'Timing')]:
    yrow(r, lab, 'Unapplied bill payments (REVIEW)' if lab == 'Timing' else 'Paid (cash basis)', lambda c, key=key: '=' + dsum(c, key)); r += 1
yrow(r, 'Cash kept', 'Cash − everything above', lambda c: f'={c}{Y["Cash collected"]}-SUM({c}{Y["Overhead"]}:{c}{Y["Timing"]})', True); r += 2
put(wsY, r, 1, 'GOAL / ALLOWED', f_h); r += 1
GA = {}
def grow(label, rule, fn):
    global r
    put(wsY, r, 1, label); put(wsY, r, 2, rule, f_sub)
    for i, m in enumerate(MONTHS): put(wsY, r, 3 + i, fn(MC[m]), f_b, CUR)
    put(wsY, r, 12, f'=SUM(C{r}:K{r})', f_bb, CUR); GA[label] = r; r += 1
oh = lambda c: f"({B['oh_base']}+IF({c}$5>={B['oh_start']},{B['oh_add']},0))"
grow('Cash collected', 'Goal', lambda c: f"={B['cash_goal']}")
grow('Breakeven', 'Overhead + debt', lambda c: f"=({oh(c)}+{B['debt']})/(1-{B['p_cogs']}-{B['p_ops']})")
grow('Overhead', 'Fixed $ (new hires from Sep)', lambda c: '=' + oh(c))
grow('Project costs', '40% of cash', lambda c: f"={c}{Y['Cash collected']}*{B['p_cogs']}")
grow('Operations', '2% of cash', lambda c: f"={c}{Y['Cash collected']}*{B['p_ops']}")
grow('Debt', '1% of cash', lambda c: f"={c}{Y['Cash collected']}*{B['p_debt']}")
grow('Debt (fixed $)', 'Fixed $10,000/month', lambda c: f"={B['debt']}")
grow('Taxes', 'Fixed $', lambda c: f"={B['tax_m']}")
grow('Reinvested', '1.8% of cash', lambda c: f"={c}{Y['Cash collected']}*{B['p_reinv']}")
grow('Owner pay', '13.5% of cash', lambda c: f"={c}{Y['Cash collected']}*{B['p_owner']}")
grow('Leakage', 'Target $0', lambda c: f"={B['leak']}")
grow('Timing', 'Target $0 (apply payments)', lambda c: '=0')
grow('Cash kept', '2.87% of cash', lambda c: f"={c}{Y['Cash collected']}*{B['p_kept']}")
# YTD compare columns on ACTUAL rows
for lab in ['Cash collected', 'Overhead', 'Project costs', 'Operations', 'Debt', 'Taxes', 'Reinvested', 'Owner pay', 'Leakage', 'Timing', 'Cash kept']:
    ra, rg = Y[lab], GA[lab]
    put(wsY, ra, 13, f'=L{rg}', f_b, CUR); put(wsY, ra, 14, f'=L{ra}-M{ra}', f_bb, CUR)
    if lab in ('Cash collected', 'Cash kept'):
        put(wsY, ra, 15, f'=IF(N{ra}>=0,"On goal","Short "&TEXT(-N{ra},"$#,##0"))', f_bb)
    else:
        put(wsY, ra, 15, f'=IF(N{ra}>0,"Over "&TEXT(N{ra},"$#,##0"),"Under "&TEXT(-N{ra},"$#,##0"))', f_bb)
status_colors(wsY, f'O{Y["Cash collected"]}:O{Y["Cash kept"]}')
r += 1; put(wsY, r, 1, 'OVER / (UNDER) BY MONTH', f_h); r += 1
for lab in ['Cash collected', 'Overhead', 'Project costs', 'Operations', 'Reinvested', 'Owner pay']:
    put(wsY, r, 1, lab); put(wsY, r, 2, 'Actual − goal', f_sub)
    for i, m in enumerate(MONTHS): put(wsY, r, 3 + i, f'={MC[m]}{Y[lab]}-{MC[m]}{GA[lab]}', f_b, CUR)
    put(wsY, r, 12, f'=SUM(C{r}:K{r})', f_bb, CUR); r += 1
r += 1
put(wsY, r, 1, 'Notes', f_h); r += 1
for t in ['January cash collected equals billed. Send the December 2025 balance sheet to correct January A/R and loan principal.',
          'Costs are what was recorded (accrual). The budget is cash-based, so a bill recorded but not yet paid still counts here.',
          'Owner pay includes owner draws and the $3,500 personal donation moved out of Charitable Contributions.']:
    put(wsY, r, 1, t, f_sub); r += 1
widths(wsY, {'A': 18, 'B': 22, 'L': 13, 'M': 14, 'N': 13, 'O': 18, **{MC[m]: 11.5 for m in MONTHS}})
wsY.freeze_panes = 'C6'

# =====================================================================
# MONTHLY SUMMARY (September)
SEP = 'K'
title(wsM, f'{CLIENT}: {PERIOD} Money Report', 'Business Management · Compared with the ROOTS budget · DRAFT: books not final')
put(wsM, 4, 1, 'Key numbers', f_h)
key = [
    ('Billed', f"='YTD Summary'!{SEP}{Y['Billed']}"),
    ('Cash collected', f"='YTD Summary'!{SEP}{Y['Cash collected']}"),
    ('Cash collected goal', f"='YTD Summary'!{SEP}{GA['Cash collected']}"),
    ('Breakeven (with new hires)', f"='YTD Summary'!{SEP}{GA['Breakeven']}"),
    ('Over / (short of) breakeven', '=B6-B8'),
    ('Bank cash change this month', -213522.80),
    ('Credit cards paid down', 89669.72),
]
for i, (lab, f) in enumerate(key):
    rr = 5 + i; put(wsM, rr, 1, lab); put(wsM, rr, 2, f, f_in if isinstance(f, float) else f_link, CUR)
wsM['B10'].comment = Comment('Balance Sheet: total bank accounts Aug $410,350.46 → Sep $196,827.66', 'Financial Reviewer')
wsM['B11'].comment = Comment('Balance Sheet: credit cards Aug $165,187.03 → Sep $75,517.31', 'Financial Reviewer')
put(wsM, 13, 1, 'ROOTS scorecard: budget vs. actual', f_h)
header(wsM, 14, ['ROOTS', 'Line', 'Rule', 'Allowed / goal', 'Actual', 'Over / (under)', '% of cash collected', 'Status'])
sc = [('R', 'Cash collected', 'Goal'), ('O', 'Overhead', 'Fixed $ (with new hires)'), ('O', 'Project costs', '40% of cash'),
      ('O', 'Operations', '2% of cash'), ('O', 'Debt', '1% of cash'), ('T', 'Taxes', 'Fixed $ (entity taxes paid)'),
      ('S', 'Reinvested', '1.8% of cash'), ('S', 'Owner pay', '13.5% of cash'), ('S', 'Leakage', 'Target $0'), ('S', 'Timing', 'Unapplied bill payments'), ('S', 'Cash kept', '2.87% of cash')]
for i, (rt, lab, rule) in enumerate(sc):
    rr = 15 + i
    put(wsM, rr, 1, rt, f_bb); put(wsM, rr, 2, lab); put(wsM, rr, 3, rule, f_sub)
    put(wsM, rr, 4, f"='YTD Summary'!{SEP}{GA[lab]}", f_link, CUR); put(wsM, rr, 5, f"='YTD Summary'!{SEP}{Y[lab]}", f_link, CUR)
    put(wsM, rr, 6, f'=E{rr}-D{rr}', f_bb, CUR); put(wsM, rr, 7, f'=IF($E$15=0,"",E{rr}/$E$15)', f_b, PCT)
    if lab in ('Cash collected', 'Cash kept'):
        put(wsM, rr, 8, f'=IF(F{rr}>=0,"On goal","Short")', f_bb)
    else:
        put(wsM, rr, 8, f'=IF(F{rr}>0,"Over","Under")', f_bb)
status_colors(wsM, 'H15:H25')
put(wsM, 26, 1, 'Taxes: what to set aside for 2026 so far', f_h)
put(wsM, 27, 1, 'Estimate. Each related-entity payout is taxed as one single filer\'s pass-through income: annualized, then the YTD share is shown. Subtract any estimated payments already made. Not included: owner W-2 wages and each owner\'s share of JVP profit (need ownership %).', f_sub)
header(wsM, 28, ['Who', 'YTD income', 'Annualized', 'CA 1.5% entity tax (YTD)', 'Federal taxable (annual)', 'Federal tax (YTD)', 'CA taxable (annual)', 'CA tax (YTD)', 'Set aside YTD'])
mf = f"{B['months']}/12"
tax_rows = [('JVP net profit (cash basis)', f'=Data!L{NI_ROW}', False),
            ('DMCS (pass-through)', '=SUMIFS(Data!$L$5:$L$%d,Data!$A$5:$A$%d,"DMCS")' % (DATA_LAST, DATA_LAST), True),
            ('Johnston Landscapes (pass-through)', '=SUMIFS(Data!$L$5:$L$%d,Data!$A$5:$A$%d,"JLI")' % (DATA_LAST, DATA_LAST), True)]
for i, (lab, src, ind) in enumerate(tax_rows):
    rr = 29 + i
    put(wsM, rr, 1, lab); put(wsM, rr, 2, src, f_link, CUR)
    put(wsM, rr, 3, f"=B{rr}*12/{B['months']}", f_b, CUR)
    put(wsM, rr, 4, f"=B{rr}*{B['ca_corp']}", f_b, CUR)
    if ind:
        put(wsM, rr, 5, f"=MAX(0,C{rr}-C{rr}*{B['ca_corp']}-{B['fed_std']})", f_b, CUR)
        put(wsM, rr, 6, f"=SUMPRODUCT((E{rr}>{fed_lo})*(E{rr}-{fed_lo})*{fed_step})*{mf}", f_b, CUR)
        put(wsM, rr, 7, f"=MAX(0,C{rr}-{B['ca_std']})", f_b, CUR)
        put(wsM, rr, 8, f"=SUMPRODUCT((G{rr}>{ca_lo})*(G{rr}-{ca_lo})*{ca_step})*{mf}", f_b, CUR)
    else:
        for cc in (5, 6, 7, 8): put(wsM, rr, cc, 0, f_b, CUR)
    put(wsM, rr, 9, f'=D{rr}+F{rr}+H{rr}', f_bb, CUR)
put(wsM, 32, 1, 'Total', f_bb, fill=fill_band)
for cc in (2, 4, 6, 8, 9):
    col = chr(64 + cc); put(wsM, 32, cc, f'=SUM({col}29:{col}31)', f_bb, CUR, fill_band)
put(wsM, 34, 1, 'What worked · What didn\'t', f_h)
ww = ['Worked: overhead stayed under budget, even with the 2 new hires.',
      'Worked: credit cards were paid down by $89,670.',
      'Didn\'t work: owner pay ran over 13.5% of cash collected.',
      'Didn\'t work: 8 jobs had costs but no invoice (see Job Profit tab).']
for i, t in enumerate(ww): put(wsM, 35 + i, 1, t)
put(wsM, 40, 1, 'Your 3 decisions for October', f_h)
dec = ['1. Collect the $112,346 that is 31–90 days late, starting with Erin Whitely ($52,700, 61–90 days), before October 15.',
       '2. Bill the 8 jobs with costs but no invoice, starting with 700 Riven Rock Dr ($6,759).',
       '3. Set October owner pay at 13.5% of cash collected. Hold reinvestment to 1.8%, operations to 2%, and debt to 1%.']
for i, t in enumerate(dec): put(wsM, 41 + i, 1, t, f_bb)
widths(wsM, {'A': 30, 'B': 16, 'C': 24, 'D': 16, 'E': 16, 'F': 16, 'G': 16, 'H': 16, 'I': 14})

# =====================================================================
# YTD SNAPSHOT (simple): goal vs actual + how much of the taxed profit is cash
title(wsS, f'{CLIENT}: YTD Snapshot (Jan – Sep 2026)', 'Goal vs. actual, and where this year\'s profit is sitting.')
put(wsS, 4, 1, '1. Goal vs. actual', f_h)
header(wsS, 5, ['Line', 'Goal', 'Goal $', 'Actual $', 'Over / (under)', 'Status'])
snap = [('Revenue (cash collected)', 'Cash collected', 'Cash collected', '$728,348 a month'),
        ('Overhead', 'Overhead', 'Overhead', 'Fixed amount'),
        ('Project costs', 'Project costs', 'Project costs', '40% of cash collected'),
        ('Operations', 'Operations', 'Operations', '2% of cash collected'),
        ('Debt', 'Debt', 'Debt', '1% of cash collected'),
        ('Debt (fixed payments)', 'Debt (fixed $)', 'Debt', '$10,000 a month'),
        ('Reinvested / discretionary', 'Reinvested', 'Reinvested', '1.8% of cash collected'),
        ('Owner pay', 'Owner pay', 'Owner pay', '13.5% of cash collected')]
for i, (lab, g, a, rule) in enumerate(snap):
    rr = 6 + i
    put(wsS, rr, 1, lab, f_bb); put(wsS, rr, 2, rule, f_b)
    put(wsS, rr, 3, f"='YTD Summary'!L{GA[g]}", f_link, CUR); put(wsS, rr, 4, f"='YTD Summary'!L{Y[a]}", f_link, CUR)
    put(wsS, rr, 5, f'=D{rr}-C{rr}', f_bb, CUR)
    put(wsS, rr, 6, f'=IF(E{rr}>=0,"On goal","Short")' if i == 0 else f'=IF(E{rr}>0,"Over","Under")', f_bb)
status_colors(wsS, 'F6:F13')

put(wsS, 15, 1, '2. This year\'s profit: how much is cash you can use?', f_h)
put(wsS, 16, 1, 'Profit you\'ll pay tax on (Jan – Sep)', f_bb); put(wsS, 16, 4, f'=Data!L{NI_ROW}', f_link, CUR)
put(wsS, 17, 1, 'Cash in the bank you can use today', f_bb); put(wsS, 17, 4, 170607.66, f_in, CUR); put(wsS, 17, 5, '=IF(D16=0,"",D17/D16)', f_bb, PCT)
put(wsS, 17, 6, 'of the profit', f_sub)
put(wsS, 18, 1, 'Profit that is NOT cash you can use', f_bb, fill=fill_band); put(wsS, 18, 4, '=D16-D17', f_bb, CUR, fill_band); put(wsS, 18, 5, '=IF(D16=0,"",D18/D16)', f_bb, PCT, fill_band)

put(wsS, 20, 1, 'Where the rest of the profit went', f_h)
header(wsS, 21, ['Where it is', 'Amount', '% of profit', 'Lowers your taxes?', 'Cash you can use?', 'What it means'])
WH = [
 ('Escrow account', 288139.71, 'No', 'Not until released', 'Set aside for the building.'),
 ('Undeposited funds', 119830.00, 'No', 'Not yet', 'Check: sitting there since May.'),
 ('Petty cash', 26220.00, 'No', 'Check', 'Confirm this cash really exists.'),
 ('Paid down credit cards', 57249.84, 'No', 'No', 'Less debt. Expenses were already written off.'),
 ('Paid down truck and equipment loans', 60571.06, 'No (only interest)', 'No', 'Less debt. Loan payoff isn\'t a write-off.'),
 ('Owner draws', f"=SUMIFS(Data!$L$5:$L${DATA_LAST},Data!$A$5:$A${DATA_LAST},\"Owner draws (Balance Sheet change)\")", 'No', 'No', 'Money the owners took out.'),
 ('Loaned to DMCS and Johnston Landscape', 18017.00, 'No', 'Only if paid back', 'They owe JVP this money.'),
 ('Payroll still owed (not paid yet)', -54702.69, 'Already written off', 'Must still be paid', 'This cash is spoken for.'),
 ('State tax refund received', -44136.00, 'No', 'Already in the bank', 'One-time money, not profit.'),
]
r = 22; W0 = r
for lab, amt, tax, cash, means in WH:
    put(wsS, r, 1, lab, f_bb); put(wsS, r, 2, amt, f_link if isinstance(amt, str) else f_in, CUR)
    put(wsS, r, 3, f'=IF($D$16=0,"",B{r}/$D$16)', f_b, PCT)
    put(wsS, r, 4, tax); put(wsS, r, 5, cash); put(wsS, r, 6, means, f_b)
    r += 1
put(wsS, r, 1, 'Cash from before 2026, January, and unapplied payments', f_bb)
put(wsS, r, 2, f'=D18-SUM(B{W0}:B{r-1})', f_b, CUR); put(wsS, r, 3, f'=IF($D$16=0,"",B{r}/$D$16)', f_b, PCT)
put(wsS, r, 4, '—'); put(wsS, r, 5, '—'); put(wsS, r, 6, 'Exact once we have the Dec 31, 2025 balance sheet.', f_b); r += 1
put(wsS, r, 1, 'Total (equals profit that is not usable cash)', f_bb, fill=fill_band)
put(wsS, r, 2, f'=SUM(B{W0}:B{r-1})', f_bb, CUR, fill_band); put(wsS, r, 3, f'=IF($D$16=0,"",B{r}/$D$16)', f_bb, PCT, fill_band); r += 2
put(wsS, r, 1, 'Negative amounts are cash that came in or is owed, not profit.', f_sub)
put(wsS, r + 1, 1, 'Amounts are Sep 30 balances or changes since Jan 31 (Balance Sheet by Month).', f_sub)
widths(wsS, {'A': 42, 'B': 22, 'C': 15, 'D': 20, 'E': 20, 'F': 44})
wsS.freeze_panes = 'A6'

# =====================================================================
# TAX PLANNING (separate tab): tax on profit vs cash, depreciation, building
wsT = wb.create_sheet('Tax Planning', index=wb.sheetnames.index('Client Requests'))
wsT.sheet_view.showGridLines = False
title(wsT, f'{CLIENT}: Tax Planning (estimates)', 'Estimates only. Confirm with the CPA before acting.')
put(wsT, 4, 1, 'Tax on this year\'s profit vs. cash in the bank', f_h)
mf = f"{B['months']}/12"
put(wsT, 5, 1, 'Profit you\'ll pay tax on (Jan – Sep)'); put(wsT, 5, 3, f"='YTD Snapshot'!D16", f_link, CUR)
put(wsT, 6, 1, 'Company tax (California 1.5%)'); put(wsT, 6, 3, f"=C5*{B['ca_corp']}", f_b, CUR)
for i, (who, own) in enumerate([('Johnston', 'own_j'), ('Vidal', 'own_v')]):
    rr = 7 + i
    ann = f"(C5*{B[own]}*(1-{B['ca_corp']})*12/{B['months']})"
    fed = f"SUMPRODUCT((MAX(0,{ann}-{B['fed_std']})>{fed_lo})*(MAX(0,{ann}-{B['fed_std']})-{fed_lo})*{fed_step})*{mf}"
    ca = f"SUMPRODUCT((MAX(0,{ann}-{B['ca_std']})>{ca_lo})*(MAX(0,{ann}-{B['ca_std']})-{ca_lo})*{ca_step})*{mf}"
    put(wsT, rr, 1, f'{who}: personal tax on 50% of the profit'); put(wsT, rr, 3, f'={fed}+{ca}', f_b, CUR)
put(wsT, 9, 1, 'Total tax on the profit', f_bb, fill=fill_band); put(wsT, 9, 3, '=SUM(C6:C8)', f_bb, CUR, fill_band)
put(wsT, 10, 1, 'Cash in the bank you can use'); put(wsT, 10, 3, "='YTD Snapshot'!D17", f_link, CUR)
put(wsT, 11, 1, 'Left after setting the tax aside', f_bb, fill=fill_band); put(wsT, 11, 3, '=C10-C9', f_bb, CUR, fill_band)
put(wsT, 12, 1, 'No 2026 estimated payments made. Next due date: Jan 15, 2027.', f_sub)
put(wsT, 14, 1, 'Depreciation: current trucks and equipment', f_h)
put(wsT, 15, 1, 'Original cost'); put(wsT, 15, 3, 637636.23, f_in, CUR)
put(wsT, 16, 1, 'Already written off'); put(wsT, 16, 3, 599145.95, f_in, CUR)
put(wsT, 17, 1, 'Most you can write off in 2026', f_bb, fill=fill_band); put(wsT, 17, 3, '=C15-C16', f_bb, CUR, fill_band)
put(wsT, 18, 1, 'The CPA\'s depreciation schedule sets the real number.', f_sub)
put(wsT, 20, 1, 'Commercial building scenario', f_h)
TB = [('Purchase price', 2000000, CUR, True), ('Land share (can\'t be written off)', 0.25, CENT, True),
      ('Building value you can write off', '=C21*(1-C22)', CUR, False), ('Month you start using it (1–12)', 11, '0', True),
      ('Share a cost study moves to fast write-off', 0.20, CENT, True),
      ('2026 federal write-off', '=C23*C25+C23*(1-C25)/39*(12-C24+0.5)/12', CUR, False),
      ('Federal tax saved in 2026 (35% rate)', '=(C26+C17)*0.35', CUR, False),
      ('Loan needed after escrow down payment', "=C21-'YTD Snapshot'!B22", CUR, False), ('Interest rate', 0.07, CENT, True), ('Loan years', 25, '0', True),
      ('Monthly loan payment', '=PMT(C29/12,C30*12,-C28)', CUR, False), ('Debt allowed (1% of cash goal)', f"={B['cash_goal']}*{B['p_debt']}", CUR, False)]
for i, (lab, v, fmt, inp) in enumerate(TB):
    rr = 21 + i
    put(wsT, rr, 1, lab, f_b); put(wsT, rr, 3, v, f_in if inp else f_bb, fmt, fill_in if inp else None)
put(wsT, 33, 1, 'California does not allow the fast write-off, so the state savings are much smaller.', f_sub)
widths(wsT, {'A': 46, 'B': 4, 'C': 18})


# =====================================================================
# QUARTERLY SUMMARY (Q3)
title(wsQ, f'{CLIENT}: Q3 2026 Summary (Jul – Sep) + Q4 Focus', 'Q3 actual vs. goal, the #1 constraint, and what to focus on next quarter.')
header(wsQ, 4, ['Line', 'Q3 goal / allowed', 'Q3 actual', 'Over / (under)', 'Status', 'Q2 actual'])
ql = ['Billed', 'Cash collected', 'Breakeven', 'Overhead', 'Project costs', 'Operations', 'Reinvested', 'Owner pay', 'Cash kept']
for i, lab in enumerate(ql):
    rr = 5 + i
    put(wsQ, rr, 1, lab)
    if lab == 'Billed':
        put(wsQ, rr, 2, '', f_b); put(wsQ, rr, 3, f"=SUM('YTD Summary'!I{Y[lab]}:K{Y[lab]})", f_link, CUR)
        put(wsQ, rr, 6, f"=SUM('YTD Summary'!F{Y[lab]}:H{Y[lab]})", f_link, CUR)
        put(wsQ, rr, 5, '=IF(F5=0,"",TEXT(C5/F5-1,"0%")&" vs Q2")', f_bb); continue
    if lab == 'Breakeven':
        put(wsQ, rr, 2, f"=SUM('YTD Summary'!I{GA[lab]}:K{GA[lab]})", f_link, CUR); put(wsQ, rr, 3, '=C6', f_b, CUR)
        put(wsQ, rr, 4, f'=C{rr}-B{rr}', f_bb, CUR); put(wsQ, rr, 5, f'=IF(D{rr}>=0,"Above breakeven","Short")', f_bb); continue
    put(wsQ, rr, 2, f"=SUM('YTD Summary'!I{GA[lab]}:K{GA[lab]})", f_link, CUR)
    put(wsQ, rr, 3, f"=SUM('YTD Summary'!I{Y[lab]}:K{Y[lab]})", f_link, CUR)
    put(wsQ, rr, 6, f"=SUM('YTD Summary'!F{Y[lab]}:H{Y[lab]})", f_link, CUR)
    put(wsQ, rr, 4, f'=C{rr}-B{rr}', f_bb, CUR)
    put(wsQ, rr, 5, f'=IF(D{rr}>=0,"On goal","Short")' if lab in ('Cash collected', 'Cash kept') else f'=IF(D{rr}>0,"Over","Under")', f_bb)
status_colors(wsQ, 'E5:E13')
put(wsQ, 15, 1, 'The 5 things that can hold a business back', f_h)
header(wsQ, 16, ['Area', 'What the numbers show', '', '', 'Is this the block?'])
cons = [('Leads', 'Billing fell vs. Q2. Cash collected was about 74% of goal. Marketing spend was 58% of its budget.', 'YES: most likely #1'),
        ('Conversions', 'The books don\'t track proposals sent or jobs won.', 'Unknown: need win rate'),
        ('Capacity', 'Crew and team costs ran at full budget while incoming work was below goal.', 'No: room for more work'),
        ('Cash', 'Collected 97¢ of every $1 billed in Q3. September slipped to 70¢.', 'Not #1: watch it'),
        ('Money Leakage', 'Project costs were under budget for the quarter. But jobs lost money in September and $18,754 of costs aren\'t tied to a job.', 'Second: fix at job level')]
for i, (a, b, c) in enumerate(cons):
    rr = 17 + i; put(wsQ, rr, 1, a, f_bb); put(wsQ, rr, 2, b, f_b, al=wrap); wsQ.merge_cells(f'B{rr}:D{rr}'); put(wsQ, rr, 5, c, f_bb)
    wsQ.row_dimensions[rr].height = 26
wsQ.conditional_formatting.add('E17:E21', FormulaRule(formula=['ISNUMBER(SEARCH("YES",E17))'], fill=fill_red))
put(wsQ, 23, 1, 'Q4 focus: bring in more work', f_h)
put(wsQ, 24, 1, 'Goal', f_bb); put(wsQ, 24, 2, 600000, f_in, CUR); put(wsQ, 24, 3, 'cash collected per month by December (step toward the $728,348 goal)', f_sub)
for i, t in enumerate(['1. Spend the full marketing budget ($5,122 a month) and count the leads it brings in.',
                       '2. Track leads, proposals sent, and jobs won every week.',
                       '3. Follow up on every open proposal older than 14 days.']):
    put(wsQ, 25 + i, 1, t, f_bb)
put(wsQ, 29, 1, 'What we track each month', f_h)
for i, t in enumerate(['Cash collected vs. goal and breakeven', 'Owner pay 13.5%, reinvested 1.8%, operations 2%, debt 1% of cash collected',
                       'New leads and jobs won (need from client)', 'Project costs per $1 collected (40¢ or less)', 'Jobs that lost money (target 0)']):
    put(wsQ, 30 + i, 1, t)
widths(wsQ, {'A': 22, 'B': 20, 'C': 18, 'D': 18, 'E': 24, 'F': 16})

# =====================================================================
# JOB PROFIT (MONTH)
CUST = {'4301 Manson': 'JP Richards -Manson (T&M)', '8410 Allenwood Rd.': 'Collaborative Construction', '1684 Hill': 'Adam Lisagor',
 '1375 Mendocino': 'Alex Azat / Alexandra Azat', '3015 Angus St': 'Graciella Sanchez', '2730 Creston Dr': 'Brad Basham',
 '1680 Hill': 'Adam Lisagor', '2307 St. George': 'Zeth Ajemian', '12360 MacDonald Dr': 'Shawn Skillern', '2169 W Live Oak': 'Michael Waldron',
 '23105 Collins Street': 'JP Richards', '16745 Bajio': 'Preston Robins (T&M)', '2326 Ewing St': 'Ryan Shaw', '2306 Kenilworth Ave': 'Josh Shenk',
 '1926 N Hobart': 'Amy Israel', '2521 Santa Anita': 'ALM Trust', '1321 New York Dr': 'Priya Satiani', '3441 Grand View': 'Cara Solomon',
 '1234 Beverly View': 'Paul & Jill Garnett', '3501 Crestmont Ave': 'Christina Ricci', '5646 Valley Oak Dr': 'Samuel Falls',
 '435 N Las Palmas': 'Elena & Ben Howell', '1831 Windsor Rd': 'Juliana Hung & Patrick Tang', '2516 Park Oak': 'Carlos Vela Prado',
 '213 N Gramercy': 'Matt Murray', '2052 Mayview Dr': 'Jason Vassiliades', '912 Kensington': 'Justin Givens',
 '2305 Kenilworth': 'Alexandra Lohse (confirm)', '975 Cliff Dr': 'Fred Taylor (confirm)', '2255 N Topanga Cyn': 'Charles Clouser',
 '2248 Kenilworth': 'Jessica Lamb Shapiro', '124 N Van Ness': 'Michael Schaefer', '2536 Boulder': 'Ross & Elise Johnson',
 '3908 Carnavon Way': 'Cody Marksohn', '2233 Glyndon': 'Luke McKelvey', '3122 Nichols Cyn': 'WCEC Trust', '1844 Upper Rim Rock': 'Erin Whitely'}
PAID = {'4301 Manson': 85782.43, '1684 Hill': 45000, '1680 Hill': 14000, '2307 St. George': 50813, '1375 Mendocino': 46384.35,
 '2730 Creston Dr': 37500, '3441 Grand View': 34550, '3908 Carnavon Way': 14281.17, '1926 N Hobart': 8548.47, '2169 W Live Oak': 7725,
 '2233 Glyndon': 7500, '213 N Gramercy': 4943.25, '2326 Ewing St': 3862.50, '2521 Santa Anita': 2832.50, '1234 Beverly View': 1000,
 '2052 Mayview Dr': 463.50, '2516 Park Oak': 336.81, '975 Cliff Dr': 257.50, '3122 Nichols Cyn': 39.75}
title(wsJ, f'{CLIENT}: Job Profit Report, {PERIOD}', 'Jobs worked on this month: what was billed, what was spent, and what cash came in. Blue = from QBO (P&L by Class; payments from the General Ledger).')
header(wsJ, 4, ['Job', 'Customer', 'Billed', 'Spent (job costs)', 'Job profit', 'Kept per $1', 'Cash collected this month', 'Overhead tagged', 'Net', 'Flag', 'Bill at least', 'Bill to reach target'])
ranked = sorted(jobs, key=lambda j: -j['gp'])
r = 5
for j in ranked:
    put(wsJ, r, 1, j['job']); put(wsJ, r, 2, CUST.get(j['job'], 'Unknown: confirm'), f_b)
    put(wsJ, r, 3, j['inc'], f_in, CUR); put(wsJ, r, 4, j['cogs'], f_in, CUR)
    put(wsJ, r, 5, f'=C{r}-D{r}', f_b, CUR); put(wsJ, r, 6, f'=IF(C{r}>0,E{r}/C{r},"")', f_b, PCT)
    put(wsJ, r, 7, PAID.get(j['job'], 0), f_in, CUR); put(wsJ, r, 8, j['exp'], f_in, CUR); put(wsJ, r, 9, f'=E{r}-H{r}', f_b, CUR)
    put(wsJ, r, 10, f'=IF(AND(C{r}=0,D{r}>0),"Bill now",IF(D{r}>C{r},"Billed below cost",IF(AND(C{r}>0,F{r}<{B["job_tgt"]}),"Under target","")))', f_bb)
    put(wsJ, r, 11, f'=IF(J{r}="Bill now",D{r},IF(J{r}="Billed below cost",D{r}-C{r},0))', f_b, CUR)
    put(wsJ, r, 12, f'=IF(J{r}="","",MAX(0,D{r}/(1-{B["job_tgt"]})-C{r}))', f_b, CUR)
    r += 1
JL = r - 1
put(wsJ, r, 1, 'Total: jobs', f_bb, fill=fill_band)
for cc in (3, 4, 5, 7, 8, 9, 11, 12):
    col = chr(64 + cc); put(wsJ, r, cc, f'=SUM({col}5:{col}{JL})', f_bb, CUR, fill_band)
put(wsJ, r, 6, f'=IF(C{r}>0,E{r}/C{r},"")', f_bb, PCT, fill_band); JT = r; r += 2
put(wsJ, r, 1, 'Not tied to a job this month', f_h); r += 1
nt = [('Job costs with no job class (COGS class, Not specified, Baijo, etc.)', 0, 18753.66, 'Fix in Corrections → Job Costing'),
      ('Unapplied deposit 9/14 (Inv 3789, 3906, 3866), no customer', 26557.12, 0, 'Fix in Corrections → A/R'),
      ('Travis Kuda (Construction): payment, no September job', 2575.00, 0, 'Confirm job')]
for lab, cash, cost, note in nt:
    put(wsJ, r, 1, lab); put(wsJ, r, 4, cost, f_in, CUR); put(wsJ, r, 7, cash, f_in, CUR); put(wsJ, r, 10, note, f_sub); r += 1
put(wsJ, r, 1, 'Total cash collected from customers (GL)', f_bb, fill=fill_band); put(wsJ, r, 7, f'=G{JT}+SUM(G{r-3}:G{r-1})', f_bb, CUR, fill_band)
put(wsJ, r, 10, 'Should equal $394,952 of customer payments in the GL.', f_sub); r += 2
put(wsJ, r, 1, 'Notes', f_h); r += 1
for t in ['Customer match: each customer\'s September invoices tie to the job\'s billing plus the 3% card surcharge. Two jobs are marked "confirm".',
          'Adam Lisagor paid $59,000, split across 1684 Hill ($45,000) and 1680 Hill ($14,000) to match the billing.',
          'Cash collected can pay for earlier months\' invoices, so it won\'t always match this month\'s billing.',
          'Negative job costs on design jobs come from card surcharges credited to Merchant Fees (a correction). Kept per $1 over 100% comes from that.']:
    put(wsJ, r, 1, t, f_sub); r += 1
wsJ.conditional_formatting.add(f'J5:J{JL}', FormulaRule(formula=['J5="Bill now"'], fill=fill_red))
wsJ.conditional_formatting.add(f'J5:J{JL}', FormulaRule(formula=['J5="Billed below cost"'], fill=fill_red))
wsJ.conditional_formatting.add(f'J5:J{JL}', FormulaRule(formula=['J5="Under target"'], fill=fill_amber))
widths(wsJ, {'A': 22, 'B': 28, 'C': 13, 'D': 14, 'E': 13, 'F': 10, 'G': 15, 'H': 12, 'I': 13, 'J': 17, 'K': 13, 'L': 14})
wsJ.freeze_panes = 'C5'; wsJ.auto_filter.ref = f'A4:L{JL}'

# =====================================================================
# OPEN JOBS
AJOB = {'Adam Lisagor (Construction)': '1684 Hill', 'Alexandra Azat (Design)': '1375 Mendocino', 'Alexandra Lohse (Design)': '2305 Kenilworth',
 'Amy Israel (design)': '1926 N Hobart', 'Basham Residence (Design)': '2730 Creston Dr', 'Cara Solomon (Construction)': '3441 Grand View',
 'Cara Solomon (Design)': '3441 Grand View', 'Carlos Vela Prado (Design)': '2516 Park Oak', 'Charles Clouser (Design)': '2255 N Topanga Cyn',
 'Christina Ricci (Design)': '3501 Crestmont Ave', 'Cody Marksohn (Design)': '3908 Carnavon Way', 'Collaborative Construction': '8410 Allenwood Rd.',
 'Elena Howell & Ben Howell (Design)': '435 N Las Palmas', 'Erin Whitely (Construction)': '1844 Upper Rim Rock', 'Fred Taylor (Design)': '975 Cliff Dr',
 'Graciella Sanchez (Construction)': '3015 Angus St', 'Jason Vassiliades (Design)': '2052 Mayview Dr', 'Jessica Lamb Shapiro (Design)': '2248 Kenilworth',
 'Josh Shenk (Construction)': '2306 Kenilworth Ave', 'Josh Shenk (Design)': '2306 Kenilworth Ave', 'JP Richards (Construction)': '23105 Collins Street',
 'JP Richards -Manson (T&M)': '4301 Manson', 'Juliana Hung & Patrick Tang (Design)': '1831 Windsor Rd', 'Justin Givens (Design)': '912 Kensington',
 'Luke McKelvey (Design)': '2233 Glyndon', 'Matt Murray (Design)': '213 N Gramercy', 'Michael Schaefer (Design)': '124 N Van Ness',
 'Michael Waldron (Design)': '2169 W Live Oak', 'Paul & Jill Garnett (Design)': '1234 Beverly View', 'Preston Robins (T&M)': '16745 Bajio',
 'Priya Satiani (Design)': '1321 New York Dr', 'Ross & Elise Johnson (Design)': '2536 Boulder', 'Samuel Falls (Design)': '5646 Valley Oak Dr',
 'Shawn Skillern (Design)': '12360 MacDonald Dr', 'WCEC Trust (Design)': '3122 Nichols Cyn', 'Zeth Ajemian (Construction)': '2307 St. George',
 'Zeth Ajemian (Design)': '2307 St. George', 'DMCS': 'Related party', 'D.W. Johnston Construction Inc.(Construction)': 'Related party?'}
title(wsO, f'{CLIENT}: Open Jobs Profitability', 'Every customer with an open balance on 9/30, plus jobs with costs but no invoice. Yellow columns: add contract and to-date numbers (P&L by Class, all dates) to see full-job profit.')
header(wsO, 4, ['Customer', 'Job', 'Open: 1–30', '31–60', '61–90', '91+', 'Total open A/R', 'Sept billed', 'Sept spent', 'Contract value', 'Billed to date', 'Spent to date', 'Profit to date', 'Kept per $1 to date', '% of contract billed', 'Next step'])
r = 5
JR = f"'Job Profit (Month)'!$A$5:$A${JL}"
for a in [x for x in aging if not x['customer'].startswith('TOTAL')]:
    job = AJOB.get(a['customer'], 'Not active in Sept')
    put(wsO, r, 1, a['customer']); put(wsO, r, 2, job)
    for i, k in enumerate(['1-30', '31-60', '61-90', '91+']): put(wsO, r, 3 + i, a.get(k, 0), f_in, CUR)
    put(wsO, r, 7, f'=SUM(C{r}:F{r})', f_bb, CUR)
    put(wsO, r, 8, f"=SUMIFS('Job Profit (Month)'!$C$5:$C${JL},{JR},B{r})", f_link, CUR)
    put(wsO, r, 9, f"=SUMIFS('Job Profit (Month)'!$D$5:$D${JL},{JR},B{r})", f_link, CUR)
    for cc in (10, 11, 12): put(wsO, r, cc, None, f_in, CUR, fill_in)
    put(wsO, r, 13, f'=IF(K{r}="","",K{r}-L{r})', f_b, CUR); put(wsO, r, 14, f'=IF(OR(K{r}="",K{r}=0),"",M{r}/K{r})', f_b, PCT)
    put(wsO, r, 15, f'=IF(OR(J{r}="",J{r}=0),"",K{r}/J{r})', f_b, PCT)
    put(wsO, r, 16, f'=IF(G{r}<0,"Apply credit / refund",IF(SUM(D{r}:F{r})>0,"Collect: "&TEXT(SUM(D{r}:F{r}),"$#,##0")&" past 30 days",IF(G{r}>0,"Current","")))', f_bb)
    r += 1
for j in [j for j in jobs if j['inc'] == 0 and j['cogs'] > 0]:
    put(wsO, r, 1, 'Unknown: confirm customer'); put(wsO, r, 2, j['job'])
    for cc in (3, 4, 5, 6): put(wsO, r, cc, 0, f_in, CUR)
    put(wsO, r, 7, f'=SUM(C{r}:F{r})', f_bb, CUR)
    put(wsO, r, 8, f"=SUMIFS('Job Profit (Month)'!$C$5:$C${JL},{JR},B{r})", f_link, CUR)
    put(wsO, r, 9, f"=SUMIFS('Job Profit (Month)'!$D$5:$D${JL},{JR},B{r})", f_link, CUR)
    for cc in (10, 11, 12): put(wsO, r, cc, None, f_in, CUR, fill_in)
    put(wsO, r, 13, f'=IF(K{r}="","",K{r}-L{r})', f_b, CUR); put(wsO, r, 14, f'=IF(OR(K{r}="",K{r}=0),"",M{r}/K{r})', f_b, PCT)
    put(wsO, r, 15, f'=IF(OR(J{r}="",J{r}=0),"",K{r}/J{r})', f_b, PCT)
    put(wsO, r, 16, 'Bill now: costs, no invoice', f_bb); r += 1
OL = r - 1
put(wsO, r, 1, 'Total', f_bb, fill=fill_band)
for cc in range(3, 8):
    col = chr(64 + cc); put(wsO, r, cc, f'=SUM({col}5:{col}{OL})', f_bb, CUR, fill_band)
put(wsO, r, 16, 'Total open A/R should equal $237,693.50 (A/R Aging 9/30).', f_sub)
wsO.conditional_formatting.add(f'P5:P{OL}', FormulaRule(formula=['ISNUMBER(SEARCH("Collect",P5))'], fill=fill_amber))
wsO.conditional_formatting.add(f'P5:P{OL}', FormulaRule(formula=['ISNUMBER(SEARCH("Bill now",P5))'], fill=fill_red))
wsO.conditional_formatting.add(f'P5:P{OL}', FormulaRule(formula=['ISNUMBER(SEARCH("credit",P5))'], fill=fill_red))
widths(wsO, {'A': 36, 'B': 20, 'C': 12, 'D': 11, 'E': 11, 'F': 11, 'G': 13, 'H': 12, 'I': 12, 'J': 13, 'K': 13, 'L': 13, 'M': 13, 'N': 11, 'O': 11, 'P': 30})
wsO.freeze_panes = 'C5'; wsO.auto_filter.ref = f'A4:P{OL}'

# =====================================================================
# CORRECTIONS (team draft)
title(wsC, f'{CLIENT}: Corrections ({PERIOD})', 'TEAM DRAFT: do not send until Ayrica approves. REVIEW items affect cash, so do them first. Update Status as items are fixed.')
header(wsC, 4, ['#', 'Section', 'Subsection', 'Correction (copy-paste ready)', 'Amount', 'Affects cash?', 'Status', 'Assigned to', 'Date fixed', 'Notes'])
CORR = [
 ('REVIEW: affects cash', '1. Balance Sheet General Corrections', 'Undeposited Funds has held $119,830.00 since May. Match it to bank deposits or clear the duplicates.', 119830.00),
 ('REVIEW: affects cash', '1. Balance Sheet General Corrections', 'BOA-4089 ends September at −$1,755.30. Confirm whether this is an overdraft or a missing transfer.', -1755.30),
 ('REVIEW: affects cash', '1. Balance Sheet General Corrections', 'Petty Cash shows $26,220.00. Confirm the actual cash on hand.', 26220.00),
 ('REVIEW: affects cash', '1. Balance Sheet General Corrections', 'Escrow shows $288,139.71. Tie it to the Glen Oaks Escrow statement. It jumped $232,825 in August.', 288139.71),
 ('REVIEW: affects cash', '1. Balance Sheet General Corrections', 'Due to DMCS is −$14,887.00, which means DMCS owes JVP. Confirm the balance.', -14887.00),
 ('REVIEW: affects cash', '1. Balance Sheet General Corrections', 'Due to Johnston Landscape is −$2,970.00 because JVP pays $495 a month in ADP 401K for Johnston Landscapes. Set up repayment or reclass.', -2970.00),
 ('REVIEW: affects cash', '1. Balance Sheet General Corrections', 'Unapplied Cash Bill Payment Expense is −$94,601.66 in September (−$94,271.66 YTD, cash basis). Apply these bill payments to their vendor bills. Until then, cash-basis expenses and taxable profit are off by this amount.', -94271.66),
 ('REVIEW: affects cash', '2. Accounts Receivable Corrections', 'Unapplied Cash Payment Income is −$14,188.48 YTD (cash basis; −$128,110 in Feb, +$140,144 in Apr). Apply customer payments to their invoices.', -14188.48),
 ('REVIEW: affects cash', '2. Accounts Receivable Corrections', 'The 9/14 deposit of $26,557.12 (TRUST DEPT) was posted to A/R with no customer. Apply it to Inv 3789 ($637.50), Inv 3906 ($225.00), and Inv 3866 ($25,694.62) under the correct customer.', 26557.12),
 ('REVIEW: affects cash', '2. Accounts Receivable Corrections', 'D.W. Johnston Construction shows a −$139,430.00 credit that is 91+ days old. Apply it to open invoices, or reclass it.', -139430.00),
 ('REVIEW: affects cash', '2. Accounts Receivable Corrections', 'Michael Balzary NKSFB LLC shows a −$6,375.00 credit. Apply it or reclass it.', -6375.00),
 ('REVIEW: affects cash', '2. Accounts Receivable Corrections', 'Emily Wassall shows a −$500.00 credit. Apply it or reclass it.', -500.00),
 ('REVIEW: affects cash', '2. Accounts Receivable Corrections', 'DMCS shows $15,184.00 in A/R (61–90 days). Confirm whether this is real or a duplicate of Due to DMCS.', 15184.00),
 ('REVIEW: affects cash', '3. Payroll Corrections', 'Other tax Payable is $16,920.08 and grows every month. Reconcile it to ADP.', 16920.08),
 ('REVIEW: affects cash', '3. Payroll Corrections', 'Other Deduction is $12,136.48 and grows every month. Reconcile it to ADP.', 12136.48),
 ('REVIEW: affects cash', '3. Payroll Corrections', 'Net Wages Payable is $38,853.26. Reconcile it to ADP and clear what was already paid.', 38853.26),
 ('REVIEW: affects cash', '4. Payments Missing', 'The Rivian R1T loan payment is missing for September. The balance has been $12,515.77 since August.', 12515.77),
 ('REVIEW: affects cash', '4. Payments Missing', 'The Chevrolet Tahoe loan payment is missing for September. The balance has been $48,233.76 since August.', 48233.76),
 ('REVIEW: affects cash', '4. Payments Missing', 'The Transit Van loan payment is missing for September. The balance has been $37,679.76 since August.', 37679.76),
 ('REVIEW: affects cash', '4. Payments Missing', 'September loan payments recorded total $4,625.63. The budget plans for $10,000 a month.', 4625.63),
 ('REVIEW: affects cash', '5. End of Year Corrections', 'No depreciation has been booked in 2026. Accumulated Depreciation is still −$599,145.95. 2025 depreciation was $281,321.', 281321.00),
 ('REVIEW: affects cash', '5. End of Year Corrections', 'The Epi F350 loan payment ($1,237.10) was posted 100% to principal. Split out the interest.', 1237.10),
 ('REVIEW: affects cash', '5. End of Year Corrections', 'The Tony F350 loan payment ($1,237.10) was posted 100% to principal. Split out the interest.', 1237.10),
 ('REVIEW: affects cash', '5. End of Year Corrections', 'The Bobcat E35 loan payment ($1,549.55) was posted 100% to principal. Split out the interest.', 1549.55),
 ('REVIEW: affects cash', '5. End of Year Corrections', 'Split principal and interest on every 2026 loan payment using each lender\'s schedule. This includes Rivian, Tahoe, and Transit once they are recorded.', None),
 ('REVIEW: affects cash', '5. End of Year Corrections', 'Move loan interest out of Bank & Credit Card Fees into its own Interest Expense account, as the ROOTS budget calls for.', 5505.71),
 ('Bookkeeping Corrections', '1. Errors & Incorrect Entries', 'Reclass the 9/1 JE "Tax donation to my son\'s school" ($3,500.00) out of Charitable Contributions and Petty Cash. It is personal, so it belongs in Owners Draw.', 3500.00),
 ('Bookkeeping Corrections', '1. Errors & Incorrect Entries', 'Merchant Fees is negative (−$2,066.06) because customer surcharges are being credited to Merchant Fees on each job. Move the surcharges to Merchant Surcharge Income.', -2066.06),
 ('Bookkeeping Corrections', '1. Errors & Incorrect Entries', 'Interest Fees shows −$2,696.24 in August. Interest can\'t be negative, so find and fix the entry.', -2696.24),
 ('Bookkeeping Corrections', '1. Errors & Incorrect Entries', 'Travel was $6,339.14 in September against a $2,833 budget. Job travel goes to Job Travel & Lodging. Personal travel goes to Owners Draw.', 6339.14),
 ('Bookkeeping Corrections', '2. Job Costing Entries', 'Class "COGS" holds $5,985.48 of job costs. Move them to the correct job classes.', 5985.48),
 ('Bookkeeping Corrections', '2. Job Costing Entries', 'Class "COGS" holds $56,463.13 of overhead. Move it to department classes, then retire the "COGS" class.', 56463.13),
 ('Bookkeeping Corrections', '2. Job Costing Entries', 'Class "COGS" shows Payroll at −$23,626.52 and Non-Payroll at $28,490.18. Confirm the reclass entry and assign the labor to jobs.', 4863.66),
 ('Bookkeeping Corrections', '2. Job Costing Entries', '"Not specified" class: assign $8,400.00 in Subcontractor Costs to jobs.', 8400.00),
 ('Bookkeeping Corrections', '2. Job Costing Entries', '"Not specified" class: assign $3,802.76 in Merchant Fees to jobs.', 3802.76),
 ('Bookkeeping Corrections', '2. Job Costing Entries', '"Not specified" class: assign $919.96 in Materials & Supplies to jobs.', 919.96),
 ('Bookkeeping Corrections', '2. Job Costing Entries', '"Not specified" class: assign $797.13 in Permits & Inspection Fees to jobs.', 797.13),
 ('Bookkeeping Corrections', '2. Job Costing Entries', '"Not specified" class: assign −$2,232.97 in Landscape materials to jobs.', -2232.97),
 ('Bookkeeping Corrections', '2. Job Costing Entries', 'Merge the duplicate class "Baijo" ($623.33) into "16745 Bajio".', 623.33),
 ('Bookkeeping Corrections', '2. Job Costing Entries', '"Glen Alysa" class ($54.85): confirm which job it belongs to, or merge it.', 54.85),
 ('Bookkeeping Corrections', '2. Job Costing Entries', 'Billable Expense Income fell to $6,359.63 against a $12,417 monthly budget. Check that job costs marked billable are being invoiced.', 6359.63),
 ('Bookkeeping Corrections', '2. Job Costing Entries', '8 jobs have September costs but no invoice ($16,233). Confirm whether each is work in progress or unbilled. See the Job Profit tab, Flag = "Bill now".', 16232.70),
 ('Bookkeeping Corrections', '3. End of Year Entries', 'Fixed assets haven\'t changed all year. Confirm any 2026 truck or equipment purchases are on the balance sheet and not expensed.', None),
 ('Bookkeeping Corrections', '3. End of Year Entries', 'Office Artwork ($65,691.28): confirm it should stay as a non-depreciating asset.', 65691.28),
 ('Bookkeeping Corrections', '3. End of Year Entries', 'Due from Shareholder ($33,124.64) hasn\'t moved all year. Settle or reclass it before year end.', 33124.64),
 ('Bookkeeping Corrections', '3. End of Year Entries', 'Owners Draw ($46,399.73 YTD): close it to distributions at year end.', 46399.73),
 ('Bookkeeping Corrections', '3. End of Year Entries', 'Keep business charitable giving separate for the K-1. September business giving was $560.00.', 560.00),
]
dv = DataValidation(type='list', formula1='"Open,In progress,Done"', allow_blank=True); wsC.add_data_validation(dv)
r = 5; last = None
for i, (sec, sub, txt, amt) in enumerate(CORR):
    if sec != last:
        c = put(wsC, r, 1, sec.upper(), f_h); r += 1; last = sec
    put(wsC, r, 1, i + 1); put(wsC, r, 2, 'REVIEW' if sec.startswith('REVIEW') else 'Bookkeeping', f_bb); put(wsC, r, 3, sub, f_b)
    put(wsC, r, 4, txt, f_b, al=wrap); put(wsC, r, 5, amt, f_in, CUR); put(wsC, r, 6, 'Yes' if sec.startswith('REVIEW') else 'No')
    put(wsC, r, 7, 'Open', f_bb); dv.add(f'G{r}'); put(wsC, r, 8, None); put(wsC, r, 9, None, fmt='mm/dd/yyyy'); put(wsC, r, 10, None)
    wsC.row_dimensions[r].height = 30 if len(txt) > 95 else 18
    r += 1
CL = r - 1
wsC.conditional_formatting.add(f'G5:G{CL}', FormulaRule(formula=['G5="Done"'], fill=fill_green))
wsC.conditional_formatting.add(f'G5:G{CL}', FormulaRule(formula=['G5="Open"'], fill=fill_red))
r += 1
put(wsC, r, 1, 'Open REVIEW items', f_bb); put(wsC, r, 4, f'=COUNTIFS(B5:B{CL},"REVIEW",G5:G{CL},"<>Done")', f_bb); r += 1
put(wsC, r, 1, 'Open bookkeeping items', f_bb); put(wsC, r, 4, f'=COUNTIFS(B5:B{CL},"Bookkeeping",G5:G{CL},"<>Done")', f_bb)
widths(wsC, {'A': 5, 'B': 12, 'C': 30, 'D': 92, 'E': 13, 'F': 9, 'G': 11, 'H': 14, 'I': 11, 'J': 28})
wsC.freeze_panes = 'D5'

# =====================================================================
# CLIENT REQUESTS (client draft)
title(wsR, f'{CLIENT}: Client Requests ({PERIOD})', 'CLIENT DRAFT: goes with the summary report. Do not send until Ayrica approves.')
header(wsR, 4, ['#', 'What we need', 'Why', 'Status', 'Date received'])
REQ = [('September loan statement: Rivian R1T', 'Payment missing in the books'), ('September loan statement: Chevrolet Tahoe', 'Payment missing in the books'),
       ('September loan statement: Transit Van', 'Payment missing in the books'), ('Glen Oaks Escrow statement as of 9/30', 'Confirm the $288,140 escrow balance'),
       ('What the $26,557.12 deposit on 9/14 (Trust Dept) was for: customer + invoices', 'Apply it to the right invoices'),
       ('What the $139,430 credit for D.W. Johnston Construction is (deposit? prepayment?)', 'Clear the A/R credit'),
       ('Petty cash count as of 9/30', 'Books show $26,220'), ('Confirm the $3,500 school donation on 9/1 was personal', 'Move it to owner draw'),
       ('Which September trips were for jobs, business development, or personal', 'Travel was over budget'),
       ('Does 1321 New York Dr have construction work not billed yet?', '$20,915 spent, $2,045 billed'),
       ('Who are the 2 new hires: role, start date, pay', 'Set the overhead budget and breakeven'),
       ('Q3 lead count, proposals sent, jobs won', 'Confirm the #1 constraint'),
       ('December 2025 balance sheet', 'Fix January cash collected and loan principal'),
       ('2025 tax return incl. depreciation schedule (Form 4562)', 'Set the real 2026 depreciation'),
       ('Contract value for each open job', 'Complete the Open Jobs profit to date'),
       ('Monthly cash collection goal for Q4 (if different from $728,348)', 'Score against the right goal')]
dv2 = DataValidation(type='list', formula1='"Requested,Received"', allow_blank=True); wsR.add_data_validation(dv2)
for i, (a, b) in enumerate(REQ):
    rr = 5 + i; put(wsR, rr, 1, i + 1); put(wsR, rr, 2, a); put(wsR, rr, 3, b, f_sub); put(wsR, rr, 4, 'Requested', f_bb); dv2.add(f'D{rr}'); put(wsR, rr, 5, None, fmt='mm/dd/yyyy')
widths(wsR, {'A': 5, 'B': 78, 'C': 44, 'D': 12, 'E': 13})

# =====================================================================
# INTERNAL NOTES
title(wsN, 'Internal notes for Ayrica (not client-facing)', f'{CLIENT} · {PERIOD}')
NOTES = ['Correction: the A/R I previously called "31–60 days late" ($103,844) is actually 61–90 days. 31–60 is $23,686. Decision #1 now uses $112,346 (31–90 days, excluding DMCS).',
         'Constraint: Leads (costs on or under budget for Q3; cash collected about 74% of goal). Money Leakage is second.',
         'New hires: team payroll ran $10,478 a month over the 2025 budget in September. It\'s added to overhead from month 9 (Budget tab). Confirm the hires.',
         'Flex rule (per Ayrica 10/08): project costs 40%, operations 2%, debt 1%, reinvested 1.8%, owner pay 13.5% of cash collected. Overhead fixed. The fixed $10,000/month debt is still tracked.',
         'Tax: the YTD set-aside treats DMCS and Johnston Landscapes payouts each as one single filer\'s pass-through income. 2026 federal brackets, 2025 CA brackets, no QBI deduction. Confirm the entity type and any estimates paid.',
         'Reasonable comp: owner W-2 wages are $47,500 YTD, while $538,000 went through DMCS and JLI.',
         'Job-to-customer matching: done by matching invoice amounts (job billing plus the 3% surcharge). 2305 Kenilworth and 975 Cliff Dr are marked "confirm".',
         'Cash collected = billed − change in A/R. September GL customer payments were $394,952. The ~$5,869 difference is card surcharges booked against Merchant Fees.']
for i, t in enumerate(NOTES):
    put(wsN, 4 + i, 1, f'• {t}', f_b, al=wrap); wsN.row_dimensions[4 + i].height = 30
widths(wsN, {'A': 140})

for ws in wb.worksheets:
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.orientation = 'landscape'; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
wb.save(OUT)
print('saved', OUT)
