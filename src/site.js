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
  if(burger&&menu){
    var shut=function(){menu.classList.remove('open');burger.setAttribute('aria-expanded','false')};
    burger.addEventListener('click',function(e){e.stopPropagation();var o=menu.classList.toggle('open');burger.setAttribute('aria-expanded',o?'true':'false')});
    // the menu floats over the page, so a tap anywhere else or Escape closes it
    document.addEventListener('click',function(e){if(menu.classList.contains('open')&&!menu.contains(e.target))shut()});
    document.addEventListener('keydown',function(e){if(e.key==='Escape')shut()});
  }

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

  // home hero: your teams' games go first and open first (the owner, Nov 13)
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
        spaces=[].slice.call(sr.querySelectorAll('[data-space]')), dots=[].slice.call(sr.querySelectorAll('.dots [data-go]')),
        next=sr.querySelector('[data-next]'), done=sr.querySelector('[data-done]'), hint=sr.querySelector('[data-hint]'),
        hdr=document.querySelector('header.top'), n=steps.length, cur=-1;
    function hh(){ return hdr?hdr.getBoundingClientRect().height:0; }
    function setH(){ sr.style.setProperty('--hh',hh()+'px'); }
    function countUp(pn){ if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      pn.querySelectorAll('[data-countto]').forEach(function(el){ var to=+el.getAttribute('data-countto'), t0=null;
        function st(ts){ if(!t0) t0=ts; var k=Math.min(1,(ts-t0)/650); el.textContent=Math.round(to*(1-Math.pow(1-k,3))); if(k<1) requestAnimationFrame(st); }
        requestAnimationFrame(st); }); }
    function show(i){ if(i===cur) return; cur=i;
      steps.forEach(function(s,j){s.classList.toggle('on',j===i)});
      panes.forEach(function(p,j){p.classList.toggle('on',j===i)});
      dots.forEach(function(d,j){d.classList.toggle('on',j===i);d.classList.toggle('seen',j<i)});
      if(hint) hint.hidden=(i!==0); if(next) next.hidden=(i===n-1); if(done) done.hidden=(i!==n-1);
      if(panes[i]) countUp(panes[i]); }
    // part i is showing while spacer i is passing the top of the screen
    function onScroll(){ var y=hh()+window.innerHeight*0.25, i=0; spaces.forEach(function(s,j){ if(s.getBoundingClientRect().top<=y) i=j; }); show(i); }
    function go(i){ var s=spaces[i]; if(!s) return; window.scrollTo({top:window.scrollY+s.getBoundingClientRect().top-hh()-window.innerHeight*0.25+24,behavior:'smooth'}); }
    sr.addEventListener('click',function(e){ var b=e.target.closest('[data-go]'); if(b){ e.preventDefault(); go(+b.getAttribute('data-go')); return; }
      if(e.target.closest('[data-next]')){ e.preventDefault(); go(cur+1); } });
    window.addEventListener('scroll',onScroll,{passive:true});
    window.addEventListener('resize',function(){ setH(); onScroll(); });
    setH(); show(0); onScroll();
  });

  // game story cards: tap the right side / swipe left to go on, left side / swipe right to go back.
  // ♪ turns the music on for the whole story; ▶ Play runs it on its own like the old recap (and turns the music on).
  document.querySelectorAll('[data-cards]').forEach(function(cs){
    var cards=[].slice.call(cs.querySelectorAll('.cs-card')), n=cards.length, cur=-1, segs=[].slice.call(cs.querySelectorAll('.cs-bars span')),
        go=cs.querySelector('[data-go]'), back=cs.querySelector('[data-back]'), done=cs.querySelector('[data-done]'), ct=cs.querySelector('[data-ct]'),
        snd=cs.querySelector('[data-sound]'), fsb=cs.querySelector('[data-fs]'), playb=cs.querySelector('[data-play]'), audio=null, timer=null, auto=false;
    function count(card){ if(window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      card.querySelectorAll('[data-countto]').forEach(function(el){ var to=+el.getAttribute('data-countto'), t0=null;
        function st(ts){ if(!t0) t0=ts; var k=Math.min(1,(ts-t0)/650); el.textContent=Math.round(to*(1-Math.pow(1-k,3))); if(k<1) requestAnimationFrame(st); }
        requestAnimationFrame(st); }); }
    function music(on){ if(on){ if(!audio){ audio=new Audio(cs.getAttribute('data-snd')); audio.loop=true; }
        var p=audio.play(); if(p&&p.catch) p.catch(function(){}); }
      else if(audio) audio.pause();
      snd.setAttribute('aria-pressed',on?'true':'false'); snd.setAttribute('aria-label',on?'Music off':'Music on'); }
    function load(i){ var c=cards[i]; if(!c) return; var f=c.querySelector('iframe[data-src]'); if(f&&!f.getAttribute('src')) f.src=f.getAttribute('data-src'); }
    function dur(i){ var d=+cards[i].getAttribute('data-dur'); return d||(cards[i].querySelector('.cs-phone iframe')?11000:7000); }
    function stopAuto(){ auto=false; clearTimeout(timer); playb.classList.remove('on'); playb.innerHTML='\u25B6\uFE0E<span class="pt"> Play</span>'; segs.forEach(function(s){s.classList.remove('run')}); }
    function arm(){ clearTimeout(timer); segs.forEach(function(s){s.classList.remove('run')}); if(!auto) return;
      var s=segs[cur]; s.classList.remove('on'); s.style.setProperty('--dur',dur(cur)+'ms'); void s.offsetWidth; s.classList.add('run');
      timer=setTimeout(function(){ if(cur<n-1) show(cur+1); else stopAuto(); }, dur(cur)); }
    function show(i){ i=Math.max(0,Math.min(n-1,i)); if(i===cur) return; cur=i;
      cards.forEach(function(c,j){ c.classList.toggle('on',j===i); c.classList.toggle('past',j<i); });
      segs.forEach(function(s,j){ s.classList.toggle('done',j<i); s.classList.toggle('on',j===i&&!auto); });
      load(i); load(i+1);
      var f=cards[i].querySelector('iframe'); if(f&&f.getAttribute('src')) f.src=f.getAttribute('data-src');
      if(ct) ct.textContent=(i+1)+' of '+n;
      back.hidden=(i===0); go.hidden=(i===n-1); done.hidden=(i!==n-1); count(cards[i]); arm(); }
    function next(){ show(cur+1); } function prev(){ show(cur-1); }
    cs.querySelector('.cs-tap.next').addEventListener('click',next); cs.querySelector('.cs-tap.prev').addEventListener('click',prev);
    go.addEventListener('click',next); back.addEventListener('click',prev);
    done.addEventListener('click',function(){ stopAuto(); if(cs.classList.contains('full')) fsb.click(); });
    var x0=null,y0=null;
    cs.addEventListener('touchstart',function(e){x0=e.touches[0].clientX;y0=e.touches[0].clientY},{passive:true});
    cs.addEventListener('touchend',function(e){ if(x0===null) return; var dx=e.changedTouches[0].clientX-x0, dy=e.changedTouches[0].clientY-y0; x0=null;
      if(Math.abs(dx)>40&&Math.abs(dx)>Math.abs(dy)*1.4){ dx<0?next():prev(); } },{passive:true});
    cs.setAttribute('tabindex','0');
    cs.addEventListener('keydown',function(e){ if(e.key==='ArrowRight'){next();e.preventDefault();} if(e.key==='ArrowLeft'){prev();e.preventDefault();} if(e.key===' '){playb.click();e.preventDefault();} });
    // music is on by default (the owner, Nov 13). Browsers only allow sound after the reader touches the page, so it starts on the
    // first tap, swipe or key in the story (or right away where the browser allows). ♪ turns it off; the choice is remembered.
    var pref=true; try{ pref=localStorage.getItem('bm_music')!=='off'; }catch(err){}
    function want(on){ pref=on; try{ localStorage.setItem('bm_music',on?'on':'off'); }catch(err){} music(on); }
    snd.addEventListener('click',function(e){ e.stopPropagation(); want(snd.getAttribute('aria-pressed')!=='true'); });
    function kick(){ if(pref&&(!audio||audio.paused)) music(true); }
    ['pointerdown','touchend','keydown'].forEach(function(ev){ cs.addEventListener(ev,kick,{passive:true}); });
    snd.setAttribute('aria-pressed',pref?'true':'false'); snd.setAttribute('aria-label',pref?'Music off':'Music on');
    if(pref){ try{ audio=new Audio(cs.getAttribute('data-snd')); audio.loop=true; var p0=audio.play(); if(p0&&p0.catch) p0.catch(function(){ snd.setAttribute('aria-pressed','true'); }); }catch(err){} }
    playb.addEventListener('click',function(){ if(auto){ stopAuto(); return; }
      auto=true; playb.classList.add('on'); playb.innerHTML='\u275A\u275A<span class="pt"> Pause</span>'; if(pref) music(true);
      if(cur===n-1){ cur=-1; show(0); } else arm(); });
    function fitZ(){ var z=Math.max(1,Math.min(2,Math.min(innerWidth/1180,innerHeight/640))); cs.style.setProperty('--z',z.toFixed(3)); }
    window.addEventListener('resize',function(){ if(cs.classList.contains('full')) fitZ(); });
    function setFull(on){ if(on) fitZ(); cs.classList.toggle('full',on); document.body.classList.toggle('cs-lock',on); fsb.textContent=on?'✕':'⤢'; fsb.setAttribute('aria-label',on?'Exit full screen':'Full screen'); }
    fsb.addEventListener('click',function(){ var on=!cs.classList.contains('full'); setFull(on);
      try{ if(on&&cs.requestFullscreen) cs.requestFullscreen().catch(function(){}); else if(!on&&document.fullscreenElement) document.exitFullscreen(); }catch(err){} });
    document.addEventListener('fullscreenchange',function(){ if(!document.fullscreenElement&&cs.classList.contains('full')) setFull(false); });
    document.addEventListener('visibilitychange',function(){ if(document.hidden){ stopAuto(); if(audio) audio.pause(); } });
    show(0);
    // auto-play by default (the owner, Nov 13): starts when the story is on screen, pauses when it scrolls away or the reader taps Pause.
    // Readers who turned on reduced motion get no auto-play. Sound still waits for the first tap (browser rule).
    var userPaused=false, reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
    playb.addEventListener('click',function(){ userPaused=!auto; });
    function startAuto(){ if(auto||userPaused||reduce||cur===n-1) return; auto=true; playb.classList.add('on'); playb.innerHTML='\u275A\u275A<span class="pt"> Pause</span>';
      segs.forEach(function(s,j){ s.classList.toggle('on',false); }); arm(); }
    if('IntersectionObserver' in window){
      new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting&&e.intersectionRatio>=0.6) startAuto(); else if(auto&&!cs.classList.contains('full')){ stopAuto(); } }); },{threshold:[0,0.6]}).observe(cs);
    } else startAuto();
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

// Shorts links (the owner, Nov 13): on a computer, open our Shorts in YouTube's normal player (it has full screen);
// on phones and tablets keep /shorts/, which opens the YouTube app's Shorts feed.
(function () {
  var computer = window.matchMedia && matchMedia('(hover: hover) and (pointer: fine)').matches && !/Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);
  if (!computer) return;
  document.querySelectorAll('a[href*="youtube.com/shorts/"]').forEach(function (a) {
    var m = a.getAttribute('href').match(/youtube\.com\/shorts\/([A-Za-z0-9_-]{6,})/);
    if (m) a.setAttribute('href', 'https://www.youtube.com/watch?v=' + m[1]);
  });
})();
