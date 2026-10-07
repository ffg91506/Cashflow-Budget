// Client Profile as a Word form: label column + fill-in column. Blank template and JVP pre-filled.
const L = require('./lib');
const { title, subtitle, h1, small, table, doc, save, CONTENT_W } = L;
const out = process.argv[2];

const SECTIONS = [
  ['1. Client basics', [
    ['Client name', 'name'], ['Tier (Monthly / Quarterly / Business Management)', 'tier'], ['Primary contact + email', 'contact'],
    ['Industry', 'industry'], ['Books in (QBO / Google Sheets) + basis (Cash / Accrual)', 'system'], ['Entity type + state', 'entity'],
    ['Owners + ownership %', 'owners'], ['How owners get paid (W-2, draw, related entity)', 'ownerpay'],
  ]],
  ['2. Budget + targets (what we score against)', [
    ['Budget file attached (name + year)', 'budgetfile'], ['Monthly cash collected goal', 'revgoal'], ['Breakeven: cash needed each month', 'breakeven'],
    ['Overhead budget (fixed $ per month)', 'oh'], ['Project costs budget (% of cash collected)', 'cogs'], ['Operations budget (% of cash collected)', 'ops'],
    ['Debt payments per month', 'debt'], ['Taxes paid per month (entity level)', 'taxes'], ['Reinvested budget (marketing, travel, meals)', 'reinv'],
    ['Owner pay budget per month', 'owner'], ['Cash kept target per month', 'kept'], ['Tax set-aside % (company / owners)', 'taxpct'],
  ]],
  ['3. Current focus', [
    ['Next goal the owner is chasing', 'nextgoal'], ['Current 90-day constraint (Leads / Conversions / Capacity / Cash / Money Leakage)', 'constraint'],
    ['Focus metric for this quarter + target', 'focus'],
  ]],
  ['4. Recurring money out', [
    ['Loans: lender, payment, due date', 'loans'], ['Big fixed bills', 'fixed'], ['Known money leaks to watch', 'leaks'],
  ]],
  ['5. This review', [
    ['Period reviewed', 'period'], ['Books final? (Yes / No)', 'final'], ['Reports included', 'reports'],
    ['What changed this month (hires, big buys, new loans, big jobs)', 'changes'], ['Open REVIEW items from last review + status', 'openreview'],
    ['Notes / special instructions', 'notes'],
  ]],
];

const JVP = {
  name: 'Johnston Vidal Projects', tier: 'Business Management', industry: 'Construction + design (job-based)',
  system: 'QuickBooks Online (class = job address) · Accrual books, cash-basis budget', entity: 'S-corp? (confirm) · California',
  owners: 'Johnston ___% / Vidal ___%', ownerpay: 'W-2 wages + payouts to DMCS and Johnston Landscapes (JLI)',
  budgetfile: 'JVP_ROOTS_Budget_2025.xlsx (2025 actuals used as 2026 targets)', revgoal: '$728,348', breakeven: '$494,945',
  oh: '$275,702 (37.85% of cash collected)', cogs: '40.15%', ops: '2.13%', debt: '$10,000', taxes: '$2,577',
  reinv: '$13,241', owner: '$98,752', kept: '$20,887 (2.87%)', taxpct: 'CA 1.5% company / about 30% owners (confirm)',
  constraint: 'Leads (Q3 2026 review; confirm with lead count and win rate)',
  focus: 'Cash collected above $600,000 a month by December · project costs 40¢ per $1 or less · 0 losing jobs',
  loans: 'Rivian R1T (bal $12,516) · Tahoe (bal $48,234) · Transit Van (bal $37,680) · Ford F350 x2 ($1,237.10 each) · Bobcat E35 ($1,549.55). Add lenders and due dates.',
  fixed: 'Office rent $4,455 · health insurance $7,371 · workers comp about $28,523 (budget avg) · software about $2,063',
  leaks: 'Already tracked in the "Leaks" class. Budget leakage = penalties, bad debt, fraud (target $0).',
  period: 'October 2026', final: '', reports: 'P&L by Month, P&L by Class, Balance Sheet by Month, AR Aging, GL, ROOTS Budget',
  openreview: 'See the REVIEW carry-forward list in the September packet (balance sheet, A/R, payroll, 3 missing loan payments, year-end).',
};

function build(values, path) {
  const kids = [title('Client Profile'), subtitle('Upload this with the financials and the budget every review. Update only what changed. Blank = not known yet.')];
  for (const [name, rows] of SECTIONS) {
    kids.push(h1(name));
    kids.push(table(rows.map(([label, key]) => [`**${label}**`, values[key] || '']), [3800, CONTENT_W - 3800], { head: false }));
  }
  return save(doc(kids), path);
}
Promise.all([build({}, `${out}/Client_Profile_TEMPLATE.docx`), build(JVP, `${out}/JVP_Client_Profile.docx`)]).then(() => console.log('profile ok'));
