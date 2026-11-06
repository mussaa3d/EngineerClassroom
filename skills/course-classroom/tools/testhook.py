"""Makes a test copy of a built classroom with a hook (window.__T) that tools/walk.js uses to step through every page.
Usage: python -I -X utf8 testhook.py <built.html> <test copy.html>   (serve the copy over http and open it in the browser)"""
import sys
L = open(sys.argv[1], encoding='utf8').read().split('\n')
i = [n for n, t in enumerate(L) if t == '})();'][0]   # end of the player's closure
L.insert(i, "window.__T={get flat(){return flat},get S(){return S},go:go,microGo:microGo,microPlan:microPlan,render:render,"
            "toggleBoard:toggleBoard,get MS(){return MS},get boardOpen(){return boardOpen},pg:pg,setSample:function(s){sample=s;},"
            "setCanImages:function(v){canImages=v;},askBoard:askBoard,solveUploads:solveUploads,boardScroll:boardScroll,"
            "get FIXES(){return FIXES},get CAM(){return CAM}};")
open(sys.argv[2], 'w', encoding='utf8').write('\n'.join(L))
print('ok', sys.argv[2])
