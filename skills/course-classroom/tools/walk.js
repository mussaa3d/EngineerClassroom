/* Paste into the browser (javascript tool) on the test copy made by testhook.py, then call __walk(a,b) on slices of
   about 50 pages at a time (a long call times out): every idea/quiz page is stepped through, every worked page is
   opened on the board and every move played; KaTeX errors and exceptions are reported. Expect errs: []. */
window.__walk=function(a,b){const T=window.__T;const errs=[];let pages=0,moves=0,other=0;
for(let i=a;i<Math.min(b,T.flat.length);i++){const p=T.flat[i];if(!p)continue;
 try{T.go(i,0);
  if(p.type!=='worked'){other++;for(let st=1;st<(p.steps||[]).length;st++){T.go(i,st);}const k=document.querySelectorAll('.katex-error,merror');if(k.length)errs.push([p.id,'katex-lesson',k[0].textContent.slice(0,80)]);continue;}
  pages++;if(!T.boardOpen)T.toggleBoard();let n=0;while(T.microGo(p,1)&&n<400){T.render();n++;moves++;const k=document.querySelectorAll('.katex-error,merror');if(k.length){errs.push([p.id,'katex',n,k[0].textContent.slice(0,80)]);break;}}}catch(e){errs.push([p.id,String(e).slice(0,120)]);}}
return {pages,other,moves,errs,total:T.flat.length};};
