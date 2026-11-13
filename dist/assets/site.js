(function(){
  var KEY='bm_favs';
  function load(){try{var v=JSON.parse(localStorage.getItem(KEY)||'[]');return Array.isArray(v)?v:[]}catch(e){return []}}
  function save(v){try{localStorage.setItem(KEY,JSON.stringify(v))}catch(e){}}
  var favs=load();
  var BM=window.BM||{teams:{}};
  var root=document.body.getAttribute('data-root')||'';

  function refreshStars(){
    document.querySelectorAll('.star[data-team]').forEach(function(b){
      var on=favs.indexOf(b.getAttribute('data-team'))>-1;
      b.classList.toggle('on',on);
      b.setAttribute('aria-pressed',on?'true':'false');
      var l=b.querySelector('.lbl'); if(l) l.textContent=on?'Following':'Follow';
    });
    document.querySelectorAll('tr[data-team]').forEach(function(r){r.classList.toggle('fav',favs.indexOf(r.getAttribute('data-team'))>-1)});
    document.querySelectorAll('.favcount').forEach(function(e){e.textContent=favs.length?('★ My teams ('+favs.length+')'):'★ My teams'});
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest('.star[data-team]'); if(!b) return;
    e.preventDefault();
    var t=b.getAttribute('data-team'), i=favs.indexOf(t);
    if(i>-1) favs.splice(i,1); else favs.push(t);
    save(favs); refreshStars(); renderMine(); filterGames();
  });

  // Home: my teams cards
  function renderMine(){
    var box=document.getElementById('mine'); if(!box) return;
    var empty=document.getElementById('mine-empty');
    box.innerHTML='';
    if(!favs.length){empty&&empty.classList.remove('hidden');return}
    empty&&empty.classList.add('hidden');
    favs.forEach(function(c){
      var t=BM.teams[c]; if(!t) return;
      var a=document.createElement('a');
      // calm card like the game cards (Nov 13): white, team color only as a thin top line and a dot
      a.className='card tcard calm'; a.href=root+'teams/'+t.slug+'/index.html';
      a.style.setProperty('--team',t.c1);
      var up=/^\+/.test(t.chg), down=/^[−-]\d/.test(t.chg);
      a.innerHTML='<span class="trow1"><i class="tdot" style="background:'+t.c1+'"></i><span class="tname">'+t.name+'</span><span class="tstar" aria-label="Your team">★</span></span>'+
        '<span class="trec">'+t.rec+' · '+t.seed+'</span>'+
        '<span class="tline"><span class="dim">Last</span>'+t.last+'</span>'+
        '<span class="tline"><span class="dim">Top-6 odds</span><b>'+t.top6+'%</b><span class="tchg'+(up?' up':down?' down':'')+'">'+t.chg+' this week</span></span>';
      box.appendChild(a);
    });
  }

  // Game filters (home + last night)
  var mode='mine';
  function filterGames(){
    document.querySelectorAll('[data-games]').forEach(function(wrap){
      var useMine=mode==='mine'&&favs.length>0, shown=0;
      // Top card: the visitor's followed teams go first (best story among them), then everyone else in story order
      if(wrap.hasAttribute('data-images')){
        var cards=[].slice.call(wrap.querySelectorAll('[data-teams]'));
        cards.forEach(function(g,i){if(!g.hasAttribute('data-i')) g.setAttribute('data-i',i)});
        var isMine=function(g){return g.getAttribute('data-teams').split(' ').some(function(t){return favs.indexOf(t)>-1})};
        cards.sort(function(x,y){return (isMine(y)-isMine(x))||(x.getAttribute('data-i')-y.getAttribute('data-i'))});
        cards.forEach(function(g){wrap.appendChild(g)});
      }
      wrap.querySelectorAll('[data-teams]').forEach(function(g){
        var ts=g.getAttribute('data-teams').split(' ');
        var mine=ts.some(function(t){return favs.indexOf(t)>-1});
        g.classList.toggle('hidden',useMine&&!mine);
        var tag=g.querySelector('.mine-tag'); if(tag) tag.classList.toggle('hidden',!mine);
        if(!(useMine&&!mine)) shown++;
      });
      if(wrap.hasAttribute('data-images')){
        var first=null;
        wrap.querySelectorAll('[data-teams]').forEach(function(g){var on=!first&&!g.classList.contains('hidden'); if(on) first=g; g.classList.toggle('hero',on)});
      }
      var note=wrap.parentNode.querySelector('.none-note');
      if(note) note.classList.toggle('hidden',shown>0);
    });
    document.querySelectorAll('[data-mode]').forEach(function(b){b.classList.toggle('on',b.getAttribute('data-mode')===(favs.length?mode:'all'))});
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-mode]'); if(!b) return;
    mode=b.getAttribute('data-mode'); filterGames();
  });

  // Generic tabs
  document.querySelectorAll('[data-tabs]').forEach(function(group){
    var name=group.getAttribute('data-tabs');
    group.addEventListener('click',function(e){
      var b=e.target.closest('[data-tab]'); if(!b) return;
      var v=b.getAttribute('data-tab');
      group.querySelectorAll('[data-tab]').forEach(function(x){x.classList.toggle('on',x===b)});
      document.querySelectorAll('[data-pane="'+name+'"]').forEach(function(p){p.classList.toggle('hidden',p.getAttribute('data-value')!==v)});
    });
  });

  // Greeting
  var gr=document.getElementById('greet');
  if(gr){var h=new Date().getHours();gr.textContent=h<12?'Good morning.':h<18?'Good afternoon.':'Good evening.'}

  refreshStars(); renderMine(); filterGames();
})();

// animation iframes report their height
window.addEventListener('message', function (e) {
  if (!e.data || typeof e.data.bmH !== 'number') return;
  document.querySelectorAll('iframe.anim').forEach(function (f) { if (f.contentWindow === e.source) f.style.height = e.data.bmH + 'px'; });
});

// phones: if the current tab is off the end of the scrolling tab row (About), bring it into view
(function () {
  var row = document.querySelector('.links'), cur = row && row.querySelector('a[aria-current]');
  if (!cur || row.scrollWidth <= row.clientWidth) return;
  var right = cur.offsetLeft + cur.offsetWidth - row.offsetLeft;
  if (right > row.clientWidth) row.scrollLeft = right - row.clientWidth + 8;
})();

// deep dives: "Play with sound" restarts the animation and plays the Film Room track under it (one track at a time)
(function () {
  var audio = null, current = null;
  function stop() { if (audio) audio.pause(); if (current) current.textContent = '▶ Play with sound'; current = null; }
  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('button[data-snd]'); if (!btn) return;
    if (current === btn) { stop(); return; }
    stop();
    if (!audio) { audio = new Audio(); audio.loop = true; audio.preload = 'auto'; }
    audio.src = btn.getAttribute('data-snd');
    var frame = btn.parentNode.querySelector('iframe'); if (frame) frame.src = frame.src;   // start the animation from the top with the music
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
