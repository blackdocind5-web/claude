"""Días hábiles por cuenta aprobada (cadena real) con el motor de pérdida flotante, 26/10/2026."""
import sys, os; AQ = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQ); os.chdir(AQ)
import motor as M
reg = M.C.regla; todo = lambda o: True
RAS = M.rascacielos(); M1 = M.mica(); M05 = M.mica("xau_v4/XAUUSD_sesion_NY_0.5R.csv", 0.5)
A50 = M.alex("Alex con VWAP · Fibo 50% · hasta 10:45")
casos = [("Rascacielos @300", [(RAS, 300, reg)]), ("Rascacielos @500", [(RAS, 500, reg)]), ("Rascacielos @600", [(RAS, 600, reg)]),
         ("Rascacielos @1000", [(RAS, 1000, reg)]), ("Mica 1R @500", [(M1, 500, reg)]), ("Mica 0,5R @1000", [(M05, 1000, reg)]),
         ("Alex F50 10:45 @500", [(A50, 500, reg)]), ("Mica0,5R@250 + Alex@250", [(M05, 250, reg), (A50, 250, reg)]),
         ("Mica1R@500 + Alex@500", [(M1, 500, reg), (A50, 500, reg)]), ("Rasc@500 + Mica0,5R@300", [(RAS, 500, reg), (M05, 300, reg)]),
         ("Rasc@400 + Mica1R@400", [(RAS, 400, reg), (M1, 400, reg)])]
for nom, patas in casos:
    D = M.dias(patas); kw = dict(obj=1250, mll=1000, cons=0.4)
    res, peor = M.cadena(D, **kw); P = [h for r, h in res if r == "pasa"]; Q = [h for r, h in res if r == "quemada"]
    tot = sum(h for _, h in res)
    print(f"{nom:28} intentos {len(res)} pases {len(P)} ({100*len(P)/len(res):.0f}%) | días hábiles por intento: pasa med {sorted(P)[len(P)//2]}, quema med {sorted(Q)[len(Q)//2] if Q else '-'} | DÍAS HÁBILES POR CUENTA APROBADA {tot/len(P):.0f} | evals por pase {len(res)/len(P):.2f} = {len(res)/len(P)*65.3:.0f} USD | peor racha {peor}")
