import json, wave, numpy as np
SR=44100
d=json.load(open('timeline.json')); T=d['total']+0.5; N=int(SR*T)
rng=np.random.default_rng(3)
mus=np.zeros(N); sfx=np.zeros(N); rev=np.zeros(N); dia=np.zeros(N)
SA=146.83
def hz(s,o=0): return SA*2**((s+12*o)/12)
def add(buf,t0,sig,g=1.0):
    i=int(t0*SR); j=min(N,i+len(sig))
    if 0<=i<N and j>i: buf[i:j]+=sig[:j-i]*g
def env(n,a,r):
    e=np.ones(n); ai=max(1,int(a*SR)); ri=max(1,int(r*SR)); e[:ai]=np.linspace(0,1,ai)
    if ri<n: e[-ri:]*=np.linspace(1,0,ri)
    return e
def tt(dur): return np.arange(int(dur*SR))/SR
def tanp(f,dur=3.5):
    t=tt(dur); s=np.zeros_like(t)
    for k in range(1,12): s+=(1/k)*np.sin(2*np.pi*f*k*(1+.0008*rng.standard_normal())*t+rng.random()*6)*np.exp(-t*(.5+.12*k))
    return s*np.minimum(1,t/.01)
def flute(notes,t0,beat,g=1.0,o=1):
    t=t0;prev=None
    for s,b in notes:
        dd=b*beat
        if s is None: t+=dd;prev=None;continue
        n=int((dd+.12)*SR);x=np.arange(n)/SR;tg=hz(s,o)
        f=np.full(n,tg) if prev is None else prev+(tg-prev)*np.minimum(1,x/.09)
        ph=2*np.pi*np.cumsum(f*(1+.006*np.sin(2*np.pi*5.3*x)*np.minimum(1,x/.5)))/SR
        sig=(np.sin(ph)+.25*np.sin(2*ph)+.08*np.sin(3*ph)+.03*rng.standard_normal(n))*env(n,.06,.18)
        add(mus,t,sig,.09*g);add(rev,t,sig,.06*g);prev=tg;t+=dd
def pad(t0,dur,semis,g=1.0,bright=.3):
    t=tt(dur);s=np.zeros_like(t)
    for sm in semis:
        for dt in(-1,0,1):
            f=hz(sm,-1)*(1+dt*.003);ph=2*np.pi*f*t+rng.random()*6
            for k in range(1,8): s+=np.sin(k*ph)/k**(1.6-bright)
    s*=env(len(t),1.2,1.5);add(mus,t0,s,.012*g);add(rev,t0,s,.012*g)
def voice(f,dur):
    t=tt(dur);fv=f*(1+.008*np.sin(2*np.pi*5*t));ph=2*np.pi*np.cumsum(fv)/SR+rng.random()*6;s=np.zeros_like(t)
    for k in range(1,int(3500/f)):
        fk=k*f;a=np.exp(-((fk-750)/180)**2)+.7*np.exp(-((fk-1150)/220)**2)+.05;s+=a*np.sin(k*ph)
    return s*env(len(t),.35,.5)
def choir(t0,dur,semis,g=1.0):
    for sm in semis:
        for dt in(-1,0,1):v=voice(hz(sm)*(1+dt*.004),dur);add(mus,t0,v,.02*g);add(rev,t0,v,.03*g)
def drum(t0,g=1.0,f0=70):
    t=tt(1.4);f=f0*np.exp(-t*2)+40;s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3.5)+rng.standard_normal(len(t))*np.exp(-t*30)*.2
    add(sfx,t0,s,.5*g);add(rev,t0,s,.15*g)
def tabla(t0,kind,g=1.0):
    t=tt(.5);low=np.sin(2*np.pi*np.cumsum(95*np.exp(-t*3)+60)/SR)*np.exp(-t*7) if kind in('dha','ge') else 0
    hi=(np.sin(2*np.pi*hz(0,1)*t)+.5*np.sin(2*np.pi*hz(0,2)*t))*np.exp(-t*14) if kind in('dha','na') else 0
    add(sfx,t0,low+.5*hi,.2*g)
def thunder(t0,g=1.0):
    t=tt(4);n=rng.standard_normal(len(t));n=np.convolve(n,np.ones(60)/60,'same')
    e=(np.exp(-t*1.2)*(1+.6*np.sin(t*9)))*np.minimum(1,t/.05);add(sfx,t0,n*e*6,.5*g);add(rev,t0,n*e*6,.3*g)
def dice(t0):
    for k in range(7):
        tk=t0+.08*k+.02*k*k;t=tt(.06);s=rng.standard_normal(len(t))*np.exp(-t*120)+np.sin(2*np.pi*(2400+300*k)*t)*np.exp(-t*90)*.5
        add(sfx,tk,s,.35*(1-k/8))
def whoosh(t0,dur=1.2):
    t=tt(dur);n=rng.standard_normal(len(t));k=int(10+30*1);n=np.convolve(n,np.ones(8)/8,'same');e=np.sin(np.pi*t/dur)**2;add(sfx,t0,n*e,.25)
def thud(t0,g=1.0):
    t=tt(.6);s=np.sin(2*np.pi*np.cumsum(60*np.exp(-t*6)+35)/SR)*np.exp(-t*9)+rng.standard_normal(len(t))*np.exp(-t*40)*.3;add(sfx,t0,s,.6*g)
def step(t0,g=.5): thud(t0,g*.5)
def heart(t0,t1,bpm=78):
    t=t0
    while t<t1: thud(t,.55); thud(t+.22,.35); t+=60/bpm
def conch(t0,dur,g=1.0):
    t=tt(dur);f=hz(0)*(2**((-.6*np.exp(-t*3))/12))*(1+.004*np.sin(2*np.pi*4.5*t));ph=2*np.pi*np.cumsum(f)/SR;s=np.zeros_like(t)
    for k in range(1,22): s+=np.sin(k*ph)/k*(1/(1+((k*f.mean()-900)/600)**2)+.15)
    e=np.minimum(1,t/.5)*np.minimum(1,(dur-t)/.6);add(mus,t0,s*e,.12*g);add(rev,t0,s*e,.1*g)
def bell(t0,f=1200,g=1.0):
    t=tt(3);s=sum(np.sin(2*np.pi*f*r*t)*np.exp(-t*(1.2+r)) for r in(1,2.76,5.4));add(sfx,t0,s,.08*g);add(rev,t0,s,.08*g)
def gong(t0,g=1.0):
    t=tt(5);s=sum(np.sin(2*np.pi*f*t+rng.random())*np.exp(-t*.8)/(i+1) for i,f in enumerate([92,148,231,307,412]));add(sfx,t0,s*np.minimum(1,t/.02),.25*g);add(rev,t0,s,.15*g)

# tanpura bed (sorrow/neutral)
t=0.0;cyc=[hz(7,-1),hz(0),hz(0),hz(0,-1)];i=0
while t<T-3: add(mus,t,tanp(cyc[i%4]),.05);t+=1.05;i+=1
A=[(7,1.5),(3,.5),(2,1),(0,3)];Bm=[(0,.5),(2,.5),(3,1),(7,1),(9,1),(7,2)];C=[(9,1),(12,1),(9,.5),(7,.5),(3,1),(2,2)];D=[(7,1),(3,1),(2,1),(0,1),(-3,1),(0,1.5)]
MO1=[(12,1),(9,1),(7,2),(4,1),(2,1)];MO2=[(7,1),(9,1),(12,2),(9,1),(7,1)]
S={e['shot']:e for e in d['tl']}
def at(name): return S[name]['shotT0'],S[name]['shotT1']
a,b=at('title'); pad(a,b-a+2,[0,7],1.2); thunder(a+3.2,1.0); gong(a+.2,.8)
a,b=at('courtWide'); pad(a,b-a,[0,3,7],1); flute(A+Bm,a+1,.75,.8)
a,b=at('diceClose'); dice(a+.6); [tabla(a+k*.2,'na' if k%2 else 'ge',.8) for k in range(10)]
a,b=at('shakuni'); pad(a,b-a,[0,1,7],.9)
a,b=at('bhimaShout'); drum(a+.2,1.2)
a,b=at('yudh'); pad(a,b-a,[-3,0,3],1)
a,b=at('diceRoll'); [tabla(a+k*(.22-.012*k),'dha' if k%4==0 else 'na',1) for k in range(12)]; dice(a+1.5); drum(b-.1,1.2)
a,b=at('shakuniWin'); gong(a,.9)
a,b=at('duryoLaugh'); pad(a,b-a,[0,1,6],1.1)
a,b=at('toChamber'); whoosh(a,1.5)
a,b=at('chamberEnter'); bell(a+.1,1500,.6); thud(a+.5,.8); step(a+1.2); step(a+1.8)
a,b=at('chamberDraupadi'); pad(a,b-a,[0,3,7],.9); flute(C+D,a+.5,.7,.6)
a,b=at('chamberGrab'); drum(a+.2,1.3); drum(b-.3,1)
a,b=at('drag'); [drum(a+k*.4,.9,60) for k in range(8)]; [step(a+k*.3+.15,.6) for k in range(10)]
a,b=at('thrown'); thud(a+.4,1.4); gong(a+.5,.6)
for nm in['draupadiAsk','bhishma','vidura','vikarna','karna']:
    a,b=at(nm); pad(a,b-a,[0,3,7] if nm!='karna' else [0,1,6],1)
a,b=at('draupadiAsk'); flute(Bm+C,a+.4,.8,.5)
a,b=at('command'); drum(a+.25,1.4); gong(a+.3,1)
a,b=at('approach'); [step(a+k*.45,.9) for k in range(6)]
a,b=at('pullShadow'); heart(a,b+9,84); pad(a,b-a+9,[0,1,6],1.1)
a,b=at('dEyesClose'); pad(a,b-a,[0,3],.6)
a,b=at('dLetGo'); t0=a+.6
for k,sm in enumerate([0,3,7]): bell(t0+k*.5,hz(sm,2),.7)
a,b=at('dPray'); pad(a,b-a,[0,4,7],1.3,.5); flute([(0,2),(2,1),(4,1),(7,2),(9,1),(12,3)],b-5,.45,.8)
t=a;k=0
while t<b-.6: tabla(t,'na',.3+.7*(t-a)/(b-a));t+=max(.12,.5-.38*(t-a)/(b-a))
a,b=at('dwarkaWake'); bell(a,1800,1); bell(a+.4,2400,.7); flute([(12,1),(14,1),(16,2)],a+.3,.4,.8)
a,b=at('dwarka'); pad(a,b-a,[0,4,7],1.1,.5); flute([(7,1),(9,1),(12,2),(9,2)],a+.5,.7,.6)
a,b=at('miracle1'); conch(a,3,1.3); c2b=at('hero')[1]
for x in np.arange(a,c2b,60/70*2): drum(x,.9)
for j,x in enumerate(np.arange(a,c2b,2.25)): choir(x,2.4,[[0,4,7],[2,7,9],[0,4,9],[0,4,7]][j%4],1.1)
flute(MO1,a+.3,.6,1.2); flute(MO2,a+4.1,.6,1.2)
a,b=at('fall'); thud(a+1.2,1.5); conch(a+1.4,2.2,.9)
a,b=at('hero'); flute(MO1+MO2,a+.5,.7,1)
a,b=at('bhimaVow'); thunder(a+.2,1); thunder(b-1.2,1.3); [drum(a+k*1.6,.8) for k in range(int((b-a)/1.6))]; pad(a,b-a,[0,1,6],1.2)
a,b=at('dHairVow'); thunder(a+.5,.6); pad(a,b-a,[0,3,7],1)
for nm in['dhrit','dBoon','dhrit2','dRefuse']:
    a,b=at(nm); pad(a,b-a,[0,4,7] if nm!='dhrit' else [0,3,7],.9)
a,b=at('exit'); flute(MO2+MO1,a,.6,1); [drum(a+k*.86,.6) for k in range(5)]
a,b=at('outro'); pad(a,b-a+5,[0,4,7],1.1,.5); flute(A+[(7,1),(9,.5),(7,.5),(4,1),(2,1),(0,3)],a+.6,.75,.9)
a,b=at('endCard'); bell(a+.2,hz(0,3),1)

# dialogue
dmask=np.zeros(N)
for e in d['tl']:
    if e['kind']!='say':continue
    w=wave.open(e['wav']);x=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
    add(dia,e['t0'],x,1.0);i0=int(e['t0']*SR);i1=min(N,int(e['t1']*SR));dmask[i0:i1]=1
k=int(.25*SR);dmask=np.convolve(dmask,np.ones(k)/k,'same');duck=1-.62*np.clip(dmask,0,1)
# reverb
irn=int(2.4*SR);ti=np.arange(irn)/SR
def fconv(x,h):
    L=1<<int(np.ceil(np.log2(len(x)+len(h))));return np.fft.irfft(np.fft.rfft(x,L)*np.fft.rfft(h,L),L)[:len(x)]
wl=fconv(rev,rng.standard_normal(irn)*np.exp(-ti*3));wr=fconv(rev,rng.standard_normal(irn)*np.exp(-ti*3))
sc=.35*np.max(np.abs(mus+sfx))/max(np.max(np.abs(wl)),1e-9)
musL=(mus+sfx*.9+wl*sc)*duck;musR=(np.roll(mus,500)+sfx*.9+wr*sc)*duck
dn=dia/np.max(np.abs(dia))*.9; mn=max(np.max(np.abs(musL)),np.max(np.abs(musR)))
L=dn+musL/mn*.45;R=dn+musR/mn*.45
fade=np.ones(N);fl=int(3*SR);fade[-fl:]=np.linspace(1,0,fl);fade[:int(.3*SR)]=np.linspace(0,1,int(.3*SR))
st=np.stack([L*fade,R*fade],1);st/=np.max(np.abs(st))*1.05;st=np.tanh(st*1.15)
with wave.open('soundtrack.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype(np.int16).tobytes())
print('ok',T)
