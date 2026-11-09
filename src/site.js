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
      a.className='card tcard'; a.href=root+'teams/'+t.slug+'/index.html';
      a.style.background='radial-gradient(120% 120% at 100% 0%,'+t.c1+' 0%,'+t.dark+' 70%)';
      a.innerHTML='<span class="d" style="color:'+t.c2+'">★ '+t.name+'</span>'+
        '<span>'+t.rec+' · '+t.seed+'</span>'+
        '<span class="sub">Last: '+t.last+'</span>'+
        '<span class="sub">Top-6 odds: <b>'+t.top6+'%</b> ('+t.chg+' this week)</span>';
      box.appendChild(a);
    });
  }

  // Game filters (home + last night)
  var mode='mine';
  function filterGames(){
    document.querySelectorAll('[data-games]').forEach(function(wrap){
      var useMine=mode==='mine'&&favs.length>0, shown=0;
      wrap.querySelectorAll('[data-teams]').forEach(function(g){
        var ts=g.getAttribute('data-teams').split(' ');
        var mine=ts.some(function(t){return favs.indexOf(t)>-1});
        g.classList.toggle('hidden',useMine&&!mine);
        var tag=g.querySelector('.mine-tag'); if(tag) tag.classList.toggle('hidden',!mine);
        if(!(useMine&&!mine)) shown++;
      });
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
