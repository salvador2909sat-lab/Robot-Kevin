import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import requests

# --- TÍTULO Y ESTILO ---
st.set_page_config(page_title="Robot Kevin - Luna Edition", page_icon="🤖")
st.title("🤖 ROBOT KEVIN - Luna Edition")
st.write("Ejecuta desde cualquier lugar, mi amor ❤️")
st.markdown("---")

# --- PRUEBA DE INTERNET ---
def tiene_internet():
    try:
        requests.get("https://www.google.com", timeout=5)
        return True
    except:
        return False

# --- BOTÓN EJECUTAR ---
if st.button("🚀 EJECUTAR ROBOT HOY", type="primary"):
    if not tiene_internet():
        st.error("❌ SIN CONEXIÓN A INTERNET\n\nEl robot necesita WiFi para bajar precios.\nPrueba mañana, mi amor. ❤️")
    else:
        with st.spinner("Descargando datos de 10 acciones..."):
            # --- 10 ACCIONES ---
            acciones = {
                "CEMEXCPO.MX": "CEMEX (~14 MXN)",
                "ALPEKA.MX": "ALPEKA (~18 MXN)",
                "BIMBOA.MX": "BIMBO (~55 MXN)",
                "WALMEX.MX": "WALMEX (~60 MXN)",
                "KIMBERA.MX": "KIMBER (~35 MXN)",
                "TLEVICPO.MX": "TELEVISA (~8 MXN)",
                "GMEXICOB.MX": "GMEXICO (~90 MXN)",
                "AC.MX": "AEROMEX (~140 MXN)",
                "LIVEPOLC-1.MX": "LIVERPOOL (~120 MXN)",
                "GAPB.MX": "GAP (~250 MXN)"
            }

            presupuesto = 250.0

            def kevin_signal(df):
                if len(df) < 3: return False, 0
                row = df.iloc[-1]
                prev1 = df.iloc[-2]
                prev2 = df.iloc[-3]
                ema40 = df['Close'].rolling(40).mean().iloc[-1]
                
                cond1 = prev2['High'] > prev1['High']
                cond2 = prev2['Low'] < prev1['Low']
                cond3 = row['Close'] > prev1['High']
                above_ema = row['Close'] > ema40
                
                if cond1 and cond2 and cond3 and above_ema:
                    atr = df['High'].sub(df['Low']).rolling(21).mean().iloc[-1]
                    return True, atr
                return False, 0

            mejor_accion = None
            mejor_ticker = None
            mejor_entry = 0
            mejor_sl = 0
            mejor_tp = 0
            mejor_cantidad = 0
            mejor_riesgo = float('inf')

            for ticker, nombre in acciones.items():
                try:
                    data = yf.Ticker(ticker).history(period="60d")
                    if data.empty or len(data) < 3: continue
                    data = data[['Open', 'High', 'Low', 'Close']].reset_index()
                    
                    señal, atr = kevin_signal(data)
                    if señal and atr > 0:
                        entry = data['Open'].iloc[-1]
                        if entry <= 0: continue
                        sl = entry - 2 * atr
                        tp = entry + (entry - sl)
                        cantidad = presupuesto / entry
                        riesgo_rel = atr / entry
                        
                        if riesgo_rel < mejor_riesgo:
                            mejor_accion = nombre
                            mejor_ticker = ticker
                            mejor_entry = entry
                            mejor_sl = sl
                            mejor_tp = tp
                            mejor_cantidad = cantidad
                            mejor_riesgo = riesgo_rel
                except: continue

            fecha = datetime.now().strftime('%Y-%m-%d %H:%M')
            resultado = f"🚨 SEÑAL WEB - {fecha}\n\n"

            if mejor_accion:
                costo = min(mejor_cantidad * mejor_entry, presupuesto)
                resultado += f"🎯 **¡COMPRA {mejor_accion}!**\n"
                resultado += f"💰 ENTRADA: ${mejor_entry:.2f} MXN\n"
                resultado += f"🛑 SL: ${mejor_sl:.22f} | 🎯 TP: ${mejor_tp:.2f}\n"
                resultado += f"📊 CANTIDAD: {mejor_cantidad:.2f} acc. | COSTO: ≈${costo:.0f} MXN\n\n"
                resultado += "✅ ¡Ve a Kuspit!"
            else:
                resultado += "😴 **ESPERA** - Ninguna de las 10 tiene señal fuerte hoy.\n"
                resultado += "   Mañana más oportunidades, mi amor."

            st.success(resultado)
            st.download_button("📄 Descargar TXT", resultado, "SEÑAL_WEB_HOY.txt")