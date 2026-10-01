/* ---------- 2025 vs 2026 ---------- */
function drawByIndex(host){
  const box=$(host); box.innerHTML='';
  const W=Math.max(320,box.clientWidth), H=300, M={l:52,r:84,t:12,b:28};
  if(W<560) M.r=14;
  const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Curva de capital de Envolvente por número de operación, 2025 y 2026'},box);
  const S=[['2025','--s-start'],['2026','--s-env']].map(([y,c])=>({y,c:css(c),p:DATA[y].envolvente.curve.map((x,i)=>({i,eq:x.eq}))}));
  const nmax=Math.max(...S.map(s=>s.p.length-1));
  let mn=Math.min(1000,...S.flatMap(s=>s.p.map(p=>p.eq))), mx=Math.max(1000,...S.flatMap(s=>s.p.map(p=>p.eq))); const pad=(mx-mn)*0.06; mn-=pad; mx+=pad;
  const X=i=>M.l+i/nmax*(W-M.l-M.r), Y=v=>M.t+(mx-v)/(mx-mn)*(H-M.t-M.b);
  niceTicks(mn,mx,5).t.forEach(v=>{el('line',{x1:M.l,x2:W-M.r,y1:Y(v),y2:Y(v),class:'gl'},svg);el('text',{x:M.l-8,y:Y(v)+4,'text-anchor':'end',class:'ax'},svg).textContent=fmt(v,0)});
  niceTicks(0,nmax,6).t.forEach(v=>el('text',{x:X(v),y:H-8,'text-anchor':'middle',class:'ax'},svg).textContent=fmt(v,0));
  el('line',{x1:M.l,x2:W-M.r,y1:Y(1000),y2:Y(1000),class:'zero','stroke-dasharray':'3 4'},svg);
  S.forEach(s=>{el('path',{d:'M'+s.p.map(p=>`${X(p.i)},${Y(p.eq)}`).join(' L'),fill:'none',stroke:s.c,'stroke-width':2,'stroke-linejoin':'round'},svg);
    const L=s.p[s.p.length-1]; el('circle',{cx:X(L.i),cy:Y(L.eq),r:4,fill:s.c,stroke:css('--panel'),'stroke-width':2},svg);
    if(M.r>50) el('text',{x:X(L.i)+8,y:Y(L.eq)+4,class:'lbl'},svg).textContent=`${s.y}: ${fmt(L.eq,0)}`;});
  const cross=el('line',{y1:M.t,y2:H-M.b,stroke:css('--fg3'),'stroke-dasharray':'2 3',visibility:'hidden'},svg);
  const hit=el('rect',{x:M.l,y:0,width:W-M.l-M.r,height:H,fill:'transparent'},svg);
  hit.addEventListener('pointermove',e=>{const r=svg.getBoundingClientRect();const sx=(e.clientX-r.left)*W/r.width;const i=Math.round((sx-M.l)/(W-M.l-M.r)*nmax);
    cross.setAttribute('x1',X(i));cross.setAttribute('x2',X(i));cross.setAttribute('visibility','visible');
    showTip(box,`Operación ${i}<br>`+S.map(s=>`<span style="color:${s.c}">■</span> ${s.y}: ${s.p[i]?fmt(s.p[i].eq)+' USD':'—'}`).join('<br>'),e.clientX-r.left,e.clientY-r.top)});
  hit.addEventListener('pointerleave',()=>{cross.setAttribute('visibility','hidden');hideTip(box)});
}
function drawMonths(host){
  const box=$(host); box.innerHTML='';
  const A=DATA.anual.meses, MS=MES;
  const W=Math.max(300,box.clientWidth), H=240, M={l:40,r:8,t:14,b:26};
  const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'R por mes de Envolvente en 2025 y 2026'},box);
  const vals=MS.flatMap(m=>[A['2025'][m],A['2026'][m]]).filter(v=>v!=null);
  let mn=Math.min(0,...vals), mx=Math.max(0,...vals); const pad=(mx-mn)*0.1; mn-=pad; mx+=pad;
  const Y=v=>M.t+(mx-v)/(mx-mn)*(H-M.t-M.b), gw=(W-M.l-M.r)/12, bw=Math.max(2,(gw-6)/2-1);
  niceTicks(mn,mx,4).t.forEach(v=>{el('line',{x1:M.l,x2:W-M.r,y1:Y(v),y2:Y(v),class:'gl'},svg);el('text',{x:M.l-6,y:Y(v)+4,'text-anchor':'end',class:'ax'},svg).textContent=fmt(v,0)+'R'});
  el('line',{x1:M.l,x2:W-M.r,y1:Y(0),y2:Y(0),class:'zero'},svg);
  MS.forEach((m,i)=>{const x0=M.l+i*gw+3;
    [['2025','--s-start'],['2026','--s-env']].forEach(([y,c],j)=>{const v=A[y][m]; if(v==null) return; const x=x0+j*(bw+2), y0=Y(0), y1=Y(v), h=Math.abs(y1-y0), r=Math.min(3,bw/2,h);
      const up=v>=0; const d=up?`M${x},${y0} V${y1+r} Q${x},${y1} ${x+r},${y1} H${x+bw-r} Q${x+bw},${y1} ${x+bw},${y1+r} V${y0} Z`:`M${x},${y0} V${y1-r} Q${x},${y1} ${x+r},${y1} H${x+bw-r} Q${x+bw},${y1} ${x+bw},${y1-r} V${y0} Z`;
      if(h>0) el('path',{d,fill:css(c)},svg);});
    el('text',{x:x0+bw,y:H-8,'text-anchor':'middle',class:'ax'},svg).textContent=m;
    const hit=el('rect',{x:M.l+i*gw,y:M.t,width:gw,height:H-M.t-M.b,fill:'transparent'},svg);
    hit.addEventListener('pointermove',e=>{const r=svg.getBoundingClientRect();showTip(box,`${m}<br><span class="y25">■</span> 2025: ${A['2025'][m]!=null?sg(A['2025'][m])+'R':'—'}<br><span class="y26">■</span> 2026: ${A['2026'][m]!=null?sg(A['2026'][m])+'R':'—'}`,e.clientX-r.left,e.clientY-r.top)});
    hit.addEventListener('pointerleave',()=>hideTip(box));});
}
function renderAnual(){
  const A=DATA.anual, E5=DATA['2025'].envolvente, E6=DATA['2026'].envolvente, T=A.dos_anios.envolvente;
  const Fk=k=>A.filtros.find(f=>f.key===k), d5=A.detalle['2025'], d6=A.detalle['2026'];
  const chg=(a,b)=>((b-a)/a*100);
  $('#a-verdict').innerHTML=`<span class="eyebrow">Veredicto</span>
    <div class="big">La ventaja de Envolvente se sostiene en 2025, pero es mucho más chica que en 2026. Con los dos años juntos el sistema es rentable y consistente, sin cambiar ninguna regla.</div>
    <p><b>2025: ${sg(E5.R_tot)}R</b> (factor ${fmt(E5.pf)}, win rate ${fmt(E5.wr,1)}%, caída máxima −${fmt(E5.mdd_pct)}%) contra <b>2026: ${sg(E6.R_tot)}R</b> (factor ${fmt(E6.pf)}, win rate ${fmt(E6.wr,1)}%, −${fmt(E6.mdd_pct)}%). 2025 no alcanza el criterio que habíamos fijado para validar (factor de ganancias mayor a 1,2), pero sí el R promedio positivo. <b>Con los dos años juntos</b>: ${T.n} operaciones, ${sg(T.R)}R, factor ${fmt(T.pf)}, win rate ${fmt(T.wr,1)}% y expectativa positiva en ${fmt(T.p,1)}% de 5.000 simulaciones. 2026 fue un año por encima de lo normal; la expectativa realista es la de los dos años juntos.</p>`;
  // KPIs
  const rows=[['Operaciones válidas','n','n',0,null],['Operaciones por semana','trades_week','tw',2,null],['Win rate','wr','wr',1,'%'],['Factor de ganancias','pf','pf',2,''],
    ['R total','R_tot','R',2,'R'],['R por operación','R_avg','R_avg',3,'R'],['R por semana','R_week','R_week',2,'R'],['PyG (%)','ret_pct',null,2,'%'],
    ['Caída máxima','mdd_pct','mdd',2,'dd'],['Caída máxima esperable (p95)','mc_dd95','mc95',2,'dd'],['Sharpe','sharpe','sharpe',2,''],['P(expectativa > 0)','p_exp_pos','p',1,'%']];
  const f=(v,dec,u)=>v==null?'—':u==='dd'?'−'+fmt(v,dec)+'%':u==='R'?`<span class="${cls(v)}">${sg(v,dec)}R</span>`:u==='%'?fmt(v,dec)+'%':fmt(v,dec);
  let h='<tr><th>Métrica</th><th class="n">2025</th><th class="n">2026</th><th class="n">Diferencia</th><th class="n">2 años</th></tr>';
  [['envolvente','Envolvente'],['combinado','Envolvente + START'],['start','START']].forEach(([k,n])=>{
    const a=DATA['2025'][k], b=DATA['2026'][k], t=A.dos_anios[k];
    h+=`<tr class="grp"><td colspan="5">${n}</td></tr>`+rows.map(([lab,key,tk,dec,u])=>{const va=a[key], vb=b[key], dv=vb-va, vt=tk?t[tk]:null;
      const pctT=key==='ret_pct'?null:vt;
      return `<tr><td>${lab}</td><td class="n">${f(va,dec,u)}</td><td class="n">${f(vb,dec,u)}</td><td class="n ${u==='dd'?cls(-dv):cls(dv)}">${(dv>0?'+':dv<0?'−':'')+fmt(Math.abs(dv),dec)}</td><td class="n">${f(pctT,dec,u)}</td></tr>`}).join('')});
  $('#t-a-kpi').innerHTML=h;
  drawByIndex('#c-a-eq');
  // causas
  const g=x=>`${sg(x.R)}R · ${fmt(x.wr,1)}% · ${x.n} ops.`;
  const tf=k=>{const x=Fk(k);return [x['2025'],x['2026']]};
  const [t5,t6]=tf('tend'), [c5,c6]=tf('contra');
  const C=[
    ['Precio del oro en el período',`${fmt(d5.precio.ini,0)} → ${fmt(d5.precio.fin,0)} (${sg(chg(d5.precio.ini,d5.precio.fin),0)}%)`,`${fmt(d6.precio.ini,0)} → ${fmt(d6.precio.fin,0)} (${sg(chg(d6.precio.ini,d6.precio.fin),0)}%), rango ${fmt(d6.precio.mn,0)}–${fmt(d6.precio.mx,0)}`,'2025: tendencia alcista fuerte y sostenida. 2026: mercado de ida y vuelta, con caída y rebote.'],
    ['Win rate y payoff',`${fmt(E5.wr,1)}% · payoff ${fmt(E5.payoff)}`,`${fmt(E6.wr,1)}% · payoff ${fmt(E6.payoff)}`,'El payoff es igual: toda la diferencia está en el acierto.'],
    ['Compras',g(d5.dir.Compras),g(d6.dir.Compras),'Positivas los dos años.'],
    ['Ventas',g(d5.dir.Ventas),g(d6.dir.Ventas),'En 2025 las ventas pierden: vender contra un oro que sube.'],
    ['A favor de la tendencia de 20 días',`${sg(t5.R)}R · ${fmt(t5.wr,1)}% · ${t5.n} ops.`,`${sg(t6.R)}R · ${fmt(t6.wr,1)}% · ${t6.n} ops.`,'Rinde parecido los dos años.'],
    ['En contra de la tendencia de 20 días',`${sg(c5.R)}R · ${fmt(c5.wr,1)}% · ${c5.n} ops.`,`${sg(c6.R)}R · ${fmt(c6.wr,1)}% · ${c6.n} ops.`,'Acá está la diferencia entre los dos años.'],
    ['Primera operación del día',g(d5.orden['1.ª del día']),g(d6.orden['1.ª del día']),'La primera entrada casi no gana en 2025.'],
    ['Segunda operación (después de una pérdida)',g(d5.orden['2.ª o más (después de una pérdida)']),g(d6.orden['2.ª o más (después de una pérdida)']),'Positiva los dos años: la reentrada funciona.'],
    ['Entradas 07:00–07:59',g(d5.hora['07:00–07:59']),g(d6.hora['07:00–07:59']),'La mejor franja de 2026 queda en cero en 2025.'],
    ['Entradas 08:00–08:59',g(d5.hora['08:00–08:59']),g(d6.hora['08:00–08:59']),'Estable los dos años.'],
    ['Operaciones de más de 30 minutos',g(d5.dur['Más de 30 min']),g(d6.dur['Más de 30 min']),'Negativas los dos años.'],
  ];
  $('#t-a-causas').innerHTML='<tr><th>Factor</th><th>2025</th><th>2026</th><th>Lectura</th></tr>'+C.map(r=>`<tr><td>${r[0]}</td><td class="mono" style="white-space:nowrap">${r[1]}</td><td class="mono" style="white-space:nowrap">${r[2]}</td><td style="color:var(--fg2);min-width:220px">${r[3]}</td></tr>`).join('');
  drawMonths('#c-a-mes');
  const m5=Object.entries(A.meses['2025']).sort((a,b)=>a[1]-b[1])[0];
  $('#a-causas-txt').innerHTML=[
    ['y','TENDENCIA',`<b>La causa principal es el tipo de mercado.</b> En 2025 el oro subió ${sg(chg(d5.precio.ini,d5.precio.fin),0)}% casi sin pausas. Las operaciones en contra de esa tendencia perdieron ${sg(c5.R)}R; las ventas, ${sg(d5.dir.Ventas.R)}R. En 2026, con un mercado de ida y vuelta, las mismas operaciones en contra ganaron ${sg(c6.R)}R.`],
    ['y','VOLATILIDAD',`<b>Un mes explica buena parte del año.</b> ${m5[0]} de 2025 dejó ${sg(m5[1])}R, en plena volatilidad por los anuncios de aranceles de abril. Sin ese mes, 2025 habría cerrado cerca de ${sg(E5.R_tot-m5[1])}R.`],
    ['g','LO QUE SE MANTIENE',`<b>Hay patrones que se repiten.</b> El payoff (≈1), la reentrada después de una pérdida, las operaciones a favor de la tendencia y la franja de 08:00 rinden de forma parecida en los dos años. Las operaciones de más de 30 minutos pierden en los dos.`],
    ['r','LO QUE NO SE MANTIENE',`<b>La franja de 07:00 y las ventas</b>, que fueron lo mejor de 2026, no rindieron en 2025. Por eso no conviene recortar horarios ni direcciones mirando un solo año.`],
  ].map(([c,t,x])=>`<li><span class="tag ${c}">${t}</span><p>${x}</p></li>`).join('');
  // filtros
  let hf='<tr><th>Filtro (Envolvente)</th><th class="n">2025 R</th><th class="n">Dif.</th><th class="n">2026 R</th><th class="n">Dif.</th><th class="n">R/op. 25 · 26</th><th class="n">Caída máx. 25 · 26</th><th>Veredicto</th></tr>';
  A.filtros.forEach(x=>{const a=x['2025'], b=x['2026'], base=x.key==='base';
    const ver=base?'<span class="tag n">REFERENCIA</span>':x.robusto?'<span class="tag g">ROBUSTO</span>':(x.dR[0]>0||x.dR[1]>0)?'<span class="tag y">SOLO UN AÑO</span>':'<span class="tag r">EMPEORA</span>';
    hf+=`<tr${base?' class="best"':''}><td>${x.nombre}</td><td class="n ${cls(a.R)}">${sg(a.R)}</td><td class="n ${cls(base?0:x.dR[0])}">${base?'':sg(x.dR[0])}</td><td class="n ${cls(b.R)}">${sg(b.R)}</td><td class="n ${cls(base?0:x.dR[1])}">${base?'':sg(x.dR[1])}</td><td class="n">${sg(a.R_avg,3)} · ${sg(b.R_avg,3)}</td><td class="n">−${fmt(a.mdd,1)}% · −${fmt(b.mdd,1)}%</td><td>${ver}</td></tr>`});
  $('#t-a-filtros').innerHTML=hf;
  // riesgo
  const best=A.riesgo.find(r=>r.nombre.startsWith('1%, baja a 0,5% con caída ≥ 5%'));
  $('#t-a-riesgo').innerHTML='<tr><th>Regla de tamaño</th><th class="n">2025 rend.</th><th class="n">2025 caída máx.</th><th class="n">2026 rend.</th><th class="n">2026 caída máx.</th></tr>'+
    A.riesgo.map(r=>`<tr${r===best?' class="best"':''}><td>${r.nombre}</td><td class="n ${cls(r['2025'].ret)}">${sg(r['2025'].ret)}%</td><td class="n">−${fmt(r['2025'].mdd)}%</td><td class="n ${cls(r['2026'].ret)}">${sg(r['2026'].ret)}%</td><td class="n">−${fmt(r['2026'].mdd)}%</td></tr>`).join('');
  // eventos
  const REC2={'CPI (USD)':'Mantener excluido. La propuesta de operarlo de 07:00 a 07:59 no se valida: en 2025 pierde.','CPI (GBP)':'Mantener excluido. La propuesta de habilitarlo no se valida: en 2025 pierde.',
    'NFP (USD)':'Mantener excluido. Gana en 2025 y no en 2026; el riesgo de salto de precio a las 08:30 no compensa.','Feriado EE. UU.':'Mantener excluido. En 2025 pierde.',
    'Feriado solo Europa continental':`Mantener. Los días solo con feriado europeo dan ${sg(A.europa_pura['2025'].R)}R en 2025 y ${sg(A.europa_pura['2026'].R)}R en 2026: no es consistente.`,
    'Feriado Reino Unido':'Mantener excluido. Resultado nulo con los dos años juntos.','Discurso Trump / Warsh':'Mantener excluido. Resultado nulo y riesgo impredecible.',
    'PIB final (USD)':'Mantener excluido. Pierde los dos años.','BCE: entrada después de 08:00':'Mantener la regla.','ADP: entrada 08:05–08:18':'Mantener el bloqueo.','Core PCE: entrada 08:20–08:33':'Mantener el bloqueo.'};
  $('#t-a-ev').innerHTML='<tr><th>Evento</th><th class="n">2025</th><th class="n">2026</th><th class="n">2 años</th><th>Recomendación</th></tr>'+
    A.eventos.map(e=>{const a=e.por_anio['2025'], b=e.por_anio['2026'];return `<tr><td>${e.cat}</td><td class="n">${a?`<span class="${cls(a.R)}">${sg(a.R)}R</span> (${a.n})`:'—'}</td><td class="n">${b?`<span class="${cls(b.R)}">${sg(b.R)}R</span> (${b.n})`:'—'}</td><td class="n"><span class="${cls(e.R)}">${sg(e.R)}R</span> (${e.n})</td><td style="color:var(--fg2);min-width:240px">${REC2[e.cat]||''}</td></tr>`}).join('');
  $('#t-a-parc').innerHTML='<tr><th>Días de</th><th class="n">2025</th><th class="n">2026</th><th class="n">2 años</th><th>Lectura</th></tr>'+
    A.parciales.map(p=>{const a=p.por_anio['2025'], b=p.por_anio['2026'];const lec=p.evento==='Core PCE'?'La idea de operar solo de 07:00 a 07:59 los días de Core PCE salió de 2026 y no se repite en 2025: no aplicarla.':p.evento==='ADP'?'Buen resultado los dos años con el bloqueo actual.':'Muestra muy chica.';
      return `<tr><td>${p.evento}</td><td class="n">${a?`<span class="${cls(a.R)}">${sg(a.R)}R</span> (${a.n})`:'—'}</td><td class="n">${b?`<span class="${cls(b.R)}">${sg(b.R)}R</span> (${b.n})`:'—'}</td><td class="n"><span class="${cls(p.R)}">${sg(p.R)}R</span> (${p.n})</td><td style="color:var(--fg2);min-width:240px">${lec}</td></tr>`}).join('');
  // recomendación
  const k2=A.kelly2, semP=T.R_week*0.9;
  $('#a-reco').innerHTML=[
    ['g','MODELO',`<b>Operar solo Envolvente.</b> Es el mejor de los tres en los dos años. START no tiene ventaja en ninguno (${sg(A.dos_anios.start.R)}R con los dos años juntos) y el combinado rinde menos que Envolvente sola en 2025 y en 2026.`],
    ['g','REGLAS',`<b>No cambiar reglas de entrada, horario, días ni calendario.</b> De los ${A.filtros.length-1} filtros probados, ninguno mejora los dos años. Las propuestas de calendario que salieron de 2026 (CPI GBP, CPI USD con ventana, Core PCE con ventana) no se validan en 2025. Lo más eficiente es no agregar complejidad.`],
    ['g','RIESGO',`<b>1% por operación, bajando a 0,5% cuando la caída desde el máximo llegue a 5%</b>, y volviendo a 1% en un nuevo máximo. Es la única regla probada que mejora los dos años: en 2025 sube el rendimiento de ${sg(A.riesgo[0]['2025'].ret)}% a ${sg(best['2025'].ret)}% y baja la caída de −${fmt(A.riesgo[0]['2025'].mdd)}% a −${fmt(best['2025'].mdd)}%; en 2026 no cambia nada (${sg(best['2026'].ret)}%).`],
    ['y','LÍMITES',`<b>Límite diario: 2 operaciones.</b> En los dos años nunca hubo más, así que formalizarlo no cuesta nada. <b>No cortar el día después de la primera pérdida</b>: la segunda operación es positiva los dos años (cortar costaría ${sg(Fk('stop1').dR[0])}R en 2025 y ${sg(Fk('stop1').dR[1])}R en 2026). Un límite semanal de −2R no aporta. Límite de cuenta: pausar y revisar si la caída llega a −${fmt(Math.ceil(T.mc95),0)}% (percentil 95 de los dos años).`],
    ['y','A DESARROLLAR',`<b>Filtro de tendencia.</b> Solo operar a favor de la tendencia de 20 días da un R por operación parecido los dos años (${sg(Fk('tend')['2025'].R_avg,2)}R y ${sg(Fk('tend')['2026'].R_avg,2)}R) y una caída máxima de −${fmt(Fk('tend')['2025'].mdd,1)}% en los dos, pero en 2026 deja afuera ${sg(-Fk('tend').dR[1])}R. Vale la pena programarlo bien en Pine Script (por ejemplo, precio sobre o bajo la media de 20 días en diario) y probarlo, pero todavía no aplicarlo.`],
    ['y','EXPECTATIVA',`<b>Qué esperar.</b> Con los dos años juntos: ${sg(T.R_avg,2)}R por operación y ${sg(T.R_week,2)}R por semana. Con 1% de riesgo son ≈${fmt(semP,2)}% por semana, alrededor de ${fmt(semP*52,0)}% al año, con caídas que pueden llegar a −${fmt(T.mc95,0)}%. Kelly con los dos años: ${fmt(k2*100,1)}%; el 1% equivale a 1/${fmt(k2*100,0)} de Kelly.`],
  ].map(([c,t,x])=>`<li><span class="tag ${c}">${t}</span><p>${x}</p></li>`).join('');
  $('#a-plan').innerHTML=[
    `<b>Modelo y reglas:</b> operar solo Envolvente, ventana de 07:00 a 09:01 y los calendarios de restricciones tal como están.`,
    `<b>Tamaño:</b> 1% por operación; 0,5% mientras la caída desde el máximo sea de 5% o más; volver a 1% al marcar un nuevo máximo.`,
    `<b>Límites:</b> máximo 2 operaciones por día. Pausa y revisión si la caída llega a −${fmt(Math.ceil(T.mc95),0)}%.`,
    `<b>START:</b> fuera del capital real; registrar sus señales en demo si querés seguir desarrollándolo.`,
    `<b>Próximo estudio:</b> programar en Pine Script un filtro de tendencia diario y correrlo sobre 2025 y 2026.`,
    `<b>Seguimiento:</b> actualizar este informe cada mes con las operaciones nuevas y comparar contra la expectativa de los dos años (${sg(T.R_avg,2)}R por operación).`,
  ].map(x=>`<li>${x}</li>`).join('');
}
