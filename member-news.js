/* Canonical, evidence-gated press view for members AND federation institutions. */
(()=>{"use strict";
const roots=[...document.querySelectorAll("[data-member-news]")];if(!roots.length)return;
const escape=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const norm=s=>String(s??"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLocaleLowerCase("hu").trim();
const validUrl=u=>{try{const p=new URL(u);return p.protocol==="https:"?p.href:""}catch{return""}};
const dateLabel=raw=>{
 const d=String(raw||"");
 try{
  if(/^\d{4}-\d{2}-\d{2}$/.test(d))return new Intl.DateTimeFormat("hu-AT",{year:"numeric",month:"long",day:"numeric",timeZone:"UTC"}).format(new Date(d+"T12:00:00Z"));
  if(/^\d{4}-\d{2}$/.test(d))return new Intl.DateTimeFormat("hu-AT",{year:"numeric",month:"long",timeZone:"UTC"}).format(new Date(d+"-01T12:00:00Z"));
  if(/^\d{4}-\d{4}$/.test(d))return d.replace("-","–");
 }catch(_){}
 return d||"A dátum nem ismert";
};
const card=(r,pre)=>{
 const orig=validUrl(r.url);if(!orig)return"";
 const member=(r.memberIds||[]).map((id,i)=>'<a href="'+escape(pre+'tagszervezetek/'+encodeURIComponent(id)+'/')+'">'+escape((r.memberNames||[])[i]||id)+'</a>');
 const institution=(r.institutionIds||[]).map((id,i)=>'<a href="'+escape(pre+'intezmenyek/'+encodeURIComponent(id)+'/')+'">'+escape((r.institutionNames||[])[i]||id)+'</a>');
 const accurate=/^\d{4}-\d{2}-\d{2}$/.test(r.date||"");
 const when=accurate?'<time datetime="'+escape(r.date)+'">'+escape(dateLabel(r.date))+'</time>':'<span>'+escape(dateLabel(r.date))+'</span>';
 return '<article class="member-news-card"><div class="news-overline"><span>'+escape(r.publisher)+'</span><span aria-hidden="true">·</span>'+when+'</div>'+
 '<h3>'+escape(r.title)+'</h3><p>'+escape(r.summary||"A cikk részletei az eredeti médiumban olvashatók.")+'</p>'+
 '<div class="news-members" aria-label="Kapcsolódó tagegyesületek és intézmények">'+[...member,...institution].join("")+'</div>'+
 '<a class="news-source-link" target="_blank" rel="noopener noreferrer" href="'+escape(orig)+'">Eredeti cikk a médiumban ↗</a></article>';
};
const setups=roots.map(root=>({
 root,base:root.dataset.root||"",tag:root.dataset.member||new URLSearchParams(location.search).get("tag")||"",
 limit:Math.max(1,Number(root.dataset.limit)||24),shown:Math.max(1,Number(root.dataset.limit)||24),
 yearly:root.dataset.newsGroupByYear==="true",rows:[]
}));
const matches=(s,r)=>{
 const tag=s.root.querySelector("[data-news-member]")?.value||s.tag;
 const medium=s.root.querySelector("[data-news-media]")?.value||"";
 const year=s.root.querySelector("[data-news-year]")?.value||"";
 const q=norm(s.root.querySelector("[data-news-search]")?.value||"");
 return (!tag||[...(r.memberIds||[]),...(r.institutionIds||[])].includes(tag)) &&
        (!medium||r.publisher===medium) &&(!year||r.year===year) &&
        (!q||norm([r.title,r.publisher,r.date,r.summary,...(r.memberNames||[]),...(r.institutionNames||[])].join(" ")).includes(q));
};
function render(s){
 const grid=s.root.querySelector("[data-news-grid]"),status=s.root.querySelector("[data-news-status]"),more=s.root.querySelector("[data-news-more]"),empty=s.root.querySelector("[data-news-empty]");
 if(!grid)return;
 const rows=s.rows.filter(r=>matches(s,r)),shown=rows.slice(0,s.shown);
 if(s.yearly){
  const years=new Map;
  for(const r of shown){const y=r.year||String(r.date).slice(0,4);if(!years.has(y))years.set(y,[]);years.get(y).push(r)}
  grid.innerHTML=[...years].map(([y,articles])=>
   '<section class="press-archive-year" aria-labelledby="year-'+escape(y)+'"><h2 id="year-'+escape(y)+'">'+escape(y)+
   ' <span class="press-count">'+articles.length+' cikk</span></h2><div class="member-news-grid">'+
   articles.map(r=>card(r,s.base)).join("")+'</div></section>').join("");
 }else grid.innerHTML=shown.map(r=>card(r,s.base)).join("");
 if(empty){empty.hidden=rows.length>0;empty.textContent="Nincs a feltételeknek megfelelő, forrásolt sajtómegjelenés."}
 if(status)status.textContent=rows.length+" dokumentált sajtómegjelenés"+(s.shown<rows.length?", az első "+s.shown+" látható":"");
 if(more)more.hidden=rows.length<=s.shown;
}
function filters(s){
 const member=s.root.querySelector("[data-news-member]"),publisher=s.root.querySelector("[data-news-media]"),year=s.root.querySelector("[data-news-year]");
 const choices=new Map,pubs=new Set,years=new Set;
 for(const r of s.rows){
  pubs.add(r.publisher);years.add(r.year||String(r.date).slice(0,4));
  (r.memberIds||[]).forEach((id,i)=>choices.set(id,(r.memberNames||[])[i]||id));
  (r.institutionIds||[]).forEach((id,i)=>choices.set(id,(r.institutionNames||[])[i]||id));
 }
 if(member){
  member.innerHTML='<option value="">Összes szervezet és intézmény</option>'+
   [...choices].sort((a,b)=>a[1].localeCompare(b[1],"hu")).map(([id,name])=>'<option value="'+escape(id)+'">'+escape(name)+'</option>').join("");
  if(s.tag&&choices.has(s.tag))member.value=s.tag;
 }
 if(publisher)publisher.innerHTML='<option value="">Összes médium</option>'+
  [...pubs].sort((a,b)=>a.localeCompare(b,"hu")).map(x=>'<option value="'+escape(x)+'">'+escape(x)+'</option>').join("");
 if(year)year.innerHTML='<option value="">Összes év</option>'+
  [...years].sort((a,b)=>b.localeCompare(a)).map(x=>'<option value="'+escape(x)+'">'+escape(x)+'</option>').join("");
}
setups.forEach(s=>{
 s.root.querySelectorAll("[data-news-member],[data-news-media],[data-news-year],[data-news-search]").forEach(el=>
  el.addEventListener(el.tagName==="SELECT"?"change":"input",()=>{s.shown=s.limit;render(s)}));
 s.root.querySelector("[data-news-more]")?.addEventListener("click",()=>{s.shown+=24;render(s)});
});
const cache=new Map;
async function get(base){
 if(!cache.has(base))cache.set(base,fetch(base+"data/ecosystem-press.json",{cache:"no-store"}).then(async r=>{
  if(!r.ok)throw Error("HTTP "+r.status);
  const d=await r.json();if(!Array.isArray(d.items)||!d.publicationPolicy)throw Error("Invalid press data");return d;
 }).catch(e=>{cache.delete(base);throw e}));
 return cache.get(base);
}
async function refresh(){
 await Promise.all(setups.map(async s=>{
  try{
   const payload=await get(s.base);
   s.rows=payload.items.filter(x=>x.approval==="curated-source-evidence"&&validUrl(x.url)&&x.title&&x.publisher&&x.date&&Array.isArray(x.memberIds)&&Array.isArray(x.institutionIds)&&(x.memberIds.length+x.institutionIds.length)>0);
   // Canonical feed is already strictly ordered; preserve its verified order.
   filters(s);render(s);
  }catch(e){const status=s.root.querySelector("[data-news-status]");if(status)status.textContent="A friss híradatbázis nem érhető el. Az előzőleg létrehozott forráslinkek megmaradnak."}
 }));
}
refresh();
setInterval(()=>{if(!document.hidden){cache.clear();refresh()}},30*60*1000);
})();