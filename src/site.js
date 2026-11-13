(function(){
  var KEY='bm_favs';
  function load(){try{var v=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(v)?v:[]}catch(e){return []}}
  function save(v){try{localStorage.setItem(KEY,JSON.stringify(v))}catch(e){}}
  var favs=load();
  var BM=window.BM||{teams:{}};
  var root=document.body.getAttribute('data-root')||'';
  function grad(c){var t=BM.teams[c];return t?'linear-gradient(90deg,'+t.c2+' 0 7px,transparent 7px),linear-gradient(120deg,'+t.c1+' 0%,'+t.dark+' 100%)':''}

  // phone menu
  var burger=document.querySelector('[data-burger]'), menu=document.querySelector('[data-menu]');
  if(burger&&menu) burger.addEventListener('click',function(){var o=menu.classList.toggle('open');burger.setAttribute('aria-expanded',o?'true':'false')});

  // followed teams: stars, team-color fills (only for your teams), labels
  function paint(){
    document.querySelectorAll('.star[data-team]').forEach(function(b){
      var on=favs.indexOf(b.getAttribute('data-team'))>-1;
      b.classList.toggle('on',on); b.setAttribute('aria-pressed',on?'true':'false');
      var l=b.querySelector('.lbl'); if(l) l.textContent=on?'Following':'Follow';
    });
    document.querySelectorAll('tr[data-team]').forEach(function(r){r.classList.toggle('fav',favs.indexOf(r.getAttribute('data-team'))>-1)});
    document.querySelectorAll('[data-team-card]').forEach(function(c){c.classList.toggle('is-mine',favs.indexOf(c.getAttribute('data-team-card'))>-1)});
    document.querySelectorAll('[data-teams]').forEach(function(g){
      var ts=g.getAttribute('data-teams').split(' '), mine=ts.filter(function(t){return favs.indexOf(t)>-1});
      g.classList.toggle('is-mine',mine.length>0);
      if(g.classList.contains('tn')) g.style.setProperty('--team-grad',mine.length?grad(mine[0]):'');
    });
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest('.star[data-team]'); if(!b) return;
    e.preventDefault();
    var t=b.getAttribute('data-team'), i=favs.indexOf(t);
    if(i>-1) favs.splice(i,1); else favs.push(t);
    save(favs); paint(); renderMine(); filterGames();
  });

  // Your Team page: one card per followed team, in its colors
  function renderMine(){
    var box=document.getElementById('yt-cards'); if(!box) return;
    var empty=document.getElementById('yt-empty');
    box.innerHTML='';
    if(empty) empty.classList.toggle('hidden',favs.length>0);
    favs.forEach(function(c){
      var t=BM.teams[c]; if(!t) return;
      var a=document.createElement('a'); a.className='ytcard'; a.href=root+'teams/'+t.slug+'/index.html';
      var up=/^\+/.test(t.chg), down=/^[−-]\d/.test(t.chg);
      a.innerHTML='<div class="ytband" style="background:'+grad(c)+'"><span class="ytab">'+c+'</span><div><div class="ytname">'+t.city+' '+t.name+'</div><div class="ytrec">'+t.rec+' · '+t.seed+'</div></div></div>'+
        '<div class="ytbody"><div class="ytrow"><span class="kk">Last game</span><span>'+t.last+'</span></div>'+
        '<div class="ytrow"><span class="kk">Next</span><span>'+(t.next||'Not scheduled yet')+'</span></div>'+
        '<div class="ytrow"><span class="kk">Top-6 odds</span><span><b>'+t.top6+'%</b> <span class="'+(up?'up':down?'down':'dim')+'">'+(t.chg==='—'?'no change':t.chg)+' this week</span></span></div>'+
        '<div class="ytrow"><span class="kk">Projected</span><span>'+t.wins+' wins</span></div></div>';
      box.appendChild(a);
    });
  }

  // game lists: your teams first (keeping story order otherwise); "Your teams / All games" filter
  var mode='all';
  function filterGames(){
    document.querySelectorAll('[data-games]').forEach(function(wrap){
      var cards=[].slice.call(wrap.querySelectorAll('[data-teams]'));
      cards.forEach(function(g,i){if(!g.hasAttribute('data-i')) g.setAttribute('data-i',i)});
      var isMine=function(g){return g.getAttribute('data-teams').split(' ').some(function(t){return favs.indexOf(t)>-1})};
      cards.sort(function(x,y){return (isMine(y)-isMine(x))||(x.getAttribute('data-i')-y.getAttribute('data-i'))});
      cards.forEach(function(g){wrap.appendChild(g)});
      var shown=0, useMine=mode==='mine'&&favs.length>0;
      cards.forEach(function(g){var hide=useMine&&!isMine(g); g.classList.toggle('hidden',hide); if(!hide) shown++});
      var note=wrap.parentNode.querySelector('.none-note'); if(note) note.classList.toggle('hidden',shown>0);
    });
    document.querySelectorAll('[data-mode]').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-mode')===(favs.length?mode:'all'))});
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-mode]'); if(!b) return;
    mode=b.getAttribute('data-mode'); filterGames();
  });

  // home hero: tabs switch the big game card
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-hero-tab]'); if(!b) return;
    var i=b.getAttribute('data-hero-tab');
    document.querySelectorAll('[data-hero-tab]').forEach(function(x){x.classList.toggle('on',x===b)});
    document.querySelectorAll('[data-hero]').forEach(function(c){c.hidden=c.getAttribute('data-hero')!==i});
  });

  // home hero: your teams' games go first and open first (Elan, Nov 13)
  (function(){
    var row=document.querySelector('.gtabs'); if(!row||!favs.length) return;
    var tabs=[].slice.call(row.querySelectorAll('[data-hero-tab]'));
    var mine=tabs.filter(function(b){ var c=document.querySelector('[data-hero="'+b.getAttribute('data-hero-tab')+'"]');
      return c&&(c.getAttribute('data-teams')||'').split(' ').some(function(t){return favs.indexOf(t)>-1}); });
    if(!mine.length) return;
    for(var k=mine.length-1;k>=0;k--) row.insertBefore(mine[k],row.firstChild);
    mine[0].click(); row.scrollLeft=0;
  })();

  // tabs (East/West etc.)
  document.querySelectorAll('[data-tabs]').forEach(function(group){
    var name=group.getAttribute('data-tabs');
    group.addEventListener('click',function(e){
      var b=e.target.closest('[data-tab]'); if(!b) return;
      var v=b.getAttribute('data-tab');
      group.querySelectorAll('[data-tab]').forEach(function(x){x.classList.toggle('on',x===b)});
      document.querySelectorAll('[data-pane="'+name+'"]').forEach(function(p){p.classList.toggle('hidden',p.getAttribute('data-value')!==v)});
    });
  });

  // Learn filters
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-filter]'); if(!b) return;
    var k=b.getAttribute('data-filter');
    document.querySelectorAll('[data-filter]').forEach(function(x){x.classList.toggle('on',x===b)});
    document.querySelectorAll('[data-lib] [data-kind]').forEach(function(c){c.classList.toggle('hidden',k!=='all'&&c.getAttribute('data-kind')!==k)});
  });

  // scroll story: the graphic on top follows the card you're reading; the dots jump between parts
  document.querySelectorAll('[data-story]').forEach(function(sr){
    var steps=[].slice.call(sr.querySelectorAll('.step')), panes=[].slice.call(sr.querySelectorAll('.pane')),
        dots=[].slice.call(sr.querySelectorAll('[data-go]')), n=steps.length, cur=0,
        prev=sr.querySelector('[data-prev]'), next=sr.querySelector('[data-next]'), done=sr.querySelector('[data-done]'), count=sr.querySelector('[data-count]');
    function show(i){ i=Math.max(0,Math.min(n-1,i)); cur=i;
      steps.forEach(function(s,j){s.classList.toggle('on',j===i)});
      panes.forEach(function(p,j){p.classList.toggle('on',j===Math.min(i,panes.length-1))});
      dots.forEach(function(d,j){d.classList.toggle('on',j===i);d.classList.toggle('seen',j<i)});
      if(prev) prev.hidden=(i===0); if(next) next.hidden=(i===n-1); if(done) done.hidden=(i!==n-1);
      if(count) count.textContent=(i+1)+' of '+n; }
    if(next) next.addEventListener('click',function(){show(cur+1)});
    if(prev) prev.addEventListener('click',function(){show(cur-1)});
    dots.forEach(function(d,j){d.addEventListener('click',function(){show(j)})});
    var x0=null,y0=null;
    sr.addEventListener('touchstart',function(e){x0=e.touches[0].clientX;y0=e.touches[0].clientY},{passive:true});
    sr.addEventListener('touchend',function(e){ if(x0===null) return; var dx=e.changedTouches[0].clientX-x0, dy=e.changedTouches[0].clientY-y0; x0=null;
      if(Math.abs(dx)>45&&Math.abs(dx)>Math.abs(dy)*1.5) show(cur+(dx<0?1:-1)); },{passive:true});
    show(0);
  });

  // official highlights: the NBA's own YouTube video loads only after a tap, in YouTube's player
  document.addEventListener('click',function(e){
    var b=e.target.closest('button.player[data-yt]'); if(!b||b.querySelector('iframe')) return;
    var f=document.createElement('iframe');
    var st=b.getAttribute('data-start'), en=b.getAttribute('data-end');
    f.src='https://www.youtube-nocookie.com/embed/'+encodeURIComponent(b.getAttribute('data-yt'))+'?autoplay=1&rel=0'+(st?'&start='+st:'')+(en?'&end='+en:'');
    f.title='Official full game highlights'; f.allow='accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share';
    f.setAttribute('allowfullscreen',''); f.referrerPolicy='strict-origin-when-cross-origin';
    b.appendChild(f);
  });

  paint(); renderMine(); filterGames();
})();

// animation iframes report their height
window.addEventListener('message', function (e) {
  if (!e.data || typeof e.data.bmH !== 'number') return;
  document.querySelectorAll('iframe.anim').forEach(function (f) { if (f.contentWindow === e.source) f.style.height = e.data.bmH + 'px'; });
});

// "Play with sound" restarts the animation and plays the track under it (one track at a time)
(function () {
  var audio = null, current = null;
  function stop() { if (audio) audio.pause(); if (current) current.textContent = '▶ Play with sound'; current = null; }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('button[data-snd]'); if (!btn) return;
    if (current === btn) { stop(); return; }
    stop();
    if (!audio) { audio = new Audio(); audio.loop = true; audio.preload = 'auto'; }
    audio.src = btn.getAttribute('data-snd');
    var frame = btn.parentNode.querySelector('iframe'); if (frame) frame.src = frame.src;
    var p = audio.play();
    current = btn; btn.textContent = 'Mute';
    if (p && p.catch) p.catch(function () { stop(); btn.textContent = 'Sound unavailable here'; });
  });
})();

// Shorts links (Elan, Nov 13): on a computer, open our Shorts in YouTube's normal player (it has full screen);
// on phones and tablets keep /shorts/, which opens the YouTube app's Shorts feed.
(function () {
  var computer = window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches && !/Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
  if (!computer) return;
  document.querySelectorAll('a[href*="youtube.com/shorts/"]').forEach(function (a) {
    var m = a.getAttribute('href').match(/youtube\.com\/shorts\/([A-Za-z0-9_-]{6,})/);
    if (m) a.setAttribute('href', 'https://www.youtube.com/watch?v=' + m[1]);
  });
})();
