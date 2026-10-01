# Series de mercado

CSV descargados por el agente investigador-mercado el **2026-09-30** (fecha de consulta).
Fecha de valorización del informe: **2026-09-28** (último cierre común; ver `data/procesado/mercado.yaml`).
Archivos originales, sin modificar, en `data/raw/mercado_2026-09-30/`.

Formato: series `fecha,valor` (tasas en %, precios en US$/bbl, TC en S/ por US$), salvo curvas/tiras (indicado).

## Tipo de cambio y tasas Perú — BCRP (API `https://estadisticas.bcrp.gob.pe/estadisticas/series/api/<codigo>/csv/2021-01-01/2026-09-30`)

| Archivo | Código | Descripción | Último dato |
|---|---|---|---|
| usdpen_interbancario_compra.csv | PD04637PD | TC interbancario compra | 28-sep-2026 |
| usdpen_interbancario_venta.csv | PD04638PD | TC interbancario venta | 28-sep-2026 |
| tasa_interbancaria_pen.csv | PD04692MD | Tasa interbancaria S/ (%) | 28-sep-2026 |
| tasa_interbancaria_usd.csv | PD04693MD | Tasa interbancaria US$ (%) | 28-sep-2026 |
| soberano10a_pen.csv | PD31893DD | Rend. bono gobierno 10a S/ (%) | 25-sep-2026 |
| soberano10a_usd.csv | PD31894DD | Rend. bono gobierno 10a US$ (%) | 25-sep-2026 |
| wti_bcrp_PD04705XD.csv | PD04705XD | Petróleo WTI (US$/bbl; coincide con settlement NYMEX frente) | 28-sep-2026 |

Días con "n.d." (feriados) se omiten.

## Curvas cupón cero — SBS (Portal Curva Soberana)

Fuente: `https://www.sbs.gob.pe/app/pp/n_CurvaSoberana/CurvaSoberana/ConsultaHistorica`
(endpoint JSON `POST /app/pp/n_CurvaSoberana/BuscarInformacionHistorica`, `{"TipoCurva":..., "FechaInicio":"2026-09-28","FechaFin":"2026-09-29"}`).
Archivos `sbs_curva_<TIPO>_2026-09-28.csv` con columnas `plazo_dias,tasa_pct` (curva del 28-sep-2026):

- CCPSS: Curva Soberana Soles (→ `tasas.pen_1a`, `tasas.pen_3a`)
- CCPEDS: Curva Cupón Cero Dólares Globales (bonos globales Perú en US$)
- CSBCRD: Curva Cupón Cero Dólares Sintética (tasa US$ implícita en forwards USD/PEN locales)
- CCCLD: Curva Cupón Cero "Libor" (curva swap US$ publicada por SBS)
- CBCRS: Curva CDBCRP ; CCSDF: Curva Dólares Corto Plazo

## EE.UU. — FRED (`https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>&cosd=2021-01-01&coed=2026-09-30`)

| Archivo | ID FRED | Último dato |
|---|---|---|
| sofr.csv | SOFR | 28-sep-2026 |
| ust_3m / 1a / 2a / 3a / 5a / 7a / 10a .csv | DGS3MO, DGS1, DGS2, DGS3, DGS5, DGS7, DGS10 | 28-sep-2026 |
| ovx.csv | OVXCLS (CBOE Crude Oil ETF Volatility Index) | 28-sep-2026 |
| brent_spot_fred.csv | DCOILBRENTEU | 22-sep-2026 |

DCOILWTICO no se pudo descargar (FRED devolvió bloqueo anti-bot); se usa EIA RWTC.

## Crudo — EIA (`https://www.eia.gov/dnav/pet/hist_xls/<ID>d.xls`)

- wti_spot_eia.csv: RWTC, WTI spot Cushing FOB (hasta 22-sep-2026; EIA publica semanalmente)
- brent_spot_eia.csv: RBRTE, Brent spot FOB (hasta 22-sep-2026)
- EIA dejó de publicar futuros NYMEX (RCLC1–4) en abr-2024.

## Futuros NYMEX CL / ICE Brent — Yahoo Finance chart API

`https://query1.finance.yahoo.com/v8/finance/chart/<SIMBOLO>?range=<1mo|5y>&interval=1d` (cierre diario = settlement).
CME Group bloquea y prohíbe por sus términos el acceso automatizado a settlements, por lo que se usó esta fuente y se validó contra fuentes independientes:
CLX26 28-sep = 92.60 (= BCRP PD04705XD); CLX26 29-sep = 89.38 y Brent 29-sep = 102.59 (= nota Reuters en Yahoo Finance
`https://finance.yahoo.com/energy/articles/oil-prices-rise-second-session-003313319.html`); tira 29-sep = oilprice.com (último − variación).

- cl_strip_yahoo_2026-09-28.csv: `simbolo,settle_2026_09_28,settle_2026_09_29` (CLX26 … CLV28, 24 vencimientos)
- cl_front_yahoo.csv: CL=F contrato frente continuo, 5 años (incluye saltos de roll)
- brent_front_yahoo.csv: BZ=F, 5 años
- cl_strip_oilprice_2026-09-30.csv: `https://oilprice.com/futures/wti`, consultado 2026-09-30 00:30 (hora Lima);
  `settle_previo = ultimo − variacion` = settlement del 29-sep-2026.

## Swaps SOFR — BlueGamma (no guardado como CSV; valores puntuales en mercado.yaml)

`https://www.bluegamma.io/usd-swap-rates/<n>-year-sofr-swap-rate` y `/3-month-sofr-swap-rate`, cierres del 28-sep-2026
(3M 4.08, 1A 4.50, 2A 4.72, 3A 4.80, 4A 4.80, 5A 4.80, 7A 4.81, 10A 4.86 %). Consultado 2026-09-30.

## Calificaciones (PDF en data/raw/mercado_2026-09-30/)

S&P 28-may-2026 (B-, Negativa); Moody's 18-sep-2026 (Caa1, Positiva); Fitch retiro 09-ene-2026.
Índice: `https://inversionistas.petroperu.com.pe/clasificadoras-de-riesgo/`.

## bcrp_mensual_tc_wti.csv
BCRP, series mensuales PN01210PM (tipo de cambio bancario promedio del periodo, S/ por US$) y PN01660XM
(petróleo WTI, promedio del periodo, US$/bbl), ene-2021 a ago-2026. Consultado 2026-09-30:
https://estadisticas.bcrp.gob.pe/estadisticas/series/api/PN01210PM-PN01660XM/csv/2021-1/2026-9
