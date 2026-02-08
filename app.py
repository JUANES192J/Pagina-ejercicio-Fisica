import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

st.set_page_config(page_title="Simulador de Lanzamiento Vertical - WEB", layout="wide")
st.title("🚀 Simulador de Lanzamiento Vertical Interactivo")

# Sidebar
st.sidebar.header("Parámetros del Problema")
y0 = st.sidebar.number_input("Altura inicial del objeto (m)", value=55.0, step=1.0, key="y0_input")
t_total = st.sidebar.number_input("Tiempo total de vuelo esperado (s)", value=10.0, step=0.5, key="t_total_input")
g = st.sidebar.slider("Gravedad (m/s²)", min_value=1.0, max_value=20.0, value=9.81, step=0.01, key="g_input")

# Cálculos
if t_total > 0:
    v0 = (0.5 * g * t_total**2 - y0) / t_total
else:
    v0 = 0.0
if g > 0:
    h_max = y0 + (v0**2 / (2 * g))
else:
    h_max = y0

st.subheader("Resultados Calculados")
col1, col2, col3 = st.columns(3)
col1.metric("Velocidad Inicial $v_0$", f"{v0:.2f} m/s")
col2.metric("Altura Máxima $h_{max}$", f"{h_max:.2f} m")
col3.metric("Gravedad $g$", f"{g} m/s²")

# Datos de la simulación
num_frames = 150
t_steps = np.linspace(0, t_total, num_frames)
y_steps = y0 + v0 * t_steps - 0.5 * g * t_steps**2
v_steps = v0 - g * t_steps

# Estado
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

def start_animation():
    st.session_state.is_playing = True
def pause_animation():
    st.session_state.is_playing = False
def reset_animation():
    st.session_state.is_playing = False
    st.session_state.current_idx = 0

st.subheader("Controles de Simulación")
btn_col1, btn_col2, btn_col3 = st.columns([1,1,4])
btn_col1.button("▶️ Iniciar / Reanudar", on_click=start_animation)
btn_col2.button("⏸️ Pausar", on_click=pause_animation)
btn_col3.button("🔄 Reiniciar", on_click=reset_animation)

# Placeholders separados para evitar re-render completo
placeholder_pos = st.empty()
placeholder_vel = st.empty()
placeholder_info = st.empty()

# Crear figuras iniciales una sola vez
def create_initial_figures():
    # Posición: edificio + trayectoria vacía + marcador
    fig_pos = go.Figure()
    fig_pos.add_shape(type="rect", x0=-0.4, y0=0, x1=0.4, y1=y0,
                      fillcolor="#34495e", opacity=0.7, line_width=0)
    # Traza 0 = trayectoria (inicial vacía)
    fig_pos.add_trace(go.Scatter(x=[], y=[], mode='lines', line=dict(color='red', width=1, dash='dot'), name="Trayectoria"))
    # Traza 1 = objeto (marcador)
    fig_pos.add_trace(go.Scatter(x=[0], y=[max(0, y_steps[0])], mode='markers',
                                 marker=dict(color='red', size=18, line=dict(width=2, color='white')), name="Objeto"))
    fig_pos.update_layout(
        title="Posición del Objeto",
        xaxis=dict(range=[-1.5, 1.5], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, h_max + 15], title="Altura (m)"),
        height=500, margin=dict(l=20, r=20, t=40, b=20), showlegend=False, template="plotly_white"
    )

    # Velocidad: línea vacía que iremos rellenando
    fig_vel = go.Figure()
    fig_vel.add_trace(go.Scatter(x=[t_steps[0]], y=[v_steps[0]], mode='lines+markers',
                                 marker=dict(size=8, color='blue'), line=dict(color='blue', width=3), name="Velocidad"))
    fig_vel.add_hline(y=0, line_dash="dash", line_color="grey", annotation_text="Velocidad Cero", annotation_position="bottom right")
    fig_vel.update_layout(
        title="Velocidad vs Tiempo",
        xaxis_title="Tiempo (s)", yaxis_title="Velocidad (m/s)",
        xaxis_range=[0, t_total + 1], yaxis_range=[min(v_steps) - 5, v0 + 5],
        height=300, showlegend=False, template="plotly_white"
    )

    return fig_pos, fig_vel

fig_pos, fig_vel = create_initial_figures()

# Mostrar estado inicial
placeholder_pos.plotly_chart(fig_pos, use_container_width=True, config={'displayModeBar': False})
placeholder_vel.plotly_chart(fig_vel, use_container_width=True, config={'displayModeBar': False})
placeholder_info.markdown(f"**Tiempo:** `0.00 s` | **Altura:** `{y0:.2f} m` | **Velocidad:** `{v0:.2f} m/s` | **Estado:** `Inicial`")

# Bucle de animación: actualizar solo datos de las trazas
# Nota: time.sleep sigue usándose pero con cuidado; no recreamos layouts ni containers.
frame_delay = 0.02  # 20 ms por frame -> ~50 FPS teórico (ajusta según servidor)
while st.session_state.is_playing and st.session_state.current_idx < len(t_steps):
    i = st.session_state.current_idx

    # Actualizar trayectoria (traza 0) y marcador (traza 1) en fig_pos
    # Evitar reconstruir shapes o layout
    fig_pos.data[0].x = [0] * max(1, i)   # trayectoria x (constante 0)
    fig_pos.data[0].y = y_steps[:max(1, i)]
    current_y_visual = max(0, y_steps[i])
    fig_pos.data[1].y = [current_y_visual]
    fig_pos.data[1].x = [0]

    # Actualizar fig_vel: extender la línea hasta el frame actual
    fig_vel.data[0].x = t_steps[:i+1]
    fig_vel.data[0].y = v_steps[:i+1]

    # Renderizar en los placeholders (actualiza en sitio, menos parpadeo)
    placeholder_pos.plotly_chart(fig_pos, use_container_width=True, config={'displayModeBar': False})
    placeholder_vel.plotly_chart(fig_vel, use_container_width=True, config={'displayModeBar': False})

    # Información dinámica
    current_time = t_steps[i]
    current_height = y_steps[i]
    current_velocity = v_steps[i]
    estado = "Subiendo" if current_velocity > 0 else "Cayendo" if current_velocity < 0 else "Punto Máximo"
    placeholder_info.markdown(f"**Tiempo:** `{current_time:.2f} s` | **Altura:** `{max(0, current_height):.2f} m` | **Velocidad:** `{current_velocity:.2f} m/s` | **Estado:** `{estado}`")

    # Avanzar frame
    st.session_state.current_idx += 1
    time.sleep(frame_delay)

    # Si llegamos al final, detener y mostrar último frame
    if st.session_state.current_idx >= len(t_steps):
        st.session_state.is_playing = False
        st.session_state.current_idx = len(t_steps) - 1
        # Mostrar estado final (sin forzar rerun para evitar parpadeo)
        placeholder_pos.plotly_chart(fig_pos, use_container_width=True, config={'displayModeBar': False})
        placeholder_vel.plotly_chart(fig_vel, use_container_width=True, config={'displayModeBar': False})
        current_time = t_steps[-1]
        current_height = y_steps[-1]
        current_velocity = v_steps[-1]
        estado = "Final"
        placeholder_info.markdown(f"**Tiempo:** `{current_time:.2f} s` | **Altura:** `{max(0, current_height):.2f} m` | **Velocidad:** `{current_velocity:.2f} m/s` | **Estado:** `{estado}`")

st.markdown("---")
st.caption("Aplicación creada con Streamlit y Plotly para simulación física.")

