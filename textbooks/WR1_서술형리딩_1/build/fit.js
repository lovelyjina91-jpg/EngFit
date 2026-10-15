(function(){
  var MM=96/25.4, report=[];
  document.querySelectorAll('.page').forEach(function(pg,i){
    var b=pg.querySelector('.body'); if(!b) return;
    var cs=getComputedStyle(pg), avail=pg.clientHeight-parseFloat(cs.paddingTop)-parseFloat(cs.paddingBottom)-(b.offsetTop-pg.offsetTop-parseFloat(cs.paddingTop))-2*MM;
    avail = pg.clientHeight - (b.getBoundingClientRect().top-pg.getBoundingClientRect().top) - 18*MM;
    var h=b.scrollHeight, s=1;
    while(h*s>avail && s>0.7){ s-=0.01; b.style.zoom=s; b.style.width=(100/s)+'%'; h=b.scrollHeight; }
    if(s<1) report.push({page:i+1, scale:+s.toFixed(2)});
  });
  window.__fit=report;
})();
