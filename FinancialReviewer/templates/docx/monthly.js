const L = require('./lib');
const { title, subtitle, h1, p, small, bullet, num, status, table, doc, save, GOOD, WARN, BAD, CONTENT_W } = L;
const out = process.argv[2];
const W = CONTENT_W;

const c = [
  title('Johnston Vidal Projects: September 2026 Money Report'),
  subtitle('Business Management · Compared with your ROOTS budget · Fixed costs are compared in dollars. Pay that can flex is compared as a % of cash collected. · DRAFT: books not final'),

  h1('The big picture'),
  bullet('You billed **$556,283** and collected about **$389,084**.'),
  bullet('Breakeven is now **$513,132** a month after the 2 new hires. You were **$124,049 short**.'),
  bullet('Owner pay, reinvestment, and operations were **$60,116 more** than September\'s cash collected allows.'),
  bullet('Cash in the bank dropped **$213,523**. About $89,670 of that paid down credit cards.'),
  bullet('**If nothing changes:** at this pace, your spendable bank cash lasts about 6 weeks.'),

  h1('ROOTS scorecard: budget vs. actual'),
  table([
    ['', 'Rule', 'Allowed', 'Actual', 'Status'],
    ['**R** Cash collected', 'Budget', '$728,348', '$389,084', { runs: status('53% of budget', BAD) }],
    ['**O** Overhead (fixed)', '$ per month, with new hires', '$286,180', '$262,208', { runs: status('Under', GOOD) }],
    ['**O** Project costs', '40.15% of cash', '$156,217', '$171,570', { runs: status('$15,353 over', BAD) }],
    ['**O** Operations', '2.13% of cash', '$8,287', '$13,664', { runs: status('$5,376 over', WARN) }],
    ['**T** Taxes', 'YTD set-aside', '$194,498', 'see below', { runs: status('Set aside', GOOD) }],
    ['**S** Reinvested', '1.82% of cash', '$7,073', '$19,083', { runs: status('$12,010 over', BAD) }],
    ['**S** Owner pay', '13.56% of cash', '$52,753', '$95,483', { runs: status('$42,730 over', BAD) }],
    ['**S** Cash kept', '2.87% of cash', '+$11,158', '−$177,550', { runs: status('Short', BAD) }],
  ], [2100, 2440, 1300, 1300, W - 7140], { right: [2, 3] }),
  small('Overhead budget = 2025 budget $275,702 + $10,478 a month for the new team payroll seen in September (Office & Admin, Project Manager, Design).'),

  h1('Taxes: what to set aside for 2026 so far (Jan – Sep)'),
  table([
    ['Who', 'YTD income', 'CA 1.5% company', 'Federal (single)', 'California (single)', 'Set aside YTD'],
    ['JVP net profit', '$785,642', '$11,785', '—', '—', '$11,785'],
    ['DMCS (pass-through)', '$333,000', '$4,995', '$87,152', '$28,401', '$120,548'],
    ['Johnston Landscapes (pass-through)', '$205,000', '$3,075', '$43,094', '$15,996', '$62,165'],
    ['**Total**', '', '**$19,855**', '**$130,246**', '**$44,397**', '**$194,498**'],
  ], [2440, 1300, 1450, 1450, 1600, W - 8240], { right: [1, 2, 3, 4, 5], lastBand: true }),
  small('Estimate. Each payout is treated as one single filer\'s income, annualized, then 9/12 is shown. Subtract any estimated payments already made. Not included: owner W-2 wages and each owner\'s share of JVP profit (we need ownership %).'),

  h1('What worked · What didn\'t'),
  bullet('**Worked:** overhead stayed $23,972 under budget, even with the new hires.'),
  bullet('**Worked:** you paid down $89,670 of credit card debt.'),
  bullet('**Didn\'t work:** owner pay was $42,730 more than September\'s cash supports.'),
  bullet('**Didn\'t work:** $16,233 of job costs had no invoice. See the Job Profit Report.'),

  h1('Your 3 decisions for October'),
  num('Collect the $103,844 that is 31–60 days late, starting with Erin Whitely ($52,700), before October 15.'),
  num('Bill the 8 jobs with costs but no invoice, starting with 700 Riven Rock Dr ($6,759).'),
  num('Set October owner pay at 13.56% of cash collected, and hold reinvestment to 1.82% and operations to 2.13%.'),
];
save(doc(c), `${out}/JVP_Sept-2026_Monthly_ROOTS_Report.docx`).then(() => console.log('monthly ok'));
