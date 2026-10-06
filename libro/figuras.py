"""Gráficos del libro. Todos los datos provienen del informe (Cuadros 1-10, Figuras 1, 3, 5, 6)
o de ejemplos didácticos del propio libro. Tamaño pensado para Kobo Libra Colour (en A4 se escalan con \\figescala)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from scipy.stats import norm

AZUL, ROJO, VERDE, GRIS, ORO, MORADO = "#1d4e9e", "#d0421b", "#1f8a3c", "#555555", "#c98a00", "#7b2f9e"
plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5,
    "legend.fontsize": 6.8, "xtick.labelsize": 7, "ytick.labelsize": 7, "lines.linewidth": 1.8,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#d8d8d8",
    "grid.linewidth": 0.5, "axes.edgecolor": "#222222", "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    "legend.frameon": False,
})
W, H = 3.4, 2.45
def fig(w=W, h=H): return plt.subplots(figsize=(w, h))
def save(f, name): f.savefig(f"fig/{name}.pdf"); plt.close(f)
def ejes0(ax): ax.axhline(0, color="#222", lw=0.7);

# ---------- Cap 2: capitalización
f, ax = fig()
t = np.linspace(0, 10, 200); r = 0.10
ax.plot(t, 100*(1+r*t), color=GRIS, ls="--", label="Simple: $100(1+rt)$")
tt = np.arange(0, 11); ax.step(tt, 100*(1+r)**tt, where="post", color=AZUL, label="Compuesta anual: $100(1+r)^t$")
ax.plot(t, 100*np.exp(r*t), color=ROJO, label="Continua: $100e^{rt}$")
ax.set_xlabel("Años"); ax.set_ylabel("Valor (US\\$)"); ax.set_title("Crecimiento de US\\$ 100 al 10 % anual")
ax.legend(loc="upper left"); save(f, "capitalizacion")

# ---------- Cap 2: factor de descuento
f, ax = fig()
t = np.linspace(0, 30, 300)
for rr, c in [(0.04, AZUL), (0.097, ROJO)]:
    ax.plot(t, np.exp(-rr*t), color=c, label=f"$r$ = {rr*100:.1f} %")
ax.set_xlabel("Plazo $t$ (años)"); ax.set_ylabel("Factor de descuento $DF(t)$")
ax.set_title("Valor hoy de US\\$ 1 recibido en $t$ (descuento continuo)"); ax.legend(); ax.set_ylim(0, 1.02); save(f, "descuento")

# ---------- Cap 2: curvas cupón cero del informe
f, ax = fig()
ts = [0.25, 1, 2, 3]; zs = [3.90, 3.97, 4.52, 5.03]; zu = [4.14, 4.50, 4.72, 4.80]
ax.plot(ts, zs, "o-", color=ROJO, label="Soberana en S/ (SBS)")
ax.plot(ts, zu, "s--", color=AZUL, label="Swaps SOFR en US\\$")
for x, y in zip(ts, zs): ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(4, -10), fontsize=6.5, color=ROJO)
for x, y in zip(ts, zu): ax.annotate(f"{y:.2f}", (x, y), textcoords="offset points", xytext=(-6, 6), fontsize=6.5, color=AZUL)
ax.set_xlabel("Plazo (años)"); ax.set_ylabel("Tasa (%)"); ax.set_title("Puntos de curva usados en el informe (28-set-2026)")
ax.legend(loc="lower right"); ax.set_ylim(3.6, 5.3); save(f, "curvas")

# ---------- Cap 3: duración y convexidad (ejemplo didáctico)
def precio_bono(y, cup=0.05, n=20, VN=100):
    t = np.arange(1, n+1); return (cup*VN/(1+y)**t).sum() + VN/(1+y)**n
ys = np.linspace(0.02, 0.16, 200); P = np.array([precio_bono(y) for y in ys])
y0 = 0.097; P0 = precio_bono(y0); dy = 1e-5
Dmod = -(precio_bono(y0+dy)-precio_bono(y0-dy))/(2*dy)/P0
f, ax = fig()
ax.plot(ys*100, P, color=AZUL, label="Precio exacto")
ax.plot(ys*100, P0*(1-Dmod*(ys-y0)), color=ROJO, ls="--", label=f"Aproximación por duración ($D_{{mod}}$={Dmod:.1f})")
ax.plot(y0*100, P0, "ko", ms=4); ax.annotate("Rendimiento 9.7 %", (y0*100, P0), xytext=(10.5, 85), arrowprops=dict(arrowstyle="->", lw=0.7))
ax.set_xlabel("Rendimiento exigido $y$ (%)"); ax.set_ylabel("Precio (por 100 de valor nominal)")
ax.set_title("Bono de 20 años, cupón 5 %: precio vs rendimiento"); ax.legend(loc="upper right"); save(f, "duracion")

# ---------- Cap 3: asimetría TC (sección 2 del informe)
f, ax = fig()
S0 = 3.367; N = 4704.0; m = np.linspace(-0.2, 0.2, 200)
res = N/S0 - N/(S0*(1+m))
ax.plot(m*100, res, color=AZUL, label="Exacto: $N/S_0 - N/S_1$")
ax.plot(m*100, N/S0*m, color=ROJO, ls="--", label="Lineal: $(N/S_0)\\times\\Delta\\%$")
for mm in [-0.1, 0.1]:
    v = N/S0 - N/(S0*(1+mm)); ax.plot(mm*100, v, "ko", ms=4)
    ax.annotate(f"{v:+.1f}", (mm*100, v), xytext=(6 if mm > 0 else 6, -12 if mm > 0 else 0), textcoords="offset points", fontsize=7)
ejes0(ax); ax.set_xlabel("Variación del tipo de cambio S/ por US\\$ (%)"); ax.set_ylabel("Resultado (US\\$ millones)")
ax.set_title("Pasivo de S/ 4,704 MM: efecto de un cambio del TC"); ax.legend(loc="upper left"); save(f, "asimetria_tc")

# ---------- Cap 4: posiciones largas y cortas (spot)
f, ax = fig()
S = np.linspace(60, 120, 100); S0_ = 90
ax.plot(S, S-S0_, color=AZUL, label="Largo: compró a 90")
ax.plot(S, S0_-S, color=ROJO, ls="--", label="Corto: vendió a 90")
ejes0(ax); ax.axvline(S0_, color=GRIS, lw=0.6, ls=":")
ax.set_xlabel("Precio futuro del activo $S_T$ (US\\$)"); ax.set_ylabel("Ganancia por unidad (US\\$)")
ax.set_title("Posición larga y posición corta"); ax.legend(); save(f, "largo_corto")

# ---------- Cap 5: forward payoff
f, ax = fig()
K = 89.38; S = np.linspace(60, 120, 100)
ax.plot(S, S-K, color=AZUL, label="Forward largo: $S_T-K$")
ax.plot(S, K-S, color=ROJO, ls="--", label="Forward corto: $K-S_T$")
ejes0(ax); ax.axvline(K, color=GRIS, lw=0.6, ls=":"); ax.text(K+1, -28, "$K$ = 89.38", fontsize=7)
ax.set_xlabel("Precio del subyacente al vencimiento $S_T$"); ax.set_ylabel("Payoff por barril (US\\$)")
ax.set_title("Payoff de un forward al vencimiento"); ax.legend(loc="upper left"); save(f, "forward_payoff")

# ---------- Cap 5: cobertura con forward corto
f, ax = fig()
ax.plot(S, S-92.60, color=ROJO, label="Inventario (vs 92.60)")
ax.plot(S, K-S, color=GRIS, ls=":", label="Forward corto a 89.38")
ax.plot(S, (S-92.60)+(K-S), color=AZUL, lw=2.4, label="Inventario + forward")
ejes0(ax); ax.set_xlabel("$S_T$ (US\\$/bl)"); ax.set_ylabel("US\\$ por barril")
ax.set_title("Una posición larga cubierta con un forward corto"); ax.legend(loc="upper left"); save(f, "cobertura_forward")

import json, pandas as pd
CAP = json.load(open("v2/capas.json")); RR, SIG = CAP["r"], CAP["sig"]
TE = 79/365; KC = CAP["capas"][2]["kc"]; KP = 77.90
REPO = "/home/claude/dlumior/tc-derivados-petroperu/data/mercado/"

# ---------- Cap 5: NDF del informe (Cuadro 6)
Sc, F = 3.4367, 3.4347; Nn = 750.7
ST = np.linspace(3.0, 3.9, 200)
f, ax = fig()
ax.plot(ST, Nn/Sc - Nn/ST, color=ROJO, label="CxP en S/ (resultado)")
ax.plot(ST, Nn/ST - Nn/F, color=VERDE, ls="--", label="NDF compra de S/")
ax.plot(ST, Nn/Sc - Nn/F + 0*ST, color=AZUL, lw=2.4, label="Neto = $N(1/S_0-1/F)$")
ejes0(ax); ax.axvline(Sc, color=GRIS, lw=0.6, ls=":")
ax.set_xlabel("TC al vencimiento $S_T$ (S/ por US\\$)"); ax.set_ylabel("US\\$ millones")
ax.set_title("NDF de S/ 750.7 MM a 91 días"); ax.legend(loc="lower right"); save(f, "ndf")

# ---------- Cap 6: estructura de futuros WTI (tira completa, 28-sep-2026)
strip = pd.read_csv(REPO+"cl_strip_yahoo_2026-09-28.csv").iloc[:13]
mes = {"F":"ene","G":"feb","H":"mar","J":"abr","K":"may","M":"jun","N":"jul","Q":"ago","U":"set","V":"oct","X":"nov","Z":"dic"}
etq = [mes[c[2]]+"-"+c[3:5] for c in strip.simbolo]
f, ax = fig()
ax.plot(range(len(strip)), strip.settle_2026_09_28, "o-", color=ROJO, ms=3, label="Futuros CL (backwardation)")
ax.axhline(89.38, color=AZUL, ls="--", lw=1.2, label="Swap: promedio nov–ene = 89.38")
for i_, v in enumerate(strip.settle_2026_09_28[:3]): ax.annotate(f"{v:.2f}", (i_, v), xytext=(5, 3), textcoords="offset points", fontsize=6.8)
ax.annotate(f"{strip.settle_2026_09_28.iloc[11]:.2f}", (11, strip.settle_2026_09_28.iloc[11]), xytext=(-8, 6), textcoords="offset points", fontsize=6.8)
ax.set_xticks(range(0, len(strip), 2)); ax.set_xticklabels(etq[::2], fontsize=6.5); ax.set_ylabel("US\\$/bl")
ax.set_title("Curva de futuros del WTI al 28-set-2026"); ax.legend(loc="lower left"); save(f, "curva_futuros")

# ---------- Cap 6: contango vs backwardation (didáctico)
f, ax = fig()
T = np.linspace(0, 1, 50); S0b = 80
ax.plot(T*12, S0b*np.exp((0.04+0.03-0.0)*T), color=AZUL, label="Contango: $r+u>y$")
ax.plot(T*12, S0b*np.exp((0.04-0.30)*T), color=ROJO, ls="--", label="Backwardation: $y>r+u$")
ax.set_xlabel("Vencimiento del futuro (meses)"); ax.set_ylabel("Precio futuro $F_{0,T}$"); ax.set_title("$F_{0,T}=S_0e^{(r+u-y)T}$, con $S_0$ = 80")
ax.legend(); save(f, "contango")

# ---------- Cap 8: payoffs y profit de opciones
S = np.linspace(50, 130, 300); Kx = 90; c, p = 6.0, 5.0
f, axs = plt.subplots(2, 2, figsize=(3.4, 3.2), sharex=True)
casos = [("Call comprada", np.maximum(S-Kx, 0), -c), ("Put comprada", np.maximum(Kx-S, 0), -p),
         ("Call vendida", -np.maximum(S-Kx, 0), c), ("Put vendida", -np.maximum(Kx-S, 0), p)]
for ax, (t_, pay, prem) in zip(axs.flat, casos):
    ax.plot(S, pay, color=AZUL, lw=1.6, label="Payoff"); ax.plot(S, pay+prem, color=ROJO, ls="--", lw=1.4, label="Profit")
    ejes0(ax); ax.set_title(t_, fontsize=7.5); ax.set_ylim(-42, 42); ax.tick_params(labelsize=6)
axs[0, 0].legend(fontsize=6, loc="upper left")
for ax in axs[1]: ax.set_xlabel("$S_T$", fontsize=7)
f.suptitle("$K$ = 90; prima call = 6, prima put = 5", fontsize=7.5, y=1.0); f.tight_layout(); save(f, "opciones_4")

# ---------- Cap 8: protective put
f, ax = fig()
ax.plot(S, S-90, color=GRIS, ls=":", label="Activo solo")
ax.plot(S, np.maximum(S, 80)-90-3, color=AZUL, lw=2.2, label="Activo + put ($K$=80, prima 3)")
ejes0(ax); ax.set_xlabel("$S_T$"); ax.set_ylabel("Ganancia"); ax.set_title("Put protectora: un seguro con deducible"); ax.legend(loc="upper left"); save(f, "put_protectora")

# ---------- Cap 8: construcción del collar
f, ax = fig()
Kp, Kc = 77.90, KC; S = np.linspace(55, 130, 300)
ax.plot(S, np.maximum(Kp-S, 0), color=VERDE, ls="--", lw=1.3, label="Put comprada (77.90)")
ax.plot(S, -np.maximum(S-Kc, 0), color=MORADO, ls="-.", lw=1.3, label=f"Call vendida ({KC:.2f})")
ax.plot(S, np.maximum(Kp-S, 0)-np.maximum(S-Kc, 0), color=AZUL, lw=2.2, label="Collar (suma)")
ejes0(ax); ax.set_xlabel("$S_T$ (US\\$/bl)"); ax.set_ylabel("Payoff por barril"); ax.set_title("Collar de costo cero, capa de enero")
ax.legend(loc="lower left"); save(f, "collar_construccion")

# ---------- Cap 9: árbol binomial (didáctico de un paso y dos pasos)
def arbol(nombre, S0, u, d, n, K, r, dt, tipo="put", futuro=False, et="S"):
    q = ((1.0 if futuro else np.exp(r*dt))-d)/(u-d); f, ax = plt.subplots(figsize=(3.4, 2.6)); ax.axis("off")
    V = {}
    for j in range(n+1):
        s = S0*u**j*d**(n-j); V[(n, j)] = max(K-s, 0) if tipo == "put" else max(s-K, 0)
    for i in range(n-1, -1, -1):
        for j in range(i+1): V[(i, j)] = np.exp(-r*dt)*(q*V[(i+1, j+1)]+(1-q)*V[(i+1, j)])
    for i in range(n+1):
        for j in range(i+1):
            x, y = i, j-i/2; s = S0*u**j*d**(i-j)
            if i < n:
                for jj in (j, j+1): ax.plot([x, x+1], [y, jj-(i+1)/2], color=GRIS, lw=0.8, zorder=0)
            ax.text(x, y, f"{et}={s:.2f}\nV={V[(i,j)]:.2f}", ha="center", va="center", fontsize=6.6,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=AZUL if i < n else ROJO, lw=0.9))
    ax.set_xlim(-0.45, n+0.45); ax.set_ylim(-(n/2)-0.5, n/2+0.5)
    ax.set_title(f"$u$={u:.4f}, $d$={d:.4f}, $q$={q:.4f}", fontsize=7.5)
    save(f, nombre); return V[(0, 0)], q
v1 = arbol("arbol1", 100, 1.2, 0.8, 1, 100, 0.0, 1, "put")
v2 = arbol("arbol2", 86.54, np.exp(SIG*np.sqrt(TE/2)), 1/np.exp(SIG*np.sqrt(TE/2)), 2, 77.90, RR, TE/2, "put", futuro=True, et="F")
print("arbol1", v1, "arbol2", v2)

# convergencia binomial
def binom_put_fut(F,K,s,T,r,n):
    dt=T/n; u=np.exp(s*np.sqrt(dt)); d=1/u; q=(1-d)/(u-d); j=np.arange(n+1)
    V=np.maximum(K-F*u**j*d**(n-j),0)
    for i in range(n): V=np.exp(-r*dt)*(q*V[1:]+(1-q)*V[:-1])
    return V[0]
ns=np.arange(1,101); vb=[binom_put_fut(86.54,77.90,SIG,TE,RR,n) for n in ns]
f, ax = fig(); ax.plot(ns, vb, color=AZUL, lw=1.0, marker="o", ms=1.5, label="Árbol binomial con $n$ pasos")
ax.axhline(4.8539, color=ROJO, ls="--", label="Black (1976): 4.85")
ax.set_xlabel("Número de pasos $n$"); ax.set_ylabel("Prima de la put (US\\$/bl)"); ax.set_title("El árbol converge al modelo de Black"); ax.legend(); save(f, "convergencia")
print("binom n=2.50.100", vb[1], vb[49], vb[99])

# ---------- Cap 9: precio Black vs F
def black(F, K, s, T, r, cp):
    d1 = (np.log(F/K)+s*s*T/2)/(s*np.sqrt(T)); d2 = d1-s*np.sqrt(T); D = np.exp(-r*T)
    return D*(F*norm.cdf(d1)-K*norm.cdf(d2)) if cp == "c" else D*(K*norm.cdf(-d2)-F*norm.cdf(-d1))
Fs = np.linspace(55, 120, 300); T, r, sg = TE, RR, SIG
f, ax = fig()
ax.plot(Fs, np.maximum(77.90-Fs, 0), color=GRIS, ls="--", label="Valor intrínseco $\\max(K-F,0)$")
ax.plot(Fs, black(Fs, 77.90, sg, T, r, "p"), color=AZUL, label="Black, $T$ = 79 días")
ax.plot(Fs, black(Fs, 77.90, sg, 20/365, r, "p"), color=ROJO, ls="-.", lw=1.4, label="Black, $T$ = 20 días")
ax.plot(86.54, black(86.54, 77.90, sg, T, r, "p"), "ko", ms=4); ax.annotate("4.85 con F = 86.54", (86.54, 4.85), xytext=(92, 12), arrowprops=dict(arrowstyle="->", lw=0.7))
ax.set_xlabel("Precio del futuro $F$"); ax.set_ylabel("Prima de la put (US\\$/bl)"); ax.set_title("Put de enero, $K$ = 77.90, $\\sigma$ = 56.1 %"); ax.legend(); save(f, "black_put")

# ---------- Cap 9: delta
def delta(F, K, s, T, r, cp):
    d1 = (np.log(F/K)+s*s*T/2)/(s*np.sqrt(T)); D = np.exp(-r*T)
    return D*norm.cdf(d1) if cp == "c" else -D*norm.cdf(-d1)
f, ax = fig()
ax.plot(Fs, delta(Fs, 77.90, sg, T, r, "p"), color=VERDE, label="Delta put ($K$=77.90)")
ax.plot(Fs, -delta(Fs, KC, sg, T, r, "c"), color=MORADO, ls="-.", label=f"Delta call vendida ($K$={KC:.2f})")
ax.plot(Fs, delta(Fs, 77.90, sg, T, r, "p")-delta(Fs, KC, sg, T, r, "c"), color=AZUL, lw=2.2, label="Delta del collar")
ax.axvline(86.54, color=GRIS, ls=":", lw=0.7); ejes0(ax)
ax.set_xlabel("Precio del futuro $F$"); ax.set_ylabel("Delta"); ax.set_title("Deltas de las piezas del collar"); ax.legend(loc="lower left"); save(f, "delta")

# ---------- Cap 9: vega/gamma
def gamma(F, K, s, T, r):
    d1 = (np.log(F/K)+s*s*T/2)/(s*np.sqrt(T)); return np.exp(-r*T)*norm.pdf(d1)/(F*s*np.sqrt(T))
def vega(F, K, s, T, r):
    d1 = (np.log(F/K)+s*s*T/2)/(s*np.sqrt(T)); return np.exp(-r*T)*F*norm.pdf(d1)*np.sqrt(T)
f, ax = fig(); ax2 = ax.twinx(); ax2.grid(False); ax2.spines["right"].set_visible(True)
ax.plot(Fs, gamma(Fs, 77.90, sg, T, r), color=AZUL, label="Gamma (eje izq.)")
ax2.plot(Fs, vega(Fs, 77.90, sg, T, r)/100, color=ROJO, ls="--", label="Vega por 1 pp (eje der.)")
ax.set_xlabel("Precio del futuro $F$"); ax.set_ylabel("Gamma"); ax2.set_ylabel("Vega (US\\$ por punto de vol.)")
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1+h2, l1+l2, loc="upper right")
ax.set_title("Gamma y vega de la put $K$ = 77.90"); save(f, "gamma_vega")

# ---------- Cap 10: posición en soles (Figura 1 del informe)
items = ["Efectivo", "CxC comerciales", "Otras CxC", "Otros pasivos financieros", "CxP comerciales", "CxP parte relacionada", "Otras CxP", "Arrendamientos"]
vals = [41.1, 482.3, 467.6, -3824.5, -517.2, -607.8, -740.6, -4.9]
f, ax = plt.subplots(figsize=(3.4, 2.6))
y = np.arange(len(items))[::-1]
ax.barh(y, vals, color=[VERDE if v > 0 else ROJO for v in vals])
for yy, v in zip(y, vals): ax.text(v + (60 if v > 0 else -60), yy, f"{v:,.1f}", va="center", ha="left" if v > 0 else "right", fontsize=6.3)
ax.set_yticks(y); ax.set_yticklabels(items, fontsize=6.5); ax.set_xlim(-5200, 1300); ax.axvline(0, color="#222", lw=0.7)
ax.set_xlabel("S/ millones (activos +, pasivos −)"); ax.set_title("Posición en soles al cierre de 2025: neto S/ (4,704.0) MM"); ax.grid(axis="y", visible=False)
save(f, "posicion_soles")

# ---------- Cap 10: deuda (Figura 3)
items = ["Bonos 2047 (5.625 %)", "Bonos 2032 (4.750 %)", "BN en S/ (5.55 %)", "CESCE (3.285 %)", "Bancarios c. plazo", "Parte relac. MEF"]
vals = [2111, 996, 1118, 705, 227, 1272]; cols = [AZUL, AZUL, ROJO, AZUL, ROJO, VERDE]
f, ax = plt.subplots(figsize=(3.4, 2.2)); y = np.arange(len(items))[::-1]
ax.barh(y, vals, color=cols)
for yy, v in zip(y, vals): ax.text(v+30, yy, f"{v:,}", va="center", fontsize=6.5)
ax.set_yticks(y); ax.set_yticklabels(items, fontsize=6.5); ax.set_xlim(0, 2600); ax.grid(axis="y", visible=False)
ax.set_xlabel("US\\$ millones (valor en libros)"); ax.set_title("Deuda al cierre de 2025: US\\$ 6,429.0 MM, toda a tasa fija")
save(f, "deuda")

# ---------- Cap 11: flujos CCS por año (Cuadro 4)
f, ax = fig()
anios = ["2026", "2027", "2028"]; recS = [51.0, 1411.6, 2619.4]; payU = [15.7, 413.9, 763.4]
x = np.arange(3); ax.bar(x-0.2, [v/3.4367 for v in recS], 0.38, color=ROJO, label="Recibe S/ (en US\\$ al TC 3.4367)")
ax.bar(x+0.2, payU, 0.38, color=AZUL, label="Paga US\\$")
for xi, a, b in zip(x, recS, payU):
    ax.text(xi-0.2, a/3.4367+8, f"{a/3.4367:.1f}", ha="center", fontsize=6.2)
    ax.text(xi+0.2, b+8, f"{b:.1f}", ha="center", fontsize=6.2)
ax.set_xticks(x); ax.set_xticklabels(anios); ax.set_ylim(0, 900); ax.set_ylabel("US\\$ millones"); ax.set_title("Flujos del CCS por año calendario"); ax.legend(loc="upper left")
save(f, "ccs_anual")

# ---------- Cap 11: saldo del préstamo BN (cronograma supuesto: solo intereses hasta jun-27 + 18 cuotas)
cr = pd.read_csv("v2/cron_bn.csv"); B = [3765.59] + list((cr.saldo_inicial - cr.amortizacion)/1e3)
f, ax = fig()
ax.plot(range(37), B, color=ROJO, marker="o", ms=1.8, label="Saldo (S/ MM)")
ax.axvspan(0, 18, color=ORO, alpha=0.10, lw=0); ax.text(9, 700, "Solo intereses\n(S/ 17.0 MM al mes)", ha="center", fontsize=6.5, color=ORO)
ax.text(30, 2300, "18 cuotas de\nS/ 218.3 MM", ha="center", fontsize=6.5, color=ROJO)
ax.axvline(9, color=GRIS, ls=":", lw=0.8); ax.annotate("Valorización: 28-set-2026\n27 pagos por delante", (9, B[9]), xytext=(11, 2300), fontsize=6.5, arrowprops=dict(arrowstyle="->", lw=0.7))
ax.set_xlabel("Mes (1 = enero 2026; 36 = diciembre 2028)"); ax.set_ylabel("S/ millones"); ax.set_ylim(0, 4200); ax.set_title("Cronograma supuesto del préstamo del BN"); ax.legend(loc="upper right")
save(f, "saldo_bn")

# ---------- Cap 11: escenarios E1 (Figura 5)
Sm = 3.4379; TC = np.linspace(3.0, 3.85, 200)
f, ax = fig()
for pos, c_, ls, lab in [(4704.0, ROJO, "-", "Sin cobertura (S/ 4,704.0)"), (938.4, ORO, "--", "Solo CCS (S/ 938.4)"), (187.7, AZUL, "-", "CCS + NDF (S/ 187.7)")]:
    ax.plot(TC, pos/Sm-pos/TC, color=c_, ls=ls, lw=2.4 if pos < 200 else 1.8, label=lab)
ejes0(ax); ax.axvline(Sm, color=GRIS, ls=":", lw=0.7)
ax.set_xlabel("Tipo de cambio al cierre (S/ por US\\$)"); ax.set_ylabel("US\\$ millones"); ax.set_title("E1: resultado cambiario según el TC"); ax.legend(loc="upper left")
save(f, "e1_escenarios")

# ---------- Cap 12: E2 perfiles (modelo del informe: 80 % cubierto, 3 capas, 20 % abierto)
capas = CAP["capas"]; S0w = 92.60; QT = 2.901; QC = QT*0.80; PSW = (92.60+89.01+86.54)/3
def neto(st, e):
    ab = (st-S0w)*(QT-QC)
    if e == "sin": return (st-S0w)*QT
    if e == "swap": return (PSW-S0w)*QC + ab
    if e == "collar": return sum(min(max(st, c["kp"]), c["kc"])-S0w for c in capas)*QC/3 + ab
    if e == "put": return sum(max(st, c["kp"])-S0w-c["prima"] for c in capas)*QC/3 + ab
    return 0.5*neto(st, "swap")+0.5*neto(st, "collar")
S = np.linspace(55, 130, 300)
f, ax = plt.subplots(figsize=(3.4, 2.7))
for e, c_, ls, lw, lab in [("sin", ROJO, "-", 1.6, "Sin cobertura"), ("swap", GRIS, ":", 1.6, "Solo swap 89.38 (80 %)"),
                           ("collar", VERDE, "--", 1.6, "Solo collar 3 capas (80 %)"), ("put", MORADO, "-.", 1.2, "Solo put, prima pagada (80 %)"),
                           ("mix", AZUL, "-", 2.6, "Propuesta 50 % + 50 %")]:
    ax.plot(S, [neto(x, e) for x in S], color=c_, ls=ls, lw=lw, label=lab)
ejes0(ax); ax.axvline(S0w, color=GRIS, lw=0.6, ls=":")
ax.set_xlabel("WTI al vencimiento (US\\$/bl)"); ax.set_ylabel("US\\$ millones"); ax.set_title("E2: resultado sobre el inventario de 2.901 MMbl")
ax.legend(loc="upper left", fontsize=6.0); ax.set_ylim(-110, 110); save(f, "e2_escenarios")
print("E2 check", [round(neto(S0w*0.7, e), 1) for e in ("sin", "swap", "collar", "put", "mix")], round(neto(S0w*1.3, "mix"), 1))

# ---------- Cap 12: las tres capas del collar
f, ax = fig()
for i_, (c, m_) in enumerate(zip(capas, ["nov-26\n(17 días)", "dic-26\n(50 días)", "ene-27\n(79 días)"])):
    ax.plot([i_, i_], [c["kp"], c["kc"]], color=VERDE, lw=7, alpha=0.35, solid_capstyle="butt")
    ax.plot(i_, c["F"], "o", color=ROJO, ms=5, label="Futuro $F$" if i_ == 0 else None)
    ax.plot(i_, c["kp"], "^", color=AZUL, ms=5, label="Piso (put al 90 % de $F$)" if i_ == 0 else None)
    ax.plot(i_, c["kc"], "v", color=MORADO, ms=5, label="Techo (call de igual prima)" if i_ == 0 else None)
    ax.text(i_+0.12, c["kp"]-0.4, f"{c['kp']:.2f}", fontsize=6.5, va="top"); ax.text(i_+0.12, c["kc"]+0.4, f"{c['kc']:.2f}", fontsize=6.5)
    ax.text(i_+0.12, c["F"], f"{c['F']:.2f}", fontsize=6.5, va="center", color=ROJO)
ax.set_xticks(range(3)); ax.set_xticklabels(["nov-26\n(17 días)", "dic-26\n(50 días)", "ene-27\n(79 días)"]); ax.set_xlim(-0.4, 2.7); ax.set_ylim(62, 108)
ax.set_ylabel("US\\$/bl"); ax.set_title("Programa rodante: piso y techo de cada capa"); ax.legend(loc="lower left", fontsize=6.2); save(f, "capas")

# ---------- Cap 10: historia TC y WTI (Figura 2 del informe)
h = pd.read_csv(REPO+"bcrp_mensual_tc_wti.csv"); xh = pd.to_datetime(h.fecha)
f, (a1, a2) = plt.subplots(2, 1, figsize=(3.4, 3.0), sharex=True)
a1.plot(xh, h.tc_bancario_promedio, color=AZUL); a1.set_title("Tipo de cambio (S/ por US\\$)", fontsize=7.5, loc="left")
a2.plot(xh, h.wti_promedio, color=ROJO); a2.set_title("Petróleo WTI (US\\$ por barril)", fontsize=7.5, loc="left")
for a in (a1, a2): a.axvspan(pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31"), color=GRIS, alpha=0.15, lw=0)
a1.text(pd.Timestamp("2025-02-15"), a1.get_ylim()[1]*0.995, "2025", fontsize=6.5, va="top", color=GRIS)
f.tight_layout(); save(f, "historia")
r_tc = np.diff(np.log(h.tc_bancario_promedio)); r_w = np.diff(np.log(h.wti_promedio))
print("vol hist", r_tc.std(ddof=1)*np.sqrt(12), r_w.std(ddof=1)*np.sqrt(12))

# ---------- Cap 4/13: perfil de exposición del CCS
pf = pd.read_csv("v2/perfil_ccs.csv")
f, ax = fig()
ax.plot(pf.t*12, pf.pfe99/1e3, color=ROJO, label="PFE al 99 %")
ax.plot(pf.t*12, pf.pfe95/1e3, color=ORO, ls="--", label="PFE al 95 %")
ax.plot(pf.t*12, pf.epe/1e3, color=AZUL, lw=2.2, label="EPE (exposición esperada)")
ax.set_xlabel("Meses desde la valorización"); ax.set_ylabel("US\\$ millones"); ax.set_title("Exposición futura del CCS (pasivo de PETROPERÚ)")
ax.legend(loc="upper right"); save(f, "perfil_ccs")
print("pfe max", pf.pfe99.max()/1e3, pf.pfe95.max()/1e3, pf.epe.max()/1e3, pf.t[pf.pfe99.idxmax()]*12)

# ---------- Cap 13: varianza: cobertura y caja (Froot) didáctico - omitido
print("ok")
