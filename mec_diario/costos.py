"""Costos reales de ejecución por operación (spread y comisiones), medidos contra el stop de cada operación.
Costo en unidades de riesgo: c = costo en precio / distancia del stop (un SL completo = −1 u).
Distancia del stop = 1% del capital al entrar / tamaño de la posición (el sistema arriesga exactamente 1%)."""
import csv, glob, json, os, sys
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import diario as Dd
B = Dd.B

PIP = {"EURUSD": 0.0001, "GBPUSD": 0.0001}


def stops():
    """(activo, hora de entrada) -> (precio, distancia del stop)."""
    out = {}
    for f in glob.glob(os.path.join(RAIZ, "mec_hibrida", "datos", "*_m1_2025-2026_*.csv")):
        if f.endswith(("_excluidos.csv", "_validos.csv")): continue
        a = os.path.basename(f).split("_")[0]
        for r in csv.DictReader(open(f, encoding="utf-8-sig")):
            if not r["Tipo"].startswith("Entrada"): continue
            pnl = float(r["PyG netas USD"]); eq = 1000 + float(r["PyG acumuladas USD"]) - pnl
            out[(a, r["Fecha y hora"])] = (float(r["Precio USD"]), 0.01 * eq / float(r["Tamaño (cant.)"]))
    return out


# Escenarios: costo ida y vuelta en precio, por activo. fee_btc = comisión ida y vuelta en % del nocional.
ESC = {
    "Sin costos (backtest)": dict(XAUUSD=0, EURUSD=0, GBPUSD=0, BTC_spread=0, fee_btc=0),
    "Spreads Multibank, sin comisión": dict(XAUUSD=0.02, EURUSD=0.1 * PIP["EURUSD"], GBPUSD=0.5 * PIP["GBPUSD"], BTC_spread=0.5, fee_btc=0),
    "Spreads + comisión ECN 6 USD/lote": dict(XAUUSD=0.02 + 0.06, EURUSD=0.7 * PIP["EURUSD"], GBPUSD=1.1 * PIP["GBPUSD"], BTC_spread=0.5, fee_btc=0),
    "Spreads + comisión ECN + BTC Bybit (maker 0,02% + maker 0,02%)": dict(XAUUSD=0.08, EURUSD=0.7 * PIP["EURUSD"], GBPUSD=1.1 * PIP["GBPUSD"], BTC_spread=0.5, fee_btc=0.04),
    "Spreads + comisión ECN + BTC Bybit (taker 0,055% × 2)": dict(XAUUSD=0.08, EURUSD=0.7 * PIP["EURUSD"], GBPUSD=1.1 * PIP["GBPUSD"], BTC_spread=0.5, fee_btc=0.11),
}


def aplicar(ts, esc, S):
    out = []
    for t in ts:
        p, d = S[(t["a"], t["ent"].strftime("%Y-%m-%d %H:%M"))]
        c = (esc["BTC_spread"] + esc["fee_btc"] / 100 * p) if t["a"] == "BTCUSD" else esc[t["a"]]
        out.append(dict(t, u=t["u"] - c / d, costo=c / d))
    return out


if __name__ == "__main__":
    S = stops(); ts = Dd.cargar(); res = {}
    for nom, esc in ESC.items():
        T = aplicar(ts, esc, S)
        por = {a: dict(n=sum(t["a"] == a for t in T), costo_R=round(sum(t["costo"] for t in T if t["a"] == a) / max(1, sum(t["a"] == a for t in T)) / 0.9, 3),
                       R_op=round(sum(t["u"] for t in T if t["a"] == a) / 0.9 / max(1, sum(t["a"] == a for t in T)), 3),
                       R25=round(sum(t["u"] for t in T if t["a"] == a and t["ent"].year == 2025) / 0.9, 1),
                       R26=round(sum(t["u"] for t in T if t["a"] == a and t["ent"].year == 2026) / 0.9, 1)) for a in Dd.PRE}
        res[nom] = dict(por_activo=por)
        for b in (1.0, 1.25):
            for sinbtc in (False, True):
                X = [t for t in T if not (sinbtc and t["a"] == "BTCUSD")]
                r = Dd.simular(X, base=b, freno=2.7 * b); m = Dd.montecarlo(X, sims=600, base=b, freno=2.7 * b)
                res[nom][f"{b}{' sin BTC' if sinbtc else ''}"] = dict(r={k: v for k, v in r.items() if k != "niveles"}, mc=m)
        print("==", nom)
        for a, x in por.items(): print("  ", a, x)
        for k, v in res[nom].items():
            if k == "por_activo": continue
            r, m = v["r"], v["mc"]
            print(f"   {k:14} hist {r['cagr']:6} dd {r['mdd']:5} {r['anios']} | MC med {m['cagr_med']} p5 {m['cagr_p5']} dd95 {m['dd_p95']} dd30 {m['p_dd30']} añoneg {m['p_anio_neg']}")
    json.dump(res, open(os.path.join(AQUI, "costos.json"), "w"), ensure_ascii=False)
