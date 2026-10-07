const L = require('./lib');
const { title, subtitle, h1, p, small, bullet, num, status, table, doc, save, GOOD, WARN, BAD, CONTENT_W } = L;
const out = process.argv[2];
const W = CONTENT_W;

const c = [
  title('Johnston Vidal Projects: Q3 2026 90-Day Review'),
  subtitle('July – September 2026 · Business Management · Compared with your ROOTS budget · DRAFT based on books that are not final yet'),

  h1('Q3 scorecard: budget vs. actual'),
  table([
    ['', 'Q3 budget', 'Q3 actual', 'Status'],
    ['Cash collected', '$2,185,045', '$1,626,355', { runs: status('74% of budget', BAD) }],
    ['Breakeven (cash needed to cover bills)', '$1,484,834', '$1,626,355', { runs: status('$141,521 above', GOOD) }],
    ['Overhead (fixed)', '$827,107', '$826,817', { runs: status('On budget', GOOD) }],
    ['Project costs per $1 collected', '40¢', '37¢', { runs: status('Under budget', GOOD) }],
    ['Operations per $1 collected', '2.1¢', '2.5¢', { runs: status('A little over', WARN) }],
    ['Marketing (client acquisition)', '$15,365', '$8,992', { runs: status('58% of budget', WARN) }],
    ['Owner pay', '$296,256', '$221,375', { runs: status('Under budget', GOOD) }],
    ['Cash kept in the business', '+$62,661', '−$117,261', { runs: status('Short', BAD) }],
  ], [3600, 1900, 1900, W - 3600 - 3800], { right: [1, 2] }),
  p('Costs were on budget or under. The problem was the money coming in. You collected **$558,690 less** than budget. Billing dropped **18%** from Q2.'),

  h1('The 5 things that can hold a business back'),
  table([
    ['Area', 'What the numbers show', 'Is this the block?'],
    ['**Leads**', 'Billing fell 18%. Cash collected was 74% of budget. Marketing spend was 58% of budget.', '**Yes. Most likely #1.**'],
    ['Conversions', 'Your books don\'t track proposals sent or jobs won.', 'Unknown. We need your win rate.'],
    ['Capacity', 'Crew and team costs ran full budget while work coming in was 74% of budget.', 'No. You have room for more work.'],
    ['Cash', 'You collected 97¢ of every $1 billed in Q3. September slipped to 70¢.', 'Not #1. Watch it.'],
    ['Money Leakage', 'Project costs came in under budget for the quarter. But 3 jobs lost money in September, and $18,754 of costs aren\'t tied to a job.', 'Second. Fix it at the job level.'],
  ], [1500, W - 1500 - 2600, 2600]),

  h1('Q4 focus: bring in more work'),
  p('**Goal:** get cash collected above $600,000 a month by December. Q3 averaged $542,118. Breakeven is $494,945 and budget is $728,348.'),
  num('Spend your full marketing budget ($5,122 a month) and count the leads it brings in.'),
  num('Track leads, proposals sent, and jobs won every week.'),
  num('Follow up on every open proposal older than 14 days.'),

  h1('What we will track on each monthly report'),
  bullet('Cash collected compared with budget ($728,348) and breakeven ($494,945).'),
  bullet('New leads and jobs won (we need these from you).'),
  bullet('Project costs per $1 collected (target: 40¢ or less).'),
  bullet('Number of jobs that lost money (target: 0).'),
  small('This review uses financial data plus your 2025 ROOTS budget. Send us your Q3 lead count and win rate so we can confirm whether leads or conversions is the real block.'),
];
save(doc(c), `${out}/JVP_Q3-2026_90-Day_Review.docx`).then(() => console.log('q3 ok'));
