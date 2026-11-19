/* Federated calendar: local authoritative member programs + DORAPP for other Austrian events. */
(()=>{'use strict';
const widgets=[...document.querySelectorAll('[data-member-calendar]')];
if(!widgets.length)return;
const endpoints=[
 'https://www.diaszporaterkep.hu/data/global-events.json',
 'https://raw.githubusercontent.com/880rzz/DORAPP/main/data/global-events.json'
];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl=v=>{try{const u=new URL(v);return u.protocol==='https:'?u.href:''}catch{return''}};
const formatDate=v=>new Intl.DateTimeFormat('hu-AT',{timeZone:'Europe/Vienna',dateStyle:'long',...(/^\d{4}-\d{2}-\d{2}$/.test(String(v))?{}:{timeStyle:'short'})}).format(new Date(v));
const clean=e=>e&&e.country==='at'&&e.id&&e.name&&e.startDate&&Number.isFinite(Date.parse(e.startDate))&&safeUrl(e.sourceUrl)&&!String(e.eventStatus||'').endsWith('EventCancelled');
const membersLink='https://www.kozpontiszovetseg.at/tagszervezetek';
// Explicit, source-backed DORAPP organizer IDs for the federation's projects;
// these are not member associations and are not assigned by name similarity.
const federationOrgIds=new Set(['kozponti-szovetseg','becsi-magyar-iskola','vipach']);
const localRoot=widgets[0].dataset.root||'';
let crosswalk={},socialSources={},programCandidates=[],verifiedMemberEvents=[],events=[],dataSource='',generatedAt='',lastError='',loaded=false,mappingAvailable=false;
const sourceUrl='https://www.diaszporaterkep.hu/';
const windowEnd=()=>{const d=new Date();d.setMonth(d.getMonth()+2);return d.getTime()};
const endAt=e=>{
 const v=String(e.endDate||'');
 if(!v)return Date.parse(e.startDate);
 const point=Date.parse(v);
 return Number.isFinite(point)?point+(/^\d{4}-\d{2}-\d{2}$/.test(v)?86400000-1:0):Date.parse(e.startDate);
};
const ongoing=e=>Date.parse(e.startDate)<Date.now()&&endAt(e)>=Date.now();
async function request(url){
 const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),3500);
 try{const r=await fetch(url,{cache:'no-store',signal:ctrl.signal});if(!r.ok)throw Error('HTTP '+r.status);const j=await r.json();if(!j||!Array.isArray(j.events))throw Error('Invalid event payload');return j}
 finally{clearTimeout(timer)}
}
async function load(){
 let payload=null;
 programCandidates=[];verifiedMemberEvents=[];
 try{
  const m=await fetch(localRoot+'member-event-map.json',{cache:'no-store'});if(!m.ok)throw Error('Mapping unavailable');
  const mapping=await m.json();crosswalk=mapping.memberToDorappId||{};socialSources=mapping.memberToSocialEventSource||{};mappingAvailable=Object.keys(crosswalk).length===29;
 }catch(e){crosswalk={};socialSources={};mappingAvailable=false;lastError=String(e.message||e)}
 try{
  const r=await fetch(localRoot+'data/member-programs.json',{cache:'no-store'});
  if(!r.ok)throw Error('Member program registry HTTP '+r.status);
  const registry=await r.json();
  if(registry.schemaVersion!==1||registry.sourceRepository!=='880rzz/okoszisztema'||!Array.isArray(registry.programCandidates)||!Array.isArray(registry.verifiedEvents))throw Error('Invalid member registry');
  programCandidates=registry.programCandidates.filter(p=>p&&p.status==='date-unverified'&&crosswalk[p.memberId]===p.organizerId&&p.title&&safeUrl(p.sourceUrl));
  verifiedMemberEvents=registry.verifiedEvents.filter(e=>e&&e.verificationStatus==='verified'&&clean(e)&&Object.values(crosswalk).includes(e.organizerId));
 }catch(e){lastError=String(e.message||e)}
 for(const url of endpoints){try{payload=await request(url);dataSource='live';break}catch(e){lastError=String(e.message||e)}}
 if(!payload){try{
  const cached=await request(localRoot+'data/austria-events-snapshot.json');
  const timestamp=Date.parse(cached.generatedAt||'');
  if(!Number.isFinite(timestamp)||Date.now()-timestamp>7*86400000||timestamp-Date.now()>12*3600000)throw Error('A tartalék naptár régi vagy dátuma hibás');
  payload=cached;dataSource='snapshot';
 }catch(e){lastError=String(e.message||e)}}
 if(payload){
 const ids=new Set(),entries=new Map;
 for(const e of payload.events.filter(clean)){
  if(ids.has(e.id))continue;ids.add(e.id);
  if(endAt(e)<Date.now()-60*60*1000||Date.parse(e.startDate)>windowEnd())continue;
  // Identical verified source, organizer and start time is the same event.
  const key=[e.organizerId,e.sourceUrl,e.startDate].join('|');
  const previous=entries.get(key);
  if(!previous||String(e.name).length>String(previous.name).length)entries.set(key,e);
 }
 events=[...entries.values()].sort((a,b)=>new Date(a.startDate)-new Date(b.startDate));
 generatedAt=payload.generatedAt||'';
}
 // The association registry overrides a mirrored DORAPP event with the same ID.
 const localIds=new Set(verifiedMemberEvents.map(e=>e.id));
 events=events.filter(e=>!localIds.has(e.id));
 events.push(...verifiedMemberEvents.filter(e=>endAt(e)>=Date.now()-60*60*1000&&Date.parse(e.startDate)<=windowEnd()));
 events.sort((a,b)=>new Date(a.startDate)-new Date(b.startDate));
 loaded=true;renderAll();
}
function card(e,memberOf){
 const who=e.organizer||'Szervező az eredeti forrásban';
 const parts=[e.city,e.venue].filter(Boolean);
 const member=memberOf.has(e.organizerId);
 return '<article class="calendar-event">'+(member?'<div class="calendar-member">Tagszervezeti esemény</div>':'')+(ongoing(e)?'<div class="calendar-ongoing">Folyamatban</div>':'')+
  '<time datetime="'+esc(e.startDate)+'">'+esc(formatDate(e.startDate))+'</time>'+
  '<h3>'+esc(e.name)+'</h3><p>'+esc(who)+'</p>'+
  (parts.length?'<p>'+esc(parts.join(' · '))+'</p>':'')+
  '<a href="'+esc(safeUrl(e.sourceUrl))+'" target="_blank" rel="noopener noreferrer">Eredeti eseményforrás ↗</a></article>';
}
function render(w){
 const list=w.querySelector('.calendar-events'),health=w.querySelector('.calendar-health'),empty=w.querySelector('.calendar-empty');
 if(!list||!health)return;
 const memberId=w.dataset.memberId||'';
 const memberIds=new Set(Object.values(crosswalk).filter(Boolean));
 const scopedId=memberId?crosswalk[memberId]:null;
 const query=(w.querySelector('[data-calendar-search]')?.value||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
 const scope=w.querySelector('[data-calendar-scope]')?.value||'members';
 const filter=events.filter(e=>(!memberId||(scopedId&&scopedId===e.organizerId))&&(memberId||scope==='all'||(scope==='members'?memberIds.has(e.organizerId):memberIds.has(e.organizerId)||federationOrgIds.has(e.organizerId)))&&(!query||[e.name,e.city,e.venue,e.organizer].join(' ').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().includes(query)));
 list.innerHTML=filter.map(e=>card(e,memberIds)).join('');
 // Undated Facebook announcements are deliberately separate from verified Events.
 let leads=w.querySelector('.calendar-program-leads');
 if(!leads){
  leads=document.createElement('section');leads.className='calendar-program-leads';
  leads.setAttribute('aria-label','Ellenőrzésre váró programbejelentések');
  list.after(leads);
 }
 leads.replaceChildren();
 const matched=programCandidates.filter(p=>(!memberId||p.memberId===memberId)&&(!query||p.title.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().includes(query))&&(memberId||scope!=='federation'));
 leads.hidden=!matched.length;
 if(matched.length){
  const heading=document.createElement('h3');heading.textContent='Programbejelentések – időpont ellenőrzés alatt';
  const intro=document.createElement('p');intro.textContent='A szervezet által megosztott programhivatkozások. Dátum és helyszín az eredeti forrásban ellenőrizendő; ezek nem megerősített naptáresemények.';
  const grid=document.createElement('div');grid.className='calendar-events';
  for(const p of matched){
   const article=document.createElement('article');article.className='calendar-event';
   const name=document.createElement('h4');name.textContent=p.title;
   const state=document.createElement('p');state.textContent='Időpont nincs megerősítve.';
   const link=document.createElement('a');link.href=safeUrl(p.sourceUrl);link.target='_blank';link.rel='noopener noreferrer';
   link.textContent='Szervezői programforrás ↗';
   article.append(name,state,link);grid.append(article);
  }
  leads.append(heading,intro,grid);
 }
 // Facebook is a verified discovery link, not a machine-imported event feed.
 // An empty DORAPP subset must not imply there are no association events.
 const socialUrl=memberId?safeUrl(socialSources[memberId]):'';
 let socialNode=w.querySelector('.calendar-social-source');
 if(memberId&&socialUrl&&!socialNode){
  socialNode=document.createElement('p');socialNode.className='calendar-social-source';
  const footer=w.querySelector('.calendar-source');
  if(footer)footer.before(socialNode);else w.append(socialNode);
 }
 if(socialNode){
  socialNode.replaceChildren();socialNode.hidden=!socialUrl;
  if(socialUrl){
   socialNode.append('További, nem automatikusan átvett programok: ');
   const link=document.createElement('a');
   link.href=socialUrl;link.target='_blank';link.rel='noopener noreferrer';
   link.textContent='A szervezet hivatalos Facebook-oldala ↗';
   socialNode.append(link);
   if(!filter.length)socialNode.append(' · A gépi eseménynaptár hiánya nem jelenti azt, hogy a szervezetnek nincs közelgő rendezvénye.');
  }
 }
 if(empty){empty.hidden=filter.length>0;empty.textContent=!loaded?'Naptár betöltése…':!events.length&&!dataSource?'A naptár most nem érhető el. A szervezők hivatalos oldalain ellenőrizhetők a programok.':memberId&&!mappingAvailable?'A tagszervezeti esemény-hozzárendelés jelenleg nem érhető el; a naptár nem tekinthető teljesnek.':memberId?'Ehhez a tagegyesülethez jelenleg nincs külön azonosított, forrásellenőrzött közelgő program a DORAPP naptárában.':'Nincs a szűrésnek megfelelő, forrásellenőrzött közelgő esemény.'}
 if(dataSource){const status=dataSource==='live'?'Friss DORAPP-forrás':'Mentett naptáradat (a friss DORAPP-forrás nem érhető el)';
 const when=generatedAt&&Number.isFinite(Date.parse(generatedAt))?' · forrás frissítve: '+formatDate(generatedAt):'';
 health.textContent=status+when+(memberId&&!mappingAvailable?' · Figyelem: a tagszervezeti hozzárendelés nem érhető el':'')+' · '+filter.length+' megjeleníthető '+(!memberId&&scope==='all'?'ausztriai':!memberId&&scope==='federation'?'tagszervezeti és intézményi':'tagszervezeti')+' program a következő két hónapban';
 }else health.textContent='A DORAPP naptáradatok jelenleg nem tölthetők be.';
}
function renderAll(){widgets.forEach(render)}
widgets.forEach(w=>{w.querySelectorAll('[data-calendar-search],[data-calendar-scope]').forEach(el=>el.addEventListener(el.tagName==='SELECT'?'change':'input',()=>render(w)))});
load();
setInterval(()=>{if(!document.hidden)load()},30*60*1000);
})();