import json
M = {
 'Jul': dict(inc=609752.06, cogs=337666.91, labor=149173.30, autoreg=895, autofees=342.85, repair=973.91, gas=8796.34, subA=0, subM=2318.97, dno=0, prop=0, health=7370.91, wc=35176.45, office=10865.64, bk=3112, design=17884.04, admin=11761.56, ocomp=53000, owages=5000, pfees=2256.29, ptax=10312.77, pm=13236.58, mkt=30.67, bankfees=67.86, interest=1341.29, brand=0, legal=25, taxprep=7470, taxes=0, soft=0, air=0, hotel=0, parking=53.70, transp=197.76, meals=2110.22, othinc=13.54, charity=0, baddebt=0, ar0=183292.97, ar1=139514.04, principal=227700.30-220032.74, draws=36079.82-32524.86, personal=0),
 'Aug': dict(inc=514721.31, cogs=438676.18, labor=192552.55, autoreg=0, autofees=342.85, repair=8113.69, gas=8910.95, subA=77.33, subM=2933.11, dno=852.50, prop=10331.00, health=7370.91, wc=9522.16, office=9549.19, bk=3815.50, design=17884.04, admin=11761.56, ocomp=55000, owages=5000, pfees=777.14, ptax=11425.64, pm=13236.58, mkt=276.00, bankfees=116.81, interest=-2696.24, brand=0, legal=0, taxprep=0, taxes=100, soft=0, air=1648.20, hotel=0, parking=303.45, transp=37.00, meals=2061.17, othinc=1399.55, charity=0, baddebt=0, ar0=139514.04, ar1=70494.47, principal=220032.74-208302.81, draws=40416.51-36079.82, personal=0),
 'Sep': dict(inc=556282.56, cogs=320655.98, labor=150301.30, autoreg=330, autofees=342.85, repair=3790.83, gas=9872.70, subA=4579.12, subM=2398.03, dno=0, prop=0, health=7370.91, wc=21748.43, office=7612.68, bk=3962, design=18910.18, admin=17384.64, ocomp=81000, owages=5000, pfees=2000.83, ptax=11206.98, pm=13910.18, mkt=8685.40, bankfees=140.92+95+125, interest=601.88, brand=1250, legal=0, taxprep=0, taxes=0, soft=150, air=3223.80, hotel=2093.99, parking=854.42, transp=1021.35, meals=2248.60, othinc=8828.15, charity=4060, baddebt=0, ar0=70494.47, ar1=237693.50, principal=208302.81-204279.06, draws=46399.73-40416.51, personal=3500),
}
B = dict(cash=728348.4533, oh=275702.4392, cogs_pct=0.4015, ops_pct=0.0213, debt=10000, taxes=2576.56, reinv=13241.06, owner=98751.9775, kept=20886.8625, breakeven=494944.6257)
R = {}
for k, d in M.items():
    r = {}
    r['billed'] = d['inc']; r['cash'] = d['inc'] - (d['ar1'] - d['ar0'])
    r['oh'] = sum(d[x] for x in 'labor office autoreg autofees wc health dno prop subA subM soft pm bk admin design pfees ptax taxprep'.split())
    r['cogs'] = d['cogs'] - d['labor'] + d['bankfees'] + d['parking']
    r['ops'] = d['gas'] + d['repair'] + d['legal']
    r['debt'] = d['interest'] + d['principal']
    r['taxes'] = d['taxes']
    biz_charity = d['charity'] - d['personal']
    r['reinv'] = d['mkt'] + d['brand'] + d['air'] + d['hotel'] + d['transp'] + d['meals'] + biz_charity
    r['owner'] = d['ocomp'] + d['owages'] + d['draws'] + d['personal']
    r['leak'] = d['baddebt']
    r['kept'] = r['cash'] - r['oh'] - r['cogs'] - r['ops'] - r['debt'] - r['taxes'] - r['reinv'] - r['owner'] - r['leak']
    # check expenses reconcile: total P&L expenses + cogs
    tot_exp_pl = r['oh'] + r['cogs'] + r['ops'] + d['interest'] + r['taxes'] + r['reinv'] + (d['ocomp'] + d['owages']) + d['personal'] - d['labor']*0  # sanity
    R[k] = r
Q = {key: sum(R[m][key] for m in R) for key in R['Sep']}
R['Q3'] = Q
for k, r in R.items():
    n = 3 if k == 'Q3' else 1
    print(f"--- {k}")
    for key, v in r.items():
        extra = ''
        if key in ('cogs', 'ops', 'oh', 'reinv', 'owner', 'kept'): extra = f"  {v/r['cash']*100:5.1f}% of cash"
        print(f"{key:7s} {v:14,.2f}{extra}")
    print(f"budget cash {B['cash']*n:,.0f}  pct {r['cash']/(B['cash']*n)*100:.1f}%  breakeven {B['breakeven']*n:,.0f}")
    print(f"budget: oh {B['oh']*n:,.0f} cogs {B['cogs_pct']*r['cash']:,.0f} ops {B['ops_pct']*r['cash']:,.0f} debt {B['debt']*n:,.0f} tax {B['taxes']*n:,.0f} reinv {B['reinv']*n:,.0f} owner {B['owner']*n:,.0f} kept {B['kept']*n:,.0f}")
json.dump(R, open('/tmp/claude-0/-home-user-Cashflow-Budget/d4cac086-f27b-512d-a0ff-1ff5e8f1696a/scratchpad/roots.json', 'w'))
# reconcile Sept: P&L COGS + expenses + other exp = ?
d = M['Sep']; r = R['Sep']
pl = 320655.98 + 231910.72 + 4060
mine = r['oh'] + r['cogs'] + r['ops'] + d['interest'] + r['taxes'] + r['reinv'] + d['ocomp'] + d['owages'] + d['personal']
print('Sept P&L costs', pl, 'mapped', mine, 'diff', pl - mine)
