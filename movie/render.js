const { chromium } = require('playwright');
const fs=require('fs');
(async()=>{
 const [mode,a,b,outdir]=process.argv.slice(2);
 const browser=await chromium.launch();
 const page=await browser.newPage({viewport:{width:+(process.env.VW||1280),height:+(process.env.VH||720)},deviceScaleFactor:1});
 await page.goto('http://127.0.0.1:'+(process.env.PORT||8765)+'/'+(process.env.PAGE||'anim.html'));
 page.on('pageerror',e=>console.log('ERR',e.message));
 await page.evaluate(()=>window.ready);
 fs.mkdirSync(outdir,{recursive:true});
 if(mode==='preview'){
  const times=a.split(',').map(Number);
  for(const t of times){await page.evaluate(t=>renderFrame(t),t);await page.screenshot({path:`${outdir}/p_${String(t).padStart(6,'0')}.png`});}
 } else {
  const fps=24, s=+a, e=+b;
  for(let f=s;f<e;f++){await page.evaluate(t=>renderFrame(t),f/fps);await page.screenshot({path:`${outdir}/f_${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:90});}
 }
 await browser.close();
})();
