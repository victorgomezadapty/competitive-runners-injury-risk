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
  if(data){$('#athlete')?.querySelectorAll('option').forEach(o=>o.textContent=t('Atleta','Athlete')+' '+o.value);timeline();validation();sensitivity();contrasts();}
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
  const W=Math.max(300,Math.round($('#timeline').getBoundingClientRect().width||1000)),L=W<600?38:55,R=W-(W<600?12:25);
  $('#timeline').setAttribute('viewBox',`0 0 ${W} 300`);
  const x=d=>L+(d-start)/(end-start)*(R-L),y=v=>255-v/max*220,bw=Math.max(2,Math.min(6,(R-L)/(end-start)*.7));
  let svg=`<title>${t('Atleta','Athlete')} ${a.id}: ${$('#signal').selectedOptions[0].textContent}</title>`;
  for(let i=0;i<5;i++){const value=max*i/4;svg+=`<line x1="${L}" y1="${y(value)}" x2="${R}" y2="${y(value)}" stroke="#d5dccf"/><text x="${L-8}" y="${y(value)+4}" text-anchor="end">${f(value,signal==='rest'?1:1)}</text>`;}
  for(let d=start;d<=end;d+=W<600?28:14)svg+=`<text x="${x(d)}" y="280" text-anchor="middle">${d}</text>`;
  let path='',previous=null;
  const bars=['distance','intensity','rest'].includes(signal);
  rows.forEach(d=>{if(d[signal]===null){previous=null;return;}
    if(bars){svg+=`<rect x="${x(d.day)-bw/2}" y="${y(d[signal])}" width="${bw}" height="${255-y(d[signal])}" fill="${signal==='intensity'?'#a25b36':'#347466'}" opacity=".85"><title>${t('Día','Day')} ${d.day}: ${f(d[signal],2)}</title></rect>`;}
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
  $('#validation-description').textContent=t(...names[protocol])+(ci.length?` · `+t('IC 95 % de AP por atleta: ','Athlete-cluster AP 95% CI: ')+`${f(ci[0].ci95_low,4)} `+t('a','to')+` ${f(ci[0].ci95_high,4)}`:'');
  $('#ap').textContent=f(metric.average_precision,3);
  const above=ci.length&&ci[0].ci95_low>metric.prevalence;
  $('#verdict').innerHTML=above?t(`<strong>Por encima del azar, pero poco.</strong> Todo el intervalo (${f(ci[0].ci95_low,4)} a ${f(ci[0].ci95_high,4)}) queda sobre el azar (${f(metric.prevalence,4)}). Es la única evaluación donde pasa, y no exige predecir el futuro.`,`<strong>Above chance, but barely.</strong> The whole interval (${f(ci[0].ci95_low,4)} to ${f(ci[0].ci95_high,4)}) sits above chance (${f(metric.prevalence,4)}). It is the only evaluation where this happens, and it does not require predicting the future.`):t(`<strong>No se distingue con claridad del azar.</strong> El intervalo (${f(ci[0].ci95_low,4)} a ${f(ci[0].ci95_high,4)}) incluye la AP esperada al azar (${f(metric.prevalence,4)}).`,`<strong>Not clearly distinguishable from chance.</strong> The interval (${f(ci[0].ci95_low,4)} to ${f(ci[0].ci95_high,4)}) includes the AP expected by chance (${f(metric.prevalence,4)}).`);
  ciChart();
  $('#metrics').innerHTML=`<div><strong>${f(metric.roc_auc,3)}</strong><span>ROC-AUC</span></div><div><strong>${f(metric.brier,5)}</strong><span>Brier</span></div><div><strong>${metric.athletes}</strong><span>${t('atletas test','test athletes')}</span></div>`;
  $('#calibration-detail').textContent=`Brier: ${f(raw.brier,6)} → ${f(metric.brier,6)}. `+t('Sin calibrar → sigmoid. Menor es mejor; un Brier pequeño también refleja eventos raros.','Raw → sigmoid. Lower is better; small Brier also reflects rare positives.');
  alerts();
}
function ciChart(){
  const svg=$('#ci-chart');if(!svg)return;
  const W=Math.max(300,Math.round(svg.getBoundingClientRect().width||520)),rowH=62,top=10,H=top+rowH*3+34,L=12,R=W-(W<420?44:70),max=.045;
  const x=v=>L+v/max*(R-L);
  const order=['known_temporal','unseen_athlete','unseen_athlete_temporal'];
  const label={known_temporal:t('Futuro de atletas conocidos','Future of known athletes'),unseen_athlete:t('Atletas nuevos, todos los periodos','Unseen athletes, all periods'),unseen_athlete_temporal:t('Atletas nuevos y periodo futuro','Unseen athletes, future period')};
  let out='';
  order.forEach((key,i)=>{const m=data.metrics.find(d=>d.protocol===key&&d.model==='logistic_load_response_sigmoid'),c=data.intervals.find(d=>d.protocol===key&&d.metric==='average_precision'),y=top+i*rowH+36,on=key===protocol;
    out+=`<g class="ci-row${on?' on':''}"><text x="${L}" y="${y-16}" class="ci-label">${label[key]}</text><line x1="${x(m.prevalence)}" x2="${x(m.prevalence)}" y1="${y-11}" y2="${y+11}" class="ci-chance"/><line x1="${x(c.ci95_low)}" x2="${x(c.ci95_high)}" y1="${y}" y2="${y}" class="ci-bar"/><circle cx="${x(m.average_precision)}" cy="${y}" r="${on?7:5}" class="ci-dot"/><text x="${x(c.ci95_high)+8}" y="${y+4}" class="ci-value">${f(m.average_precision,3)}</text></g>`;});
  const axisY=top+rowH*3+8;out+=`<line x1="${L}" x2="${R}" y1="${axisY}" y2="${axisY}" class="ci-axis"/>`;
  [0,.01,.02,.03,.04].forEach(v=>{out+=`<text x="${x(v)}" y="${axisY+18}" text-anchor="middle" class="ci-tick">${f(v,2)}</text>`;});
  svg.setAttribute('viewBox',`0 0 ${W} ${H}`);svg.setAttribute('height',H);svg.innerHTML=out;
  svg.setAttribute('aria-label',order.map(key=>{const m=data.metrics.find(d=>d.protocol===key&&d.model==='logistic_load_response_sigmoid'),c=data.intervals.find(d=>d.protocol===key&&d.metric==='average_precision');return `${label[key]}: AP ${f(m.average_precision,4)}, IC ${f(c.ci95_low,4)} ${t('a','to')} ${f(c.ci95_high,4)}, ${t('azar','chance')} ${f(m.prevalence,4)}`;}).join('. '));
}
const featureNames={sessions:['Sesiones','Sessions'],distance:['Distancia total · km','Total distance · km'],z3_4_distance:['Distancia Z3 y Z4 · km','Z3 and Z4 distance · km'],z5_t1_t2_distance:['Distancia Z5, T1 y T2 · km','Z5, T1 and T2 distance · km'],sprint_distance:['Distancia de sprint · km','Sprint distance · km'],strength_sessions:['Sesiones de fuerza','Strength sessions'],cross_training_hours:['Entrenamiento cruzado · h','Cross training · h'],rest_days:['Días sin sesiones','Days without sessions'],mean_exertion:['Esfuerzo percibido medio','Mean perceived exertion'],mean_training_success:['Éxito percibido medio','Mean perceived success'],mean_recovery:['Recuperación percibida media','Mean perceived recovery']};
let contrastWindow=7;
function contrasts(){
  if(!$('#contrast-rows')||!data.contrasts)return;
  const rows=data.contrasts.filter(d=>d.window_days===contrastWindow),lim=.8,pos=v=>50+Math.max(-lim,Math.min(lim,v))/lim*50;
  $('#contrast-rows').innerHTML=rows.map(d=>{const base=d.feature.replace(/_\dd$/,''),name=t(...featureNames[base]),sig=d.ci95_low>0||d.ci95_high<0,total=d.higher+d.lower+d.equal,unit=d.feature.includes('mean_')?3:(d.feature.includes('distance')||d.feature.includes('hours')?1:2);
    return `<div class="contrast-row"><span class="c-name">${name}</span><span class="c-track" title="${t('Diferencia pareada','Paired difference')} ${f(d.difference,unit)} (IC ${f(d.ci95_low,unit)} ${t('a','to')} ${f(d.ci95_high,unit)})"><i class="c-zero"></i><b class="c-dot${sig?' sig':''}${d.standardized<0?' neg':''}" style="left:${pos(d.standardized)}%"></b><em style="left:${pos(d.standardized)}%">${f(d.standardized,2)}</em></span><span class="c-split" aria-label="${d.higher} ${t('de','of')} ${total} ${t('atletas con más antes de la lesión','athletes with more before injury')}, ${d.lower} ${t('con menos','with less')}"><i class="more" style="width:${d.higher/total*100}%"></i><i class="less" style="width:${d.lower/total*100}%"></i><small>${d.higher} / ${d.lower}</small></span><span class="sr-only">${name}: ${t('diferencia pareada','paired difference')} ${f(d.difference,unit)}, IC 95 % ${f(d.ci95_low,unit)} ${t('a','to')} ${f(d.ci95_high,unit)}; ${d.higher} ${t('de','of')} ${total} ${t('atletas con más antes de la lesión','athletes with more before injury')}.</span></div>`;}).join('');
  const dist=rows.find(d=>d.feature.startsWith('distance')),rest=rows.find(d=>d.feature.startsWith('rest_days')),total=dist.higher+dist.lower+dist.equal;
  $('#contrast-headline').innerHTML=t(`En <strong>${dist.higher} de ${total} atletas</strong> la distancia de los ${contrastWindow} días previos fue mayor antes de una etiqueta de lesión (media +${f(dist.difference,1)} km). En ${rest.lower} de ${total} hubo menos días sin sesiones. La recuperación percibida también fue algo mayor, no menor.`,`In <strong>${dist.higher} of ${total} athletes</strong> distance over the previous ${contrastWindow} days was higher before an injury label (mean +${f(dist.difference,1)} km). In ${rest.lower} of ${total} there were fewer days without sessions. Perceived recovery was also slightly higher, not lower.`);
  const q=data.distance_7d_rows,mx=160,px=v=>v/mx*100;
  $('#iqr').innerHTML=[['healthy',t('Sin etiqueta','Unlabelled')],['injury',t('Con etiqueta','Labelled')]].map(([k,l])=>`<div class="iqr-row ${k}"><span>${l}</span><span class="iqr-track"><i style="left:${px(q[k].q25)}%;width:${px(q[k].q75-q[k].q25)}%"></i><b style="left:${px(q[k].median)}%"></b></span><small>${f(q[k].q25,1)} · ${f(q[k].median,1)} · ${f(q[k].q75,1)} km</small></div>`).join('')+`<div class="iqr-axis"><span></span><span class="iqr-ticks">${[0,40,80,120,160].map(v=>`<em style="left:${px(v)}%">${v}</em>`).join('')}</span><small></small></div>`;
}
document.querySelectorAll('[data-window]').forEach(button=>button.addEventListener('click',()=>{contrastWindow=Number(button.dataset.window);document.querySelectorAll('[data-window]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));contrasts();}));
let resizeTimer;addEventListener('resize',()=>{clearTimeout(resizeTimer);resizeTimer=setTimeout(()=>{if(data){timeline();ciChart();}},150);});
function alerts(){
  const budget=[.05,.1,.2][Number($('#budget').value)];
  const a=data.alerts.find(d=>d.protocol===protocol&&d.requested_budget===budget);
  const items=[[f(a.alerts_per_100_selected_rows,1),t('alertas / 100 filas seleccionadas','alerts / 100 selected rows')],[pct(a.recall),t('etiquetas positivas capturadas','positive labels captured')],[pct(a.precision),t('precisión de las alertas','alert precision')],[f(a.alerts_per_captured_positive,1),t('revisiones / positivo capturado','reviews / captured positive')]];
  $('#alert-counts').innerHTML=items.map(([value,label])=>`<div><strong>${value}</strong><span>${label}</span></div>`).join('');
  $('#alert-grid').innerHTML=Array.from({length:100},(_,i)=>`<i class="${i<Math.round(a.alerts_per_100_selected_rows)?'alert':''}"></i>`).join('');
}
function sensitivity(){
  const labels={day_logistic:['Diaria · logística','Day · logistic'],day_week_logistic:['Diaria + 14/21 d · logística','Day + 14/21d · logistic'],athlete_balanced_logistic:['Diaria + 14/21 d · peso por atleta','Day + 14/21d · athlete weights'],day_week_forest:['Diaria + 14/21 d · bosque fijo','Day + 14/21d · fixed forest']};
  $('#sensitivity tbody').innerHTML=Object.entries(labels).map(([key,label])=>`<tr><td>${t(...label)}</td>${[20261025,20261026,20261027].map(seed=>{const m=data.final.find(d=>d.protocol==='unseen_athlete_temporal'&&d.model===key+'_sigmoid'&&d.seed===seed);return `<td>${m?f(m.average_precision,4):'—'}</td>`;}).join('')}</tr>`).join('')+`<tr class="chance-row"><td>${t('Azar (fracción positiva)','Chance (positive fraction)')}</td>${[20261025,20261026,20261027].map(seed=>{const m=data.final.find(d=>d.protocol==='unseen_athlete_temporal'&&d.seed===seed);return `<td>${m?f(m.prevalence,4):''}</td>`;}).join('')}</tr>`;
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
