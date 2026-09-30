import csv, json, datetime as dt, statistics as st, math
from collections import OrderedDict, defaultdict
CAP=1000.0
rows=list(csv.DictReader(open("XAU_m1_Envolvente_y_START_validos.csv",encoding="utf-8-sig")))
ops=OrderedDict()
for r in rows: ops.setdefault(int(r["Número de operación"]),[]).append(r)
T=[]
for n,fs in ops.items():
    e=next(f for f in fs if f["Tipo"].startswith("Entrada")); s=next(f for f in fs if f["Tipo"].startswith("Salida"))
    T.append(dict(n=n,dir="BUY" if "largo" in e["Tipo"] else "SELL",ent=dt.datetime.strptime(e["Fecha y hora"],"%Y-%m-%d %H:%M"),
      sal=dt.datetime.strptime(s["Fecha y hora"],"%Y-%m-%d %H:%M"),pnl=float(e["PyG netas USD"]),bars=int(e["Duración (barras)"]),salida=s["Señal"]))
T.sort(key=lambda t:t["sal"])
eq=CAP; peak=CAP; curve=[dict(t="2026-01-26",eq=CAP)]; mdd=0; ddinfo=None; peak_t=None
for t in T:
    t["eq0"]=eq; t["R"]=t["pnl"]/(0.009*eq)  # 1R = 1 TP = 0,9% del capital
    eq+=t["pnl"]; t["eq1"]=eq
    curve.append(dict(t=t["sal"].strftime("%Y-%m-%d %H:%M"),eq=round(eq,2),n=t["n"]))
    if eq>peak: peak=eq; peak_t=t
    dd=(peak-eq)/peak
    if dd>mdd: mdd=dd; ddinfo=dict(peak=peak,peak_n=peak_t["n"] if peak_t else 0,peak_t=(peak_t["sal"] if peak_t else dt.datetime(2026,1,26)),trough=eq,trough_t=t["sal"],trough_n=t["n"])
# recuperación
rec=None
for t in T:
    if t["sal"]>ddinfo["trough_t"] and t["eq1"]>=ddinfo["peak"]: rec=t; break
# drawdown series
peak=CAP; ddser=[]
for c in curve:
    peak=max(peak,c["eq"]); ddser.append(round(-(peak-c["eq"])/peak*100,3))
wins=[t for t in T if t["pnl"]>0]; loss=[t for t in T if t["pnl"]<=0]
gw=sum(t["pnl"] for t in wins); gl=-sum(t["pnl"] for t in loss)
# rachas
def streaks(sign):
    best=cur=0; bestend=None
    for t in T:
        if (t["pnl"]>0)==sign: cur+=1
        else: cur=0
        if cur>best: best=cur; bestend=t
    return best
# semanas
wk=defaultdict(list)
for t in T: wk[t["ent"].isocalendar()[:2]].append(t)
weeks=[]
for k in sorted(wk):
    ts=wk[k]; mon=dt.date.fromisocalendar(k[0],k[1],1)
    weeks.append(dict(sem=mon.strftime("%d/%m"),iso=k[1],n=len(ts),pnl=round(sum(x["pnl"] for x in ts),2),wr=round(100*sum(x["pnl"]>0 for x in ts)/len(ts),1),R=round(sum(x["R"] for x in ts),2)))
first=T[0]["ent"].date(); last=T[-1]["ent"].date()
nweeks_cal=((last-first).days)//7+1
# meses
mn=["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"]
mo=defaultdict(list)
for t in T: mo[t["ent"].month].append(t)
months=[]
for m in sorted(mo):
    ts=mo[m]; e0=ts[0]["eq0"]
    months.append(dict(mes=mn[m-1],n=len(ts),pnl=round(sum(x["pnl"] for x in ts),2),pct=round(100*sum(x["pnl"] for x in ts)/e0,2),wr=round(100*sum(x["pnl"]>0 for x in ts)/len(ts),1),R=round(sum(x["R"] for x in ts),2)))
# dias
dn=["Lunes","Martes","Miércoles","Jueves","Viernes"]
days=[]
for d in range(5):
    ts=[t for t in T if t["ent"].weekday()==d]
    days.append(dict(dia=dn[d],n=len(ts),wr=round(100*sum(x["pnl"]>0 for x in ts)/len(ts),1) if ts else 0,pnl=round(sum(x["pnl"] for x in ts),2),pct=round(100*sum(x["pnl"] for x in ts)/CAP,2),R=round(sum(x["R"] for x in ts),2)))
hours=[]
for lab,a,b in [("07:00–07:59",7,8),("08:00–08:59",8,9),("09:00 o más",9,24)]:
    ts=[t for t in T if a<=t["ent"].hour<b]
    if ts: hours.append(dict(franja=lab,n=len(ts),wr=round(100*sum(x["pnl"]>0 for x in ts)/len(ts),1),pnl=round(sum(x["pnl"] for x in ts),2),pct=round(100*sum(x["pnl"] for x in ts)/CAP,2),R=round(sum(x["R"] for x in ts),2),
        entradas=sorted({x["ent"].strftime("%H:%M") for x in ts})[:3] if a==9 else None))
# tipos de salida
ex=defaultdict(lambda:[0,0.0])
for t in T:
    k="TP" if t["salida"].startswith("Salida PreNY") and t["pnl"]>0 else ("SL" if t["salida"].startswith("Salida PreNY") else t["salida"])
    ex[k][0]+=1; ex[k][1]+=t["pnl"]
# daily returns for sharpe/sortino
dd_=defaultdict(float)
for t in T: dd_[t["sal"].date()]+=t["pnl"]
# build business-day series between first and last
d=first; eqd=CAP; rets=[]
while d<=last:
    if d.weekday()<5:
        p=dd_.get(d,0.0); rets.append(p/eqd); eqd+=p
    d+=dt.timedelta(days=1)
mu=st.mean(rets); sd=st.pstdev(rets); dsd=math.sqrt(sum(min(0,r)**2 for r in rets)/len(rets))
days_span=(T[-1]["sal"].date()-first).days
ret_tot=(eq-CAP)/CAP
cagr=(eq/CAP)**(365/days_span)-1
hist=defaultdict(int)
for t in T:
    b=round(t["R"]*4)/4  # bins de 0,25R
    hist[b]+=1
dur_w=st.mean(t["bars"] for t in wins); dur_l=st.mean(t["bars"] for t in loss)
out=dict(
  n=len(T), n_total=181, n_excl=181-len(T), cap=CAP, eq_final=round(eq,2), pnl=round(eq-CAP,2), ret_pct=round(ret_tot*100,2),
  wr=round(100*len(wins)/len(T),2), nw=len(wins), nl=len(loss), pf=round(gw/gl,2), gw=round(gw,2), gl=round(gl,2),
  avg_w=round(gw/len(wins),2), avg_l=round(-gl/len(loss),2), payoff=round((gw/len(wins))/(gl/len(loss)),2),
  exp_usd=round((eq-CAP)/len(T),2), R_tot=round(sum(t["R"] for t in T),2), R_avg=round(st.mean(t["R"] for t in T),3),
  R_w=round(st.mean(t["R"] for t in wins),2), R_l=round(st.mean(t["R"] for t in loss),2),
  mdd_pct=round(mdd*100,2), mdd_usd=round(ddinfo["peak"]-ddinfo["trough"],2),
  mdd_peak=ddinfo["peak_t"].strftime("%d/%m/%Y"), mdd_trough=ddinfo["trough_t"].strftime("%d/%m/%Y"),
  mdd_rec=rec["sal"].strftime("%d/%m/%Y") if rec else None,
  mdd_rec_days=(rec["sal"].date()-ddinfo["trough_t"].date()).days if rec else None,
  mdd_total_days=(rec["sal"].date()-ddinfo["peak_t"].date()).days if rec else None,
  mdd_rec_trades=(rec["n"] and sum(1 for t in T if ddinfo["trough_t"]<t["sal"]<=rec["sal"])) if rec else None,
  recovery_factor=round((eq-CAP)/(ddinfo["peak"]-ddinfo["trough"]),2), calmar=round(cagr/mdd,2), cagr=round(cagr*100,1),
  sharpe=round(mu/sd*math.sqrt(252),2), sortino=round(mu/dsd*math.sqrt(252),2),
  streak_w=streaks(True), streak_l=streaks(False),
  weeks_n=len(weeks), weeks_cal=nweeks_cal, trades_week=round(len(T)/nweeks_cal,2), trades_week_active=round(len(T)/len(weeks),2),
  wk_pos=sum(w["pnl"]>0 for w in weeks), wk_neg=sum(w["pnl"]<0 for w in weeks), wk_zero=sum(w["pnl"]==0 for w in weeks),
  best_week=max(weeks,key=lambda w:w["pnl"]), worst_week=min(weeks,key=lambda w:w["pnl"]),
  dur_avg=round(st.mean(t["bars"] for t in T),1), dur_med=st.median(t["bars"] for t in T), dur_w=round(dur_w,1), dur_l=round(dur_l,1),
  long=dict(n=sum(t["dir"]=="BUY" for t in T),wr=round(100*sum(t["dir"]=="BUY" and t["pnl"]>0 for t in T)/sum(t["dir"]=="BUY" for t in T),1),pnl=round(sum(t["pnl"] for t in T if t["dir"]=="BUY"),2)),
  short=dict(n=sum(t["dir"]=="SELL" for t in T),wr=round(100*sum(t["dir"]=="SELL" and t["pnl"]>0 for t in T)/sum(t["dir"]=="SELL" for t in T),1),pnl=round(sum(t["pnl"] for t in T if t["dir"]=="SELL"),2)),
  exits={k:[v[0],round(v[1],2)] for k,v in ex.items()},
  max_win=round(max(t["pnl"] for t in T),2), max_loss=round(min(t["pnl"] for t in T),2),
  first=first.strftime("%d/%m/%Y"), last=T[-1]["sal"].strftime("%d/%m/%Y"),
  curve=curve, dd=ddser, weeks=weeks, months=months, days=days, hours=hours,
  hist=sorted([[k,v] for k,v in hist.items()]),
  trades=[dict(n=t["n"],d=t["ent"].strftime("%d/%m"),dir=t["dir"],h=t["ent"].strftime("%H:%M"),pnl=round(t["pnl"],2),R=round(t["R"],2)) for t in T],
)
json.dump(out,open("metricas.json","w"),ensure_ascii=False)
for k,v in out.items():
    if k not in("curve","dd","weeks","trades","hist"): print(k,v)
