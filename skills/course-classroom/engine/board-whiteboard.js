/* Solution on the paper, one literal move at a time.
   Each page's drawing is split into moves, the way a student draws it by hand:
     empty sheet → axes and scales → each given point → each curve as three dots, then the curve through them →
     then, step by step, each new line, each point, and each stage of a staircase.
   Text labels travel with the drawing they belong to. A step that adds nothing to the graph still gets one move,
   so its working is shown. Elements a step highlights (data-k keys in its `hi`) belong to that step; everything else
   is the foundation.
   The written working goes on a plain A4 "working sheet", step by step like the homework's text pages; the drawing
   goes on the graph paper. Each step first writes its working, then draws, and the board shows the sheet the
   current move is on (the Working / Graph buttons switch by hand). The card on the right only explains. */
/* Whiteboard mode: the board is an adaptive whiteboard the shape of the panel (WBH = its height in board units). The
   drawing's camera fits what is on the board so far (CAM), and the written working zooms to fit its lines (WKC). */
var WBH=0,CAM={pid:null,vb:null},WKC={pid:null,s:1,ty:0};
var VBOX={},PLANS={},MS={pid:null,m:-1,view:null},solOn=true,BOARD_AUTO=true,userClosed={},autoOn=false;
var LEAF='path,line,polyline,polygon,circle,ellipse,rect,text,image';
/* Idea pages are taught in the lesson panel (interactive visual and checks), never on graph paper. */
function boardHasPhases(p){return !!(p&&p.type==='worked'&&nLesson(p));}
/* Crop each drawing to its content (measured once, everything shown) so the graph fills the paper. */
function fullBox(p){
  if(p.id in VBOX)return VBOX[p.id];
  var d=document.createElement('div');d.className='visual';d.style.cssText='position:absolute;left:-9999px;top:0;width:600px;visibility:hidden';
  d.innerHTML=p.visual||'';document.body.append(d);var s=d.querySelector('svg'),b=null;
  try{var r=s.getBBox();if(r.width>40&&r.height>40)b=[r.x-8,r.y-8,r.width+16,r.height+16].map(function(v){return Math.round(v*10)/10;}).join(' ');}catch(e){}
  d.remove();return VBOX[p.id]=b;
}
function leaves(svg){return [].filter.call(svg.querySelectorAll(LEAF),function(n){return !n.closest('defs,marker,pattern,clipPath,mask');});}
/* A path or polyline as subpaths of points; null when it has curve commands. */
function pathPts(n){
  var tag=n.tagName.toLowerCase();
  if(tag==='line')return [[[+n.getAttribute('x1'),+n.getAttribute('y1')],[+n.getAttribute('x2'),+n.getAttribute('y2')]]];
  if(tag==='polyline'||tag==='polygon'){var a=(n.getAttribute('points')||'').trim().split(/[\s,]+/).map(Number),q=[];for(var i=0;i+1<a.length;i+=2)q.push([a[i],a[i+1]]);return [q];}
  var d=n.getAttribute('d')||'';if(/[CcSsQqTtAa]/.test(d))return null;
  var tk=d.match(/[MmLlHhVvZz]|-?\d*\.?\d+(?:e-?\d+)?/g)||[],subs=[],cur=null,x=0,y=0,cmd='',i=0,sx=0,sy=0;
  while(i<tk.length){
    if(/[A-Za-z]/.test(tk[i])){cmd=tk[i++];if(cmd==='Z'||cmd==='z'){if(cur){cur.push([sx,sy]);}continue;}}
    var C=cmd.toUpperCase(),rel=cmd!==C;
    if(C==='M'){x=(rel?x:0)+(+tk[i]);y=(rel?y:0)+(+tk[i+1]);i+=2;cur=[[x,y]];subs.push(cur);sx=x;sy=y;cmd=rel?'l':'L';}
    else if(C==='L'){x=(rel?x:0)+(+tk[i]);y=(rel?y:0)+(+tk[i+1]);i+=2;if(!cur){cur=[];subs.push(cur);}cur.push([x,y]);}
    else if(C==='H'){x=(rel?x:0)+(+tk[i]);i++;cur.push([x,y]);}
    else if(C==='V'){y=(rel?y:0)+(+tk[i]);i++;cur.push([x,y]);}
    else i++;
  }
  return subs;
}
function segCount(subs){return subs.reduce(function(a,s){return a+Math.max(0,s.length-1);},0);}
function partD(subs,n){var d='';subs.forEach(function(s){if(n<=0||s.length<2)return;d+='M'+s[0][0]+' '+s[0][1];for(var i=1;i<s.length&&n>0;i++,n--)d+='L'+s[i][0]+' '+s[i][1];});return d;}
function kindOf(n){
  var tag=n.tagName.toLowerCase();
  if(tag==='text')return {k:'text'};
  if(tag==='circle'||tag==='ellipse')return {k:'point'};
  if(tag==='rect'||tag==='image')return {k:'shape'};
  var subs=pathPts(n),filled=(n.getAttribute('class')||'').split(' ').indexOf('f')>=0||(n.getAttribute('fill')&&n.getAttribute('fill')!=='none');
  if(!subs){try{return n.getTotalLength()>60?{k:'curve',len:n.getTotalLength()}:{k:'line'};}catch(e){return {k:'line'};}}
  var ns=segCount(subs);if(!ns)return {k:'line'};
  /* a staircase is made of real horizontal and vertical runs (not the tiny steep pieces of a fine curve) */
  var al=0,runs=0;subs.forEach(function(s){for(var i=1;i<s.length;i++){var dx=Math.abs(s[i][0]-s[i-1][0]),dy=Math.abs(s[i][1]-s[i-1][1]);
    if(dx<.6||dy<.6){al++;if(Math.max(dx,dy)>=3)runs++;}}});
  if(filled&&tag!=='line')return {k:'shape'};
  if(ns>=4&&ns<=120&&al/ns>=.8&&runs/ns>=.8)return {k:'stairs',subs:subs,ns:ns};
  if(ns>=4)return {k:'curve',subs:subs};
  return {k:al===ns?'aligned':'line'};
}
function curveDots(n,info){
  var pts=[];
  if(info.subs){var all=[].concat.apply([],info.subs);[.15,.5,.85].forEach(function(f){pts.push(all[Math.round(f*(all.length-1))]);});}
  else{try{var L=n.getTotalLength();[.15,.5,.85].forEach(function(f){var q=n.getPointAtLength(L*f);pts.push([q.x,q.y]);});}catch(e){}}
  return pts;
}
/* Build the move list for a page (cached). Moves: {step, show:[{i,segs?}], dots:[[x,y]], label}. */
function microPlan(p){
  if(PLANS[p.id])return PLANS[p.id];
  var d=document.createElement('div');d.className='visual';d.style.cssText='position:absolute;left:-9999px;top:0;width:600px;visibility:hidden';
  d.innerHTML=p.visual||'';document.body.append(d);
  var svg=d.querySelector('svg'),lv=svg?leaves(svg):[],list=p.steps||[],firstStep={};
  list.forEach(function(s,i){(s.hi||[]).forEach(function(k){if(!(k in firstStep))firstStep[k]=i;});});
  var atoms=lv.map(function(n,i){
    var g=n.closest('[data-k]'),st=-1;
    if(g)g.getAttribute('data-k').split(' ').forEach(function(k){if(k in firstStep&&(st<0||firstStep[k]<st))st=firstStep[k];});
    var info=kindOf(n),soft=(n.getAttribute('class')||'').split(' ').indexOf('soft')>=0;
    return {i:i,n:n,step:st,info:info,soft:soft};
  });
  var moves=[],axes={step:-1,show:[],dots:[],label:'Axes and scales'};
  function addAtomMoves(a,step,pending){
    var k=a.info.k,base=pending.splice(0).map(function(t){return {i:t.i};});
    if(k==='curve'){
      moves.push({step:step,show:base,dots:curveDots(a.n,a.info),label:'Mark three points of the curve'});
      moves.push({step:step,show:[{i:a.i}],dots:[],label:'Draw the curve through them'});
    }else if(k==='stairs'){
      for(var s=2;s<=a.info.ns+1;s+=2){moves.push({step:step,show:(s===2?base:[]).concat([{i:a.i,segs:Math.min(s,a.info.ns),subs:a.info.subs}]),dots:[],label:'Step off one stage'});}
    }else moves.push({step:step,show:base.concat([{i:a.i}]),dots:[],label:{point:'Plot a point',shape:'Draw it',line:'Draw a line',aligned:'Draw a line'}[k]||'Draw it'});
  }
  /* foundation: axes, scales and grid first, then each given point, line and curve */
  var rest=[];
  atoms.filter(function(a){return a.step<0;}).forEach(function(a){
    var k=a.info.k;
    if(k==='text'||k==='aligned'||a.soft||(k==='shape'&&a.n.tagName.toLowerCase()==='rect'))axes.show.push({i:a.i});else rest.push(a);
  });
  if(axes.show.length)moves.push(axes);
  /* given points first, then the curves through them, then any other lines and shapes */
  var rank={point:0,curve:1};
  rest.map(function(a,j){return {a:a,j:j};}).sort(function(x,y){return ((x.a.info.k in rank?rank[x.a.info.k]:2)-(y.a.info.k in rank?rank[y.a.info.k]:2))||x.j-y.j;})
    .forEach(function(o){addAtomMoves(o.a,-1,[]);});
  /* then every lesson step, one drawing move at a time; labels travel with their drawing */
  list.forEach(function(s,k){
    var mine=atoms.filter(function(a){return a.step===k;}),pending=[];
    moves.push({step:k,show:[],dots:[],label:(s.lines&&s.lines.length)?'Write the working':'',write:true});
    var start=moves.length;
    mine.forEach(function(a){if(a.info.k==='text'){pending.push(a);return;}addAtomMoves(a,k,pending);});
    if(pending.length){if(moves.length>start)moves[moves.length-1].show=moves[moves.length-1].show.concat(pending.map(function(t){return {i:t.i};}));else moves.push({step:k,show:pending.map(function(t){return {i:t.i};}),dots:[],label:'Label it'});}
  });
  d.remove();
  return PLANS[p.id]={moves:moves,n:moves.length};
}
function microReset(p){MS={pid:p.id,m:-1,view:null};}
/* Which sheet the board shows now: 'work' (plain A4 with the written working) or 'graph' (the graph paper). */
function sheetView(p,it){
  if(it&&it.kind)return 'graph';
  if(!p.visual)return 'work';
  if(MS.view&&MS.pid===p.id)return MS.view;
  if(MS.m<0)return 'graph';
  var mv=microPlan(p).moves[MS.m];
  return mv&&mv.write?'work':'graph';
}
/* The working sheet: every step so far, its title underlined and each line of working below it, answers boxed.
   It is cut into A4 pages after it is laid out (paginateWork) and shows the page the current step is on. */
function workLayer(p,it){
  var g=paperBox('wb'),box=el('div',{class:'bdwork',id:'bdWork',dir:'ltr'}),inner=el('div',{class:'wkin',id:'bdWorkIn'});
  box.style.left=(g.x0/g.W*100)+'%';box.style.top=(g.y0/g.H*100)+'%';
  box.style.width=((g.x1-g.x0)/g.W*100)+'%';box.style.height=((g.y1-g.y0)/g.H*100)+'%';
  if(!solOn||(it&&it.kind))return box;
  var st=p.steps||[],k=MS.m<0?-1:microStep(p);
  if(!p.visual&&MS.m<0)k=-1;
  box.append(inner);
  inner.append(el('div',{class:'wkb wkhead',text:(p.chip?p.chip+'  ':'')+p.title}));
  for(var i=0;i<=k&&i<st.length;i++){
    var s=st[i],bl=el('div',{class:'wkb'+(i===k?' now':'')});
    bl.append(el('div',{class:'wkt',text:s.title||''}));
    (s.lines||[]).forEach(function(ln,j){var o=typeof ln==='string'?{tex:ln}:ln;
      bl.append(el('div',{class:'wkl'+(o.ans?' ans':'')+(hlLine(p,i,j)?' hl':'')+(p._fixed&&p._fixed[i+':'+j]?' fixed':''),title:p._fixed&&p._fixed[i+':'+j]?u('Corrected')+': '+p._fixed[i+':'+j]:null},o.note?el('span',{class:'wkn',text:o.note}):el('span',{html:texSpan(o.ans||o.tex,false)})));});
    inner.append(bl);
  }
  tex(box);
  /* the zoom depends on the laid-out height: measure again after layout and once the handwriting font is in.
     Only the sheet's own box is watched (not the writing, whose width the fit itself changes). */
  requestAnimationFrame(paginateWork);setTimeout(paginateWork,300);setTimeout(paginateWork,1000);if(document.fonts)document.fonts.ready.then(paginateWork);
  if(window.ResizeObserver)new ResizeObserver(function(){paginateWork();}).observe(box);
  return box;
}
/* Zoom the written working to fit the board: large while there are few lines, smaller as lines are added; once
   it is as small as is readable, the newest lines stay in view and the rest can be scrolled up and down
   (wheel, two fingers, the Pan tool, or the ▲ ▼ buttons). WKC.uy is the reader's own scroll. */
function shrinkLines(c){[].forEach.call(c.querySelectorAll('.wkl'),function(l){l.style.fontSize='';var r=l.clientWidth/Math.max(1,l.scrollWidth);if(r<1)l.style.fontSize=Math.max(40,Math.floor(r*98))+'%';});}
function paginateWork(){
  var w=$('bdWork'),c=$('bdWorkIn');if(!w||!c||!w.clientWidth||w._busy)return;
  w._busy=true;
  var W=w.clientWidth,H=w.clientHeight,base=Math.max(13,Math.min(30,W*0.034)),s=1.6,h=0;
  c.style.transition='none';c.style.fontSize=base+'px';
  for(var it=0;it<4;it++){
    c.style.width=(W/s)+'px';shrinkLines(c);
    h=Math.max(1,c.scrollHeight);var ns=Math.max(.8,Math.min(1.6,.96*H/h));
    if(Math.abs(ns-s)<.01)break;s=ns;
  }
  c.style.width=(W/s)+'px';shrinkLines(c);h=Math.max(1,c.scrollHeight);   /* lines fitted at the final width */
  var pid=pg()&&pg().id,auto=h*s>H?H-h*s:0;
  /* a line the course AI is explaining is brought into view (about a third of the way down) */
  var hl=c.querySelector('.wkl.hl');
  if(hl&&h*s>H){var y=hl.offsetTop*s;if(y+auto<0||y+auto>H-hl.offsetHeight*s-8)auto=Math.max(H-h*s,Math.min(0,H*.33-y));}
  var same=WKC.pid===pid,uy=same&&WKC.m===MS.m?WKC.uy||0:0;
  if(same){c.style.transform='translateY('+WKC.ty+'px) scale('+WKC.s+')';void c.offsetHeight;}
  var ty=Math.max(Math.min(0,H-h*s),Math.min(0,auto+uy));
  if(!(same&&Math.abs(WKC.s-s)<.002&&Math.abs(WKC.ty-ty)<.5)){
    c.style.transition='transform .45s ease';c.style.transform='translateY('+ty.toFixed(1)+'px) scale('+s.toFixed(3)+')';
  }
  WKC={pid:pid,m:MS.m,s:+s.toFixed(3),ty:+ty.toFixed(1),auto:auto,uy:ty-auto,h:h,H:H};
  var pn=$('bdPageNo');if(pn)pn.textContent='';
  requestAnimationFrame(function(){w._busy=false;});
}
/* the reader scrolls the board: the working sheet moves up/down; the drawing's camera pans */
function boardScroll(dy,dx){
  var c=$('bdWorkIn');
  if(c&&WKC.h){var lo=Math.min(0,WKC.H-WKC.h*WKC.s),ty=Math.max(lo,Math.min(0,WKC.ty-dy));WKC.ty=ty;WKC.uy=ty-WKC.auto;c.style.transition='none';c.style.transform='translateY('+ty.toFixed(1)+'px) scale('+WKC.s+')';return;}
  var sv=document.querySelector('#bdSol svg'),p=pg();if(!sv||!p)return;
  if(!CAM.vb||CAM.pid!==p.id){var v0=(sv.getAttribute('viewBox')||'').split(/[\s,]+/).map(Number);if(v0.length!==4||v0.some(isNaN))return;CAM={pid:p.id,vb:v0};}
  var r=sv.getBoundingClientRect(),k=Math.max(CAM.vb[2]/Math.max(1,r.width),CAM.vb[3]/Math.max(1,r.height));
  CAM.vb=[CAM.vb[0]+(dx||0)*k,CAM.vb[1]+dy*k,CAM.vb[2],CAM.vb[3]];sv.setAttribute('viewBox',CAM.vb.map(function(v){return v.toFixed(2);}).join(' '));
}
function microStep(p){var pl=microPlan(p),mv=pl.moves[MS.m];return mv?mv.step:-1;}
/* Move forward or back one move; false when the page's moves are used up in that direction. */
function microGo(p,d){
  var pl=microPlan(p),m=MS.m+d;
  if(m<-1||m>=pl.n)return false;
  MS.m=m;MS.view=null;var st=microStep(p);if(st>=0){S.st=st;markDone();save();}else S.st=0;
  return true;
}
function solutionLayer(p,it){
  /* A homework-sheet page (p.sheet) is drawn over the whole paper at 4 units per mm, so it lands where the
     student drew it, at the same scale; it only shows on its own paper. Other pages are fitted to the grid. */
  var sheet=false,g=paperBox('wb'),box=el('div',{class:'bdsol',id:'bdSol'});
  if(sheet)g={W:1,H:1,x0:0,y0:0,x1:1,y1:1};
  box.style.left=(g.x0/g.W*100)+'%';box.style.top=(g.y0/g.H*100)+'%';
  box.style.width=((g.x1-g.x0)/g.W*100)+'%';box.style.height=((g.y1-g.y0)/g.H*100)+'%';
  if(!solOn||!p.visual||(it&&it.kind)||MS.m<0)return box;
  var pl=microPlan(p),st=microStep(p),v=visual(p,st,true);if(!v||!v.querySelector('svg'))return box;
  var sv=v.querySelector('svg'),vb=fullBox(p);
  if(CAM.pid===p.id&&CAM.vb)vb=CAM.vb.join(' ');
  if(vb)sv.setAttribute('viewBox',vb);
  sv.setAttribute('preserveAspectRatio','xMidYMid meet');
  var lv=leaves(sv),vis={},segs={},dots=[],fresh={};
  for(var m=0;m<=MS.m&&m<pl.n;m++){
    var mv=pl.moves[m];
    mv.show.forEach(function(e){vis[e.i]=true;if(e.segs){segs[e.i]=e;}if(m===MS.m)fresh[e.i]=true;});
    mv.dots.forEach(function(q){dots.push({q:q,fresh:m===MS.m});});
  }
  /* handwriting is narrower than the drawing font, so it is written 1.3 times larger, as big as in the homework */
  [].forEach.call(sv.querySelectorAll('text'),function(t){var fs=parseFloat(t.style.fontSize)||parseFloat(t.getAttribute('font-size'))||13;t.style.fontSize=(fs*1.3).toFixed(1)+'px';});
  lv.forEach(function(n,i){
    if(!vis[i]){n.style.display='none';return;}
    if(segs[i])n.setAttribute('d',partD(segs[i].subs,segs[i].segs));
    if(fresh[i])n.classList.add('fresh');
  });
  dots.forEach(function(o){var c=svgEl('circle',{cx:o.q[0],cy:o.q[1],r:3.4,class:'mdot'+(o.fresh?' fresh':'')});sv.append(c);});
  markGraph(p,sv);
  box.append(v);var once=false;function cf(){if(once)return;once=true;camFit(p,sv);}requestAnimationFrame(cf);setTimeout(cf,80);return box;
}
/* Point the camera at what is drawn so far (plus a margin), never closer than 40% of the whole drawing, and glide
   there from where it was, so the board zooms in on the first marks and out as the drawing grows. */
function camFit(p,sv){
  if(!sv.isConnected)return;
  var full=(fullBox(p)||'0 0 600 300').split(' ').map(Number),r;
  try{r=sv.getBBox();}catch(e){return;}
  if(!r||!r.width&&!r.height)r={x:full[0],y:full[1],width:full[2],height:full[3]};
  var pad=Math.max(10,.06*Math.max(r.width,r.height)),x=r.x-pad,y=r.y-pad,w=r.width+2*pad,h=r.height+2*pad;
  var mw=.4*full[2],mh=.4*full[3];if(w<mw){x-=(mw-w)/2;w=mw;}if(h<mh){y-=(mh-h)/2;h=mh;}
  var to=[x,y,w,h],from=(CAM.pid===p.id&&CAM.vb)?CAM.vb:full,t0=null;
  CAM={pid:p.id,vb:to};
  function ease(t){return t<.5?2*t*t:1-Math.pow(-2*t+2,2)/2;}
  function frame(ts){if(!sv.isConnected)return;if(t0===null)t0=ts;var t=Math.min(1,(ts-t0)/550),e=ease(t);
    sv.setAttribute('viewBox',from.map(function(f,i){return (f+(to[i]-f)*e).toFixed(2);}).join(' '));if(t<1)requestAnimationFrame(frame);}
  requestAnimationFrame(frame);
  setTimeout(function(){if(t0===null&&sv.isConnected)sv.setAttribute('viewBox',to.map(function(v){return v.toFixed(2);}).join(' '));},700);
}
function solutionCard(p,it){
  var st=p.steps||[];
  if(!st.length||(it&&it.kind)||p.type==='home')return null;
  var card=el('div',{class:'bdcard',dir:isAr()?'rtl':'ltr'}),has=boardHasPhases(p),pl=has?microPlan(p):{n:0,moves:[]};
  var next=el('button',{class:'btn primary',type:'button',text:u('Next move'),onclick:function(){if(microGo(p,1))render();else move(1);}});
  var back=el('button',{class:'btn',type:'button',text:u('Previous move'),onclick:function(){if(microGo(p,-1))render();else move(-1);}});
  var tog=el('button',{class:'btn ghost',type:'button',text:u(solOn?'Hide solution':'Show solution'),onclick:function(){solOn=!solOn;render();}});
  if(has&&MS.m<0){
    card.append(el('div',{class:'count',text:u('Solution on the paper')+' · '+u('empty paper')}),el('h3',{text:u('A clean sheet of paper')}),
      el('div',{class:'say',html:'<p>'+u(p.visual?'Start like the exam: an empty sheet. Each press adds one move: the axes and scales, each given point, each curve (three points first, then the curve), then every line and stage of the solution.':'Start like the exam: an empty sheet. Each press writes the next step of the working on the paper; this card explains why.')+'</p>'}));
    back.disabled=true;card.append(el('div',{class:'tools'},back,next));return card;
  }
  var mv=pl.moves[MS.m],k=mv?mv.step:Math.min(S.st,st.length-1);
  card.append(el('div',{class:'count',text:has?(u('Move')+' '+(MS.m+1)+(isAr()?' من ':' of ')+pl.n+(k>=0?' · '+u('step')+' '+(k+1)+(isAr()?' من ':' of ')+st.length:'')):(u('step')+' '+(k+1)+(isAr()?' من ':' of ')+st.length)}));
  if(k<0){
    card.append(el('h3',{text:u('The foundation')}),el('p',{class:'mvlabel',text:u(mv.label)}),
      el('div',{class:'say',html:'<p>'+u('Axes and scales, the given data and the given points. Try the next move yourself with the pen, then press Next move to compare.')+'</p>'}));
  }else{
    var s=st[k];card.append(el('h3',{html:T(s,'title')||T(p,'title')}));
    if(mv&&mv.label)card.append(el('p',{class:'mvlabel',text:u(mv.label)}));
    card.append(el('div',{class:'say',html:T(s,'say')||''}));
    ['warn','check'].forEach(function(f){var t=T(s,f);if(t)card.append(el('div',{class:'say bd'+f,html:t}));});
  }
  /* long drawings (many points or tie lines): finish the current step in one press */
  var last=MS.m;while(last+1<pl.n&&pl.moves[last+1].step===k)last++;
  var fin=last>MS.m?el('button',{class:'btn ghost',type:'button',text:u('Finish this step')+' ('+(last-MS.m)+')',onclick:function(){MS.m=last;var s2=microStep(p);if(s2>=0){S.st=s2;markDone();save();}render();}}):null;
  card.append(el('div',{class:'tools'},back,next,fin,p.visual?tog:null));
  var fp=fixPanel(p);if(fp)card.append(fp);
  tex(card);return card;
}
/* Called at the start of every render: the board is the default view for any lesson step that has a graph;
   moving on to a question (or a page without a graph) closes a board that opened by itself. */
function autoBoard(){
  var p=pg(),it=steps(p)[S.st],want=BOARD_AUTO&&boardHasPhases(p)&&!(it&&it.kind)&&!userClosed[p.id];
  if(want&&!boardOpen){boardOpen=true;autoOn=true;}
  else if(!want&&boardOpen&&autoOn){boardOpen=false;autoOn=false;}
  if(boardOpen&&MS.pid!==p.id){microReset(p);}
}

/* Question pictures (the original sheets) are stored once in QPICS and filled in wherever a question is shown. */
(function(){function fill(){[].forEach.call(document.querySelectorAll('img[data-qpic]:not([src])'),function(i){var u=(window.QPICS||{})[i.getAttribute('data-qpic')];if(u)i.src=u;});}
new MutationObserver(fill).observe(document.documentElement,{childList:true,subtree:true});fill();})();
/* Zoom and pan on every paper: the buttons, Ctrl + wheel or a trackpad pinch zoom around the pointer, two fingers
   pinch and pan on a touch screen, the Move tool drags the sheet, and the wheel scrolls it when zoomed in. */
var BZ=1,BZMOVE=false,BZS={id:null,l:0,t:0};
function setZoom(z,cx,cy){
  var f=$('bdFit'),st=$('bdStage');if(!f||!st)return;
  z=Math.max(1,Math.min(6,z));if(Math.abs(z-BZ)<1e-3)return;
  var r=st.getBoundingClientRect(),fr=f.getBoundingClientRect();
  if(cx==null){cx=fr.left+fr.width/2;cy=fr.top+fr.height/2;}
  var rx=(cx-r.left)/r.width,ry=(cy-r.top)/r.height;
  BZ=z;fitBoard();
  var n=st.getBoundingClientRect();f.scrollLeft+=n.left+rx*n.width-cx;f.scrollTop+=n.top+ry*n.height-cy;
  var zl=$('bdZoomPct');if(zl)zl.textContent=Math.round(BZ*100)+'%';
}
function zoomCtl(){
  var g=el('span',{class:'bdzoom'});
  g.append(el('button',{class:'btn tiny',type:'button','aria-label':'Zoom out',title:'Zoom out',text:'−',onclick:function(){setZoom(BZ/1.25);}}),
    el('span',{class:'bdpn',id:'bdZoomPct',text:Math.round(BZ*100)+'%'}),
    el('button',{class:'btn tiny',type:'button','aria-label':'Zoom in',title:'Zoom in',text:'+',onclick:function(){setZoom(BZ*1.25);}}),
    el('button',{class:'btn tiny',type:'button',text:u('Fit'),onclick:function(){setZoom(1);}}),
    el('button',{class:'btn tiny',type:'button','aria-label':u('Scroll up'),title:u('Scroll up'),text:'▲',onclick:function(){var f=$('bdFit');if(BZ>1.001&&f)f.scrollTop-=f.clientHeight*.4;else boardScroll(-(f?f.clientHeight:300)*.4);}}),
    el('button',{class:'btn tiny',type:'button','aria-label':u('Scroll down'),title:u('Scroll down'),text:'▼',onclick:function(){var f=$('bdFit');if(BZ>1.001&&f)f.scrollTop+=f.clientHeight*.4;else boardScroll((f?f.clientHeight:300)*.4);}}),
    el('button',{class:'btn tiny',type:'button','aria-pressed':BZMOVE?'true':'false',title:u('Drag the sheet around'),text:u('Pan'),onclick:function(){BZMOVE=!BZMOVE;this.setAttribute('aria-pressed',BZMOVE?'true':'false');var c=$('bdCanvas');if(c)c.classList.toggle('bdmove',BZMOVE);}}));
  return g;
}
function wireZoom(){
  var f=$('bdFit'),cv=$('bdCanvas');if(!f||!cv)return;
  if(BZMOVE)cv.classList.add('bdmove');
  /* keep the view where it was while the steps re-draw the board */
  if(BZS.id===(B&&B.id)){f.scrollLeft=BZS.l;f.scrollTop=BZS.t;}else BZS={id:B&&B.id,l:0,t:0};
  f.addEventListener('scroll',function(){BZS.l=f.scrollLeft;BZS.t=f.scrollTop;});
  f.addEventListener('wheel',function(e){if(!e.ctrlKey&&!e.metaKey){if(BZ>1.001)return;e.preventDefault();var k=e.deltaMode===1?30:e.deltaMode===2?300:1;boardScroll(e.deltaY*k,e.deltaX*k);return;}e.preventDefault();setZoom(BZ*Math.exp(-e.deltaY*(e.deltaMode?0.05:0.0025)),e.clientX,e.clientY);},{passive:false});
  var tp={},pinch=null,drag=null;
  function mid(){var k=Object.keys(tp),a=tp[k[0]],b=tp[k[1]];return {x:(a.x+b.x)/2,y:(a.y+b.y)/2,d:Math.hypot(a.x-b.x,a.y-b.y)||1};}
  /* capture phase, so a second finger or the Move tool stops the pen before it draws */
  cv.addEventListener('pointerdown',function(e){
    if(BZMOVE){e.stopImmediatePropagation();e.preventDefault();cv.setPointerCapture(e.pointerId);drag={x:e.clientX,y:e.clientY,l:f.scrollLeft,t:f.scrollTop,lx:e.clientX,ly:e.clientY};return;}
    if(e.pointerType!=='touch')return;
    tp[e.pointerId]={x:e.clientX,y:e.clientY};
    if(Object.keys(tp).length===2){
      e.stopImmediatePropagation();e.preventDefault();
      var s=B&&B.strokes[B.strokes.length-1];if(s&&s.pts.length<40){B.strokes.pop();paintStrokes();}   /* the first finger's mark was the start of a pinch */
      cv.dispatchEvent(new PointerEvent('pointercancel'));pinch=mid();pinch.z=BZ;
    }
  },true);
  cv.addEventListener('pointermove',function(e){
    if(drag){e.stopImmediatePropagation();if(BZ>1.001){f.scrollLeft=drag.l-(e.clientX-drag.x);f.scrollTop=drag.t-(e.clientY-drag.y);}else boardScroll(-(e.clientY-drag.ly),-(e.clientX-drag.lx));drag.lx=e.clientX;drag.ly=e.clientY;return;}
    if(!tp[e.pointerId])return;tp[e.pointerId]={x:e.clientX,y:e.clientY};
    if(pinch&&Object.keys(tp).length>=2){e.stopImmediatePropagation();var m=mid();setZoom(pinch.z*m.d/pinch.d,m.x,m.y);if(BZ>1.001){f.scrollLeft-=m.x-pinch.x;f.scrollTop-=m.y-pinch.y;}else boardScroll(-(m.y-pinch.y),-(m.x-pinch.x));pinch.x=m.x;pinch.y=m.y;}
  },true);
  function up(e){delete tp[e.pointerId];if(drag){drag=null;e.stopImmediatePropagation();}if(Object.keys(tp).length<2)pinch=null;}
  cv.addEventListener('pointerup',up,true);cv.addEventListener('pointercancel',up,true);
}
