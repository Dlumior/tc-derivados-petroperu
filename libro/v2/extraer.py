import sys, json
from pathlib import Path
REPO=Path('/home/claude/dlumior/tc-derivados-petroperu')
sys.path.insert(0,str(REPO/'src')); sys.path.insert(0,str(REPO/'scripts'))
import numpy as np, pandas as pd
import run_all as ra
from derivados import datos, swaps, opciones, fx, riesgo
ex,mk=datos.cargar('exposiciones'),datos.cargar('mercado')
v=lambda k: ex[k].valor; w=lambda k: mk[k].valor
# BN schedule
cron=swaps.cronograma_cuota_constante(v('prestamo_bn.saldo_pen'),v('prestamo_bn.tasa'),18,gracia=18)
print(cron.head(3).round(2)); print(cron.iloc[16:21].round(2)); print(cron.tail(2).round(2))
rem=swaps.cronograma_remanente(cron,9,17)
bid=w('usdpen.spot_bid')
c_pen=ra.curva_sbs('sbs_curva_CCPSS_2026-09-28.csv'); c_usd=ra.curva_sofr(mk)
ccs=swaps.CrossCurrencySwap(rem,bid,0.0); t=ccs.tasa_usd_justa(c_pen,c_usd); ccs=swaps.CrossCurrencySwap(rem,bid,t)
pu=ccs.cron_usd()
print('tasa',t,'VP pen soles',swaps.vp_flujos(rem,c_pen),'VP usd',swaps.vp_flujos(pu,c_usd))
print('cuota usd interes',pu.cuota.iloc[0],'cuota usd amort',pu.cuota.iloc[-1], 'cuota pen', rem.cuota.iloc[0], rem.cuota.iloc[-1])
s0=(bid+w('usdpen.spot_ask'))/2
print('val -10',ccs.valor_usd(c_pen,c_usd,s0*0.9),'+10',ccs.valor_usd(c_pen,c_usd,s0*1.1))
print('i mensual',(1.0555)**(1/12)-1,(1+t)**(1/12)-1)
# curva nodes
for x in [0.25,0.5,1,1.5,2,2.25]:
    print('curva',x, c_pen(x)**(-1/x)-1, c_usd(x)**(-1/x)-1)
# CVA profile
cva=riesgo.cva_ccs(rem,pu,bid,c_pen,c_usd,w('usdpen.vol_implicita_1a'),0.0569,0.6); print('cva',cva)
epe=riesgo.epe_ccs(rem,pu,bid,c_pen,c_usd,w('usdpen.vol_implicita_1a'))
pfe=riesgo.pfe_ccs(rem,pu,bid,c_pen,c_usd,w('usdpen.vol_implicita_1a'),0.99)
pfe95=riesgo.pfe_ccs(rem,pu,bid,c_pen,c_usd,w('usdpen.vol_implicita_1a'),0.95)
pd.DataFrame({'t':epe.t,'epe':epe.epe,'pfe99':pfe.pfe,'pfe95':pfe95.pfe}).to_csv('v2/perfil_ccs.csv',index=False)
rem.to_csv('v2/rem_pen.csv',index=False); pu.to_csv('v2/rem_usd.csv',index=False); cron.to_csv('v2/cron_bn.csv',index=False)
print('epe max',epe.epe.max(),'pfe99 max',pfe.pfe.max())
# E2 capas
dias_op=w('crudo.dias_venc_opciones'); r=fx.tasa_continua_desde_simple(w('tasas.usd_3m'),dias_op); sig=w('crudo.vol_implicita')
print('r',r,'sig',sig)
capas=[]
for F,d in ((92.60,17),(89.01,50),(86.54,79)):
    T=d/365; kp=round(F*0.9,1); kc=opciones.strike_collar_costo_cero(F,kp,T,r,sig,fijo='put')
    capas.append(dict(F=F,d=d,kp=kp,kc=kc,prima=opciones.black76(F,kp,T,r,sig,'put'),delta=opciones.delta_black76(F,kp,T,r,sig,'put')))
for c in capas: print(c)
json.dump(dict(r=r,sig=sig,capas=capas,tasa_ccs=t),open('v2/capas.json','w'),indent=1)
