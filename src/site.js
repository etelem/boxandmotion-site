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
    var isMine=function(g){return g.getAttribute('data-teams').split(' ').some(function(t){return favs.indexOf(t)>-1})};
    var useMine=mode==='mine'&&favs.length>0;
    // no teams followed yet: "Your teams" says so and links to the Teams page instead of doing nothing
    document.querySelectorAll('.nofav-note').forEach(function(n){n.classList.toggle('hidden',!(mode==='mine'&&!favs.length))});
    // last night's top game is filtered too (it sat outside the list, so the page looked unchanged)
    var topMine=false;
    document.querySelectorAll('[data-topgame]').forEach(function(sec){
      var c=sec.querySelector('[data-teams]'); var mine=!!c&&isMine(c); if(mine) topMine=true;
      sec.classList.toggle('hidden',useMine&&!mine);
    });
    document.querySelectorAll('[data-games]').forEach(function(wrap){
      var cards=[].slice.call(wrap.querySelectorAll('[data-teams]'));
      cards.forEach(function(g,i){if(!g.hasAttribute('data-i')) g.setAttribute('data-i',i)});
      cards.sort(function(x,y){return (isMine(y)-isMine(x))||(x.getAttribute('data-i')-y.getAttribute('data-i'))});
      cards.forEach(function(g){wrap.appendChild(g)});
      var shown=0;
      cards.forEach(function(g){var hide=useMine&&!isMine(g); g.classList.toggle('hidden',hide); if(!hide) shown++});
      var top=wrap.closest('section')&&wrap.closest('section').previousElementSibling;
      var note=wrap.parentNode.querySelector('.none-note');
      if(note) note.classList.toggle('hidden',shown>0||(top&&top.hasAttribute('data-topgame')&&topMine));
      // a day with none of your games disappears in "Your teams" mode
      var day=wrap.closest('.sec'); if(day&&!note) day.classList.toggle('hidden',useMine&&shown===0);
    });
    document.querySelectorAll('[data-mine-label]').forEach(function(k){
      if(!k.hasAttribute('data-all-label')) k.setAttribute('data-all-label',k.textContent);
      k.textContent=k.getAttribute(useMine&&!topMine?'data-mine-label':'data-all-label');
    });
    document.querySelectorAll('[data-mode]').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-mode')===mode)});
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
    function load(i){ var c=cards[i]; if(!c) return; var f=c.querySelector('iframe[data-src]');
      if(f&&!f.getAttribute('src')){ f.addEventListener('load',function(){ f.setAttribute('data-ready','1'); }); f.src=f.getAttribute('data-src'); } }
    // replay a card's scene in place (no reload, which blinks; Nov 14). A frame still loading starts from the top by itself.
    function replay(f){ if(!f||f.getAttribute('data-ready')!=='1') return;
      try{ var w=f.contentWindow; if(w&&typeof w.__bmRestart==='function'){ w.__bmRestart(); return; } }catch(err){}
      f.removeAttribute('data-ready'); f.src=f.getAttribute('data-src'); }
    function dur(i){ var d=+cards[i].getAttribute('data-dur'); return d||(cards[i].querySelector('.cs-phone iframe')?11000:7000); }
    function stopAuto(){ auto=false; clearTimeout(timer); playb.classList.remove('on'); playb.innerHTML='\u25B6\uFE0E<span class="pt"> Play</span>'; segs.forEach(function(s){s.classList.remove('run')}); }
    function arm(){ clearTimeout(timer); segs.forEach(function(s){s.classList.remove('run')}); if(!auto) return;
      var s=segs[cur]; s.classList.remove('on'); s.style.setProperty('--dur',dur(cur)+'ms'); void s.offsetWidth; s.classList.add('run');
      timer=setTimeout(function(){ if(cur<n-1) show(cur+1); else stopAuto(); }, dur(cur)); }
    function show(i){ i=Math.max(0,Math.min(n-1,i)); if(i===cur) return; cur=i;
      cards.forEach(function(c,j){ c.classList.toggle('on',j===i); c.classList.toggle('past',j<i); });
      segs.forEach(function(s,j){ s.classList.toggle('done',j<i); s.classList.toggle('on',j===i&&!auto); });
      var f=cards[i].querySelector('iframe[data-src]'), had=!!(f&&f.getAttribute('src'));
      load(i); load(i+1); load(i-1); if(had) replay(f);
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

  // the moment on X: the NBA's own post loads by itself as the reader scrolls near it (X's player, do-not-track on);
  // a tap on the card also starts it; if it can't load, our drawing plays instead
  function loadX(box){
    if(box.getAttribute('data-x-started')) return; box.setAttribute('data-x-started','1');
    var b=box.querySelector('button.player'), id=box.getAttribute('data-xid'), done=false;
    var say=function(t){ var s=b&&b.querySelector('.pcap span'); if(s) s.textContent=t; };
    var fallback=function(){ if(done) return; done=true; var fb=box.getAttribute('data-fallback'); if(!fb){ say('Couldn’t load the clip. Open it on X.'); return; }
      var f=document.createElement('iframe'); f.src=fb; f.title='The play, drawn'; f.className='mo-fb'; box.replaceChildren(f); };
    say('Loading the NBA’s clip…');
    var go=function(){ window.twttr.widgets.createTweet(id, box, {dnt:true, conversation:'none', align:'center', theme:'light'})
      .then(function(el){ if(el){ done=true; if(b) b.remove(); } else fallback(); }, fallback); };
    setTimeout(fallback, 12000);
    if(window.twttr&&window.twttr.widgets) return go();
    var s=document.createElement('script'); s.src='https://platform.twitter.com/widgets.js'; s.async=true; s.charset='utf-8';
    s.onload=function(){ (window.twttr&&window.twttr.ready)?window.twttr.ready(go):fallback(); }; s.onerror=fallback; document.head.appendChild(s);
  }
  document.addEventListener('click',function(e){ var b=e.target.closest('.mo-x > button.player'); if(b) loadX(b.parentNode); });
  (function(){ var xs=document.querySelectorAll('.mo-x'); if(!xs.length) return;
    if(!('IntersectionObserver' in window)){ xs.forEach(loadX); return; }
    var io=new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting){ io.unobserve(en.target); loadX(en.target); } }); }, {rootMargin:'700px 0px'});
    xs.forEach(function(x){ io.observe(x); }); })();

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

// game story as one scroll-down page (the owner, Nov 14): scenes load a little before they come on screen, then replay from the top each time they come into view
(function(){
  var cs=document.querySelector('[data-flow]'); if(!cs) return;
  var cards=[].slice.call(cs.querySelectorAll('.cs-card'));
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  function load(f){ if(f&&!f.getAttribute('src')){ f.addEventListener('load',function(){ f.setAttribute('data-ready','1'); }); f.src=f.getAttribute('data-src'); } }
  function replay(f){ if(!f||f.getAttribute('data-ready')!=='1') return;
    try{ var w=f.contentWindow; if(w&&typeof w.__bmRestart==='function') w.__bmRestart(); }catch(e){} }
  function count(card){ if(reduce) return; card.querySelectorAll('[data-countto]').forEach(function(el){ var to=+el.getAttribute('data-countto'), wait=+(el.getAttribute('data-delay')||0), t0=null; el.textContent='0';
    function st(ts){ if(!t0) t0=ts+wait; var k=Math.max(0,Math.min(1,(ts-t0)/800)); el.textContent=Math.round(to*(1-Math.pow(1-k,3))); if(k<1) requestAnimationFrame(st); } requestAnimationFrame(st); }); }
  if(!('IntersectionObserver' in window)){ cards.forEach(function(c){ c.classList.add('on'); load(c.querySelector('iframe[data-src]')); }); return; }
  var near=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting) load(e.target.querySelector('iframe[data-src]')); }); },{rootMargin:'900px 0px'});
  cards.forEach(function(c){ near.observe(c); });
  var seen=new IntersectionObserver(function(es){ es.forEach(function(e){ var c=e.target;
      if(e.isIntersecting&&!c.classList.contains('on')){ c.classList.add('on'); replay(c.querySelector('iframe[data-src]')); count(c); }
      else if(!e.isIntersecting&&e.boundingClientRect.top>0){ c.classList.remove('on'); } }); },{threshold:0.35});
  cards.forEach(function(c){ seen.observe(c); });
  // the line down the side fills to the point you've read to
  var rail=cs.querySelector('.rail'), ticking=false;
  function fill(){ ticking=false; var r=cs.getBoundingClientRect(), h=r.height-20, at=innerHeight*0.6-r.top-10;
    rail.style.height=Math.max(0,Math.min(h,at)).toFixed(0)+'px'; }
  addEventListener('scroll',function(){ if(!ticking){ ticking=true; requestAnimationFrame(fill); } },{passive:true});
  addEventListener('resize',fill); fill();
})();
(function(){
  // home library feed: load each animation when it comes near the screen (Nov 15)
  var fs=[].slice.call(document.querySelectorAll('iframe[data-lazy]')); if(!fs.length) return;
  var go=function(f){ if(!f.src) f.src=f.getAttribute('data-lazy'); };
  if(!('IntersectionObserver' in window)){ fs.forEach(go); return; }
  var io=new IntersectionObserver(function(es){ es.forEach(function(e){ if(e.isIntersecting){ go(e.target); io.unobserve(e.target); } }); },{rootMargin:'600px 0px'});
  fs.forEach(function(f){ io.observe(f); });
})();

// music for the scroll-down game story (Nov 15): an optional loop of our own track. Off until the reader taps ♪ Music
// (phones block sound until a tap anyway). The button floats in the corner only while the story is on screen; the music
// fades out when the story scrolls away or the tab is hidden and back in when it returns. The choice is remembered.
(function(){
  var cs=document.querySelector('[data-flow]'), b=cs&&cs.querySelector('[data-flowsnd]'); if(!b) return;
  var a=null, on=false, inView=false, fadeT=null;
  try{ on=localStorage.getItem('bm_flowmusic')==='on'; }catch(e){}
  // iPhones ignore audio.volume (it stays at 1), so a fade there can never "arrive": count steps instead and always finish (Nov 15 fix)
  function fade(to,done){ clearInterval(fadeT); var from=a.volume, n=0;
    fadeT=setInterval(function(){ n++; try{ a.volume=Math.max(0,Math.min(1,from+(to-from)*n/12)); }catch(e){}
      if(n>=12){ clearInterval(fadeT); if(done) done(); } },35); }
  function play(){ if(!a){ a=new Audio(b.getAttribute('data-flowsnd')); a.loop=true; a.volume=0; }
    var p=a.play(); if(p&&p.catch) p.catch(function(){}); fade(.55); }
  function stop(){ if(a&&!a.paused) fade(0,function(){ a.pause(); }); }
  function paint(){ b.setAttribute('aria-pressed',on?'true':'false'); b.setAttribute('aria-label',on?'Turn music off':'Turn music on');
    b.classList.toggle('on',on); b.querySelector('.t').textContent=on?'Music on':'Music'; }
  function sync(){ (on&&inView&&!document.hidden)?play():stop(); }
  b.addEventListener('click',function(){ on=!on; try{ localStorage.setItem('bm_flowmusic',on?'on':'off'); }catch(e){} paint();
    if(!on&&a){ clearInterval(fadeT); a.pause(); } else sync(); });
  // a reader who turned music on before gets it back on their first tap in the story (the browser needs a tap)
  cs.addEventListener('pointerdown',function(e){ if(on&&inView&&(!a||a.paused)&&!b.contains(e.target)) play(); },{passive:true});
  if('IntersectionObserver' in window){
    new IntersectionObserver(function(es){ inView=es[0].isIntersecting; b.classList.toggle('show',inView); sync(); },{threshold:0.08}).observe(cs);
  } else { inView=true; b.classList.add('show'); }
  document.addEventListener('visibilitychange',sync);
  paint();
})();

// "What changed" story (the owner, Nov 17): same feel as the game-page scroll story. Each part fades up and its dot turns orange
// when it comes into view; numbers count up and rows/bars phase in one at a time; scrolling back above a part resets it so it replays.
(function(){
  var cs=document.querySelector('[data-wc]'); if(!cs) return;
  var parts=[].slice.call(cs.querySelectorAll('.wc-part'));
  var reduce=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  function fmt(el,v){ var dec=+el.getAttribute('data-dec')||0; el.textContent=(el.getAttribute('data-pre')||'')+v.toFixed(dec)+(el.getAttribute('data-suf')||''); }
  function count(p){ if(reduce) return; p.querySelectorAll('.wc-n').forEach(function(el){ var to=+el.getAttribute('data-to'), host=el.closest('.ph'),
      wait=host?parseFloat(getComputedStyle(host).getPropertyValue('--d'))*1000||0:0, t0=null; fmt(el,0);
    function st(ts){ if(!t0) t0=ts+wait; var k=Math.max(0,Math.min(1,(ts-t0)/900)); fmt(el,to*(1-Math.pow(1-k,3))); if(k<1) requestAnimationFrame(st); } requestAnimationFrame(st); }); }
  if(!('IntersectionObserver' in window)||reduce){ parts.forEach(function(p){ p.classList.add('on'); }); }
  else { var seen=new IntersectionObserver(function(es){ es.forEach(function(e){ var p=e.target;
      if(e.isIntersecting&&!p.classList.contains('on')){ p.classList.add('on'); count(p); }
      else if(!e.isIntersecting&&e.boundingClientRect.top>0){ p.classList.remove('on'); } }); },{threshold:0.3});
    parts.forEach(function(p){ seen.observe(p); }); }
  var rail=cs.querySelector('.rail'), ticking=false;
  function fill(){ ticking=false; var r=cs.getBoundingClientRect(), h=r.height-20, at=innerHeight*0.6-r.top-10; rail.style.height=Math.max(0,Math.min(h,at)).toFixed(0)+'px'; }
  addEventListener('scroll',function(){ if(!ticking){ ticking=true; requestAnimationFrame(fill); } },{passive:true});
  addEventListener('resize',fill); fill();
})();
