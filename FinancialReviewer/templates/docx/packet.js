const L = require('./lib');
const { title, subtitle, h1, h2, h3, p, small, bullet, doc, save } = L;
const out = process.argv[2];
const B = (items) => items.map(bullet);

const c = [
  title('Johnston Vidal Projects: September 2026 Review Packet'),
  subtitle('Business Management · Prepared 2026-10-07 · Sources: P&L by Month, P&L by Class, Balance Sheet, AR Aging, GL (not final), and the 2025 ROOTS Budget'),

  h1('DRAFT 1: Team corrections'),
  p('**Do not send until Ayrica approves.**'),
  p('Hi team, please fix the items below in JVP\'s September books before we finalize. The REVIEW items affect cash, so please do those first.'),

  h2('REVIEW: affects cash'),
  h3('1. Balance Sheet General Corrections'),
  ...B([
    'REVIEW: Undeposited Funds has held $119,830.00 since May. Match it to bank deposits or clear the duplicates.',
    'REVIEW: BOA-4089 ends September at −$1,755.30. Confirm whether this is an overdraft or a missing transfer.',
    'REVIEW: Petty Cash shows $26,220.00. Confirm the actual cash on hand.',
    'REVIEW: Escrow shows $288,139.71. Tie it to the Glen Oaks Escrow statement. It jumped $232,825 in August.',
    'REVIEW: Due to DMCS is −$14,887.00, which means DMCS owes JVP. Confirm the balance.',
    'REVIEW: Due to Johnston Landscape is −$2,970.00 because JVP pays $495 a month in ADP 401K for Johnston Landscapes. Set up repayment or reclass.',
  ]),
  h3('2. Accounts Receivable Corrections'),
  ...B([
    'REVIEW: The 9/14 deposit of $26,557.12 (TRUST DEPT) was posted to A/R with no customer. Apply it to Inv 3789 ($637.50), Inv 3906 ($225.00), and Inv 3866 ($25,694.62) under the correct customer.',
    'REVIEW: D.W. Johnston Construction shows a −$139,430.00 credit that is 91+ days old. Apply it to open invoices, or reclass it.',
    'REVIEW: Michael Balzary NKSFB LLC shows a −$6,375.00 credit. Apply it or reclass it.',
    'REVIEW: Emily Wassall shows a −$500.00 credit. Apply it or reclass it.',
    'REVIEW: DMCS shows $15,184.00 in A/R (61–90 days). Confirm whether this is real or a duplicate of Due to DMCS.',
  ]),
  h3('3. Payroll Corrections'),
  ...B([
    'REVIEW: Other tax Payable is $16,920.08 and grows every month. Reconcile it to ADP.',
    'REVIEW: Other Deduction is $12,136.48 and grows every month. Reconcile it to ADP.',
    'REVIEW: Net Wages Payable is $38,853.26. Reconcile it to ADP and clear what was already paid.',
  ]),
  h3('4. Payments Missing'),
  ...B([
    'REVIEW: The Rivian R1T loan payment is missing for September. The balance has been $12,515.77 since August.',
    'REVIEW: The Chevrolet Tahoe loan payment is missing for September. The balance has been $48,233.76 since August.',
    'REVIEW: The Transit Van loan payment is missing for September. The balance has been $37,679.76 since August.',
    'REVIEW: September loan payments recorded total $4,625.63. The budget plans for $10,000 a month.',
  ]),
  h3('5. End of Year Corrections'),
  ...B([
    'REVIEW: No depreciation has been booked in 2026. Accumulated Depreciation is still −$599,145.95. 2025 depreciation was $281,321.',
    'REVIEW: The Epi F350 loan payment ($1,237.10) was posted 100% to principal. Split out the interest.',
    'REVIEW: The Tony F350 loan payment ($1,237.10) was posted 100% to principal. Split out the interest.',
    'REVIEW: The Bobcat E35 loan payment ($1,549.55) was posted 100% to principal. Split out the interest.',
    'REVIEW: Split principal and interest on every 2026 loan payment using each lender\'s schedule. This includes Rivian, Tahoe, and Transit once they are recorded.',
    'REVIEW: Move loan interest out of Bank & Credit Card Fees into its own Interest Expense account, as the ROOTS budget calls for.',
  ]),

  h2('Bookkeeping corrections'),
  h3('1. Errors & Incorrect Entries'),
  ...B([
    'Reclass the 9/1 JE "Tax donation to my son\'s school" ($3,500.00) out of Charitable Contributions and Petty Cash. It is personal, so it belongs in Owners Draw.',
    'Merchant Fees is negative (−$2,066.06) because customer surcharges are being credited to Merchant Fees on each job. Move the surcharges to Merchant Surcharge Income.',
    'Interest Fees shows −$2,696.24 in August. Interest can\'t be negative, so find and fix the entry.',
    'Travel was $6,339.14 in September against a $2,833 budget. Job travel goes to Job Travel & Lodging. Personal travel goes to Owners Draw.',
  ]),
  h3('2. Job Costing Entries'),
  ...B([
    'Class "COGS" holds $5,985.48 of job costs. Move them to the correct job classes.',
    'Class "COGS" holds $56,463.13 of overhead. Move it to department classes, then retire the "COGS" class.',
    'Class "COGS" shows Payroll at −$23,626.52 and Non-Payroll at $28,490.18. Confirm the reclass entry and assign the labor to jobs.',
    '"Not specified" class: assign $8,400.00 in Subcontractor Costs to jobs.',
    '"Not specified" class: assign $3,802.76 in Merchant Fees to jobs.',
    '"Not specified" class: assign $919.96 in Materials & Supplies to jobs.',
    '"Not specified" class: assign $797.13 in Permits & Inspection Fees to jobs.',
    '"Not specified" class: assign −$2,232.97 in Landscape materials to jobs.',
    'Merge the duplicate class "Baijo" ($623.33) into "16745 Bajio".',
    '"Glen Alysa" class ($54.85): confirm which job it belongs to, or merge it.',
    'Billable Expense Income fell to $6,359.63 against a $12,417 monthly budget. Check that job costs marked billable are being invoiced.',
    'These 8 jobs have September costs but no September invoice. Confirm whether each one is work in progress or unbilled: 700 Riven Rock ($6,759), 285 Via Lola ($2,882), 36 Echo Glen ($2,294), 31435 Arena ($1,661), 30447 Mallorca ($842), 3144 Nichols Canyon ($821), 1673 Sargent Place ($543), 3509 Griffith Park ($430).',
  ]),
  h3('3. End of Year Entries'),
  ...B([
    'Fixed assets haven\'t changed all year. Confirm any 2026 truck or equipment purchases are on the balance sheet and not expensed.',
    'Office Artwork ($65,691.28): confirm it should stay as a non-depreciating asset.',
    'Due from Shareholder ($33,124.64) hasn\'t moved all year. Settle or reclass it before year end.',
    'Owners Draw ($46,399.73 YTD): close it to distributions at year end.',
    'Keep business charitable giving separate for the K-1. September business giving was $560.00.',
  ]),

  h1('DRAFT 2: Client info request (goes with the summary report)'),
  p('**Do not send until Ayrica approves.**'),
  p('Hi [Client name],'),
  p('Your September report and Q3 90-Day Review are attached. To finalize them, we need the items below:'),
  ...B([
    'Your September loan statements for the Rivian R1T.',
    'Your September loan statements for the Chevrolet Tahoe.',
    'Your September loan statements for the Transit Van.',
    'Your Glen Oaks Escrow statement as of 9/30.',
    'What the $26,557.12 deposit on 9/14 from Trust Dept was for: which customer and which invoices.',
    'What the $139,430 credit for D.W. Johnston Construction is, such as a deposit or prepayment.',
    'A petty cash count as of 9/30.',
    'Confirmation that the $3,500 school donation on 9/1 was personal.',
    'Which September trips were for jobs, which were for business development, and which were personal.',
    'Whether 1321 New York Dr has construction work that hasn\'t been billed yet.',
    'Your lead count, proposals sent, and jobs won for Q3.',
    'Your monthly cash collection goal for Q4, if it differs from the $728,348 budget.',
  ]),
  p('Thank you!'),

  h1('Internal notes for Ayrica (not client-facing)'),
  ...B([
    '**The constraint call changed.** With the budget, costs were on or under budget for Q3. The gap is cash collected: 74% of budget, with billing down 18%. That points to Leads, not Money Leakage. Money Leakage is now second.',
    '**Budget mapping:** I used the 2025 ROOTS budget as the 2026 target. Crew labor counts as Overhead. D&O and property insurance were added to Overhead. Owner pay includes draws and the $3,500 personal donation.',
    '**Cash vs. recorded costs:** the budget is cash-based. I used cash collected as the base, but costs are what was recorded (accrual). A/P rose $80,046 in September, so some costs aren\'t paid yet.',
    '**Breakeven:** the budget\'s $494,945 breakeven covers overhead and debt only. It does not cover owner pay. Q3 cleared breakeven by $141,521 but did not cover owner pay plus reinvestment.',
    '**Tax assumption:** I treated JVP as a California S-corp. Please confirm the entity type and ownership split.',
    '**Reasonable comp flag:** owner W-2 wages are $47,500 YTD, while $538,000 was paid through DMCS and JLI.',
    '**Owner pay:** it was on budget at $95,483. But September\'s cash collected was 53% of budget. It\'s your call whether to raise that with the client.',
  ]),

  h1('Unresolved cash items to carry forward (REVIEW)'),
  ...B([
    'Balance Sheet: Undeposited Funds $119,830 · BOA-4089 −$1,755 · petty cash $26,220 · escrow $288,140 · DMCS and Johnston Landscape balances.',
    'Accounts Receivable: unapplied $26,557 deposit · D.W. Johnston −$139,430 · Balzary −$6,375 · Wassall −$500 · DMCS A/R $15,184.',
    'Payroll: Other tax Payable · Other Deduction · Net Wages Payable.',
    'Payments Missing: Rivian, Tahoe, and Transit loans.',
    'End of Year: 2026 depreciation · principal and interest split on all loan payments.',
  ]),
];
save(doc(c), `${out}/JVP_Sept-2026_Review_Packet.docx`).then(() => console.log('packet ok'));
