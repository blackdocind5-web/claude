/* ---------- Escalera de riesgo ---------- */
const ESC={mod:'envolvente',per:'2 años',obj:1,perf:'moderado'};
const PCOL={conservador:'--s-comb',moderado:'--s-env',agresivo:'--s-start'};
window.EXTRA_VIEWS={escalera:{h1:'XAUUSD | Escalera de riesgo',nota:'Esta vista usa su propio selector de modelo y período',render:()=>renderEscalera()}};
function segBtns(id,opts,cur,on){
  const box=$(id); box.innerHTML=opts.map(([v,l])=>`<button type="button" data-v="${v}" aria-pressed="${String(v)===String(cur)}">${l}</button>`).join('');
  box.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{on(b.dataset.v);renderEscalera()}));
}
function drawLogEq(host){
  const box=$(host); box.innerHTML='';
  const X0=DATA.escalera.envolvente[ESC.per];
  const S=X0.escenarios.filter(e=>e.obj===ESC.obj).map(e=>({n:e.nombre,c:css(PCOL[e.perfil]),p:(e.escalera.curve||[]).map(x=>({t:parseT(x.t).getTime(),eq:Math.max(x.eq,1)}))})).filter(s=>s.p.length);
  if(!S.length){box.innerHTML='<p class="note">Sin datos.</p>';return}
  const W=Math.max(320,box.clientWidth), H=320, M={l:58,r:W<560?14:110,t:12,b:24};
  const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Curvas de capital de los tres perfiles en escala logarítmica'},box);
  const a=Math.min(...S.map(s=>s.p[0].t)), b=Math.max(...S.map(s=>s.p[s.p.length-1].t));
  const lo=Math.log10(Math.min(1000,...S.flatMap(s=>s.p.map(p=>p.eq)))*0.95), hi=Math.log10(Math.max(1000,...S.flatMap(s=>s.p.map(p=>p.eq)))*1.05);
  const X=t=>M.l+(t-a)/(b-a)*(W-M.l-M.r), Y=v=>M.t+(hi-Math.log10(v))/(hi-lo)*(H-M.t-M.b);
  [1,2,5].flatMap(m=>[100,1000,10000,100000].map(p=>m*p)).filter(v=>Math.log10(v)>=lo&&Math.log10(v)<=hi).forEach(v=>{el('line',{x1:M.l,x2:W-M.r,y1:Y(v),y2:Y(v),class:'gl'},svg);el('text',{x:M.l-8,y:Y(v)+4,'text-anchor':'end',class:'ax'},svg).textContent=fmt(v,0)});
  const y0=new Date(a).getFullYear(), y1=new Date(b).getFullYear();
  for(let y=y0;y<=y1;y++) for(const m of [0,3,6,9]){const d=new Date(y,m,1).getTime(); if(d<a||d>b) continue; el('line',{x1:X(d),x2:X(d),y1:M.t,y2:H-M.b,class:'gl'},svg); el('text',{x:X(d),y:H-6,'text-anchor':'middle',class:'ax'},svg).textContent=MES[m]+(m===0?' '+String(y).slice(2):'');}
  el('line',{x1:M.l,x2:W-M.r,y1:Y(1000),y2:Y(1000),class:'zero','stroke-dasharray':'3 4'},svg);
  const ends=[];
  S.forEach(s=>{el('path',{d:'M'+s.p.map(p=>`${X(p.t)},${Y(p.eq)}`).join(' L'),fill:'none',stroke:s.c,'stroke-width':2,'stroke-linejoin':'round'},svg); const L=s.p[s.p.length-1]; ends.push({s,y:Y(L.eq),v:L.eq,x:X(L.t)}); el('circle',{cx:X(L.t),cy:Y(L.eq),r:4,fill:s.c,stroke:css('--panel'),'stroke-width':2},svg)});
  if(M.r>50){ends.sort((p,q)=>p.y-q.y);for(let i=1;i<ends.length;i++)if(ends[i].y-ends[i-1].y<16)ends[i].y=ends[i-1].y+16;ends.forEach(e=>el('text',{x:W-M.r+10,y:e.y+4,class:'lbl'},svg).textContent=`${e.s.n} ${fmt(e.v,0)}`)}
  const cross=el('line',{y1:M.t,y2:H-M.b,stroke:css('--fg3'),'stroke-dasharray':'2 3',visibility:'hidden'},svg);
  const hit=el('rect',{x:M.l,y:0,width:W-M.l-M.r,height:H,fill:'transparent'},svg);
  hit.addEventListener('pointermove',e=>{const r=svg.getBoundingClientRect();const sx=(e.clientX-r.left)*W/r.width;const t=a+(sx-M.l)/(W-M.l-M.r)*(b-a);cross.setAttribute('x1',sx);cross.setAttribute('x2',sx);cross.setAttribute('visibility','visible');
    showTip(box,dmy(new Date(t))+'<br>'+S.map(s=>{let v=1000;for(const p of s.p){if(p.t<=t)v=p.eq;else break}return `<span style="color:${s.c}">■</span> ${s.n}: ${fmt(v,0)} USD`}).join('<br>'),e.clientX-r.left,e.clientY-r.top)});
  hit.addEventListener('pointerleave',()=>{cross.setAttribute('visibility','hidden');hideTip(box)});
}
function renderEscalera(){
  document.querySelectorAll('.yr').forEach(b=>b.disabled=true);
  const X0=DATA.escalera[ESC.mod][ESC.per], XE=DATA.escalera.envolvente[ESC.per], E2=DATA.escalera.envolvente['2 años'];
  segBtns('#e-mod',[['envolvente','Envolvente'],['combinado','Envolvente + START'],['start','START']],ESC.mod,v=>ESC.mod=v);
  segBtns('#e-per',[['2025','2025'],['2026','2026'],['2 años','2 años']],ESC.per,v=>ESC.per=v);
  segBtns('#e-obj',[[1,'1% diario'],[2,'2% diario']],ESC.obj,v=>ESC.obj=+v);
  segBtns('#e-perf',[['conservador','Conservador'],['moderado','Moderado'],['agresivo','Agresivo']],ESC.perf,v=>ESC.perf=v);
  const sc=(X,p,o)=>X.escenarios.find(e=>e.perfil===p&&e.obj===o);
  const c1=sc(E2,'conservador',1), m1=sc(E2,'moderado',1), a1=sc(E2,'agresivo',1);
  const tp=(p,t,o)=>E2.tope.find(x=>x.perfil===p&&x.tope===t&&x.obj===o);
  const best=[...E2.tope].filter(x=>x.mc.p_ruina===0&&x.mc.p_dd30<5).sort((a,b)=>b.mc.ret_med-a.mc.ret_med)[0];
  $('#e-verdict').innerHTML=`<span class="eyebrow">Veredicto</span>
    <div class="big">En el orden histórico la escalera multiplica la cuenta, pero si las rachas perdedoras llegan en otro orden, la mayoría de los caminos termina en la ruina. Tal como está planteada, no sirve para un flujo de caja estable.</div>
    <p>Envolvente, 2025 y 2026 juntos, objetivo diario de 1%: en el orden histórico el perfil conservador gana <b>${sg(c1.escalera.ret,0)}%</b>, el moderado <b>${sg(m1.escalera.ret,0)}%</b> y el agresivo <b>${sg(a1.escalera.ret,0)}%</b>, con todos los meses positivos. La racha perdedora más larga fue de ${E2.racha_max} operaciones. Reordenando las mismas operaciones al azar, la cuenta llega a cero en <b>${fmt(c1.mc.p_ruina,0)}%</b>, <b>${fmt(m1.mc.p_ruina,0)}%</b> y <b>${fmt(a1.mc.p_ruina,0)}%</b> de los casos. El problema es la duplicación sin límite: con un win rate de ${fmt(100-E2.q_perdida,0)}%, una racha de 9 pérdidas en dos años aparece en ${fmt(E2.p_racha['9'],0)}% de los casos, y desde el 5.º escalón un TP ya no recupera lo perdido. ${best?`<b>La alternativa viable es la escalera con tope</b>: ${best.nombre.toLowerCase()} con tope de ${best.tope} escalones y objetivo de ${best.obj}% no tuvo ruina en ninguna simulación.`:''}</p>`;
  // pasos
  const P=[0,1,2,3,4,5,6].map(k=>{const r=2**k, prev=r-1, tpv=0.9*r;return {k,r,prev,tpv,net:tpv-prev}});
  $('#t-e-pasos').innerHTML='<tr><th>Escalón</th><th class="n">Riesgo</th><th class="n">Pérdida previa</th><th class="n">Si sale TP</th><th class="n">Neto</th><th class="n">Riesgo real (cons. · mod. · agr.)</th></tr>'+
    P.map(p=>`<tr${p.net<0?' style="background:var(--loss-soft)"':''}><td>${p.k+1}.º</td><td class="n">×${p.r}</td><td class="n">−${p.prev}</td><td class="n">+${fmt(p.tpv,1)}</td><td class="n ${cls(p.net)}">${sg(p.net,1)}</td><td class="n">${fmt(0.25*p.r,2)}% · ${fmt(0.5*p.r,1)}% · ${fmt(p.r,0)}%</td></tr>`).join('');
  $('#e-pasos-txt').innerHTML=[
    ['r','R:R 1:0,9',`<b>Con TP a 0,9R, duplicar no alcanza siempre.</b> Hasta el 4.º escalón un TP recupera todo y deja ganancia; desde el 5.º (16 veces el riesgo base), un TP deja la escalera todavía en negativo y el riesgo sigue alto.`],
    ['r','SALIDAS PARCIALES',`<b>Las salidas por gestión cuentan como pérdida.</b> Un CHoCH en contra de −0,1R también duplica el riesgo de la siguiente operación.`],
    ['y','PERFILES',`<b>El agresivo llega a 64% de riesgo en el 7.º escalón</b> y el conservador al 16%. Después de 8 pérdidas seguidas, la siguiente operación pide 256 veces el riesgo base: con base 0,25% es el 64% de la cuenta; después de 9, más que la cuenta entera.`],
  ].map(([c,t,x])=>`<li><span class="tag ${c}">${t}</span><p>${x}</p></li>`).join('');
  // tabla principal
  $('#e-s1p').textContent=`${ESC.mod==='envolvente'?'Envolvente':ESC.mod==='start'?'START':'Envolvente + START'} · ${ESC.per} · ${X0.n} operaciones válidas · racha perdedora más larga: ${X0.racha_max}`;
  const ES=X0.escenarios;
  const pct=(v,d=1)=>`<span class="${cls(v)}">${sg(v,d)}%</span>`;
  const R=[
    ['Histórico',null],
    ['Rendimiento total',e=>e.escalera.ruina?'<span class="neg">Ruina</span>':pct(e.escalera.ret,0)],
    ['Rendimiento mensual promedio',e=>pct(e.escalera.mes_prom,2)],
    ['Meses positivos',e=>fmt(e.escalera.meses_pos,0)+'%'],
    ['Peor mes',e=>pct(e.escalera.peor_mes,1)],
    ['Rendimiento diario promedio',e=>pct(e.escalera.dia_prom,2)],
    ['Días positivos',e=>fmt(e.escalera.dias_pos,0)+'%'],
    ['Días que alcanzan el objetivo',e=>fmt(e.escalera.dias_obj,0)+'%'],
    ['Peor día',e=>pct(e.escalera.peor_dia,1)],
    ['Caída máxima',e=>'−'+fmt(e.escalera.mdd,1)+'%'],
    ['Riesgo máximo usado en una operación',e=>fmt(e.escalera.max_riesgo,1)+'%'],
    ['Mismo riesgo base, sin escalera',null],
    ['Rendimiento total',e=>pct(e.fijo.ret,1)],
    ['Caída máxima',e=>'−'+fmt(e.fijo.mdd,1)+'%'],
    ['Simulaciones (orden al azar)',null],
    ['Probabilidad de ruina',e=>`<span class="${e.mc.p_ruina>5?'neg':''}">${fmt(e.mc.p_ruina,1)}%</span>`],
    ['Probabilidad de caída ≥ 30%',e=>fmt(e.mc.p_dd30,1)+'%'],
    ['Probabilidad de terminar en pérdida',e=>fmt(e.mc.p_perdida,1)+'%'],
    ['Rendimiento mediano',e=>e.mc.ret_med<=-99?'<span class="neg">Ruina</span>':pct(e.mc.ret_med,0)],
  ];
  $('#t-e-main').innerHTML='<tr><th></th>'+ES.map(e=>`<th class="n"><i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:var(${PCOL[e.perfil]});margin-right:6px"></i>${e.nombre} · ${fmt(e.obj,0)}%</th>`).join('')+'</tr>'+
    R.map(([l,f])=>f?`<tr><td>${l}</td>${ES.map(e=>`<td class="n">${f(e)}</td>`).join('')}</tr>`:`<tr class="grp"><td colspan="${ES.length+1}">${l}</td></tr>`).join('');
  drawLogEq('#c-e-eq');
  // meses
  const em=sc(XE,ESC.perf,ESC.obj);
  $('#e-s3p').textContent=`${em.nombre}, objetivo ${ESC.obj}% · ${ESC.per} · ${em.escalera.meses.length} meses · promedio ${sg(em.escalera.mes_prom,2)}% por mes`;
  drawBars('#c-e-mes',em.escalera.meses,{aria:'Rendimiento mensual',H:240,val:m=>m.pct,tickFmt:v=>fmt(v,0)+'%',label:m=>sg(m.pct,1),xlab:m=>MES[+m.mes.slice(5)-1]+(m.mes.slice(5)==='01'?' '+m.mes.slice(2,4):''),xEvery:em.escalera.meses.length>12?2:1,
    tip:m=>`${MES[+m.mes.slice(5)-1]} ${m.mes.slice(0,4)}<br><span class="${cls(m.pct)}">${sg(m.pct)}% · ${sg(m.usd)} USD</span>`});
  // rachas
  $('#e-s4p').textContent=`Envolvente · ${ESC.per} · ${fmt(XE.q_perdida,1)}% de operaciones perdedoras`;
  $('#t-e-rachas').innerHTML='<tr><th>Racha de pérdidas</th><th class="n">Veces que pasó</th><th class="n">Prob. de ver una racha igual o mayor</th></tr>'+
    Object.entries(XE.p_racha).filter(([k])=>+k>=3&&+k<=11).map(([k,p])=>`<tr><td>${k} seguidas</td><td class="n">${XE.rachas[k]||0}</td><td class="n">${fmt(p,1)}%</td></tr>`).join('');
  const cum=k=>2**k-1;
  $('#t-e-impl').innerHTML='<tr><th>Tras perder</th><th class="n">Pérdida acumulada (cons. · mod. · agr.)</th><th class="n">Riesgo siguiente (cons. · mod. · agr.)</th></tr>'+
    [3,4,5,6,7,8,9].map(k=>`<tr><td>${k} seguidas</td><td class="n">−${fmt(0.25*cum(k),1)}% · −${fmt(0.5*cum(k),1)}% · ${cum(k)>=100?'<span class="neg">ruina</span>':'−'+fmt(cum(k),0)+'%'}</td><td class="n">${fmt(0.25*2**k,1)}% · ${fmt(0.5*2**k,0)}% · ${2**k>=100?'<span class="neg">imposible</span>':fmt(2**k,0)+'%'}</td></tr>`).join('');
  const om=sc(XE,ESC.perf,1).escalera.ops_max||[];
  $('#t-e-ops').innerHTML='<tr><th>Fecha</th><th>Entrada</th><th class="n">Escalón</th><th class="n">Riesgo</th><th class="n">Resultado (× riesgo)</th><th class="n">PyG USD</th><th class="n">Capital después</th></tr>'+
    om.map(o=>`<tr><td>${o.f}</td><td class="mono">${o.h}</td><td class="n">${o.esc+1}.º</td><td class="n">${fmt(o.riesgo,2)}%</td><td class="n ${cls(o.u)}">${sg(o.u,2)}</td><td class="n ${cls(o.pnl)}">${sg(o.pnl)}</td><td class="n">${fmt(o.eq)}</td></tr>`).join('');
  // tope
  $('#t-e-tope').innerHTML='<tr><th>Perfil · tope · objetivo</th><th class="n">Riesgo máx.</th><th class="n">Rend. histórico</th><th class="n">Caída máx.</th><th class="n">Meses +</th><th class="n">Mensual prom.</th><th class="n">Peor mes</th><th class="n">Ruina (sim.)</th><th class="n">Caída ≥30% (sim.)</th><th class="n">Pérdida (sim.)</th><th class="n">Rend. mediano (sim.)</th></tr>'+
    XE.tope.map(x=>`<tr${x===best&&ESC.per==='2 años'?' class="best"':''}><td>${x.nombre} · ${x.tope} escalones · ${x.obj}%</td><td class="n">${fmt(x.escalera.max_riesgo,2)}%</td><td class="n ${cls(x.escalera.ret)}">${sg(x.escalera.ret,1)}%</td><td class="n">−${fmt(x.escalera.mdd,1)}%</td><td class="n">${fmt(x.escalera.meses_pos,0)}%</td><td class="n ${cls(x.escalera.mes_prom)}">${sg(x.escalera.mes_prom,2)}%</td><td class="n ${cls(x.escalera.peor_mes)}">${sg(x.escalera.peor_mes,1)}%</td><td class="n">${fmt(x.mc.p_ruina,1)}%</td><td class="n">${fmt(x.mc.p_dd30,1)}%</td><td class="n">${fmt(x.mc.p_perdida,1)}%</td><td class="n ${cls(x.mc.ret_med)}">${sg(x.mc.ret_med,1)}%</td></tr>`).join('');
  // recomendación
  const t2m=best, t2c=tp('conservador',2,1), fx=sc(E2,'agresivo',1).fijo;
  const meses=E2.escenarios[0].escalera.meses.length;
  $('#e-reco').innerHTML=[
    ['r','ESCALERA SIN TOPE',`<b>No usarla con capital real.</b> En los tres perfiles, la probabilidad de llevar la cuenta a cero en dos años va de ${fmt(c1.mc.p_ruina,0)}% a ${fmt(a1.mc.p_ruina,0)}%. Los meses 100% positivos del orden histórico se deben a que la racha más larga fue de ${E2.racha_max}; una racha de 8 o 9, que es normal con este win rate, liquida la cuenta.`],
    ['y','OBJETIVO DIARIO',`<b>El 1% o 2% diario no es alcanzable de forma sostenida.</b> Con riesgo fijo, Envolvente promedia ${sg(sc(E2,'agresivo',1).fijo.mes_prom,2)}% por mes al 1% de riesgo. Con la escalera, el moderado alcanza el objetivo de 1% en ${fmt(m1.escalera.dias_obj,0)}% de los días; para acercarse a 1% diario hay que usar el perfil agresivo, que tiene ${fmt(a1.mc.p_ruina,0)}% de ruina. Entre 1% y 2% de objetivo casi no hay diferencia, porque pocos días llegan a cualquiera de los dos.`],
    ['g','ALTERNATIVA',`<b>Escalera con tope</b> (se duplica hasta un máximo de escalones; si se pierde el último, se acepta la pérdida y se reinicia al riesgo base). ${t2m?`La mejor combinación sin ruina y con menos de 5% de probabilidad de una caída de 30%: ${t2m.nombre.toLowerCase()} con tope de ${t2m.tope} escalones y objetivo de ${t2m.obj}%: ${sg(t2m.escalera.ret,0)}% histórico en dos años, ${sg(t2m.escalera.mes_prom,2)}% por mes, riesgo máximo ${fmt(t2m.escalera.max_riesgo,0)}%, sin ruina en las simulaciones y ${fmt(t2m.mc.p_perdida,1)}% de probabilidad de terminar en pérdida.`:''} ${t2c?`Conservador con objetivo de 1%: ${sg(t2c.escalera.ret,0)}% con riesgo máximo de ${fmt(t2c.escalera.max_riesgo,0)}%.`:''} Para comparar: 1% fijo sin escalera rinde ${sg(fx.ret,0)}% con −${fmt(fx.mdd,1)}% de caída.`],
    ['y','FLUJO DE CAJA',`<b>Para retirar dinero todos los meses</b>, el flujo tiene que salir de una ganancia esperable y no de la suerte del orden. Con la escalera con tope, la mitad de las simulaciones queda por encima de ${t2m?sg(t2m.mc.ret_med,0)+'%':'—'} en ${meses} meses. Eso es un retiro razonable de alrededor de ${t2m?fmt(t2m.mc.ret_med/meses,1):'—'}% por mes, no de 1% por día.`],
    ['y','ANTES DE OPERARLA',`<b>Validar la escalera con tope en demo</b> durante 2 o 3 meses, con ${t2m?t2m.nombre.toLowerCase()+', tope de '+t2m.tope+' escalones y objetivo de '+t2m.obj+'%':'el perfil moderado'}. Regla de corte: si la caída llega a −${t2m?fmt(Math.ceil(t2m.mc.dd_p95),0):'20'}% (percentil 95 de las simulaciones), volver a riesgo fijo.`],
  ].map(([c,t,x])=>`<li><span class="tag ${c}">${t}</span><p>${x}</p></li>`).join('');
}
