import pdfplumber, re, json, sys
f = sys.argv[1]; out = {}
num = re.compile(r'^-?\$?[\d,]+\.\d\d$')
with pdfplumber.open(f) as pdf:
    for p in pdf.pages:
        ws = p.extract_words(x_tolerance=1.5)
        hdr = [w for w in ws if re.match(r'^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep)$', w['text'])]
        cols = sorted([(w['x1'] + 30, w['text']) for w in hdr])  # month right edge approx (year word follows)
        yrs = {round(w['top']): w for w in ws if w['text'] == '2026'}
        # use '2026' words right edges as column anchors
        anchors = sorted([w['x1'] for w in ws if w['text'] == '2026' and w['top'] < 140 and w['top'] > 100])
        tot = [w for w in ws if w['text'] == 'Total' and w['top'] < 140 and w['top'] > 100]
        if tot: anchors.append(tot[0]['x1'])
        names = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Total']
        lines = {}
        for w in ws: lines.setdefault(round(w['top']), []).append(w)
        for y, L in sorted(lines.items()):
            L.sort(key=lambda w: w['x0'])
            label = ' '.join(w['text'] for w in L if not num.match(w['text'])).strip()
            vals = [w for w in L if num.match(w['text'])]
            if not vals or not label or len(anchors) < 10: continue
            row = {}
            for w in vals:
                i = min(range(len(anchors)), key=lambda k: abs(anchors[k] - w['x1']))
                row[names[i]] = float(w['text'].replace('$', '').replace(',', ''))
            key = label; n = 2
            while key in out: key = f'{label} #{n}'; n += 1
            out[key] = row
json.dump(out, open(sys.argv[2], 'w'), indent=0)
for k, v in out.items(): print(f"{k[:45]:45s}", [v.get(m, 0) for m in ['Jan','Jun','Sep','Total']])
