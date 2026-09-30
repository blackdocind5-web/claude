/* ---------- Comparativa y recomendación ---------- */
const MODS=[['envolvente','Envolvente','--s-env'],['combinado','Envolvente + START','--s-comb'],['start','START','--s-start']];
function drawMulti(host){
  const box=$(host); box.innerHTML='';
  const W=Math.max(320,box.clientWidth), H=320, M={l:52,r:120,t:12,b:24};
  if(W<560) M.r=14;
  const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Curvas de capital de los tres modelos'},box);
  const S=MODS.map(([k,n,c])=>({k,n,c:css(c),p:DATA[k].curve.map(x=>({t:parseT(x.t).getTime(),eq:x.eq}))}));
  const a=Math.min(...S.map(s=>s.p[0].t)), b=Math.max(...S.map(s=>s.p[s.p.length-1].t));
  let mn=Math.min(1000,...S.flatMap(s=>s.p.map(p=>p.eq))), mx=Math.max(1000,...S.flatMap(s=>s.p.map(p=>p.eq))); const pad=(mx-mn)*0.06; mn-=pad; mx+=pad;
  const X=t=>M.l+(t-a)/(b-a)*(W-M.l-M.r), Y=v=>M.t+(mx-v)/(mx-mn)*(H-M.t-M.b);
  niceTicks(mn,mx,5).t.forEach(v=>{el('line',{x1:M.l,x2:W-M.r,y1:Y(v),y2:Y(v),class:'gl'},svg);el('text',{x:M.l-8,y:Y(v)+4,'text-anchor':'end',class:'ax'},svg).textContent=fmt(v,0)});
  monthGrid(svg,X,M,H,a,b);
  el('line',{x1:M.l,x2:W-M.r,y1:Y(1000),y2:Y(1000),class:'zero','stroke-dasharray':'3 4'},svg);
  const ends=[];
  S.forEach(s=>{el('path',{d:'M'+s.p.map(p=>`${X(p.t)},${Y(p.eq)}`).join(' L'),fill:'none',stroke:s.c,'stroke-width':2,'stroke-linejoin':'round'},svg);
    const L=s.p[s.p.length-1]; el('circle',{cx:X(L.t),cy:Y(L.eq),r:4,fill:s.c,stroke:css('--panel'),'stroke-width':2},svg); ends.push({s,x:X(L.t),y:Y(L.eq),v:L.eq});});
  if(M.r>50){ends.sort((p,q)=>p.y-q.y);for(let i=1;i<ends.length;i++)if(ends[i].y-ends[i-1].y<16)ends[i].y=ends[i-1].y+16;
    ends.forEach(e=>{const t=el('text',{x:W-M.r+10,y:e.y+4,class:'lbl'},svg);t.textContent=`${e.s.n} ${fmt(e.v,0)}`;})}
  const cross=el('line',{y1:M.t,y2:H-M.b,stroke:css('--fg3'),'stroke-dasharray':'2 3',visibility:'hidden'},svg);
  const hit=el('rect',{x:M.l,y:0,width:W-M.l-M.r,height:H,fill:'transparent'},svg);
  hit.addEventListener('pointermove',e=>{const r=svg.getBoundingClientRect();const sx=(e.clientX-r.left)*W/r.width;const t=a+(sx-M.l)/(W-M.l-M.r)*(b-a);
    cross.setAttribute('x1',sx);cross.setAttribute('x2',sx);cross.setAttribute('visibility','visible');
    const lines=S.map(s=>{let v=s.p[0].eq;for(const p of s.p){if(p.t<=t)v=p.eq;else break}return `<span style="color:${s.c}">■</span> ${s.n}: ${fmt(v)} USD`});
    showTip(box,dmy(new Date(t))+'<br>'+lines.join('<br>'),e.clientX-r.left,e.clientY-r.top)});
  hit.addEventListener('pointerleave',()=>{cross.setAttribute('visibility','hidden');hideTip(box)});
}
function drawCI(host){
  const box=$(host); box.innerHTML='';
  const W=Math.max(300,box.clientWidth), rowH=46, M={l:130,r:20,t:10,b:28}, H=M.t+M.b+rowH*MODS.length;
  const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Intervalo de confianza del R promedio'},box);
  const lo=Math.min(...MODS.map(([k])=>DATA[k].exp_ci[0]),0)-0.05, hi=Math.max(...MODS.map(([k])=>DATA[k].exp_ci[1]),0)+0.05;
  const X=v=>M.l+(v-lo)/(hi-lo)*(W-M.l-M.r);
  niceTicks(lo,hi,5).t.forEach(v=>{el('line',{x1:X(v),x2:X(v),y1:M.t,y2:H-M.b,class:'gl'},svg);el('text',{x:X(v),y:H-8,'text-anchor':'middle',class:'ax'},svg).textContent=sg(v,1)+'R'});
  el('line',{x1:X(0),x2:X(0),y1:M.t,y2:H-M.b,class:'zero'},svg);
  MODS.forEach(([k,n,c],i)=>{const d=DATA[k], y=M.t+rowH*i+rowH/2, col=css(c);
    el('text',{x:M.l-10,y:y+4,'text-anchor':'end',class:'lbl'},svg).textContent=n;
    el('line',{x1:X(d.exp_ci[0]),x2:X(d.exp_ci[1]),y1:y,y2:y,stroke:col,'stroke-width':6,'stroke-linecap':'round',opacity:.45},svg);
    el('circle',{cx:X(d.R_avg),cy:y,r:6,fill:col,stroke:css('--panel'),'stroke-width':2},svg);
    const hit=el('rect',{x:M.l,y:y-rowH/2,width:W-M.l-M.r,height:rowH,fill:'transparent'},svg);
    hit.addEventListener('pointermove',e=>{const r=svg.getBoundingClientRect();showTip(box,`${n}<br>R promedio ${sg(d.R_avg,3)}R<br>IC 95%: ${sg(d.exp_ci[0],3)} a ${sg(d.exp_ci[1],3)}R<br>P(expectativa &gt; 0): ${fmt(d.p_exp_pos,1)}%`,e.clientX-r.left,e.clientY-r.top)});
    hit.addEventListener('pointerleave',()=>hideTip(box));});
}
function cmpTable(id,groups){
  // groups: [[titulo,[ [etiqueta, fn(d)->valor, formato(v)->html, mejor:'max'|'min'|null ], ...]], ...]
  let h='<tr><th>Métrica</th>'+MODS.map(([k,n,c])=>`<th class="n"><i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:var(${c});margin-right:6px"></i>${n}</th>`).join('')+'</tr>';
  groups.forEach(([g,rows])=>{h+=`<tr class="grp"><td colspan="4">${g}</td></tr>`;
    rows.forEach(([lab,f,fm,best])=>{const vals=MODS.map(([k])=>f(DATA[k]));const ok=vals.filter(v=>v!=null);
      const bv=best==='max'?Math.max(...ok):best==='min'?Math.min(...ok):null;
      h+=`<tr><td>${lab}</td>`+vals.map(v=>`<td class="n${best&&v===bv?' best':''}">${fm(v)}</td>`).join('')+'</tr>';});});
  $(id).innerHTML=h;
}
function renderCompare(){
  const E=DATA.envolvente, C=DATA.combinado, S=DATA.start, O=DATA.solapamiento;
  const kelly=E.wr/100-(1-E.wr/100)/E.payoff;
  $('#verdict').innerHTML=`<span class="eyebrow">Veredicto</span>
    <div class="big">Operar solo el patrón envolvente. START queda fuera del capital real hasta que demuestre ventaja.</div>
    <p>Con la misma muestra y las mismas reglas, <b>Envolvente sola gana ${sg(E.R_tot)}R</b> (${sg(E.R_week)}R por semana) con una caída máxima de −${fmt(E.mdd_pct)}%. <b>Sumarle START la empeora</b>: ${sg(C.R_tot)}R y −${fmt(C.mdd_pct)}%. <b>START sola pierde ${sg(S.R_tot)}R</b> y su caída de −${fmt(S.mdd_pct)}% sigue sin recuperarse. Envolvente es además el único de los tres con ventaja estadísticamente consistente: la expectativa sale positiva en ${fmt(E.p_exp_pos,1)}% de 5.000 simulaciones.</p>`;
  const pct=v=>v==null?'—':sg(v)+'%', R=v=>`<span class="${cls(v)}">${sg(v)}R</span>`, usd=v=>`<span class="${cls(v)}">${sg(v)}</span>`, num=v=>v==null?'—':fmt(v), neg=v=>`−${fmt(v)}%`;
  cmpTable('#t-cmp',[
    ['Rendimiento',[
      ['PyG total (USD)',d=>d.pnl,usd,'max'],['PyG total (%)',d=>d.ret_pct,pct,'max'],['R total',d=>d.R_tot,R,'max'],
      ['R promedio por operación',d=>d.R_avg,v=>`<span class="${cls(v)}">${sg(v,3)}R</span>`,'max'],['R promedio por semana',d=>d.R_week,R,'max'],
      ['Operaciones válidas',d=>d.n,v=>v,null],['Operaciones por semana',d=>d.trades_week,num,null]]],
    ['Calidad de las operaciones',[
      ['Win rate',d=>d.wr,v=>fmt(v)+'%','max'],['Factor de ganancias',d=>d.pf,num,'max'],['Payoff (ganancia media / pérdida media)',d=>d.payoff,num,'max'],
      ['Win rate de equilibrio',d=>100/(1+d.payoff),v=>fmt(v,1)+'%','min']]],
    ['Riesgo',[
      ['Caída máxima',d=>d.mdd_pct,neg,'min'],['Caída máxima esperable (Monte Carlo, p95)',d=>d.mc_dd95,neg,'min'],
      ['Días de pico a nuevo máximo',d=>d.mdd_total_days,v=>v==null?'<span class="neg">Sin recuperar</span>':v+' días','min'],
      ['Racha perdedora más larga',d=>d.streak_l,v=>v+' ops.','min'],['Semanas positivas',d=>100*d.wk_pos/(d.wk_pos+d.wk_neg),v=>fmt(v,1)+'%','max']]],
    ['Ajustado por riesgo',[
      ['Sharpe (anualizado)',d=>d.sharpe,num,'max'],['Sortino (anualizado)',d=>d.sortino,num,'max'],['Calmar',d=>d.calmar,num,'max'],['Factor de recuperación',d=>d.recovery_factor,num,'max']]],
  ]);
  drawMulti('#c-multi');
  $('#t-overlap').innerHTML=`<tr><th>Operaciones válidas</th><th class="n">Cantidad</th><th class="n">R</th></tr>
    <tr><td>Envolvente sola</td><td class="n">${E.n}</td><td class="n pos">${sg(E.R_tot)}</td></tr>
    <tr><td>START sola</td><td class="n">${S.n}</td><td class="n neg">${sg(S.R_tot)}</td></tr>
    <tr><td>Señales iguales en los dos modelos</td><td class="n">${O.ambos}</td><td class="n">—</td></tr>
    <tr><td>Envolvente que el combinado no tomó</td><td class="n">${O.env_fuera_comb}</td><td class="n pos">${sg(O.R_env_fuera_comb)}</td></tr>
    <tr><td>START (sin envolvente) que el combinado sí tomó</td><td class="n">${O.comb_solo_start}</td><td class="n neg">${sg(O.R_comb_solo_start)}</td></tr>
    <tr><td><b>Envolvente + START</b></td><td class="n">${C.n}</td><td class="n pos">${sg(C.R_tot)}</td></tr>`;
  $('#overlap-text').innerHTML=`<p class="note" style="font-size:14px;color:var(--fg2)">El sistema opera <b style="color:var(--fg)">una operación a la vez</b>. Cuando START abre primero, ocupa el lugar de una envolvente que llega después, o el Reset la cierra antes de tiempo.</p>
    <p class="note" style="font-size:14px;color:var(--fg2)">En esta muestra, el combinado <b style="color:var(--fg)">dejó afuera ${O.env_fuera_comb} envolventes que sumaban ${sg(O.R_env_fuera_comb)}R</b> y a cambio <b style="color:var(--fg)">tomó ${O.comb_solo_start} operaciones START que sumaron ${sg(O.R_comb_solo_start)}R</b>. Esas dos cosas explican casi toda la diferencia entre ${sg(E.R_tot)}R y ${sg(C.R_tot)}R; el resto son diferencias de tamaño por el interés compuesto.</p>
    <p class="note" style="font-size:14px;color:var(--fg2)">START no aporta diversificación: opera el mismo activo, en la misma sesión y compite por el mismo lugar. Solo sumaría si tuviera ventaja propia, y en esta muestra no la tiene.</p>`;
  cmpTable('#t-stat',[['Pruebas sobre el R por operación',[
    ['Estadístico t',d=>d.t_stat,num,'max'],['P(expectativa > 0)',d=>d.p_exp_pos,v=>fmt(v,1)+'%','max'],
    ['IC 95% del R promedio',d=>d.exp_ci,v=>`${sg(v[0],2)} a ${sg(v[1],2)}R`,null]]]]);
  drawCI('#c-ci');
  let hv='<tr><th>Modelo · variante</th><th class="n">Ops.</th><th class="n">Win rate</th><th class="n">Factor</th><th class="n">R total</th><th class="n">R/op.</th><th class="n">R/semana</th><th class="n">Caída máx.</th></tr>';
  MODS.forEach(([k,n])=>{hv+=`<tr class="grp"><td colspan="8">${n}</td></tr>`+DATA[k].variantes.map(v=>`<tr><td>${v.nombre}</td><td class="n">${v.n}</td><td class="n">${fmt(v.wr,1)}%</td><td class="n">${fmt(v.pf)}</td><td class="n ${cls(v.R)}">${sg(v.R)}</td><td class="n ${cls(v.R_avg)}">${sg(v.R_avg,3)}</td><td class="n ${cls(v.R_week)}">${sg(v.R_week)}</td><td class="n">−${fmt(v.mdd)}%</td></tr>`).join('')});
  $('#t-var').innerHTML=hv;
  const rk=[0.5,1,1.5,2];
  $('#t-risk').innerHTML='<tr><th>Riesgo por operación</th><th class="n">R en %</th><th class="n">Rend. semanal esperado</th><th class="n">Rend. del período</th><th class="n">Caída máx. histórica</th><th class="n">Caída máx. esperable (p95)</th></tr>'+
    rk.map(r=>`<tr${r===1?' class="best"':''}><td>${fmt(r,1)}%${r===1?' (actual)':''}</td><td class="n">${fmt(0.9*r,2)}%</td><td class="n pos">${sg(E.R_week*0.9*r)}%</td><td class="n pos">${sg(E.R_tot*0.9*r,1)}%</td><td class="n neg">−${fmt(E.mdd_pct*r,1)}%</td><td class="n neg">−${fmt(E.mc_dd95*r,1)}%</td></tr>`).join('');
  $('#risk-note').textContent=`El criterio de Kelly calculado sobre este backtest daría ${fmt(kelly*100,1)}% de riesgo por operación. Es un techo teórico que supone que el win rate y el payoff medidos son exactos; las mesas profesionales usan entre 1/10 y 1/4 de Kelly y lo acotan por la caída máxima que toleran. El 1% actual equivale a 1/${fmt(kelly*100,0)} de Kelly: conservador y adecuado mientras el modelo no esté validado fuera de muestra. Proyección lineal, sin interés compuesto.`;
  const eh=E.hours, ed=[...E.days].sort((a,b)=>a.R-b.R)[0], eMg=MGMT.reduce((a,k)=>[a[0]+(E.exits[k]?.[0]||0),a[1]+(E.exits[k]?.[1]||0)],[0,0]);
  const eReset=E.exits['Reset antes de nueva entrada']||[0,0];
  const ukE=E.excl_cats.find(c=>c.cat==='Feriado Reino Unido');
  const sH7=S.hours.find(h=>h.franja.startsWith('07'));
  const RECO=[
    ['g','MODELO',`<b>Operar solo Envolvente.</b> Es mejor en rendimiento, calidad y riesgo: ${sg(E.R_tot)}R contra ${sg(C.R_tot)}R del combinado, factor de ganancias ${fmt(E.pf)} contra ${fmt(C.pf)}, caída máxima −${fmt(E.mdd_pct)}% contra −${fmt(C.mdd_pct)}%, Sharpe ${fmt(E.sharpe)} contra ${fmt(C.sharpe)}. Opera menos (${fmt(E.trades_week)} operaciones por semana contra ${fmt(C.trades_week)}) y gana más: más eficiente por operación y por hora de pantalla.`],
    ['r','START',`<b>Sacar START del capital real.</b> Win rate ${fmt(S.wr,1)}%, factor ${fmt(S.pf)}, ${sg(S.R_avg,3)}R por operación y la expectativa sale positiva solo en ${fmt(S.p_exp_pos,0)}% de las simulaciones. Su peor franja es la de 07:00 a 07:59 (${sg(sH7.R)}R), justo donde Envolvente rinde más. Ninguna variante lo rescata. Si querés seguir desarrollándolo, registralo en demo sin capital hasta que muestre ventaja propia.`],
    ['g','HORARIO',`<b>Mantener la ventana completa para Envolvente.</b> Las dos franjas son positivas: ${eh[0].franja} ${sg(eh[0].R)}R (win rate ${fmt(eh[0].wr,1)}%) y ${eh[1].franja} ${sg(eh[1].R)}R (${fmt(eh[1].wr,1)}%). Cortar la segunda hora dejaría afuera ${sg(eh[1].R)}R. Las entradas de 09:00 siguen en prueba (${eh[2]?eh[2].n+' operaciones, '+sg(eh[2].R)+'R':'sin operaciones'}).`],
    ['y','DÍAS',`<b>No filtrar días todavía.</b> El día más flojo de Envolvente es ${ed.dia} (${sg(ed.R)}R, win rate ${fmt(ed.wr,1)}%), pero con ${ed.n} operaciones la diferencia puede ser azar y no hay una razón de mercado clara. Seguirlo en los próximos meses.`],
    ['y','GESTIÓN',`<b>Mantener CHoCH en contra; revisar solo el cierre de fin de sesión.</b> La variante que deja correr todo hasta SL o TP empeoró los tres modelos (Envolvente: ${sg(DATA.envolvente_v.R_tot)}R contra ${sg(E.R_tot)}R). El CHoCH en contra protege capital; el cierre de fin de sesión es el único que resta en Envolvente, con muy pocas operaciones. Detalle en la pestaña “Gestión: variante SL/TP”.`],
    ['y','CALENDARIO',`<b>Mismas recomendaciones de calendario, aplicadas a Envolvente.</b> Habilitar CPI (GBP) y operar CPI (USD) solo de 07:00 a 07:59 sumaría ${sg(E.escenarios[2].R-E.escenarios[0].R)}R. El feriado del Reino Unido${ukE?` (${sg(ukE.R)}R)`:''} y el NFP se mantienen excluidos. Validar antes con 2025.`],
    ['y','RIESGO',`<b>Mantener 1% por operación.</b> Con Envolvente, la caída máxima esperable es −${fmt(E.mc_dd95)}% (percentil 95). Subir a 1,5% solo después de validar con 2025 y con al menos 100 operaciones en real que confirmen el win rate. Regla de corte: si la caída real supera −${fmt(Math.ceil(E.mc_dd95),0)}%, pausar y revisar.`],
  ];
  $('#reco').innerHTML=RECO.map(([c,t,h])=>`<li><span class="tag ${c}">${t}</span><p>${h}</p></li>`).join('');
  $('#plan').innerHTML=[
    `<b>Desde la próxima sesión:</b> operar solo Envolvente, riesgo 1%, ventana de 07:00 a 09:01 y el calendario de restricciones actual.`,
    `<b>START:</b> registrar sus señales en demo o en una planilla aparte, sin capital, durante 3 meses o 50 operaciones.`,
    `<b>Validación fuera de muestra:</b> correr Envolvente sobre 2025 con el backtest profundo de TradingView y pasarme el CSV. Si la ventaja se mantiene (factor de ganancias mayor a 1,2 y R promedio positivo), el modelo queda validado.`,
    `<b>Gestión:</b> la variante sin CHoCH ni cierre de sesión no mejora (ver pestaña “Gestión: variante SL/TP”). Siguiente prueba: Envolvente con CHoCH en contra y sin cierre de fin de sesión, con un cierre forzado a las 09:30.`,
    `<b>Calendario:</b> registrar aparte los días de CPI (GBP) y CPI (USD) con ventana. Habilitarlos si 2025 confirma el resultado.`,
    `<b>Control:</b> revisión mensual con este mismo informe. Pausar si la caída supera −${fmt(Math.ceil(E.mc_dd95),0)}% o si 20 operaciones seguidas promedian menos de −0,2R.`,
  ].map(x=>`<li>${x}</li>`).join('');
}
