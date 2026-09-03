(function(){
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  async function enrich(){
    try{
      const r=await fetch('member-organizations.json',{cache:'no-store'});
      if(!r.ok) return;
      const d=await r.json();
      const byName=new Map((d.members||[]).map(m=>[String(m.name||'').trim(),m]));
      document.querySelectorAll('.member').forEach(card=>{
        const h=card.querySelector('h3');
        if(!h) return;
        const m=byName.get(h.textContent.trim());
        if(!m) return;
        card.querySelectorAll('.member-enrichment').forEach(x=>x.remove());
        const box=document.createElement('div');
        box.className='member-enrichment';
        let out='';
        const emails=(m.contact&&m.contact.emails)||[];
        if(emails.length){
          out+='<div class="member-contact"><span class="enrich-label">Kapcsolat</span>'+emails.map(e=>'<a href="mailto:'+esc(e)+'">'+esc(e)+'</a>').join('<span class="sep">·</span>')+'</div>';
        }
        const a=m.featuredProfileArticle;
        if(a&&a.url){
          out+='<a class="press-link" href="'+esc(a.url)+'" target="_blank" rel="noopener"><span class="press-mark" aria-hidden="true">↗</span><span><small>Sajtó / bemutató</small><strong>'+esc(a.title||a.publisher||'Cikk')+'</strong>'+(a.publisher?'<em>'+esc(a.publisher)+(a.date?' · '+esc(a.date):'')+'</em>':'')+'</span></a>';
        }
        box.innerHTML=out;
        if(out) card.appendChild(box);
      });
    }catch(e){}
  }
  document.addEventListener('DOMContentLoaded',()=>{setTimeout(enrich,120);setTimeout(enrich,1000)});
})();
