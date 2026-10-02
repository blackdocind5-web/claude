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
  const LIM=DATA.muestra!=='sin_limite', FL=A.filtros.filter(f=>!(LIM&&f.key==='sesion'));
  const Fk=k=>A.filtros.find(f=>f.key===k), d5=A.detalle['2025'], d6=A.detalle['2026'];
  const chg=(a,b)=>((b-a)/a*100);
  const sgn=v=>v>0?1:v<0?-1:0;
  const lec2=(a,b,pos,neg,mix)=>sgn(a)>0&&sgn(b)>0?pos:sgn(a)<0&&sgn(b)<0?neg:mix;
  const consistente=T.p>=95;
  $('#a-verdict').innerHTML=`<span class="eyebrow">Veredicto</span>
    <div class="big">${E5.R_tot>0&&E6.R_tot>0?`Envolvente gana los dos años, ${Math.abs(E5.R_tot-E6.R_tot)>5?'pero con mucha diferencia entre uno y otro':'con resultados parecidos'}. Con los dos años juntos el sistema es ${consistente?'rentable y estadísticamente consistente':'rentable, pero todavía sin firmeza estadística'}.`:'Envolvente no gana los dos años: revisar con cuidado antes de operar.'}</div>
    <p><b>2025: ${sg(E5.R_tot)}R</b> (factor ${fmt(E5.pf)}, win rate ${fmt(E5.wr,1)}%, caída máxima −${fmt(E5.mdd_pct)}%) contra <b>2026: ${sg(E6.R_tot)}R</b> (factor ${fmt(E6.pf)}, win rate ${fmt(E6.wr,1)}%, −${fmt(E6.mdd_pct)}%). ${[E5,E6].every(x=>x.pf>1.2)?'Los dos años superan el criterio de validación (factor de ganancias mayor a 1,2).':`${[['2025',E5],['2026',E6]].filter(([,x])=>x.pf<=1.2).map(([y])=>y).join(' y ')} no alcanza el criterio de validación (factor de ganancias mayor a 1,2).`} <b>Con los dos años juntos</b>: ${T.n} operaciones, ${sg(T.R)}R, factor ${fmt(T.pf)}, win rate ${fmt(T.wr,1)}% y expectativa positiva en ${fmt(T.p,1)}% de 5.000 simulaciones. La expectativa realista es la de los dos años juntos.</p>`;
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
  const ch5=chg(d5.precio.ini,d5.precio.fin), ch6=chg(d6.precio.ini,d6.precio.fin);
  const filas=[
    ['Compras',d5.dir.Compras,d6.dir.Compras],['Ventas',d5.dir.Ventas,d6.dir.Ventas],
    ['A favor de la tendencia de 20 días',t5,t6],['En contra de la tendencia de 20 días',c5,c6],
    ['Primera operación del día',d5.orden['1.ª del día'],d6.orden['1.ª del día']],['Segunda operación o más del día',d5.orden['2.ª o más del día'],d6.orden['2.ª o más del día']],
    ['Entradas 07:00–07:59',d5.hora['07:00–07:59'],d6.hora['07:00–07:59']],['Entradas 08:00–08:59',d5.hora['08:00–08:59'],d6.hora['08:00–08:59']],
    ['Operaciones de más de 30 minutos',d5.dur['Más de 30 min'],d6.dur['Más de 30 min']],
  ];
  const C=[
    ['Precio del oro en el período',`${fmt(d5.precio.ini,0)} → ${fmt(d5.precio.fin,0)} (${sg(ch5,0)}%)`,`${fmt(d6.precio.ini,0)} → ${fmt(d6.precio.fin,0)} (${sg(ch6,0)}%), rango ${fmt(d6.precio.mn,0)}–${fmt(d6.precio.mx,0)}`,`2025: tendencia ${ch5>20?'alcista fuerte':ch5<-20?'bajista fuerte':'moderada'}. 2026: ${Math.abs(ch6)<20?'mercado de ida y vuelta':'tendencia marcada'}.`],
    ['Win rate y payoff',`${fmt(E5.wr,1)}% · payoff ${fmt(E5.payoff)}`,`${fmt(E6.wr,1)}% · payoff ${fmt(E6.payoff)}`,Math.abs(E5.payoff-E6.payoff)<0.1?'El payoff es casi igual: la diferencia está en el acierto.':'Cambian el acierto y el payoff.'],
    ...filas.map(([n,a,b])=>[n,g(a),g(b),lec2(a.R,b.R,'Positivo los dos años.','Negativo los dos años.',`${a.R>b.R?'Mejor en 2025':'Mejor en 2026'}: no se repite.`)]),
  ];
  $('#t-a-causas').innerHTML='<tr><th>Factor</th><th>2025</th><th>2026</th><th>Lectura</th></tr>'+C.map(r=>`<tr><td>${r[0]}</td><td class="mono" style="white-space:nowrap">${r[1]}</td><td class="mono" style="white-space:nowrap">${r[2]}</td><td style="color:var(--fg2);min-width:220px">${r[3]}</td></tr>`).join('');
  drawMonths('#c-a-mes');
  const peor=y=>Object.entries(A.meses[y]).sort((a,b)=>a[1]-b[1])[0];
  const m5=peor('2025'), m6=peor('2026');
  const same=filas.filter(([,a,b])=>sgn(a.R)===sgn(b.R)&&sgn(a.R)!==0).map(([n,a])=>`${n.toLowerCase()} (${a.R>0?'positivo':'negativo'})`);
  const diff=filas.filter(([,a,b])=>sgn(a.R)!==sgn(b.R)).map(([n])=>n.toLowerCase());
  $('#a-causas-txt').innerHTML=[
    ['y','TENDENCIA',`<b>El tipo de mercado pesa.</b> En 2025 el oro se movió ${sg(ch5,0)}% y en 2026 ${sg(ch6,0)}%. Las operaciones en contra de la tendencia de 20 días dieron ${sg(c5.R)}R en 2025 y ${sg(c6.R)}R en 2026; a favor, ${sg(t5.R)}R y ${sg(t6.R)}R.`],
    ['y','VOLATILIDAD',`<b>Los peores meses:</b> ${m5[0]} de 2025 (${sg(m5[1])}R${m5[0]==='Abr'?', en plena volatilidad por los anuncios de aranceles':''}) y ${m6[0]} de 2026 (${sg(m6[1])}R).`],
    ['g','LO QUE SE MANTIENE',same.length?`<b>Se repite en los dos años:</b> ${same.join(', ')}.`:'<b>Ningún factor tiene el mismo signo los dos años.</b>'],
    ['r','LO QUE NO SE MANTIENE',diff.length?`<b>Cambia de un año a otro:</b> ${diff.join(', ')}. Por eso no conviene recortar horarios ni direcciones mirando un solo año.`:'<b>Todos los factores mantienen el signo.</b>'],
  ].map(([c,t,x])=>`<li><span class="tag ${c}">${t}</span><p>${x}</p></li>`).join('');
  // filtros
  let hf='<tr><th>Filtro (Envolvente)</th><th class="n">2025 R</th><th class="n">Dif.</th><th class="n">2026 R</th><th class="n">Dif.</th><th class="n">R/op. 25 · 26</th><th class="n">Caída máx. 25 · 26</th><th>Veredicto</th></tr>';
  FL.forEach(x=>{const a=x['2025'], b=x['2026'], base=x.key==='base';
    const ver=base?'<span class="tag n">REFERENCIA</span>':x.robusto?'<span class="tag g">MEJORA LOS DOS AÑOS</span>':(x.dR[0]>0||x.dR[1]>0)?'<span class="tag y">SOLO UN AÑO</span>':'<span class="tag r">EMPEORA</span>';
    hf+=`<tr${base?' class="best"':''}><td>${x.nombre}</td><td class="n ${cls(a.R)}">${sg(a.R)}</td><td class="n ${cls(base?0:x.dR[0])}">${base?'':sg(x.dR[0])}</td><td class="n ${cls(b.R)}">${sg(b.R)}</td><td class="n ${cls(base?0:x.dR[1])}">${base?'':sg(x.dR[1])}</td><td class="n">${sg(a.R_avg,3)} · ${sg(b.R_avg,3)}</td><td class="n">−${fmt(a.mdd,1)}% · −${fmt(b.mdd,1)}%</td><td>${ver}</td></tr>`});
  $('#t-a-filtros').innerHTML=hf;
  const rob=FL.filter(x=>x.robusto);
  // riesgo: la regla con mejor relación rendimiento/caída en el peor de los dos años
  const ratio=r=>Math.min(r['2025'].ret/Math.max(r['2025'].mdd,0.1),r['2026'].ret/Math.max(r['2026'].mdd,0.1));
  const base0=A.riesgo[0], best=[...A.riesgo].sort((a,b)=>ratio(b)-ratio(a))[0];
  const mejoraAmbos=A.riesgo.filter(r=>r!==base0&&r['2025'].ret>=base0['2025'].ret&&r['2026'].ret>=base0['2026'].ret);
  $('#t-a-riesgo').innerHTML='<tr><th>Regla de tamaño</th><th class="n">2025 rend.</th><th class="n">2025 caída máx.</th><th class="n">2026 rend.</th><th class="n">2026 caída máx.</th></tr>'+
    A.riesgo.map(r=>`<tr${r===best?' class="best"':''}><td>${r.nombre}</td><td class="n ${cls(r['2025'].ret)}">${sg(r['2025'].ret)}%</td><td class="n">−${fmt(r['2025'].mdd)}%</td><td class="n ${cls(r['2026'].ret)}">${sg(r['2026'].ret)}%</td><td class="n">−${fmt(r['2026'].mdd)}%</td></tr>`).join('');
  // eventos
  const rec2=e=>{const a=e.por_anio['2025'], b=e.por_anio['2026'];
    if(/BCE/.test(e.cat)) return 'Mantener la regla.'; if(/ADP|Core PCE/.test(e.cat)) return 'Mantener el bloqueo.';
    if(e.cat==='Feriado solo Europa continental') return `Mantener. Los días solo con feriado europeo dan ${sg(A.europa_pura['2025'].R)}R en 2025 y ${sg(A.europa_pura['2026'].R)}R en 2026${sgn(A.europa_pura['2025'].R)===sgn(A.europa_pura['2026'].R)?'':': no es consistente'}.`;
    if(a&&b&&a.R>0&&b.R>0) return `Gana los dos años con pocas operaciones (${e.n}). Mantener excluido y seguir observando antes de habilitarlo.`;
    if(e.R<0) return 'Mantener excluido. Pierde con los dos años juntos.';
    return 'Mantener excluido. Gana un año y pierde el otro: no es consistente.';};
  $('#t-a-ev').innerHTML='<tr><th>Evento</th><th class="n">2025</th><th class="n">2026</th><th class="n">2 años</th><th>Recomendación</th></tr>'+
    A.eventos.map(e=>{const a=e.por_anio['2025'], b=e.por_anio['2026'];return `<tr><td>${e.cat}</td><td class="n">${a?`<span class="${cls(a.R)}">${sg(a.R)}R</span> (${a.n})`:'—'}</td><td class="n">${b?`<span class="${cls(b.R)}">${sg(b.R)}R</span> (${b.n})`:'—'}</td><td class="n"><span class="${cls(e.R)}">${sg(e.R)}R</span> (${e.n})</td><td style="color:var(--fg2);min-width:240px">${rec2(e)}</td></tr>`}).join('');
  $('#t-a-parc').innerHTML='<tr><th>Días de</th><th class="n">2025</th><th class="n">2026</th><th class="n">2 años</th><th>Lectura</th></tr>'+
    A.parciales.map(p=>{const a=p.por_anio['2025'], b=p.por_anio['2026'];const lec=p.n<8?'Muestra muy chica.':lec2(a?a.R:0,b?b.R:0,'Positivo los dos años con la regla actual.','Negativo los dos años: revisar la regla.','Cambia de un año a otro: mantener la regla actual.');
      return `<tr><td>${p.evento}</td><td class="n">${a?`<span class="${cls(a.R)}">${sg(a.R)}R</span> (${a.n})`:'—'}</td><td class="n">${b?`<span class="${cls(b.R)}">${sg(b.R)}R</span> (${b.n})`:'—'}</td><td class="n"><span class="${cls(p.R)}">${sg(p.R)}R</span> (${p.n})</td><td style="color:var(--fg2);min-width:240px">${lec}</td></tr>`}).join('');
  // recomendación
  const k2=A.kelly2, semP=T.R_week*0.9, envBest=['2025','2026'].every(y=>DATA[y].envolvente.R_tot>=DATA[y].combinado.R_tot&&DATA[y].envolvente.R_tot>=DATA[y].start.R_tot);
  const ses=Fk('sesion'), stop1=Fk('stop1'), tend=Fk('tend');
  const riesgoTxt=mejoraAmbos.length?`<b>${mejoraAmbos[0].nombre}.</b> Es la única regla probada que mejora el rendimiento de los dos años.`:`<b>Ninguna regla de tamaño mejora el rendimiento de los dos años.</b> La que mejor relación rendimiento/caída da en el peor año es “${best.nombre}” (2025: ${sg(best['2025'].ret)}% con −${fmt(best['2025'].mdd)}%; 2026: ${sg(best['2026'].ret)}% con −${fmt(best['2026'].mdd)}%). Si la caída de −${fmt(base0['2025'].mdd)}% del 1% fijo es tolerable, el 1% fijo rinde más.`;
  $('#a-reco').innerHTML=[
    [envBest?'g':'y','MODELO',envBest?`<b>Operar solo Envolvente.</b> Es el mejor de los tres en los dos años. START da ${sg(A.dos_anios.start.R)}R con los dos años juntos y el combinado rinde menos que Envolvente sola.`:'<b>Revisar el modelo:</b> Envolvente no es el mejor los dos años.'],
    ['g','REGLAS',rob.length?`<b>Solo ${rob.length===1?'un filtro mejora':rob.length+' filtros mejoran'} los dos años:</b> ${rob.map(x=>`${x.nombre} (${sg(x.dR[0])}R y ${sg(x.dR[1])}R)`).join('; ')}. El resto de los ${FL.length-1} filtros probados no se sostiene. Aplicar solo lo que mejore los dos años y tenga una razón de mercado.`:`<b>No cambiar reglas de entrada, horario, días ni calendario.</b> De los ${FL.length-1} filtros probados, ninguno mejora los dos años.`],
    LIM?['g','LÍMITE POR SESIÓN',`<b>El límite de 1 TP o 2 SL por sesión ya está en esta muestra.</b> Cortar el día tras la primera pérdida: ${sg(stop1.dR[0])}R y ${sg(stop1.dR[1])}R contra las reglas actuales.`]:['y','LÍMITE POR SESIÓN',`<b>Límite de 1 TP o 2 SL por sesión:</b> ${sg(ses.dR[0])}R en 2025 y ${sg(ses.dR[1])}R en 2026 contra operar todo. ${ses.robusto?'Mejora los dos años: mantenerlo.':`${ses.dR[0]+ses.dR[1]>0?`Con los dos años juntos suma ${sg(ses.dR[0]+ses.dR[1])}R, pero no mejora los dos años.`:'No mejora.'}`} Cortar el día tras la primera pérdida: ${sg(stop1.dR[0])}R y ${sg(stop1.dR[1])}R.`],
    ['y','RIESGO',riesgoTxt+` Pausar y revisar si la caída llega a −${fmt(Math.ceil(T.mc95),0)}% (percentil 95 de los dos años).`],
    ['y','A DESARROLLAR',`<b>Filtro de tendencia.</b> Solo a favor de la tendencia de 20 días: ${sg(tend['2025'].R_avg,2)}R y ${sg(tend['2026'].R_avg,2)}R por operación, caída máxima −${fmt(tend['2025'].mdd,1)}% y −${fmt(tend['2026'].mdd,1)}%; cambia el R total en ${sg(tend.dR[0])}R y ${sg(tend.dR[1])}R. Vale la pena programarlo bien en Pine Script (media de 20 días en diario) y probarlo antes de aplicarlo.`],
    ['y','EXPECTATIVA',`<b>Qué esperar.</b> Con los dos años juntos: ${sg(T.R_avg,2)}R por operación y ${sg(T.R_week,2)}R por semana. Con 1% de riesgo son ≈${fmt(semP,2)}% por semana, alrededor de ${fmt(semP*52,0)}% al año, con caídas que pueden llegar a −${fmt(T.mc95,0)}%. Kelly con los dos años: ${fmt(k2*100,1)}%; el 1% equivale a 1/${fmt(k2*100,0)} de Kelly.`],
  ].map(([c,t,x])=>`<li><span class="tag ${c}">${t}</span><p>${x}</p></li>`).join('');
  $('#a-plan').innerHTML=[
    `<b>Modelo y reglas:</b> ${envBest?'operar solo Envolvente':'revisar el modelo'}, ventana de 07:00 a 09:01 y los calendarios de restricciones tal como están${rob.length?`; evaluar ${rob.map(x=>x.nombre.toLowerCase()).join(' y ')}`:''}.`,
    `<b>Tamaño:</b> ${mejoraAmbos.length?mejoraAmbos[0].nombre:'1% por operación'}.`,
    `<b>Límites:</b> ${LIM?'mantener el límite de 1 TP o 2 SL por sesión':ses.robusto?'mantener 1 TP o 2 SL por sesión':'decidir el límite por sesión según la tabla de filtros'}. Pausa y revisión si la caída llega a −${fmt(Math.ceil(T.mc95),0)}%.`,
    `<b>START:</b> fuera del capital real; registrar sus señales en demo si querés seguir desarrollándolo.`,
    `<b>Próximo estudio:</b> programar en Pine Script un filtro de tendencia diario y correrlo sobre 2025 y 2026.`,
    `<b>Seguimiento:</b> actualizar este informe cada mes y comparar contra la expectativa de los dos años (${sg(T.R_avg,2)}R por operación).`,
  ].map(x=>`<li>${x}</li>`).join('');
}
