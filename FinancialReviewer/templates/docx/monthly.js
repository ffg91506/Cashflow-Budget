const L = require('./lib');
const { title, subtitle, h1, p, small, bullet, num, status, table, gap, doc, save, GOOD, WARN, BAD, CONTENT_W } = L;
const out = process.argv[2];
const W = CONTENT_W;

const c = [
  title('Johnston Vidal Projects: September 2026 Money Report'),
  subtitle('Business Management · Compared with your 2025 ROOTS budget · Tax is an estimate (CA S-corp, to confirm) · DRAFT based on books that are not final yet'),

  h1('The big picture'),
  bullet('You billed **$556,283** and collected about **$389,084**.'),
  bullet('Budget: **$728,348** collected a month. Breakeven: **$494,945**. You were **$105,861 short** of breakeven.'),
  bullet('Your fixed costs stayed on budget. Job costs, truck costs, and travel ran over budget.'),
  bullet('Cash in the bank dropped **$213,523**. About $89,670 of that paid down credit cards.'),
  bullet('**If nothing changes:** at this pace, your spendable bank cash lasts about 6 weeks.'),

  h1('ROOTS scorecard: budget vs. actual'),
  table([
    ['', 'Budget', 'Actual', 'What it means', 'Status'],
    ['**R** Cash collected', '$728,348', '$389,084', 'You collected 53% of budget. You billed $556,283, which is 76% of budget.', { runs: status('Short', BAD) }],
    ['**O** Overhead (fixed)', '$275,702', '$262,208', 'You were $13,494 under budget. But overhead used 67¢ of every $1 collected, against a target of 38¢.', { runs: status('On budget', GOOD) }],
    ['**O** Project costs', '40¢ per $1', '44¢ per $1', 'You spent $15,353 more than your budget allows for the cash you collected.', { runs: status('Over', BAD) }],
    ['**O** Operations', '2¢ per $1', '3.5¢ per $1', 'Fuel and truck repairs ran $5,376 over budget.', { runs: status('Over', WARN) }],
    ['**T** Tax', '$2,577 paid', '$0 paid', 'Set aside about **$2,672**: $127 for the company (CA 1.5%) and $2,545 for the owners (about 30% of profit).', { runs: status('Set aside', GOOD) }],
    ['**S** Surplus', '+$20,887 kept', '−$177,550', 'Money in did not cover money out. Cash on hand covered the gap.', { runs: status('Short', BAD) }],
  ], [1650, 1050, 1050, 5390, 1300], { right: [1, 2] }),

  h1('Where the money went'),
  table([
    ['Step', 'Budget', 'Actual'],
    ['Invoices sent', '', '$556,283'],
    ['Cash actually collected', '$728,348', '$389,084'],
    ['Recurring overhead (crew, team, insurance, rent, software)', '−$275,702', '−$262,208'],
    ['Project costs (materials, subs, equipment, permits)', '−$156,217', '−$171,570'],
    ['Operations (fuel, truck repairs)', '−$8,287', '−$13,664'],
    ['Loan payments (3 truck and van payments missing)', '−$10,000', '−$4,626'],
    ['Taxes paid', '−$2,577', '$0'],
    ['Money leaks (penalties, bad debt, fraud)', '$0', '$0'],
    ['Reinvested (marketing, travel, meals, brand)', '−$13,241', '−$19,083'],
    ['Owner pay', '−$98,752', '−$95,483'],
    ['**Cash kept in the business**', '**+$20,887**', '**−$177,550**'],
  ], [W - 2 * 1500, 1500, 1500], { right: [1, 2], lastBand: true }),

  h1('Job profit: which jobs made you money'),
  table([
    ['Made the most', 'Kept', 'Lost money or barely made money', 'Result'],
    ['4301 Manson', '$53,136 (71%)', '1321 New York Dr: spent $20,915, billed $2,045', '−$19,540'],
    ['8410 Allenwood Rd', '$50,090 (74%)', '1844 Upper Rim Rock: costs were higher than the bill', '−$2,571'],
    ['1684 Hill', '$36,783 (82%)', '3441 Grand View: billed $41,858, kept 2%', '$1,020'],
  ], [1700, 1500, W - 1700 - 1500 - 1100, 1100], { right: [3] }),
  p('$16,233 was spent on 8 jobs that sent no bill in September.'),

  h1('What worked · What didn\'t'),
  bullet('**Worked:** overhead stayed $13,494 under budget.'),
  bullet('**Worked:** you paid down $89,670 of credit card debt.'),
  bullet('**Didn\'t work:** cash collected was $339,264 below budget.'),
  bullet('**Didn\'t work:** project costs were 4¢ per $1 over budget.'),

  h1('Your 3 decisions for October'),
  num('Collect the $103,844 that is 31–60 days late, starting with Erin Whitely ($52,700), before October 15.'),
  num('Bill every job that has costs but no invoice, starting with 1321 New York Dr.'),
  num('Check pricing on Upper Rim Rock and Grand View before quoting the next job like them.'),
];
save(doc(c), `${out}/JVP_Sept-2026_Monthly_ROOTS_Report.docx`).then(() => console.log('monthly ok'));
