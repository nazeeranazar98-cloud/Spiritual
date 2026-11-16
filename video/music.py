import numpy as np, wave
SR=44100; T=112.0; N=int(SR*T)
rng=np.random.default_rng(1)
mix=np.zeros(N); rev_send=np.zeros(N)
SA=146.83  # tonic D3
def hz(semi,octv=0): return SA*2**((semi+12*octv)/12)
def add(buf,start,sig,gain=1.0):
    i=int(start*SR); j=min(N,i+len(sig))
    if i>=N or j<=i: return
    buf[i:j]+=sig[:j-i]*gain
def env_adsr(n,a,r,sus=1.0):
    e=np.ones(n)*sus; ai=max(1,int(a*SR)); ri=max(1,int(r*SR))
    e[:ai]=np.linspace(0,1,ai)*1.0
    if ri<n: e[-ri:]*=np.linspace(1,0,ri)
    return e
# automation curve (section volume)
def curve(points):
    t=np.arange(N)/SR; xs=[p[0] for p in points]; ys=[p[1] for p in points]
    return np.interp(t,xs,ys)

# ---- tanpura ----
def tanpura_pluck(f,dur=3.5):
    n=int(dur*SR); t=np.arange(n)/SR; s=np.zeros(n)
    for k in range(1,14):
        amp=(1/k)*(1+.6*np.sin(k*1.7)); det=1+0.0009*rng.standard_normal()
        s+=amp*np.sin(2*np.pi*f*k*det*t+rng.random()*6)*np.exp(-t*(0.5+0.12*k))
    s*=np.minimum(1,t/0.01)
    return s
tan=np.zeros(N)
cyc=[hz(7,-1),hz(0),hz(0),hz(0,-1)]
t0=0.3;i=0
while t0<T:
    add(tan,t0,tanpura_pluck(cyc[i%4]),0.06); t0+=1.05; i+=1

# ---- flute ----
def flute(notes,start,beat,octv=1,gain=1.0,buf=None,brightness=0.25):
    buf=mix if buf is None else buf
    t=start; prev=None
    for semi,b in notes:
        d=b*beat
        if semi is None: t+=d; prev=None; continue
        n=int((d+0.12)*SR); tt=np.arange(n)/SR
        tgt=hz(semi,octv)
        if prev is None: f=np.full(n,tgt)
        else: f=prev+(tgt-prev)*np.minimum(1,tt/0.09)
        vib=1+0.006*np.sin(2*np.pi*5.3*tt)*np.minimum(1,tt/0.5)
        ph=2*np.pi*np.cumsum(f*vib)/SR
        s=np.sin(ph)+brightness*np.sin(2*ph)+0.08*np.sin(3*ph)
        s+=0.04*rng.standard_normal(n)*np.minimum(1,tt/0.05)
        e=env_adsr(n,0.06,0.18)*(0.85+0.15*np.sin(np.pi*np.minimum(1,tt/d)))
        add(buf,t,s*e,0.11*gain); add(rev_send,t,s*e,0.06*gain)
        prev=tgt; t+=d
    return t

# ---- veena (Karplus-Strong) ----
def veena(f,dur=2.5):
    n=int(dur*SR); p=int(SR/f); buf=rng.uniform(-1,1,p); out=np.zeros(n)
    for i in range(n):
        out[i]=buf[i%p]; buf[i%p]=0.996*0.5*(buf[i%p]+buf[(i+1)%p])
    return out

# ---- tabla ----
def drum(kind):
    n=int(0.5*SR); t=np.arange(n)/SR
    if kind in('dha','ge','dhi'):
        f=95*np.exp(-t*3)+60; low=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*7)
    else: low=0
    if kind in('dha','na','dhi','ti'):
        dec=25 if kind=='ti' else 14
        high=(np.sin(2*np.pi*hz(0,1)*t)+.5*np.sin(2*np.pi*hz(0,2)*t*1.01))*np.exp(-t*dec)
    else: high=0
    click=rng.standard_normal(n)*np.exp(-t*80)*.3 if kind=='ka' else 0
    return low*1.0+high*.5+click
THEKA=['dha','ge','na','ti','na','ka','dhi','na']
def tabla(start,end,beat,gain=1.0,double=False):
    step=beat/2/(2 if double else 1); t=start;i=0
    while t<end-0.01:
        k=THEKA[i%8]; add(mix,t,drum(k),0.22*gain*(1.2 if i%8==0 else 1)); t+=step; i+=1

def bigdrum(t0,g=1.0):
    n=int(1.5*SR); t=np.arange(n)/SR; f=70*np.exp(-t*2)+40
    s=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*3)+rng.standard_normal(n)*np.exp(-t*30)*.2
    add(mix,t0,s,0.5*g); add(rev_send,t0,s,0.2*g)

# ---- conch ----
def conch(t0,dur,g=1.0):
    n=int(dur*SR); t=np.arange(n)/SR
    f=hz(0,0)*(2**((-0.6*np.exp(-t*3))/12))*(1+0.004*np.sin(2*np.pi*4.5*t))
    ph=2*np.pi*np.cumsum(f)/SR; s=np.zeros(n)
    for k in range(1,22):
        s+=np.sin(k*ph)/k*(1/(1+((k*f.mean()-900)/600)**2)+.15)
    e=np.minimum(1,t/0.5)*np.minimum(1,(dur-t)/0.6)
    add(mix,t0,s*e,0.11*g); add(rev_send,t0,s*e,0.1*g)

# ---- choir (formant 'aa') ----
def voice(f,dur,vib=True):
    n=int(dur*SR); t=np.arange(n)/SR
    fv=f*(1+0.008*np.sin(2*np.pi*(5+rng.random())*t+rng.random()*6))
    ph=2*np.pi*np.cumsum(fv)/SR+rng.random()*6; s=np.zeros(n)
    for k in range(1,int(3500/f)):
        fk=k*f; a=np.exp(-((fk-750)/180)**2)+.7*np.exp(-((fk-1150)/220)**2)+.25*np.exp(-((fk-2600)/300)**2)+.05
        s+=a*np.sin(k*ph)
    return s*env_adsr(n,0.35,0.5)
def choir_chord(t0,dur,semis,g=1.0):
    for s in semis:
        for d in(-1,0,1):
            v=voice(hz(s)*(1+d*0.004),dur); add(mix,t0,v,0.022*g); add(rev_send,t0,v,0.03*g)
def choir_mel(notes,t0,beat,g=1.0):
    t=t0
    for s,b in notes:
        d=b*beat
        if s is not None:
            for d2 in(-1,0,1):
                v=voice(hz(s)*(1+d2*0.005),d+0.15); add(mix,t,v,0.03*g); add(rev_send,t,v,0.035*g)
        t+=d

def swell(t0,dur,g=1.0):
    n=int(dur*SR); t=np.arange(n)/SR; s=rng.standard_normal(n)
    s=np.convolve(s,np.ones(30)/30,'same')*(t/dur)**3
    add(mix,t0,s,0.35*g); add(rev_send,t0,s,0.2*g)

BEAT=60/70  # 0.857
A=[(7,1.5),(3,.5),(2,1),(0,3)]
B=[(0,.5),(2,.5),(3,1),(7,1),(9,1),(7,2)]
C=[(9,1),(12,1),(9,.5),(7,.5),(3,1),(2,2)]
Dp=[(7,1),(3,1),(2,1),(0,1),(-3,1),(0,1.5)]
E=[(12,1),(14,1),(12,.5),(9,.5),(7,1),(9,2)]
F=[(7,1),(9,.5),(7,.5),(3,1),(2,1),(0,2)]
def line(notes,t0,length=5.0):
    tot=sum(b for _,b in notes); beat=length*0.92/tot
    flute(notes,t0,beat)

# intro alap 0.5-12
flute([(0,3),(2,1),(3,2),(2,1),(0,3)],4.2,0.62,gain=.9)
flute([(-3,1),(0,2)],10.2,0.6,gain=.7)
# pallavi 12-32
for i,ph in enumerate([A,B,C,Dp]): line(ph,12+5*i)
tabla(12,70,BEAT,0.9)
# charanam 1 32-52
for i,ph in enumerate([B,C,E,F]): line(ph,32+5*i)
# charanam 2 52-70
for i,ph in enumerate([E,C,B,F]): line(ph,52+4.5*i,4.5)
# bridge 70-84: veena + soft flute, near silence 75-79
for tt,s in [(70,0),(71.2,3),(72.4,7),(73.6,3),(74.6,2),(77,0),(78.2,-3),(79.4,0),(80.6,7),(81.8,9),(83,12)]:
    v=veena(hz(s,1)); add(mix,tt,v,0.18); add(rev_send,tt,v,0.12)
flute([(7,2),(3,1),(2,1),(0,3)],70.2,0.55,gain=.6)
flute([(0,2),(2,1),(3,1),(7,2),(9,1),(12,3)],80.5,0.42,gain=.8)
swell(81.8,2.2)
# climax 84-102 (Mohanam)
conch(84.0,2.8,1.2); conch(98.0,2.2,0.8)
for b in np.arange(84,102,BEAT*2): bigdrum(b,0.9)
tabla(86,102,BEAT,1.1,double=True)
chords=[[0,4,7],[2,7,9],[0,4,9],[0,4,7]]
for i,tt in enumerate(np.arange(84,102,2.25)): choir_chord(tt,2.4,chords[i%4],1.0)
M1=[(12,1),(9,1),(7,2),(4,1),(2,1)]
M2=[(7,1),(9,1),(12,2),(9,1),(7,1)]
flute(M1,84.2,0.6,gain=1.2,brightness=.35); flute(M2,88.1,0.6,gain=1.2,brightness=.35)
GOV=[(7,.7),(9,.7),(12,1.6),(None,.2),(7,.7),(9,.7),(12,1.6),(None,.2),(9,.7),(7,.7),(4,1.6)]
choir_mel(GOV,92.0,0.48,1.3)
flute([(12,1),(14,1),(16,2)],96.0,0.5,gain=1.1); flute([(14,1),(12,1),(9,1),(7,2)],99.0,0.55,gain=1.1)
# outro 102-112
for i,ph in enumerate([A,F]): line(ph,102+4*i,4.0)
v=veena(hz(0,1),4); add(mix,109.5,v,.15); add(rev_send,109.5,v,.1)

# master automation: tanpura level
tan*=curve([(0,0),(2.5,1),(74,1),(75.5,.45),(80,.45),(84,.8),(102,.6),(103,1),(110,1),(112,0)])
mix+=tan; rev_send+=tan*.3
# reverb (FFT conv)
ir_n=int(2.2*SR); ti=np.arange(ir_n)/SR
irL=rng.standard_normal(ir_n)*np.exp(-ti*3.2); irR=rng.standard_normal(ir_n)*np.exp(-ti*3.2)
def fconv(x,h):
    L=1<<int(np.ceil(np.log2(len(x)+len(h)))); return np.fft.irfft(np.fft.rfft(x,L)*np.fft.rfft(h,L),L)[:len(x)]
wetL=fconv(rev_send,irL); wetR=fconv(rev_send,irR)
wet_s=0.25/np.max(np.abs(wetL))
L=mix+wetL*wet_s*np.max(np.abs(mix)); R=np.roll(mix,int(.012*SR))*.97+wetR*wet_s*np.max(np.abs(mix))
master=curve([(0,0),(0.4,.8),(70,.8),(74,.65),(75.5,.5),(80.5,.5),(84,1.0),(102,1.0),(103,.75),(110.6,.75),(112,0)])
st=np.stack([L*master,R*master],1)
st/=np.max(np.abs(st))*1.12
st=np.tanh(st*1.1)
with wave.open('music.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(SR);w.writeframes((st*32767).astype(np.int16).tobytes())
print('done',st.shape)
