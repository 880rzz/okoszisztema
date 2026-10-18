/* Curated original-source press feed. Candidate discovery is never a publication source. */
(()=>{"use strict";
 const roots=[...document.querySelectorAll("[data-member-news]")];if(!roots.length)return;
 const escape=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
 const norm=s=>String(s??"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLocaleLowerCase("hu").trim();
 const validUrl=u=>{try{const p=new URL(u);return p.protocol==="https:"?p.href:""}catch{return""}};
 const monthDate=raw=>{
  const d=String(raw||"");
  try{
   if(/^\d{4}-\d{2}-\d{2}$/.test(d))return new Intl.DateTimeFormat("hu-AT",{year:"numeric",month:"long",day:"numeric",timeZone:"UTC"}).format(new Date(d+"T12:00:00Z"));
   if(/^\d{4}-\d{2}$/.test(d))return new Intl.DateTimeFormat("hu-AT",{year:"numeric",month:"long",timeZone:"UTC"}).format(new Date(d+"-01T12:00:00Z"));
   if(/^\d{4}-\d{4}$/.test(d))return d.replace("-","–");
  }catch(_){}
  return d||"Dátum nincs megadva";
 };
 const htmlCard=(row,rootBase)=>{
  const url=validUrl(row.url);if(!url)return"";
  const related=(row.memberIds||[]).map((id,i)=>'<a href="'+escape(rootBase+'tagszervezetek/'+encodeURIComponent(id)+'/')+'">'+escape((row.memberNames||[])[i]||id)+'</a>').join("");
  const dateLabel=monthDate(row.date);
  const isDate=/^\d{4}-\d{2}-\d{2}$/.test(row.date||"");
  const dateHtml=isDate?'<time datetime="'+escape(row.date)+'">'+escape(dateLabel)+'</time>':'<span>'+escape(dateLabel)+'</span>';
  return '<article class="member-news-card"><div class="news-overline"><span>'+escape(row.publisher)+'</span><span aria-hidden="true">·</span>'+dateHtml+'</div>'+
   '<h3>'+escape(row.title)+'</h3><p>'+escape(row.summary||"A cikk részletei az eredeti médiumban olvashatók.")+'</p>'+
   '<div class="news-members" aria-label="Kapcsolódó tagegyesületek">'+related+'</div>'+
   '<a class="news-source-link" target="_blank" rel="noopener noreferrer" href="'+escape(url)+'" aria-label="'+escape(row.title+' – eredeti cikk megnyitása a(z) '+row.publisher+' oldalán')+'">Eredeti cikk a médiumban ↗</a></article>';
 };
 const setups=roots.map(root=>{
  const base=root.dataset.root||"";
  const param=new URLSearchParams(location.search).get("tag")||"";
  const filterMember=root.dataset.member||param||"";
  return {root,base,filterMember,limit:Math.max(1,Number(root.dataset.limit)||24),renderLimit:Math.max(1,Number(root.dataset.limit)||24),rows:[]};
 });
 function filterRows(setup){
  let member=setup.root.querySelector("[data-news-member]")?.value||setup.filterMember;
  const publisher=setup.root.querySelector("[data-news-media]")?.value||"";
  const query=norm(setup.root.querySelector("[data-news-search]")?.value||"");
  return setup.rows.filter(x=>(!member||(x.memberIds||[]).includes(member))&&(!publisher||x.publisher===publisher)&&(!query||norm([x.title,x.publisher,x.date,...(x.memberNames||[])].join(" ")).includes(query)));
 }
 function render(setup){
  const node=setup.root.querySelector("[data-news-grid]");
  const status=setup.root.querySelector("[data-news-status]");
  const more=setup.root.querySelector("[data-news-more]");
  if(!node)return;
  const rows=filterRows(setup);
  node.innerHTML=rows.slice(0,setup.renderLimit).map(x=>htmlCard(x,setup.base)).join("");
  const empty=setup.root.querySelector("[data-news-empty]");
  if(empty){empty.hidden=!!rows.length;empty.textContent="Nincs a feltételeknek megfelelő, forrásolt sajtómegjelenés."}
  if(status)status.textContent=rows.length+" dokumentált cikk"+(setup.limit<rows.length?", az első "+Math.min(rows.length,setup.renderLimit)+" látható":"");
  if(more)more.hidden=rows.length<=setup.renderLimit;
 }
 function populateFilters(setup){
  const selectM=setup.root.querySelector("[data-news-member]");
  const selectP=setup.root.querySelector("[data-news-media]");
  const memberMap=new Map,pubs=new Set;
  for(const row of setup.rows){pubs.add(row.publisher);(row.memberIds||[]).forEach((id,i)=>memberMap.set(id,(row.memberNames||[])[i]||id))}
  if(selectM){
   selectM.innerHTML='<option value="">Összes tagegyesület</option>'+[...memberMap].sort((a,b)=>a[1].localeCompare(b[1],"hu")).map(([id,name])=>'<option value="'+escape(id)+'">'+escape(name)+'</option>').join("");
   if(setup.filterMember && memberMap.has(setup.filterMember))selectM.value=setup.filterMember;
  }
  if(selectP)selectP.innerHTML='<option value="">Összes médium</option>'+[...pubs].sort((a,b)=>a.localeCompare(b,"hu")).map(s=>'<option value="'+escape(s)+'">'+escape(s)+'</option>').join("");
 }
 function install(setup){
  setup.root.querySelectorAll("[data-news-member],[data-news-media],[data-news-search]").forEach(el=>{
   el.addEventListener(el.tagName==="SELECT"?"change":"input",()=>{setup.renderLimit=setup.limit;render(setup)});
  });
  setup.root.querySelector("[data-news-more]")?.addEventListener("click",()=>{setup.renderLimit+=24;render(setup)});
 }
 setups.forEach(install);
 const cache=new Map;
 const fetchJson=async(base)=>{
  if(!cache.has(base))cache.set(base,fetch(base+"data/member-news.json",{cache:"no-store"}).then(async r=>{
   if(!r.ok)throw Error("HTTP "+r.status);
   const d=await r.json();
   if(!Array.isArray(d.items)||d.publicationPolicy===undefined)throw Error("Érvénytelen sajtóadat");
   return d;
  }).catch(err=>{cache.delete(base);throw err}));
  return cache.get(base);
 };
 async function refresh(){
  await Promise.all(setups.map(async s=>{
   try{
    const data=await fetchJson(s.base);
    // Refuse candidate or missing publication provenance even if accidentally included.
    s.rows=data.items.filter(x=>x.approval==="curated-source-evidence" && x.url && x.title && x.date && x.publisher && Array.isArray(x.memberIds) && x.memberIds.length && validUrl(x.url));
    populateFilters(s);render(s);
   }catch(e){
    const label=s.root.querySelector("[data-news-status]");
    if(label)label.textContent="A friss sajtólista jelenleg nem érhető el. Az alábbi mentett hivatkozások továbbra is megnyithatók.";
   }
  }));
 }
 refresh();
 // Visible, low-cost refresh; GitHub Actions handles upstream daily discovery.
 setInterval(()=>{if(!document.hidden){cache.clear();refresh()}},30*60*1000);
})();
