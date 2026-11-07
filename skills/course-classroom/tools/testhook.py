"""Makes a test copy of a built classroom with a hook (window.__T) that tools/walk.js uses to step through every page.
Usage: python -I -X utf8 testhook.py <built.html> <test copy.html>   (serve the copy over http and open it in the browser)
Functions a build does not have (an older build without the AI, say) are simply left out of the hook."""
import sys
L = open(sys.argv[1], encoding='utf8').read().split('\n')
i = [n for n, t in enumerate(L) if t == '})();'][-1]   # end of the player's closure (the last one, before Course.boot)
OPT = ['askBoard', 'solveUploads', 'boardScroll']
GET = ['FIXES', 'CAM']
hook = ("window.__T={get flat(){return flat},get S(){return S},go:go,microGo:microGo,microPlan:microPlan,render:render,"
        "toggleBoard:toggleBoard,get MS(){return MS},get boardOpen(){return boardOpen},pg:pg,"
        "setSample:function(s){sample=s;},setCanImages:function(v){canImages=v;}};"
        + ''.join(f"if(typeof {f}==='function')window.__T.{f}={f};" for f in OPT)
        + ''.join(f"try{{if(typeof {g}!=='undefined')Object.defineProperty(window.__T,'{g}',{{get:function(){{return {g};}}}});}}catch(e){{}}" for g in GET))
L.insert(i, hook)
open(sys.argv[2], 'w', encoding='utf8').write('\n'.join(L))
print('ok', sys.argv[2])
