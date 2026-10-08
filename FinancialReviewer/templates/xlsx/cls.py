import pdfplumber,sys,re
f=sys.argv[1]
rows_want=["Total for Income","Total for Cost of Goods Sold","Gross Profit","Total for Expenses","Net Income"]
out={}
with pdfplumber.open(f) as pdf:
    # pages come in groups; each column-group spans multiple pages. Use words with x positions.
    groups=[]; cur=None
    for i,p in enumerate(pdf.pages):
        words=p.extract_words(keep_blank_chars=False,x_tolerance=1.5)
        # header region: words between y of title and 'Income' line
        inc=[w for w in words if w['text']=='Income' and w['x0']<60]
        if inc:
            ytop=inc[0]['top']
            hdr=[w for w in words if 95<w['top']<ytop and w['x0']>150]
            # cluster header words by x-center
            cols=[]
            for w in sorted(hdr,key=lambda w:w['x0']):
                xc=(w['x0']+w['x1'])/2
                for c in cols:
                    if abs(c['xc']-xc)<28 or (w['x0']<c['x1']+3 and w['x1']>c['x0']-3):
                        c['w'].append(w); c['x0']=min(c['x0'],w['x0']); c['x1']=max(c['x1'],w['x1']); break
                else:
                    cols.append({'xc':xc,'x0':w['x0'],'x1':w['x1'],'w':[w]})
            for c in cols:
                c['name']=' '.join(x['text'] for x in sorted(c['w'],key=lambda w:(round(w['top']),w['x0'])))
            cur={'cols':cols,'pages':[]}; groups.append(cur)
        cur['pages'].append(p)
    for g in groups:
        cols=sorted(g['cols'],key=lambda c:c['x1'])
        for p in g['pages']:
            lines={}
            for w in p.extract_words(x_tolerance=1.5):
                lines.setdefault(round(w['top']),[]).append(w)
            for y,ws in lines.items():
                label=' '.join(w['text'] for w in ws if w['x1']<150*1.0 or not re.match(r'^-?\$?[\d,]+\.\d\d$',w['text']))
                for rw in rows_want:
                    if label.strip().startswith(rw):
                        for w in ws:
                            if re.match(r'^-?\$?[\d,]+\.\d\d$',w['text']):
                                # assign to column whose right edge is nearest
                                c=min(cols,key=lambda c:abs(c['x1']-w['x1']))
                                out.setdefault(c['name'],{})[rw]=float(w['text'].replace('$','').replace(',',''))
for k,v in out.items():
    print(f"{k[:40]:40s} | "+" | ".join(f"{v.get(r,0):>11,.2f}" for r in rows_want))
