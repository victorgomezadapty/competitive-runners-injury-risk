const $=s=>document.querySelector(s);
let lang=localStorage.getItem('runners-language')||'es';
let protocol='unseen_athlete_temporal',data;
const t=(es,en)=>lang==='es'?es:en;
const f=(v,n=3)=>Number(v).toLocaleString(lang==='es'?'es-ES':'en-US',{maximumFractionDigits:n,minimumFractionDigits:n});
const pct=v=>f(v*100,1)+'%';
function translate(){
  document.documentElement.lang=lang;
  document.querySelectorAll('[data-es]').forEach(el=>el.innerHTML=el.dataset[lang]);
  if($('#lang')){$('#lang').textContent=lang==='es'?'EN':'ES';$('#lang').setAttribute('aria-label',t('Cambiar a inglés','Switch to Spanish'));}
  if(data){$('#athlete')?.querySelectorAll('option').forEach(o=>o.textContent=t('Atleta','Athlete')+' '+o.value);timeline();validation();sensitivity();}
  document.querySelectorAll('a[href^="/evidence.html"],a[href="/"]').forEach(a=>{const url=new URL(a.href);url.searchParams.set('lang',lang);a.href=url.pathname+url.search+url.hash;});
}
const queryLang=new URLSearchParams(location.search).get('lang');
if(['es','en'].includes(queryLang))lang=queryLang;
$('#lang')?.addEventListener('click',()=>{lang=lang==='es'?'en':'es';localStorage.setItem('runners-language',lang);translate();motion();});
let paused=localStorage.getItem('runners-paused')==='true'||matchMedia('(prefers-reduced-motion: reduce)').matches;
function motion(){document.body.classList.toggle('paused',paused);document.querySelectorAll('animateMotion').forEach(el=>paused?el.ownerSVGElement.pauseAnimations():el.ownerSVGElement.unpauseAnimations());$('#motion')?.setAttribute('aria-pressed',String(paused));if($('#motion'))$('#motion').textContent=paused?t('Activar movimiento','Enable motion'):t('Pausar movimiento','Pause motion');}
$('#motion')?.addEventListener('click',()=>{paused=!paused;localStorage.setItem('runners-paused',String(paused));motion();});
function timeline(){
  if(!$('#athlete'))return;
  const a=data.athletes.find(a=>String(a.id)===$('#athlete').value);
  if(!a)return;
  const view=a[$('#event').value],signal=$('#signal').value;
  const rows=view.days,values=rows.map(d=>d[signal]).filter(v=>v!==null);
  const max=Math.max(...values,signal==='rest'?1:.01)*1.12;
  const start=view.start,end=view.end;
  const x=d=>55+(d-start)/(end-start)*920,y=v=>255-v/max*220;
  let svg=`<title>${t('Atleta','Athlete')} ${a.id}: ${$('#signal').selectedOptions[0].textContent}</title>`;
  for(let i=0;i<5;i++){const value=max*i/4;svg+=`<line x1="55" y1="${y(value)}" x2="975" y2="${y(value)}" stroke="#d5dccf"/><text x="45" y="${y(value)+4}" text-anchor="end">${f(value,signal==='rest'?1:1)}</text>`;}
  for(let d=start;d<=end;d+=14)svg+=`<text x="${x(d)}" y="280" text-anchor="middle">${d}</text>`;
  let path='',previous=null;
  const bars=['distance','intensity','rest'].includes(signal);
  rows.forEach(d=>{if(d[signal]===null){previous=null;return;}
    if(bars){svg+=`<rect x="${x(d.day)-3}" y="${y(d[signal])}" width="6" height="${255-y(d[signal])}" fill="${signal==='intensity'?'#a25b36':'#347466'}" opacity=".85"><title>${t('Día','Day')} ${d.day}: ${f(d[signal],2)}</title></rect>`;}
    else{path+=`${previous===d.day-1?'L':'M'}${x(d.day)},${y(d[signal])} `;svg+=`<circle cx="${x(d.day)}" cy="${y(d[signal])}" r="2.4" fill="#24645a"><title>${t('Día','Day')} ${d.day}: ${f(d[signal],3)}</title></circle>`;previous=d.day;}
  });
  if(path)svg+=`<path d="${path}" fill="none" stroke="#24645a" stroke-width="1.7"/>`;
  view.injuries.forEach(d=>{svg+=`<line x1="${x(d)}" x2="${x(d)}" y1="20" y2="255" stroke="#bc4b28" stroke-dasharray="4 5"/><circle cx="${x(d)}" cy="18" r="4" fill="#bc4b28"/>`;});
  svg+=`<text x="${x(view.event)}" y="9" text-anchor="middle" class="event-text">E = ${view.event}</text>`;
  $('#timeline').innerHTML=svg;
  $('#timeline').setAttribute('aria-label',t(`Atleta ${a.id}, ${signal}, días relativos ${start} a ${end}. Etiquetas de lesión en ${view.injuries.join(', ')||'ninguno'}.`,`Athlete ${a.id}, ${signal}, relative days ${start} to ${end}. Injury labels at ${view.injuries.join(', ')||'none'}.`));
  $('#timeline-meta').textContent=t(`Atleta ${a.id} · ${a.rows} filas seleccionadas · ${a.injuries} etiquetas retenidas`,`Athlete ${a.id} · ${a.rows} selected rows · ${a.injuries} retained labels`)+` | `+t(`Día relativo ${view.event} · ${rows.length} días con historia`,`Relative day ${view.event} · ${rows.length} days with history`);
  $('#profile').textContent=t('Ventana anterior a E: ','Window before E: ')+`${f(view.distance_7d,1)} km / 7d · ${f(view.rest_days_7d,0)} `+t('días sin sesiones','days without sessions')+` · `+t('Puntuación fuera de entrenamiento: ','Held-out score: ')+pct(view.probability)+t(' de etiqueta positiva en la muestra seleccionada.',' positive-label probability in the selected sample.');
}
const names={known_temporal:['Futuro de atletas presentes en entrenamiento. 23 atletas, 5.254 filas y 89 positivos.','Future of athletes present in fitting. 23 athletes, 5,254 rows and 89 positives.'],unseen_athlete:['Atletas separados entre ajuste, calibración y test. Cinco folds, 74 atletas y 583 positivos.','Athlete-disjoint fitting, calibration and test. Five folds, 74 athletes and 583 positives.'],unseen_athlete_temporal:['Atletas nuevos y periodo posterior. Cinco folds, 32 atletas y 122 positivos en 7.596 filas.','Unseen athletes and a later period. Five folds, 32 athletes and 122 positives in 7,596 rows.']};
function validation(){
  if(!$('#ap'))return;
  const metric=data.metrics.find(d=>d.protocol===protocol&&d.model==='logistic_load_response_sigmoid');
  const raw=data.metrics.find(d=>d.protocol===protocol&&d.model==='logistic_load_response_raw');
  const ci=data.intervals.filter(d=>d.protocol===protocol&&d.metric==='average_precision');
  $('#validation-description').textContent=t(...names[protocol])+(ci.length?` · `+t('IC 95% AP por atleta: ','Athlete-cluster AP 95% CI: ')+`${f(ci[0].ci95_low,4)}–${f(ci[0].ci95_high,4)}`:'');
  $('#ap').textContent=f(metric.average_precision,3);
  $('#ap-bars').innerHTML=`<div><label>${t('Modelo calibrado','Calibrated model')}<span>${f(metric.average_precision,4)}</span></label><i style="width:${metric.average_precision/.04*100}%"></i></div><div><label>${t('Fracción positiva del test','Test label fraction')}<span>${f(metric.prevalence,4)}</span></label><i class="reference" style="width:${metric.prevalence/.04*100}%"></i></div>`;
  $('#metrics').innerHTML=`<div><strong>${f(metric.roc_auc,3)}</strong><span>ROC-AUC</span></div><div><strong>${f(metric.brier,5)}</strong><span>Brier</span></div><div><strong>${metric.athletes}</strong><span>${t('atletas test','test athletes')}</span></div>`;
  $('#calibration-detail').textContent=`Brier: ${f(raw.brier,6)} → ${f(metric.brier,6)}. `+t('Sin calibrar → sigmoid. Menor es mejor; un Brier pequeño también refleja eventos raros.','Raw → sigmoid. Lower is better; small Brier also reflects rare positives.');
  alerts();
}
function alerts(){
  const budget=[.05,.1,.2][Number($('#budget').value)];
  const a=data.alerts.find(d=>d.protocol===protocol&&d.requested_budget===budget);
  const items=[[f(a.alerts_per_100_selected_rows,1),t('alertas / 100 filas seleccionadas','alerts / 100 selected rows')],[pct(a.recall),t('etiquetas positivas capturadas','positive labels captured')],[pct(a.precision),t('precisión de las alertas','alert precision')],[f(a.alerts_per_captured_positive,1),t('revisiones / positivo capturado','reviews / captured positive')]];
  $('#alert-counts').innerHTML=items.map(([value,label])=>`<div><strong>${value}</strong><span>${label}</span></div>`).join('');
  $('#alert-grid').innerHTML=Array.from({length:100},(_,i)=>`<i class="${i<Math.round(a.alerts_per_100_selected_rows)?'alert':''}"></i>`).join('');
}
function sensitivity(){
  const labels={day_logistic:['Day · logística','Day · logistic'],day_week_logistic:['Day + 14/21d · logística','Day + 14/21d · logistic'],athlete_balanced_logistic:['Day + 14/21d · peso por atleta','Day + 14/21d · athlete weights'],day_week_forest:['Day + 14/21d · bosque fijo','Day + 14/21d · fixed forest']};
  $('#sensitivity tbody').innerHTML=Object.entries(labels).map(([key,label])=>`<tr><td>${t(...label)}</td>${[20261025,20261026,20261027].map(seed=>{const m=data.final.find(d=>d.protocol==='unseen_athlete_temporal'&&d.model===key+'_sigmoid'&&d.seed===seed);return `<td>${m?f(m.average_precision,4):'—'}</td>`;}).join('')}</tr>`).join('');
}
document.querySelectorAll('[data-protocol]').forEach(button=>button.addEventListener('click',()=>{protocol=button.dataset.protocol;document.querySelectorAll('[data-protocol]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));validation();}));
$('#budget')?.addEventListener('input',alerts);
['athlete','event','signal'].forEach(id=>$('#'+id)?.addEventListener('change',timeline));
translate();motion();
if($('#athlete')){
  try{const res=await fetch('/data.json');if(!res.ok)throw new Error('Data download failed');data=await res.json();$('#athlete').innerHTML=data.athletes.map(a=>`<option value="${a.id}">${t('Atleta','Athlete')} ${a.id}</option>`).join('');translate();motion();}
  catch(error){$('#load-error').hidden=false;$('#load-error').textContent=t('No se pudieron cargar los datos. Recarga la página o consulta las tablas en GitHub.','Data could not load. Reload the page or consult the GitHub tables.');console.error(error);}
}
if('IntersectionObserver'in window){const observer=new IntersectionObserver(entries=>entries.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');observer.unobserve(e.target);}}),{threshold:.06});document.querySelectorAll('.reveal').forEach(el=>{el.classList.add('js-reveal');observer.observe(el);});}
