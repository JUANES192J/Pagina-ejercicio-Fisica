import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador de Lanzamiento Vertical", layout="wide")
st.title("🚀 Simulador de Lanzamiento Vertical (Animación Fluida)")

# --- Parámetros ---
y0 = st.sidebar.number_input("Altura inicial (m)", value=55.0)
t_total = st.sidebar.number_input("Tiempo total (s)", value=10.0)
g = st.sidebar.slider("Gravedad (m/s²)", 1.0, 20.0, 9.81)

# --- Física ---
v0 = (0.5 * g * t_total**2 - y0) / t_total
h_max = y0 + v0**2 / (2 * g)

# --- Datos ---
N = 150
t = np.linspace(0, t_total, N)
y = y0 + v0 * t - 0.5 * g * t**2
v = v0 - g * t

# --- Figura base ---
fig = go.Figure(
    data=[
        # Objeto
        go.Scatter(
            x=[0], y=[y[0]],
            mode="markers",
            marker=dict(size=18, color="red"),
            name="Objeto"
        ),
        # Trayectoria
        go.Scatter(
            x=[0], y=[y[0]],
            mode="lines",
            line=dict(color="red", dash="dot"),
            name="Trayectoria"
        )
    ],
    layout=go.Layout(
        title="Movimiento vertical",
        xaxis=dict(range=[-1, 1], showticklabels=False),
        yaxis=dict(range=[0, h_max + 15], title="Altura (m)"),
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="▶ Reproducir",
                        method="animate",
                        args=[None, {
                            "frame": {"duration": 40, "redraw": False},
                            "fromcurrent": True
                        }]
                    ),
                    dict(
                        label="⏸ Pausar",
                        method="animate",
                        args=[[None], {
                            "frame": {"duration": 0},
                            "mode": "immediate"
                        }]
                    )
                ]
            )
        ],
        template="plotly_white",
        height=550
    ),
    frames=[
        go.Frame(
            data=[
                go.Scatter(x=[0], y=[max(0, y[i])]),
                go.Scatter(x=[0]*i, y=y[:i])
            ],
            name=str(i)
        )
        for i in range(N)
    ]
)

st.plotly_chart(fig, use_container_width=True)
