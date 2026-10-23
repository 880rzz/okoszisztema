/* Read-only DORAPP calendar: remote canonical events, local sourced snapshot if unreachable. */
(()=>{'use strict';
const widgets=[...document.querySelectorAll('[data-member-calendar]')];
if(!widgets.length)return;
const endpoints=[
 'https://www.diaszporaterkep.hu/data/global-events.json',
 'https://raw.githubusercontent.com/880rzz/DORAPP/main/data/global-events.json'
];
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const safeUrl=v=>{try{const u=new URL(v);return u.protocol==='https:'?u.href:''}catch{return''}};
const formatDate=v=>new Intl.DateTimeFormat('hu-AT',{timeZone:'Europe/Vienna',dateStyle:'long',timeStyle:'short'}).format(new Date(v));
const clean=e=>e&&e.country==='at'&&e.id&&e.name&&e.startDate&&Number.isFinite(Date.parse(e.startDate))&&safeUrl(e.sourceUrl)&&!String(e.eventStatus||'').endsWith('EventCancelled');
const membersLink='https://www.kozpontiszovetseg.at/tagszervezetek';
const localRoot=widgets[0].dataset.root||'';
let crosswalk={},events=[],dataSource='',generatedAt='',lastError='',loaded=false,mappingAvailable=false;
const sourceUrl='https://www.diaszporaterkep.hu/';
async function request(url){
 const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),3500);
 try{const r=await fetch(url,{cache:'no-store',signal:ctrl.signal});if(!r.ok)throw Error('HTTP '+r.status);const j=await r.json();if(!j||!Array.isArray(j.events))throw Error('Invalid event payload');return j}
 finally{clearTimeout(timer)}
}
async function load(){
 let payload=null;
 try{
  const m=await fetch(localRoot+'member-event-map.json',{cache:'no-store'});if(!m.ok)throw Error('Mapping unavailable');
  crosswalk=(await m.json()).memberToDorappId||{};mappingAvailable=Object.keys(crosswalk).length===29;
 }catch(e){crosswalk={};mappingAvailable=false;lastError=String(e.message||e)}
 for(const url of endpoints){try{payload=await request(url);dataSource='live';break}catch(e){lastError=String(e.message||e)}}
 if(!payload){try{payload=await request(localRoot+'data/austria-events-snapshot.json');dataSource='snapshot'}catch(e){lastError=String(e.message||e)}}
 if(payload){const ids=new Set();events=payload.events.filter(clean).filter(e=>{if(ids.has(e.id))return false;ids.add(e.id);return new Date(e.startDate).getTime()>=Date.now()-60*60*1000}).sort((a,b)=>new Date(a.startDate)-new Date(b.startDate));generatedAt=payload.generatedAt||''}
 loaded=true;renderAll();
}
function card(e,memberOf){
 const who=e.organizer||'Szervező az eredeti forrásban';
 const parts=[e.city,e.venue].filter(Boolean);
 const member=memberOf.has(e.organizerId);
 return '<article class="calendar-event">'+(member?'<div class="calendar-member">Tagszervezeti esemény</div>':'')+
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
 const filter=events.filter(e=>(!memberId||(scopedId&&scopedId===e.organizerId))&&(!(!memberId&&scope==='members')||memberIds.has(e.organizerId))&&(!query||[e.name,e.city,e.venue,e.organizer].join(' ').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().includes(query)));
 list.innerHTML=filter.map(e=>card(e,memberIds)).join('');
 if(empty){empty.hidden=filter.length>0;empty.textContent=!loaded?'Naptár betöltése…':!events.length&&!dataSource?'A naptár most nem érhető el. A szervezők hivatalos oldalain ellenőrizhetők a programok.':memberId&&!mappingAvailable?'A tagszervezeti esemény-hozzárendelés jelenleg nem érhető el; a naptár nem tekinthető teljesnek.':memberId?'Ehhez a tagegyesülethez jelenleg nincs külön azonosított, forrásellenőrzött közelgő program a DORAPP naptárában.':'Nincs a szűrésnek megfelelő, forrásellenőrzött közelgő esemény.'}
 if(dataSource){const status=dataSource==='live'?'Friss DORAPP-forrás':'Mentett naptáradat (a friss DORAPP-forrás nem érhető el)';
 const when=generatedAt&&Number.isFinite(Date.parse(generatedAt))?' · forrás frissítve: '+formatDate(generatedAt):'';
 health.textContent=status+when+(memberId&&!mappingAvailable?' · Figyelem: a tagszervezeti hozzárendelés nem érhető el':'')+' · '+filter.length+' megjeleníthető tagszervezeti program';
 }else health.textContent='A DORAPP naptáradatok jelenleg nem tölthetők be.';
}
function renderAll(){widgets.forEach(render)}
widgets.forEach(w=>{w.querySelectorAll('[data-calendar-search],[data-calendar-scope]').forEach(el=>el.addEventListener(el.tagName==='SELECT'?'change':'input',()=>render(w)))});
load();
setInterval(()=>{if(!document.hidden)load()},30*60*1000);
})();