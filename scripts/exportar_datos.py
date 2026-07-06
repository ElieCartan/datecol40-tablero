#!/usr/bin/env python3
"""Regenera los JSON del tablero web desde las fuentes locales.

Fuentes:
  - ../cronograma_DATECOL_UNIMINUTO.xlsx  (hoja Cronograma)  -> data/actividades.json
  - ../Claude-Datecol/track_b_datos/tablas/resumen_comparativo.csv -> data/resultados.json
  - plan_capacitacion_telemetria.xlsx (si está junto al cronograma) -> data/formacion.json
Uso:  python scripts/exportar_datos.py   (ejecutar desde Regalias_Webpage/)
"""
import json, sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]      # Regalias_Webpage/
BASE = ROOT.parent                               # DataProyectoUniminuto2025/
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

# ---- actividades.json ----
xlsx = BASE / "cronograma_DATECOL_UNIMINUTO.xlsx"
df = pd.read_excel(xlsx, "Cronograma", header=1)
df = df.dropna(subset=["ID"])
acts = []
for _, r in df.iterrows():
    acts.append({
        "id": str(r["ID"]),
        "frente": str(r["Frente"]),
        "actividad": str(r["Actividad"]),
        "entregable": str(r["Entregable"]),
        "responsable": str(r["Responsable"]),
        "inicio": pd.Timestamp(r["Inicio"]).strftime("%Y-%m-%d"),
        "fin": pd.Timestamp(r["Fin"]).strftime("%Y-%m-%d"),
        "estado": str(r["Estado"]),
        "avance": float(r["% Avance"]),
        "fuente": str(r["Fuente"]),
    })
(DATA / "actividades.json").write_text(
    json.dumps(acts, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"actividades.json: {len(acts)} actividades")

# ---- resultados.json ----
csvp = BASE / "Claude-Datecol/track_b_datos/tablas/resumen_comparativo.csv"
if csvp.exists():
    rc = pd.read_csv(csvp, index_col=0)
    res = {c: {k: (None if pd.isna(v) else round(float(v), 6))
               for k, v in rc[c].items()} for c in rc.columns}
    (DATA / "resultados.json").write_text(
        json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print("resultados.json: ok")
else:
    print("AVISO: no se encontró resumen_comparativo.csv", file=sys.stderr)

# ---- formacion.json ----
plan = None
for cand in [BASE / "plan_capacitacion_telemetria.xlsx", ROOT / "plan_capacitacion_telemetria.xlsx"]:
    if cand.exists():
        plan = cand
        break
if plan:
    cat = pd.read_excel(plan, "Catálogo de Cursos", header=1).dropna(how="all")
    cursos = []
    for _, r in cat.iterrows():
        if pd.isna(r.iloc[0]) and pd.isna(r.iloc[1]):
            continue
        links = [str(x) for x in r.iloc[6:10] if pd.notna(x)]
        cursos.append({
            "categoria": str(r.iloc[0]) if pd.notna(r.iloc[0]) else "",
            "curso": str(r.iloc[1]) if pd.notna(r.iloc[1]) else "",
            "plataforma": str(r.iloc[2]) if pd.notna(r.iloc[2]) else "",
            "costo": str(r.iloc[3]) if pd.notna(r.iloc[3]) else "",
            "enfoque": str(r.iloc[4]) if pd.notna(r.iloc[4]) else "",
            "nivel": str(r.iloc[5]) if pd.notna(r.iloc[5]) else "",
            "enlaces": links,
            "estado": "Pendiente",
        })
    cong = pd.read_excel(plan, "Congresos y Eventos", header=4).dropna(how="all")
    eventos = []
    for _, r in cong.iterrows():
        if pd.isna(r.iloc[0]):
            continue
        eventos.append({
            "evento": str(r.iloc[0]), "entidad": str(r.iloc[1]),
            "espacios": str(r.iloc[2]), "periodicidad": str(r.iloc[3]),
            "relevancia": str(r.iloc[4]),
        })
    (DATA / "formacion.json").write_text(
        json.dumps({"cursos": cursos, "eventos": eventos},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"formacion.json: {len(cursos)} cursos, {len(eventos)} eventos")
else:
    print("AVISO: no se encontró plan_capacitacion_telemetria.xlsx", file=sys.stderr)
