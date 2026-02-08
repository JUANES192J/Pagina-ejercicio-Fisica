import streamlit as st
import numpy as np
import plotly.graph_objects as go
import time

# Configuración de la página
st.set_page_config(page_title="Simulador de Lanzamiento Vertical - WEB", layout="wide")

st.title("🚀 Simulador de Lanzamiento Vertical Interactivo")
st.markdown("""
Esta aplicación web simula el movimiento de un objeto lanzado verticalmente desde una altura. 
Realizado por Juan Daza, Juan Vargas y Samuel Zorro - 1103 - CMSB 2026
""")

# --- Sidebar: Parámetros del Problema ---
st.sidebar.header("Parámetros del Problema")
y0 = st.sidebar.number_input("Altura inicial del objeto (m)", value=55.0, step=1.0, key="y0_input")
t_total = st.sidebar.number_input("Tiempo total de vuelo esperado (s)", value=10.0, step=0.5, key="t_total_input")
g = st.sidebar.slider("Gravedad (m/s²)", min_value=1.0, max_value=20.0, value=9.81, step=0.01, key="g_input")

# --- Cálculos Físicos ---
# Fórmula para la velocidad inicial: v0 = (0.5 * g * t^2 - y0) / t
if t_total > 0:
    v0 = (0.5 * g * t_total**2 - y0) / t_total
else:
    v0 = 0.0 # Evitar división por cero

# Altura máxima: h_max = y0 + (v0^2 / (2*g))
if g > 0:
    h_max = y0 + (v0**2 / (2 * g))
else:
    h_max = y0 # Si no hay gravedad, no sube más

# Mostrar métricas clave
st.subheader("Resultados Calculados")
col1, col2, col3 = st.columns(3)
col1.metric("Velocidad Inicial ($v_0$)", f"{v0:.2f} m/s")
col2.metric("Altura Máxima ($h_{max}$)", f"{h_max:.2f} m")
col3.metric("Gravedad ($g$)", f"{g} m/s²")

# --- Generación de Datos para la simulación ---
# Más pasos para una animación más suave (reduce el 'time.sleep' en el bucle para más velocidad)
num_frames = 150 
t_steps = np.linspace(0, t_total, num_frames)
y_steps = y0 + v0 * t_steps - 0.5 * g * t_steps**2
v_steps = v0 - g * t_steps

# --- Control de la Animación (Streamlit state management) ---
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'is_playing' not in st.session_state:
    st.session_state.is_playing = False

# Funciones para los botones de Streamlit
def start_animation():
    st.session_state.is_playing = True
def pause_animation():
    st.session_state.is_playing = False
def reset_animation():
    st.session_state.is_playing = False
    st.session_state.current_idx = 0

st.subheader("Controles de Simulación")
btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 4]) # Ajuste de columnas para los botones

btn_col1.button("▶️ Iniciar / Reanudar", on_click=start_animation)
btn_col2.button("⏸️ Pausar", on_click=pause_animation)
btn_col3.button("🔄 Reiniciar", on_click=reset_animation)

# --- Fragmento de Gráfica (Solución al parpadeo en Streamlit) ---
# El decorador @st.fragment asegura que solo esta parte se re-renderice.
@st.fragment
def animate_simulation():
    # Placeholder para las gráficas que se actualizarán
    plot_placeholder = st.empty()

    # Bucle principal de la animación
    while st.session_state.is_playing and st.session_state.current_idx < len(t_steps):
        i = st.session_state.current_idx
        
        # --- Gráfica de Posición ---
        fig_pos = go.Figure()
        
        # 1. Dibujar Edificio
        fig_pos.add_shape(type="rect", x0=-0.4, y0=0, x1=0.4, y1=y0, 
                          fillcolor="#34495e", opacity=0.7, line_width=0, name="Edificio")
        
        # 2. Trayectoria (estela)
        fig_pos.add_trace(go.Scatter(x=[0]*i, y=y_steps[:i], mode='lines', 
                                     line=dict(color='red', width=1, dash='dot'), 
                                     name="Trayectoria"))
        
        # 3. Objeto (Bola)
        # Asegurarse de que la bola no baje del suelo visualmente
        current_y_visual = max(0, y_steps[i]) 
        fig_pos.add_trace(go.Scatter(x=[0], y=[current_y_visual], mode='markers',
                                     marker=dict(color='red', size=18, line=dict(width=2, color='white')), 
                                     name="Objeto"))
        
        fig_pos.update_layout(
            title="Posición del Objeto",
            xaxis=dict(range=[-1.5, 1.5], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, h_max + 15], title="Altura (m)"),
            height=500,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=False,
            template="plotly_white"
        )

        # --- Gráfica de Velocidad ---
        fig_vel = go.Figure()
        fig_vel.add_trace(go.Scatter(x=t_steps[:i+1], y=v_steps[:i+1], mode='lines+markers', 
                                     marker=dict(size=8, color='blue'),
                                     line=dict(color='blue', width=3), name="Velocidad"))
        fig_vel.add_hline(y=0, line_dash="dash", line_color="grey", annotation_text="Velocidad Cero", 
                          annotation_position="bottom right")
        fig_vel.update_layout(
            title="Velocidad vs Tiempo", 
            xaxis_title="Tiempo (s)", yaxis_title="Velocidad (m/s)",
            xaxis_range=[0, t_total + 1], yaxis_range=[min(v_steps) - 5, v0 + 5], 
            height=300, showlegend=False, template="plotly_white"
        )

        # --- Actualizar Contenedor y Texto de Información ---
        with plot_placeholder.container():
            col_graph1, col_graph2 = st.columns([1, 1.5])
            with col_graph1:
                st.plotly_chart(fig_pos, use_container_width=True, config={'displayModeBar': False})
            with col_graph2:
                st.plotly_chart(fig_vel, use_container_width=True, config={'displayModeBar': False})
            
            # Texto de información dinámica
            current_time = t_steps[i]
            current_height = y_steps[i]
            current_velocity = v_steps[i]
            estado = "Subiendo" if current_velocity > 0 else "Cayendo" if current_velocity < 0 else "Punto Máximo"
            
            st.markdown(f"**Tiempo:** `{current_time:.2f} s` | **Altura:** `{max(0, current_height):.2f} m` | **Velocidad:** `{current_velocity:.2f} m/s` | **Estado:** `{estado}`")

        # Avanzar el índice y controlar la velocidad
        st.session_state.current_idx += 1
        time.sleep(0.01) # Pequeña pausa para controlar la velocidad de la animación (menor valor = más rápido/fluido)
        
        # Si la animación llega al final, detenerla
        if st.session_state.current_idx >= len(t_steps):
            st.session_state.is_playing = False
            st.session_state.current_idx = len(t_steps) -1 # Asegurarse de mostrar el último frame
            st.rerun() # Forzar re-renderizado para mostrar el estado final estático

    # --- Mostrar estado estático (cuando no está reproduciendo o al inicio) ---
    # Este bloque se ejecuta cuando la animación no está activa (pausada, reiniciada, o al inicio)
    # y asegura que las gráficas muestren el estado actual sin animación.
    i = st.session_state.current_idx
    if i >= len(t_steps): i = len(t_steps) - 1 # Asegurar que el índice no exceda el límite

    fig_pos_static = go.Figure()
    fig_pos_static.add_shape(type="rect", x0=-0.4, y0=0, x1=0.4, y1=y0, 
                             fillcolor="#34495e", opacity=0.7, line_width=0, name="Edificio")
    fig_pos_static.add_trace(go.Scatter(x=[0]*i, y=y_steps[:i+1], mode='lines', 
                                        line=dict(color='red', width=1, dash='dot'), 
                                        name="Trayectoria"))
    current_y_visual_static = max(0, y_steps[i])
    fig_pos_static.add_trace(go.Scatter(x=[0], y=[current_y_visual_static], mode='markers',
                                        marker=dict(color='red', size=18, line=dict(width=2, color='white')), 
                                        name="Objeto"))
    fig_pos_static.update_layout(title="Posición del Objeto", xaxis_range=[-1.5, 1.5], 
                                 yaxis_range=[0, h_max + 15], height=500, showlegend=False, template="plotly_white")

    fig_vel_static = go.Figure()
    fig_vel_static.add_trace(go.Scatter(x=t_steps[:i+1], y=v_steps[:i+1], mode='lines+markers', 
                                        marker=dict(size=8, color='blue'),
                                        line=dict(color='blue', width=3), name="Velocidad"))
    fig_vel_static.add_hline(y=0, line_dash="dash", line_color="grey")
    fig_vel_static.update_layout(title="Velocidad vs Tiempo", xaxis_title="Tiempo (s)", 
                                 yaxis_title="Velocidad (m/s)",
                                 xaxis_range=[0, t_total + 1], yaxis_range=[min(v_steps) - 5, v0 + 5], 
                                 height=300, showlegend=False, template="plotly_white")

    with plot_placeholder.container():
        col_graph1, col_graph2 = st.columns([1, 1.5])
        with col_graph1:
            st.plotly_chart(fig_pos_static, use_container_width=True, config={'displayModeBar': False})
        with col_graph2:
            st.plotly_chart(fig_vel_static, use_container_width=True, config={'displayModeBar': False})
        
        current_time_static = t_steps[i]
        current_height_static = y_steps[i]
        current_velocity_static = v_steps[i]
        estado_static = "Subiendo" if current_velocity_static > 0 else "Cayendo" if current_velocity_static < 0 else "Punto Máximo"
        st.markdown(f"**Tiempo:** `{current_time_static:.2f} s` | **Altura:** `{max(0, current_height_static):.2f} m` | **Velocidad:** `{current_velocity_static:.2f} m/s` | **Estado:** `{estado_static}`")

# Ejecutar el fragmento de animación
animate_simulation()

st.markdown("---")

st.caption("Aplicación creada con Streamlit y Plotly para simulación física.")
