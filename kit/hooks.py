import sys
s=open(sys.argv[1]).read()
a="  const playBtn = document.getElementById('play');"; b="  function frame(now) {"
assert s.count(a)==1 and s.count(b)==1
s=s.replace(a,"  window.__R = {render: (t) => render(t), build: (p) => build(p)};\n"+a).replace(b,"  window.__hold = true;\n"+b+"\n    if (window.__hold) return;")
c="  function build(portrait) {"
assert s.count(c)==1
s=s.replace(c,c+"\n    if (window.__forceP !== undefined) portrait = window.__forceP;")
open(sys.argv[2],'w').write(s)
