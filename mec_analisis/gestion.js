/* ---------- Gestión: original vs variante SL/TP ---------- */
function drawPair(host,k,color){
  const box=$(host); box.innerHTML='';
  const W=Math.max(260,box.clientWidth), H=210, M={l:44,r:10,t:10,b:22};
  const svg=el('svg',{viewBox:`0 0 ${W} ${H}`,role:'img','aria-label':'Curva original y variante de '+DATA[k].nombre},box);
  const S=[['Original',DATA[k],null],['Variante',DATA[k+'_v'],'4 4']].map(([n,d,dash])=>({n,dash,p:d.curve.map(x=>({t:parseT(x.t).getTime(),eq:x.eq}))}));
  const a=Math.min(...S.map(s=>s.p[0].t)), b=Math.max(...S.map(s=>s.p[s.p.length-1].t));
  let mn=Math.min(1000,...S.flatMap(s=>s.p.map(p=>p.eq))), mx=Math.max(1000,...S.flatMap(s=>s.p.map(p=>p.eq))); const pad=(mx-mn)*0.08; mn-=pad; mx+=pad;
  const X=t=>M.l+(t-a)/(b-a)*(W-M.l-M.r), Y=v=>M.t+(mx-v)/(mx-mn)*(H-M.t-M.b);
  niceTicks(mn,mx,4).t.forEach(v=>{el('line',{x1:M.l,x2:W-M.r,y1:Y(v),y2:Y(v),class:'gl'},svg);el('text',{x:M.l-6,y:Y(v)+4,'text-anchor':'end',class:'ax'},svg).textContent=fmt(v,0)});
  [1,3,5,7,9].forEach(m=>{const d=new Date(2026,m-1,1).getTime();if(d<a||d>b)return;el('text',{x:X(d),y:H-5,'text-anchor':'middle',class:'ax'},svg).textContent=MES[m-1]});
  el('line',{x1:M.l,x2:W-M.r,y1:Y(1000),y2:Y(1000),class:'zero','stroke-dasharray':'3 4'},svg);
  const col=css(color);
  S.forEach(s=>el('path',{d:'M'+s.p.map(p=>`${X(p.t)},${Y(p.eq)}`).join(' L'),fill:'none',stroke:s.dash?css('--fg2'):col,'stroke-width':s.dash?1.6:2,'stroke-dasharray':s.dash||'none','stroke-linejoin':'round'},svg));
  const cross=el('line',{y1:M.t,y2:H-M.b,stroke:css('--fg3'),'stroke-dasharray':'2 3',visibility:'hidden'},svg);
  const hit=el('rect',{x:M.l,y:0,width:W-M.l-M.r,height:H,fill:'transparent'},svg);
  hit.addEventListener('pointermove',e=>{const r=svg.getBoundingClientRect();const sx=(e.clientX-r.left)*W/r.width;const t=a+(sx-M.l)/(W-M.l-M.r)*(b-a);
    cross.setAttribute('x1',sx);cross.setAttribute('x2',sx);cross.setAttribute('visibility','visible');
    const v=S.map(s=>{let q=s.p[0].eq;for(const p of s.p){if(p.t<=t)q=p.eq;else break}return `${s.n}: ${fmt(q)} USD`});
    showTip(box,dmy(new Date(t))+'<br>'+v.join('<br>'),e.clientX-r.left,e.clientY-r.top)});
  hit.addEventListener('pointerleave',()=>{cross.setAttribute('visibility','hidden');hideTip(box)});
}
function cambiosRows(cs,withModel){
  return cs.map(c=>`<tr>${withModel?`<td>${c.m}</td>`:''}<td>${c.f}</td><td class="mono">${c.h}</td><td>${c.dir}</td><td>${c.sal_o.startsWith('CHoCH')?'CHoCH en contra':'Cierre fin de sesión'}</td><td class="mono">${c.hs_o}</td><td class="n ${cls(c.R_o)}">${sg(c.R_o)}</td><td>${c.sal_v}</td><td class="mono">${c.hs_v}</td><td class="n ${cls(c.R_v)}">${sg(c.R_v)}</td><td class="n ${cls(c.R_v-c.R_o)}">${sg(c.R_v-c.R_o)}</td></tr>`).join('');
}
const CAMB_HEAD=m=>`<tr>${m?'<th>Modelo</th>':''}<th>Fecha</th><th>Entrada</th><th>Dir.</th><th>Salida original</th><th>Hora</th><th class="n">R</th><th>Variante</th><th>Hora</th><th class="n">R</th><th class="n">Diferencia</th></tr>`;
function renderGestion(){
  const V=DATA.variante, E=DATA.envolvente, Ev=DATA.envolvente_v;
  const eT=Object.fromEntries(V.envolvente.por_tipo.map(x=>[x.tipo,x]));
  const ch=eT['CHoCH en contra'], ci=eT['Cierre fin de sesión'];
  const est=E.R_tot+(ci.R_v-ci.R_o);
  $('#g-verdict').innerHTML=`<span class="eyebrow">Veredicto</span>
    <div class="big">Dejar correr todo hasta SL o TP empeora los tres modelos. La salida por CHoCH en contra protege capital y hay que mantenerla.</div>
    <p>En Envolvente la variante baja de <b>${sg(E.R_tot)}R a ${sg(Ev.R_tot)}R</b> y la caída máxima sube de −${fmt(E.mdd_pct)}% a −${fmt(Ev.mdd_pct)}%. En el combinado cae de ${sg(DATA.combinado.R_tot)}R a ${sg(DATA.combinado_v.R_tot)}R y en START, de ${sg(DATA.start.R_tot)}R a ${sg(DATA.start_v.R_tot)}R. Pero las dos salidas no valen lo mismo: <b>el CHoCH en contra le ahorra ${fmt(ch.R_o-ch.R_v)}R a Envolvente</b>, mientras que <b>el cierre de fin de sesión le cuesta ${fmt(ci.R_v-ci.R_o)}R</b>. Ahí puede estar la mejora real.</p>`;
  const M3=[['envolvente','Envolvente','--s-env'],['combinado','Envolvente + START','--s-comb'],['start','START','--s-start']];
  const rows=[['R total',d=>d.R_tot,v=>`<span class="${cls(v)}">${sg(v)}R</span>`,1],['R por operación',d=>d.R_avg,v=>`<span class="${cls(v)}">${sg(v,3)}R</span>`,1],['R por semana',d=>d.R_week,v=>`<span class="${cls(v)}">${sg(v)}R</span>`,1],
    ['PyG (USD)',d=>d.pnl,v=>`<span class="${cls(v)}">${sg(v)}</span>`,1],['Win rate',d=>d.wr,v=>fmt(v,1)+'%',1],['Factor de ganancias',d=>d.pf,v=>fmt(v),1],
    ['Caída máxima',d=>d.mdd_pct,v=>'−'+fmt(v)+'%',-1],['Caída máxima esperable (p95)',d=>d.mc_dd95,v=>'−'+fmt(v)+'%',-1],['P(expectativa > 0)',d=>d.p_exp_pos,v=>fmt(v,1)+'%',1],
    ['Sharpe',d=>d.sharpe,v=>fmt(v),1],['Duración media',d=>d.dur_avg,v=>fmt(v,0)+' min',-1],['Duración máxima',d=>Math.max(...[]),v=>v,0]];
  let h='<tr><th>Métrica</th>'+M3.map(([k,n,c])=>`<th class="n" colspan="3"><i style="display:inline-block;width:9px;height:9px;border-radius:2px;background:var(${c});margin-right:6px"></i>${n}</th>`).join('')+'</tr>';
  h+='<tr><th></th>'+M3.map(()=>'<th class="n">Original</th><th class="n">Variante</th><th class="n">Dif.</th>').join('')+'</tr>';
  rows.slice(0,-1).forEach(([lab,f,fm,dir])=>{h+=`<tr><td>${lab}</td>`+M3.map(([k])=>{const o=f(DATA[k]),v=f(DATA[k+'_v']),d=v-o,better=dir*d>1e-9,worse=dir*d<-1e-9;
    return `<td class="n${!better&&!worse?'':worse?' best':''}">${fm(o)}</td><td class="n${better?' best':''}">${fm(v)}</td><td class="n ${better?'pos':worse?'neg':''}">${Math.abs(d)<1e-9?'=':(d>0?'+':'−')+fmt(Math.abs(d),lab.includes('operación')?3:lab.includes('Duración')?0:2)}</td>`}).join('')+'</tr>'});
  h+='<tr><td>Operación más larga</td>'+M3.map(([k])=>`<td class="n">${fmt(V[k].max_min_o,0)} min</td><td class="n">${fmt(V[k].max_min,0)} min</td><td class="n"></td>`).join('')+'</tr>';
  h+='<tr><td>Cierres después de las 09:30</td>'+M3.map(([k])=>`<td class="n">0</td><td class="n neg">${V[k].tardias}</td><td class="n"></td>`).join('')+'</tr>';
  $('#t-gv').innerHTML=h;
  let ht='<tr><th>Modelo · salida</th><th class="n">Ops.</th><th class="n">R original</th><th class="n">R variante</th><th class="n">Variante: TP / SL</th><th class="n">Diferencia</th><th>Lectura</th></tr>';
  M3.forEach(([k,n])=>{ht+=`<tr class="grp"><td colspan="7">${n}</td></tr>`+V[k].por_tipo.map(x=>{const d=x.R_v-x.R_o;return `<tr><td>${x.tipo}</td><td class="n">${x.n}</td><td class="n ${cls(x.R_o)}">${sg(x.R_o)}</td><td class="n ${cls(x.R_v)}">${sg(x.R_v)}</td><td class="n">${x.tp} / ${x.sl}</td><td class="n ${cls(d)}">${sg(d)}</td><td style="color:var(--fg2)">${d<0?'La salida protege: mantener':'La salida resta: candidata a quitar'}</td></tr>`}).join('')});
  $('#t-gtipo').innerHTML=ht;
  $('#g-curves').innerHTML=M3.map(([k,n])=>`<div class="panel"><h3>${n}</h3><div class="chart" id="gc-${k}"></div><p class="note">Original ${sg(DATA[k].R_tot)}R · Variante ${sg(DATA[k+'_v'].R_tot)}R</p></div>`).join('');
  M3.forEach(([k,,c])=>drawPair('#gc-'+k,k,c));
  $('#g-s4p').textContent=`${V.envolvente.n_cambios} operaciones: ${V.envolvente.cambios_a_tp} terminaron en TP y ${V.envolvente.cambios_a_sl} en SL al dejarlas correr`;
  $('#t-gcamb').innerHTML=CAMB_HEAD(false)+cambiosRows(V.envolvente.cambios,false);
  $('#t-gcamb2').innerHTML=CAMB_HEAD(true)+cambiosRows([...V.combinado.cambios.map(c=>({...c,m:'Env. + START'})),...V.start.cambios.map(c=>({...c,m:'START'}))],true);
  const lateE=V.envolvente.tardias_list, lateS=V.start.tardias_list[0];
  const R=[
    ['g','CHOCH',`<b>Mantener la salida por CHoCH en contra.</b> En Envolvente, esas ${ch.n} operaciones sumaron ${sg(ch.R_o)}R con la salida; dejándolas correr, ${ch.tp} llegó a TP y ${ch.sl} a SL, y sumaron ${sg(ch.R_v)}R. El CHoCH ahorra ${fmt(ch.R_o-ch.R_v)}R: detecta bien las operaciones que se dan vuelta.`],
    ['y','CIERRE DE SESIÓN',`<b>El cierre de fin de sesión es el que resta en Envolvente.</b> Esas ${ci.n} operaciones sumaron ${sg(ci.R_o)}R cerrándolas a las 09:02; dejándolas correr, ${ci.tp} llegaron a TP y sumaron ${sg(ci.R_v)}R (${sg(ci.R_v-ci.R_o)}R). Pero son solo ${ci.n} operaciones: con esa muestra no alcanza para cambiar una regla. En START pasa lo contrario (${sg(V.start.por_tipo[1].R_v-V.start.por_tipo[1].R_o)}R).`],
    ['y','EXPOSICIÓN',`<b>Sin salidas por gestión, las operaciones salen de la sesión.</b> En Envolvente, ${V.envolvente.tardias} cerraron después de las 09:30 (la más larga, a las ${lateE[0]?.sal||'—'}), ya con la apertura del mercado de acciones de Nueva York. En START hubo una que quedó abierta hasta las ${lateS?.sal||'—'} (${fmt(lateS?.min||0,0)} minutos). Eso es riesgo que la sesión Pre NY no busca tomar.`],
    ['g','SIGUIENTE PRUEBA',`<b>Correr una tercera variante solo en Envolvente: con CHoCH en contra y sin cierre de fin de sesión.</b> Sumando lo que hoy resta el cierre de sesión, la estimación da ≈ ${sg(est)}R contra ${sg(E.R_tot)}R actuales. Si el backtest real se acerca a ese número y las operaciones que pasan de las 09:02 no superan un límite razonable (por ejemplo, cierre forzado a las 09:30), es una mejora a considerar. Validarla después con 2025.`],
  ];
  $('#g-reco').innerHTML=R.map(([c,t,x])=>`<li><span class="tag ${c}">${t}</span><p>${x}</p></li>`).join('');
}
