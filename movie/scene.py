# Movie scene: Vastrakshepam. Builds voices (espeak-ng or custom WAVs), timeline.js and mouth envelopes.
import subprocess, json, os, wave, numpy as np
VOICE={ # espeak variant, pitch, speed
 'narrator':('ml+m1',32,105),'draupadi':('ml+f3',62,118),'krishna':('ml+m2',50,112),'shakuni':('ml+m4',60,122),
 'yudh':('ml+m1',42,105),'bhima':('ml+m3',14,122),'duryo':('ml+m3',30,128),'dush':('ml+m6',18,132),
 'bhishma':('ml+m5',24,98),'vidura':('ml+m1',40,118),'vikarna':('ml+m2',62,132),'karna':('ml+m3',36,120),'dhrit':('ml+m7',34,102)}
B=[ # (kind, who|dur, text|None, shot)
 ('act',5.5,None,'title'),
 ('say','narrator','ഹസ്തിനപുരിയിലെ രാജസഭ. ശകുനിയുടെ കള്ളപ്പകിടയിൽ യുധിഷ്ഠിരൻ എല്ലാം നഷ്ടപ്പെടുത്തി. രാജ്യം, സഹോദരന്മാർ, സ്വയം പോലും.','courtWide'),
 ('act',2.4,None,'diceClose'),
 ('say','shakuni','ഇനിയും ഒരു രത്നം ബാക്കിയുണ്ട്, യുധിഷ്ഠിരാ. നിന്റെ രാജ്ഞി, ദ്രൗപദി.','shakuni'),
 ('say','bhima','ജ്യേഷ്ഠാ! അരുത്!','bhimaShout'),
 ('say','yudh','ദ്രൗപദിയെ… ഞാൻ പണയം വെക്കുന്നു.','yudh'),
 ('act',2.6,None,'diceRoll'),
 ('say','shakuni','ജയിച്ചു!','shakuniWin'),
 ('say','duryo','ഹ ഹ ഹ! ദുശ്ശാസനാ! ആ ദാസിയെ ഈ സഭയിലേക്ക് വലിച്ചുകൊണ്ടുവാ!','duryoLaugh'),
 ('act',1.6,None,'toChamber'),
 ('say','dush','വാടീ, ദാസീ! നിന്റെ ഭർത്താക്കന്മാർ നിന്നെ ചൂതിൽ തോറ്റിരിക്കുന്നു!','chamberEnter'),
 ('say','draupadi','എന്ത് ധൈര്യം! ഞാൻ ഒരു രാജ്ഞിയാണ്. എന്റെ ഭർത്താവ് ആദ്യം തോറ്റത് സ്വയമാണോ, അതോ എന്നെയോ?','chamberDraupadi'),
 ('say','dush','അത് സഭയിൽ വന്ന് ചോദിക്ക്!','chamberGrab'),
 ('act',3.2,None,'drag'),
 ('act',2.2,None,'thrown'),
 ('say','draupadi','പിതാമഹൻ ഭീഷ്മരേ! ഗുരു ദ്രോണരേ! മഹാരാജാവേ! നിങ്ങളെല്ലാം നോക്കിയിരിക്കെ ഒരു സ്ത്രീയെ ഇങ്ങനെ അപമാനിക്കുന്നതാണോ ധർമ്മം?','draupadiAsk'),
 ('say','bhishma','ധർമ്മത്തിന്റെ വഴി വളരെ സൂക്ഷ്മമാണ് മകളേ. എനിക്ക് ഉത്തരം പറയാനാവുന്നില്ല.','bhishma'),
 ('say','vidura','മഹാരാജാവേ, ഇത് നിർത്തൂ! ഇത് കുരുവംശത്തിന്റെ നാശമാണ്!','vidura'),
 ('say','vikarna','ദ്രൗപദി പറയുന്നത് ശരിയാണ്! യുധിഷ്ഠിരൻ ആദ്യം സ്വയം തോറ്റു. ഈ പണയം ന്യായമല്ല!','vikarna'),
 ('say','karna','മിണ്ടാതിരിക്കൂ, കുട്ടീ. ദുശ്ശാസനാ, പാണ്ഡവരുടെ ഉത്തരീയങ്ങൾ അഴിപ്പിക്കൂ. അവളുടേതും.','karna'),
 ('say','duryo','ദുശ്ശാസനാ! അവളുടെ വസ്ത്രം അഴിക്കൂ!','command'),
 ('act',2.6,None,'approach'),
 ('act',3.0,None,'pullShadow'),
 ('say','draupadi','അർജ്ജുനാ… ഭീമാ… ആരെങ്കിലും…','dClutch'),
 ('say','draupadi','കൃഷ്ണാ! ഗോവിന്ദാ!','dOneUp'),
 ('say','narrator','സ്വന്തം ശക്തിയിൽ മുറുകെ പിടിച്ചിരുന്നിടത്തോളം, അവൾ ഒറ്റയ്ക്കായിരുന്നു.','dEyesClose'),
 ('act',2.2,None,'dLetGo'),
 ('say','draupadi','ഹേ ഗോവിന്ദാ! ഹേ ഗോപാലാ! ഹേ ദ്വാരകാനാഥാ! അങ്ങല്ലാതെ എനിക്ക് മറ്റാരുമില്ല! എന്നെ രക്ഷിക്കണേ, കൃഷ്ണാ!','dPray'),
 ('act',1.4,None,'dwarkaWake'),
 ('say','krishna','ഭയപ്പെടേണ്ട. ഞാൻ ഇവിടെയുണ്ട്, കൃഷ്ണേ.','dwarka'),
 ('act',4.0,None,'miracle1'),
 ('act',4.0,None,'miracle2'),
 ('say','vidura','നാരായണാ…!','eldersFold'),
 ('say','duryo','ഇത്… ഇതെന്ത് മായയാണ്?','react'),
 ('act',3.0,None,'fall'),
 ('say','narrator','അവൾ അവന് ഒരു നൂൽ പട്ട് നൽകി. അവൻ അത് അവസാനമില്ലാത്ത വസ്ത്രനദിയായി തിരികെ നൽകി.','hero'),
 ('say','bhima','എല്ലാവരും കേൾക്കൂ! ഭീമനായ ഞാൻ ശപഥം ചെയ്യുന്നു. ഒരുനാൾ യുദ്ധഭൂമിയിൽ ഈ ദുശ്ശാസനന്റെ നെഞ്ച് ഞാൻ പിളർക്കും! ദുര്യോധനാ, നിന്റെ തുട എന്റെ ഗദ കൊണ്ട് ഞാൻ തകർക്കും!','bhimaVow'),
 ('say','draupadi','ഈ അപമാനത്തിന് നീതി ലഭിക്കുന്നത് വരെ, ഞാൻ ഈ മുടി കെട്ടുകയില്ല.','dHairVow'),
 ('say','dhrit','നിർത്തൂ! ദ്രൗപദീ, എന്റെ മകളേ, എന്റെ മക്കളോട് ക്ഷമിക്കൂ. എന്ത് വരം വേണമെങ്കിലും ചോദിച്ചോളൂ!','dhrit'),
 ('say','draupadi','എന്റെ ഭർത്താക്കന്മാരെ അവരുടെ ആയുധങ്ങളോടൊപ്പം മോചിപ്പിക്കണം. അവർ ആരുടെയും ദാസന്മാരാകരുത്.','dBoon'),
 ('say','dhrit','തന്നിരിക്കുന്നു! ഇനിയൊരു വരം കൂടി ചോദിക്കൂ!','dhrit2'),
 ('say','draupadi','വേണ്ട. അത്യാഗ്രഹം ധർമ്മത്തെ നശിപ്പിക്കും. ബാക്കിയെല്ലാം എന്റെ ഭർത്താക്കന്മാർ സ്വന്തം ശക്തി കൊണ്ട് തിരിച്ചുനേടും.','dRefuse'),
 ('act',4.5,None,'exit'),
 ('say','narrator','ലോകം മുഖം തിരിക്കുമ്പോൾ, പാഞ്ചാലിയെ ഓർക്കുക. ഭക്തിയോടെ വിളിക്കുന്നവരെ ഭഗവാൻ ഒരിക്കലും കൈവിടില്ല.','outro'),
 ('act',4.5,None,'endCard'),
]
SR=44100; FPS=24
def readwav(p):
    w=wave.open(p); sr=w.getframerate(); n=w.getnframes(); ch=w.getnchannels()
    a=np.frombuffer(w.readframes(n),np.int16).astype(np.float32)/32768
    if ch>1: a=a.reshape(-1,ch).mean(1)
    if sr!=SR: a=np.interp(np.arange(int(len(a)*SR/sr))/SR*sr,np.arange(len(a)),a)
    return a
tl=[];t=0.0;lines=[]
for i,(k,a,txt,shot) in enumerate(B):
    if k=='act':
        tl.append(dict(i=i,kind='act',t0=round(t,3),t1=round(t+a,3),shot=shot)); t+=a; continue
    who=a; raw=f'voices/raw_{i:02d}.wav'; out=f'voices/line_{i:02d}.wav'
    custom=f'custom_voices/line_{i:02d}.wav'
    if os.path.exists(custom):
        subprocess.run(['ffmpeg','-loglevel','error','-y','-i',custom,'-ac','1','-ar',str(SR),out],check=True)
    else:
        v,p,s=VOICE[who]; s=int(s*1.22)
        subprocess.run(['espeak-ng','-v',v,'-p',str(p),'-s',str(s),'-g','3','-w',raw,txt],check=True)
        flt='highpass=f=90,lowpass=f=6500,aecho=0.8:0.6:45|90:0.25|0.15,volume=1.6'
        if who=='narrator': flt='highpass=f=70,lowpass=f=6000,aecho=0.8:0.7:60|120:0.3|0.2,volume=1.6'
        if who=='krishna': flt='highpass=f=90,lowpass=f=6000,aecho=0.8:0.75:80|160:0.35|0.25,volume=1.5'
        subprocess.run(['ffmpeg','-loglevel','error','-y','-i',raw,'-af',flt,'-ar',str(SR),'-ac','1',out],check=True)
    a_=readwav(out); dur=len(a_)/SR
    # mouth envelope per frame
    hop=SR//FPS; fr=int(np.ceil(dur*FPS)); env=[]
    for f in range(fr):
        seg=a_[f*hop:(f+1)*hop+hop//2]; env.append(float(np.sqrt((seg**2).mean())) if len(seg) else 0)
    env=np.array(env); ref=np.percentile(env,92)+1e-6; env=np.clip(env/ref,0,1); env[env<.12]=0
    pre=0.25 if who!='narrator' else 0.4
    tl.append(dict(i=i,kind='say',who=who,text=txt,t0=round(t+pre,3),t1=round(t+pre+dur,3),shot=shot,shotT0=round(t,3),shotT1=round(t+pre+dur+0.45,3),mouth=[round(x,2) for x in env],wav=out))
    t+=pre+dur+0.45
for e in tl:
    if e['kind']=='act': e['shotT0'],e['shotT1']=e['t0'],e['t1']
TOTAL=round(t,3)
open('timeline.js','w').write('window.TL='+json.dumps(tl,ensure_ascii=False)+';window.TOTAL='+str(TOTAL)+';')
json.dump(dict(total=TOTAL,tl=[{k:v for k,v in e.items() if k!='mouth'} for e in tl]),open('timeline.json','w'),ensure_ascii=False,indent=1)
print('TOTAL',TOTAL,'lines',sum(1 for e in tl if e['kind']=='say'))
