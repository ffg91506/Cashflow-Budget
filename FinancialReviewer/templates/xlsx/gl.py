import pdfplumber,re,json,sys
f=sys.argv[1]
rows=[];acct=None
with pdfplumber.open(f) as pdf:
    hdr=None
    for p in pdf.pages:
        ws=p.extract_words(x_tolerance=1.5)
        h={w['text']:w for w in ws if w['text'] in('Name','Description','Split','Amount','Balance','Num')}
        if 'Name' in h: hdr=h
        cols=[('acct',0,hdr['Num']['x0']-120),]
        # bounds
        b={'date':(95,160),'type':(160,240),'num':(hdr['Num']['x0']-5,hdr['Name']['x0']-5),'name':(hdr['Name']['x0']-5,hdr['Description']['x0']-5),
           'desc':(hdr['Description']['x0']-5,hdr['Split']['x0']-5),'split':(hdr['Split']['x0']-5,hdr['Amount']['x0']-40),'amt':(hdr['Amount']['x0']-40,hdr['Balance']['x0']-5)}
        lines={}
        for w in ws: lines.setdefault(round(w['top']/2),[]).append(w)
        keys=sorted(lines)
        # find date rows; gather wrapped text within +-14px
        allw=ws
        for k in keys:
            L=lines[k]
            d=[w for w in L if re.match(r'\d\d/\d\d/\d{4}$',w['text'])]
            if not d: 
                # account header lines: leftmost word at x<40 and no date
                t=' '.join(w['text'] for w in sorted(L,key=lambda w:w['x0']))
                if L and min(w['x0'] for w in L)<35 and not t.startswith('Total') and 'Distribution' not in t and 'Beginning' not in t and 'Accrual' not in t:
                    acct=t
                continue
            y=d[0]['top']
            near=[w for w in allw if abs(w['top']-y)<9]
            r={'acct':acct,'date':d[0]['text']}
            for c,(a,z) in b.items():
                if c=='date':continue
                r[c]=' '.join(w['text'] for w in sorted(near,key=lambda w:(round(w['top']),w['x0'])) if a<=w['x0']<z)
            # dist account from row itself
            r['dist']=' '.join(w['text'] for w in L if w['x0']<d[0]['x0'])
            nums=[w['text'] for w in sorted(L,key=lambda w:w['x0']) if re.match(r'^-?[\d,]+\.\d\d$',w['text'])]
            r['amt']=float(nums[-2].replace(',','')) if len(nums)>=2 else None
            r['type']=' '.join(w['text'] for w in near if d[0]['x1']<w['x0']<hdr['Num']['x0']-5)
            rows.append(r)
json.dump(rows,open(sys.argv[2],'w'),indent=0)
print(len(rows))
