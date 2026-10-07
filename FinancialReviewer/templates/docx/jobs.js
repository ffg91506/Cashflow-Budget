// Job Profit Report: every job ranked, plus jobs that should have been invoiced based on costs.
const L = require('./lib');
const { title, subtitle, h1, p, small, bullet, table, doc, save, CONTENT_W } = L;
const [out, jobsPath, period = 'September 2026', target = '0.43'] = process.argv.slice(2);
const T = Number(target);
const jobs = JSON.parse(require('fs').readFileSync(jobsPath, 'utf8'));
const W = CONTENT_W;
const $ = (n) => (n < 0 ? '−$' : '$') + Math.abs(Math.round(n)).toLocaleString('en-US');
const pct = (j) => j.inc > 0 ? Math.round((j.gp / j.inc) * 100) + '%' : '—';
const sum = (a, k) => a.reduce((s, j) => s + (typeof k === 'function' ? k(j) : j[k]), 0);

const noBill = jobs.filter(j => j.inc === 0 && j.cogs > 0).sort((a, b) => b.cogs - a.cogs);
const under = jobs.filter(j => j.inc > 0 && j.cogs > j.inc).sort((a, b) => a.gp - b.gp);
const low = jobs.filter(j => j.inc > 0 && j.cogs <= j.inc && j.cogs / j.inc > 1 - T).sort((a, b) => b.cogs / b.inc - a.cogs / a.inc);
const ranked = [...jobs].sort((a, b) => b.gp - a.gp);
const billed = sum(jobs, 'inc'), costs = sum(jobs, 'cogs');
const losers = jobs.filter(j => j.gp < 0).length;
const atTarget = (j) => j.cogs / (1 - T);
const tgt = Math.round(T * 100);

const c = [
  title(`Johnston Vidal Projects: Job Profit Report`),
  subtitle(`${period} · From the P&L by Class · Target job profit: ${tgt}¢ per $1 (your 2026 average) · DRAFT: books not final`),

  h1('The big picture'),
  bullet(`**${jobs.length} jobs** billed **${$(billed)}**. Their job costs were **${$(costs)}**.`),
  bullet(`Jobs kept **${Math.round((billed - costs) / billed * 100)}¢** of every $1 billed.`),
  bullet(`**${losers} jobs** lost money this month. ${noBill.length} of them sent no invoice.`),
  bullet(`**${$(sum(noBill, 'cogs'))}** was spent on ${noBill.length} jobs that sent no invoice.`),
  bullet('**$18,754** of job costs aren\'t tied to any job, so they are missing from this report. See the team corrections.'),

  h1('1. Bill now: jobs with costs but no invoice'),
  table([
    ['Job', 'Costs this month', 'Bill at least (cost)', `Bill at ${tgt}¢ target`],
    ...noBill.map(j => [j.job, $(j.cogs), $(j.cogs), $(atTarget(j))]),
    ['**Total**', `**${$(sum(noBill, 'cogs'))}**`, `**${$(sum(noBill, 'cogs'))}**`, `**${$(sum(noBill, atTarget))}**`],
  ], [W - 3 * 2000, 2000, 2000, 2000], { right: [1, 2, 3], lastBand: true }),
  small('If a job is still in progress, confirm the next invoice date instead.'),

  h1('2. Billed less than it cost: check for unbilled work or change orders'),
  table([
    ['Job', 'Billed', 'Costs', 'Loss', `Bill to reach ${tgt}¢`],
    ...under.map(j => [j.job, $(j.inc), $(j.cogs), $(j.gp), $(atTarget(j) - j.inc)]),
    ['**Total**', `**${$(sum(under, 'inc'))}**`, `**${$(sum(under, 'cogs'))}**`, `**${$(sum(under, 'gp'))}**`, `**${$(sum(under, j => atTarget(j) - j.inc))}**`],
  ], [W - 4 * 1700, 1700, 1700, 1700, 1700], { right: [1, 2, 3, 4], lastBand: true }),

  h1(`3. Made money, but under ${tgt}¢: check the price`),
  table([
    ['Job', 'Billed', 'Costs', 'Kept per $1', `Short of ${tgt}¢ target`],
    ...low.map(j => [j.job, $(j.inc), $(j.cogs), pct(j), $(atTarget(j) - j.inc)]),
  ], [W - 4 * 1700, 1700, 1700, 1700, 1700], { right: [1, 2, 3, 4] }),
  small('Fixed-price jobs may not be billable for more. Use these to price the next similar job.'),

  h1('4. Every job, ranked by job profit'),
  table([
    ['Job', 'Billed', 'Job costs', 'Job profit', 'Kept per $1', 'Overhead tagged', 'Net'],
    ...ranked.map(j => [j.job, $(j.inc), $(j.cogs), $(j.gp), pct(j), $(j.exp), $(j.ni)]),
    ['**Total**', `**${$(billed)}**`, `**${$(costs)}**`, `**${$(billed - costs)}**`, `**${Math.round((billed - costs) / billed * 100)}%**`, `**${$(sum(jobs, 'exp'))}**`, `**${$(sum(jobs, 'ni'))}**`],
  ], [2840, 1300, 1300, 1300, 1100, 1300, 1300], { right: [1, 2, 3, 4, 5, 6], lastBand: true }),
  small('Design-only jobs can show negative costs. That happens because card surcharges are credited to Merchant Fees, which is a correction in the review packet. Kept per $1 over 100% comes from that.'),
];
save(doc(c), `${out}/JVP_Sept-2026_Job_Profit_Report.docx`).then(() => console.log('jobs ok'));
