# Regalias_Webpage — Tablero de seguimiento DATECOL 4.0 (UNIMINUTO)

Sitio estático (HTML + JS, sin dependencias externas) que muestra: datos técnicos del
proyecto, labores de UNIMINUTO y coinvestigadores, cronograma jul-2026 – jun-2027 con
Gantt, resultados del análisis de datos IPSE (Track B), plan de formación e informes de
actividad.

## Estructura

```
Regalias_Webpage/
├── index.html              # tablero (single-page, lee los JSON de data/)
├── data/
│   ├── proyecto.json       # datos técnicos, equipo, avances, selección de cabecera (EDITABLE)
│   ├── actividades.json    # generado desde el cronograma xlsx
│   ├── resultados.json     # generado desde resumen_comparativo.csv (Track B)
│   ├── formacion.json      # generado desde plan_capacitacion_telemetria.xlsx
│   └── informes.json       # índice de informes (EDITABLE: una entrada por informe)
├── informes/               # informes por actividad (.md) + plantilla_informe.md
├── assets/figuras/         # figuras del Track B (consolidado + Acandí)
├── assets/logos/           # logos oficiales extraídos del doc técnico (DATECOL, MinCiencias, SGR, Colombia)
│   └── aliadas/            # colocar aquí los logos de las IES aliadas (PNG) y añadirlos al bloque "logos" de proyecto.json
└── scripts/exportar_datos.py  # regenera los JSON desde las fuentes
```

## Flujo de actualización

1. Actualizar estado/avance de actividades en `../cronograma_DATECOL_UNIMINUTO.xlsx`.
2. Escribir el informe de la actividad en `informes/` (copiar `plantilla_informe.md`)
   y añadir su entrada en `data/informes.json`.
3. Regenerar los JSON: `python scripts/exportar_datos.py` (requiere `pandas`, `openpyxl`).
4. `git add -A && git commit -m "avance AAAA-MM" && git push` — GitHub Pages se
   actualiza solo en 1–2 minutos.

## Ver localmente

`fetch()` no funciona abriendo `index.html` con doble clic (bloqueo `file://`). Servir así:

```bash
cd Regalias_Webpage
python -m http.server 8000
# abrir http://localhost:8000
```

## Publicar en GitHub Pages (usuario: ElieCartan)

Una sola vez:

```bash
cd Regalias_Webpage
git init -b main
git add -A
git commit -m "Tablero DATECOL 4.0 - version inicial"
# crear el repo vacío en https://github.com/new  (nombre sugerido: datecol40-tablero, público)
git remote add origin https://github.com/ElieCartan/datecol40-tablero.git
git push -u origin main
```

Luego en GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a
branch → Branch: `main` / `(root)` → Save**.

El tablero quedará en: `https://eliecartan.github.io/datecol40-tablero/`

Con GitHub CLI es una línea: `gh repo create datecol40-tablero --public --source=. --push`
y activar Pages en Settings.

> Nota: si el repo es público, todo su contenido lo es. Los CSV crudos de IPSE **no**
> están en esta carpeta (solo agregados y figuras); mantenerlo así salvo autorización.
> Si se requiere privacidad, GitHub Pages sobre repos privados exige plan de pago; la
> alternativa gratuita es compartir el sitio localmente o usar Cloudflare Pages.

## Gobernanza de datos

- Ningún valor del tablero se digita a mano: todo proviene del xlsx del cronograma,
  del CSV comparativo del Track B o del plan de capacitación (trazabilidad en la
  columna/campo `fuente`).
- Los ceros de telemetría se interpretan como cortes de servicio (no como potencia
  válida); Unguía tiene 1.199 marcas faltantes y cambio de medidor el 21-jul-2025.
