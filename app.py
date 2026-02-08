import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# Configuración de página
st.set_page_config(page_title="Simulador de Física Fluido", layout="wide")

st.title("🚀 Lanzamiento Vertical (Versión Pro - Alta Fluidez)")

# --- Parámetros en la barra lateral ---
st.sidebar.header("Configuración")
y0 = st.sidebar.number_input("Altura inicial (m)", value=55.0)
t_total = st.sidebar.number_input("Tiempo de vuelo (s)", value=10.0)
g = 9.81

# Cálculos físicos base
v0 = (0.5 * g * t_total**2 - y0) / t_total
h_max = y0 + (v0**2 / (2 * g))

# Datos precargados para evitar cálculos en el bucle
t_steps = np.linspace(0, t_total, 120)  # Más pasos para mayor suavidad
y_steps = y0 + v0 * t_steps - 0.5 * g * t_steps**2
v_steps = v0 - g * t_steps

# Métricas
c1, c2 = st.columns(2)
c1.metric("Velocidad Inicial", f"{v0:.2f} m/s")
c2.metric("Altura Máxima", f"{h_max:.2f} m")

# --- Lógica de Control de Animación ---
if 'idx' not in st.session_state:
    st.session_state.idx = 0
if 'run' not in st.session_state:
    st.session_state.run = False

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])

def start(): st.session_state.run = True
def stop(): st.session_state.run = False
def reset():
    st.session_state.run = False
    st.session_state.idx = 0

col_btn1.button("▶️ Iniciar", on_click=start)
col_btn2.button("⏸️ Pausar", on_click=stop)
col_btn3.button("🔄 Reiniciar", on_click=reset)

# --- Fragmento de Gráfica (Evita el parpadeo de la web) ---
@st.fragment
def mostrar_animacion():
    # Contenedor para que la gráfica no se mueva de lugar
    placeholder = st.empty()
    
    while st.session_state.run and st.session_state.idx < len(t_steps):
        i = st.session_state.idx
        
        # Crear Figura principal
        fig = go.Figure()

        # 1. Edificio
        fig.add_shape(type="rect", x0=-0.4, y0=0, x1=0.4, y1=y0, fillcolor="#34495e", opacity=0.7)
        
        # 2. Trayectoria
        fig.add_trace(go.Scatter(x=[0]*i, y=y_steps[:i], mode='lines', line=dict(color='red', width=1, dash='dot')))
        
        # 3. Objeto (Bola)
        fig.add_trace(go.Scatter(x=[0], y=[max(0, y_steps[i])], mode='markers+text',
                                 marker=dict(color='red', size=18, line=dict(width=2, color='white')),
                                 text=[f"{v_steps[i]:.1f} m/s"], textposition="top center"))

        fig.update_layout(
            title="Simulación Dinámica",
            xaxis=dict(range=[-1.5, 1.5], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, h_max + 15], title="Altura (m)"),
            height=600,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            template="plotly_white"
        )

        # Actualizar solo el contenedor
        placeholder.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.session_state.idx += 1
        time.sleep(0.01) # Control de FPS (menor tiempo = más rápido/suave)
        
    # Si no está corriendo, mostrar el estado actual
    if not st.session_state.run:
        i = st.session_state.idx if st.session_state.idx < len(t_steps) else len(t_steps)-1
        fig_static = go.Figure()
        fig_static.add_shape(type="rect", x0=-0.4, y0=0, x1=0.4, y1=y0, fillcolor="#34495e", opacity=0.7)
        fig_static.add_trace(go.Scatter(x=[0], y=[max(0, y_steps[i])], mode='markers', marker=dict(color='red', size=18)))
        fig_static.update_layout(xaxis_range=[-1.5, 1.5], yaxis_range=[0, h_max + 15], height=600, template="plotly_white")
        placeholder.plotly_chart(fig_static, use_container_width=True)

# Ejecutar el fragmento
mostrar_animacion()