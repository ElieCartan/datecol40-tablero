#!/usr/bin/env python3
"""Regenera los JSON del tablero web desde las fuentes locales.

Fuentes:
  - ../cronograma_DATECOL_UNIMINUTO.xlsx  (hoja Cronograma)  -> data/actividades.json
  - ../Claude-Datecol/track_b_datos/tablas/resumen_comparativo.csv -> data/resultados.json
  - ../plan_capacitacion_telemetria.xlsx -> data/formacion.json
  - ../Revistas_Publicacion_Fotovoltaica_ZNI.xlsx -> data/revistas.json
Uso:  python scripts/exportar_datos.py   (ejecutar desde Regalias_Webpage/)
"""
import json, sys
from pathlib import Path
from urllib.parse import quote_plus
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
    raw = pd.read_excel(plan, "Congresos y Eventos", header=None)
    estrategia = " ".join(str(v) for v in raw.iloc[1:3, 0] if pd.notna(v))
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
        json.dumps({"cursos": cursos, "eventos": eventos, "estrategia": estrategia},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"formacion.json: {len(cursos)} cursos, {len(eventos)} eventos")
else:
    print("AVISO: no se encontró plan_capacitacion_telemetria.xlsx", file=sys.stderr)

# ---- revistas.json ----
# Mapa curado de URLs (homepage). Scimago usa la búsqueda oficial por nombre
# (determinista); verificar homepage antes de someter.
URLS = {
 "Revista Facultad de Ingeniería Universidad de Antioquia": "https://revistas.udea.edu.co/index.php/ingenieria",
 "Revista Iberoamericana de Automática e Informática Industrial (RIAI)": "https://polipapers.upv.es/index.php/RIAI",
 "Ingeniería e Investigación": "https://revistas.unal.edu.co/index.php/ingeinv",
 "Energies": "https://www.mdpi.com/journal/energies",
 "IEEE Access": "https://ieeeaccess.ieee.org/",
 "Sustainability": "https://www.mdpi.com/journal/sustainability",
 "Frontiers in Energy Research": "https://www.frontiersin.org/journals/energy-research",
 "Global Energy Interconnection": "https://www.sciencedirect.com/journal/global-energy-interconnection",
 "Journal of King Saud University - Science": "https://www.sciencedirect.com/journal/journal-of-king-saud-university-science",
 "Engineering, Technology & Applied Science Research (ETASR)": "https://etasr.com/index.php/ETASR",
 "Journal of Advanced Research in Applied Sciences and Engineering Technology": "https://semarakilmu.com.my/journals/index.php/applied_sciences_eng_tech",
 "Clean Energy": "https://academic.oup.com/ce",
 "Applied Energy": "https://www.sciencedirect.com/journal/applied-energy",
 "Renewable Energy": "https://www.sciencedirect.com/journal/renewable-energy",
 "Solar Energy": "https://www.sciencedirect.com/journal/solar-energy",
 "International Journal of Electrical Power & Energy Systems": "https://www.sciencedirect.com/journal/international-journal-of-electrical-power-and-energy-systems",
 "IEEE Transactions on Sustainable Energy": "https://ieeexplore.ieee.org/xpl/RecentIssue.jsp?punumber=5165391",
}
rev_x = None
for cand in [BASE / "Revistas_Publicacion_Fotovoltaica_ZNI.xlsx", ROOT / "Revistas_Publicacion_Fotovoltaica_ZNI.xlsx"]:
    if cand.exists():
        rev_x = cand
        break
if rev_x:
    rv = pd.read_excel(rev_x, "Propuestas de Revistas", header=2).dropna(how="all")
    revistas = []
    for _, r in rv.iterrows():
        nombre = r.iloc[0]
        if pd.isna(nombre):
            continue
        nombre = str(nombre).strip()
        acceso = str(r.iloc[2]) if pd.notna(r.iloc[2]) else ""
        revistas.append({
            "nombre": nombre,
            "editorial": str(r.iloc[1]) if pd.notna(r.iloc[1]) else "",
            "acceso": acceso,
            "open_access": ("No OA" not in acceso and "Suscripción" not in acceso),
            "cuartil": str(r.iloc[3]) if pd.notna(r.iloc[3]) else "",
            "enfoque": str(r.iloc[4]) if pd.notna(r.iloc[4]) else "",
            "idiomas": str(r.iloc[5]) if pd.notna(r.iloc[5]) else "",
            "apc": str(r.iloc[6]) if pd.notna(r.iloc[6]) else "",
            "ventajas": str(r.iloc[7]) if pd.notna(r.iloc[7]) else "",
            "web": URLS.get(nombre, ""),
            "scimago": "https://www.scimagojr.com/journalsearch.php?q=" + quote_plus(nombre.split("(")[0].strip()),
        })
    (DATA / "revistas.json").write_text(
        json.dumps(revistas, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"revistas.json: {len(revistas)} revistas")
else:
    print("AVISO: no se encontró Revistas_Publicacion_Fotovoltaica_ZNI.xlsx", file=sys.stderr)
