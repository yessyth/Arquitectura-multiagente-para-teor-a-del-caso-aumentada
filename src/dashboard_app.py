import sys
import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    HPN_CSV_PATH, HPN_JSON_PATH, NETWORK_PATH,
    METRICS_PATH, SCENARIOS_PATH, FRAGMENTS_PATH,
)


def load_data():
    data = {}
    if os.path.exists(HPN_JSON_PATH):
        with open(HPN_JSON_PATH, "r", encoding="utf-8") as f:
            data["hpn"] = json.load(f)
    if os.path.exists(HPN_CSV_PATH):
        data["hpn_df"] = pd.read_csv(HPN_CSV_PATH)
    if os.path.exists(NETWORK_PATH):
        with open(NETWORK_PATH, "r", encoding="utf-8") as f:
            data["network"] = json.load(f)
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r", encoding="utf-8") as f:
            data["metrics"] = json.load(f)
    if os.path.exists(SCENARIOS_PATH):
        with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
            data["scenarios"] = json.load(f)
    if os.path.exists(FRAGMENTS_PATH):
        fragments = []
        with open(FRAGMENTS_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    fragments.append(json.loads(line))
        data["fragments"] = fragments
    return data


st.set_page_config(
    page_title="Teoría del Caso Aumentada - Dashboard",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Teoría del Caso Aumentada")
st.markdown("Dashboard de apoyo estratégico para litigio aumentado")

# Show detected case type
if data.get("metrics") and data["metrics"].get("tipo_caso"):
    case_label = data["metrics"]["tipo_caso"]
    colors = {"Civil": "🔵", "Penal": "🔴", "Laboral": "🟠", "Familia": "🟢"}
    icon = colors.get(case_label, "⚪")
    st.markdown(f"### {icon} Tipo de caso detectado: **{case_label}**")
st.markdown("---")

data = load_data()

if not data.get("hpn") and not data.get("metrics"):
    st.warning(
        "No se encontraron datos. Ejecute primero el orquestador:\n\n"
        "```bash\npython src/orchestrator.py ruta/al/expediente.pdf\n```\n\n"
        "Luego recargue este dashboard."
    )
    st.stop()

# --- Sidebar ---
st.sidebar.header("Panel de Control")

if data.get("metrics"):
    m = data["metrics"]
    st.sidebar.metric("Cobertura Elementos", f"{m.get('cobertura_elementos_juridicos', 0)}%")
    st.sidebar.metric("Cobertura Probatoria", f"{m.get('cobertura_probatoria', 0)}%")
    st.sidebar.metric("Cobertura Normativa", f"{m.get('cobertura_normativa', 0)}%")
    st.sidebar.metric("Nodos en Red", m.get("total_nodos", 0))
    st.sidebar.metric("Aristas en Red", m.get("total_aristas", 0))

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Vista General", "📋 Matriz HPN", "🕸️ Red Multicapa",
    "📈 Métricas", "🎯 Simulación", "⚠️ Alertas"
])

# ===== TAB 1: Vista General =====
with tab1:
    st.header("Vista General del Caso")

    if data.get("hpn"):
        hpn = data["hpn"]
        estados = {}
        riesgos = {}
        for fila in hpn:
            est = fila.get("estado", "desconocido")
            rie = fila.get("riesgo", "desconocido")
            estados[est] = estados.get(est, 0) + 1
            riesgos[rie] = riesgos.get(rie, 0) + 1

        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                names=list(estados.keys()),
                values=list(estados.values()),
                title="Distribución por Estado",
                color_discrete_sequence=px.colors.qualitative.Set2,
            )
            st.plotly_chart(fig, width='stretch', key='pie_estado')
        with col2:
            fig = px.pie(
                names=list(riesgos.keys()),
                values=list(riesgos.values()),
                title="Distribución por Riesgo",
                color_discrete_sequence=["#2ecc71", "#f39c12", "#e74c3c", "#c0392b"],
            )
            st.plotly_chart(fig, width='stretch', key='pie_riesgo')

    if data.get("metrics"):
        m = data["metrics"]
        st.subheader("Resumen de Métricas Clave")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Cobertura Elementos Jurídicos", f"{m.get('cobertura_elementos_juridicos', 0)}%")
        with col2:
            st.metric("Cobertura Probatoria", f"{m.get('cobertura_probatoria', 0)}%")
        with col3:
            st.metric("Cobertura Normativa", f"{m.get('cobertura_normativa', 0)}%")
        with col4:
            st.metric("Índice de Contradicción",
                      f"{m.get('indice_contradiccion', {}).get('porcentaje', 0)}%")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Vacíos Críticos",
                      f"{m.get('indice_vacios_criticos', {}).get('cantidad', 0)}")
        with col2:
            st.metric("Debilidad Argumentativa",
                      f"{m.get('debilidad_argumentativa', {}).get('porcentaje', 0)}%")
        with col3:
            st.metric("Acciones Pendientes",
                      f"{m.get('acciones_pendientes', {}).get('cantidad', 0)}")
        with col4:
            st.metric("Densidad de Red", m.get("densidad_red", 0))

    if data.get("fragments"):
        with st.expander("Fragmentos del Expediente", expanded=False):
            for frag in data["fragments"]:
                st.markdown(f"**Página {frag['pagina']}** | `{frag['fragment_id']}` | Sección: {frag.get('seccion', 'N/A')}")
                st.text(frag["texto"][:300])
                st.markdown("---")

# ===== TAB 2: Matriz HPN =====
with tab2:
    st.header("Matriz HPN (Hecho-Prueba-Norma)")
    st.markdown("Cada fila representa una unidad jurídico-probatoria del caso.")

    if data.get("hpn_df") is not None:
        df = data["hpn_df"]

        col1, col2 = st.columns([3, 1])
        with col1:
            estado_filter = st.multiselect(
                "Filtrar por Estado",
                options=df["Estado"].unique() if "Estado" in df.columns else [],
                default=[],
            )
        with col2:
            riesgo_filter = st.multiselect(
                "Filtrar por Riesgo",
                options=df["Riesgo"].unique() if "Riesgo" in df.columns else [],
                default=[],
            )

        filtered = df.copy()
        if estado_filter:
            filtered = filtered[filtered["Estado"].isin(estado_filter)]
        if riesgo_filter:
            filtered = filtered[filtered["Riesgo"].isin(riesgo_filter)]

        st.dataframe(filtered, width='stretch', height=500, key='hpn_dataframe')
    elif data.get("hpn"):
        st.json(data["hpn"])
    else:
        st.info("No hay datos de matriz HPN disponibles.")

# ===== TAB 3: Red Multicapa =====
with tab3:
    st.header("Red Compleja Multicapa")
    st.markdown("Nodos por capa y relaciones entre entidades del caso.")

    if data.get("network"):
        net = data["network"]
        nodes = net.get("nodes", [])
        edges = net.get("edges", [])

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Nodos", len(nodes))
        with col2:
            st.metric("Total Aristas", len(edges))
        with col3:
            capas = {}
            for n in nodes:
                c = n.get("capa", "desconocida")
                capas[c] = capas.get(c, 0) + 1
            st.metric("Capas", len(capas))

        st.subheader("Distribución por Capa")
        fig = px.bar(
            x=list(capas.keys()),
            y=list(capas.values()),
            labels={"x": "Capa", "y": "Nodos"},
            color=list(capas.values()),
            color_continuous_scale="viridis",
        )
        st.plotly_chart(fig, width='stretch', key='bar_capas')

        st.subheader("Visualización de Red")
        G = nx.MultiDiGraph()
        for n in nodes:
            G.add_node(n["id"], **{k: v for k, v in n.items() if k != "id"})
        for e in edges:
            G.add_edge(e["source"], e["target"],
                       **{k: v for k, v in e.items() if k not in ("source", "target")})

        if G.number_of_nodes() > 0:
            pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

            edge_traces = []
            for u, v, k, d in G.edges(keys=True, data=True):
                x0, y0 = pos[u]
                x1, y1 = pos[v]
                edge_traces.append(
                    go.Scatter(
                        x=[x0, x1, None],
                        y=[y0, y1, None],
                        mode="lines",
                        line=dict(width=1, color="rgba(100,100,100,0.3)"),
                        hoverinfo="none",
                    )
                )

            node_colors = {
                "hecho": "#3498db", "prueba": "#2ecc71", "norma": "#e74c3c",
                "precedente": "#9b59b6", "argumento": "#f39c12", "riesgo": "#e67e22",
                "tiempo": "#1abc9c", "actor": "#34495e", "pretension": "#c0392b",
            }

            node_trace = go.Scatter(
                x=[], y=[], mode="markers+text",
                text=[], textposition="top center",
                hoverinfo="text",
                marker=dict(
                    size=10,
                    color=[],
                    line=dict(width=1, color="white"),
                ),
            )

            for n in G.nodes():
                x, y = pos[n]
                node_trace["x"] += (x,)
                node_trace["y"] += (y,)
                nd = G.nodes[n]
                capa = nd.get("capa", "desconocida")
                color = node_colors.get(capa, "#95a5a6")
                node_trace["marker"]["color"] += (color,)
                label = nd.get("label", n)[:30]
                node_trace["text"] += (label,)

            fig = go.Figure(
                data=[*edge_traces, node_trace],
                layout=go.Layout(
                    showlegend=False,
                    hovermode="closest",
                    margin=dict(b=0, l=0, r=0, t=0),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=600,
                ),
            )
            st.plotly_chart(fig, width='stretch', key='network_graph')

        with st.expander("Ver datos de nodos y aristas", expanded=False):
            st.subheader("Nodos")
            st.json(nodes[:20])
            st.subheader("Aristas")
            st.json(edges[:20])
    else:
        st.info("No hay datos de red multicapa disponibles.")

# ===== TAB 4: Métricas =====
with tab4:
    st.header("Métricas de Matriz HPN y Red")
    st.markdown("Indicadores calculados a partir de la matriz y la red multicapa.")

    if data.get("metrics"):
        m = data["metrics"]

        st.subheader("Métricas de Matriz HPN")
        hpn_metrics = {k: v for k, v in m.items()
                       if k in ("cobertura_elementos_juridicos", "cobertura_probatoria",
                                "cobertura_normativa")}
        cols = st.columns(len(hpn_metrics))
        for i, (k, v) in enumerate(hpn_metrics.items()):
            with cols[i]:
                st.metric(k.replace("_", " ").title(), f"{v}%")

        st.subheader("Índices")
        col1, col2, col3, col4 = st.columns(4)
        for i, idx in enumerate(["indice_vacios_criticos", "indice_contradiccion",
                                  "debilidad_argumentativa", "acciones_pendientes"]):
            val = m.get(idx, {})
            with [col1, col2, col3, col4][i]:
                if isinstance(val, dict):
                    st.metric(
                        idx.replace("_", " ").title(),
                        f"{val.get('cantidad', 0)} ({val.get('porcentaje', 0)}%)"
                    )
                else:
                    st.metric(idx.replace("_", " ").title(), val)

        st.subheader("Métricas de Red")
        net_metrics = {k: v for k, v in m.items()
                       if k in ("total_nodos", "total_aristas", "densidad_red",
                                "grado_promedio", "grado_maximo", "grado_minimo")}
        cols = st.columns(len(net_metrics))
        for i, (k, v) in enumerate(net_metrics.items()):
            with cols[i]:
                st.metric(k.replace("_", " ").title(), v)

        if "distribucion_capas" in m:
            st.subheader("Distribución de Nodos por Capa")
            capas = m["distribucion_capas"]
            fig = px.bar(
                x=list(capas.keys()),
                y=list(capas.values()),
                title="Nodos por Capa",
                labels={"x": "Capa", "y": "Cantidad"},
                color=list(capas.values()),
                color_continuous_scale="viridis",
            )
            st.plotly_chart(fig, width='stretch', key='bar_metric_capas')

        if "trazabilidad" in m:
            st.subheader("Trazabilidad")
            traz = m["trazabilidad"]
            st.metric("Filas con Fuente", f"{traz.get('con_fuente', 0)}%")
            st.metric("Filas con Agente", f"{traz.get('con_agente', 0)}%")
    else:
        st.info("No hay métricas disponibles.")

# ===== TAB 5: Simulación =====
with tab5:
    st.header("Simulación de Escenarios Procesales")
    st.markdown("Laboratorio estratégico: se perturba la matriz y la red para observar efectos.")

    if data.get("scenarios"):
        for esc in data["scenarios"]:
            with st.expander(f"{esc.get('id', 'N/A')}: {esc.get('nombre', 'Sin nombre')}", expanded=False):
                st.markdown(f"**Descripción:** {esc.get('descripcion', '')}")
                st.markdown(f"**Confianza:** {esc.get('confianza', 'N/A')}")

                if esc.get("supuestos"):
                    st.markdown("**Supuestos:**")
                    for s in esc["supuestos"]:
                        st.markdown(f"- {s}")

                if esc.get("antes") and esc.get("despues"):
                    before = esc["antes"]
                    after = esc["despues"]
                    st.markdown("**Efectos (antes → después):**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Antes**")
                        for k, v in before.items():
                            st.markdown(f"- {k}: {v}")
                    with col2:
                        st.markdown("**Después**")
                        for k, v in after.items():
                            st.markdown(f"- {k}: {v}")

                    diff_data = []
                    for k in before:
                        diff_data.append({
                            "Métrica": k,
                            "Antes": before[k],
                            "Después": after[k],
                        })
                    if diff_data:
                        fig = px.bar(
                            pd.DataFrame(diff_data),
                            x="Métrica",
                            y=["Antes", "Después"],
                            barmode="group",
                            title="Comparación Antes/Después",
                        )
                        st.plotly_chart(fig, width='stretch', key=f"scenario_{esc.get('id', 'none')}")

                if esc.get("acciones_sugeridas"):
                    st.markdown("**Acciones Sugeridas:**")
                    for a in esc["acciones_sugeridas"]:
                        st.markdown(f"- ✅ {a}")
    else:
        st.info("No hay escenarios simulados disponibles.")

# ===== TAB 6: Alertas =====
with tab6:
    st.header("Alertas y Auditoría")
    st.markdown("Verificación de trazabilidad, coherencia y calidad de los artefactos.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Alertas del Sistema")
        st.info("Las alertas señalan vacíos críticos, pruebas únicas, contradicciones y baja trazabilidad.")

    with col2:
        if data.get("metrics"):
            m = data["metrics"]
            vacios = m.get("indice_vacios_criticos", {}).get("cantidad", 0)
            if vacios > 0:
                st.error(f"⚠️ {vacios} vacío(s) crítico(s) detectado(s)")
            contrad = m.get("indice_contradiccion", {}).get("cantidad", 0)
            if contrad > 0:
                st.warning(f"⚡ {contrad} contradicción(es) detectada(s)")

    if data.get("hpn"):
        st.subheader("Revisión de Filas HPN")
        pendientes = sum(1 for f in data["hpn"] if f.get("revision_humana") == "pendiente")
        st.metric("Filas Pendientes de Revisión Humana", pendientes)

        for fila in data["hpn"]:
            if fila.get("estado") in ("vacio_critico", "debil"):
                st.warning(
                    f"**{fila['id']}** - {fila.get('elemento_juridico', 'N/A')}: "
                    f"Estado '{fila['estado']}', Riesgo '{fila.get('riesgo', 'N/A')}'"
                )
            if fila.get("riesgo") in ("alto", "critico"):
                st.error(
                    f"**{fila['id']}** - {fila.get('elemento_juridico', 'N/A')}: "
                    f"Riesgo {fila['riesgo']} - {fila.get('accion_sugerida', '')}"
                )

    st.subheader("Preguntas Sugeridas para Preparación")
    preguntas = [
        "¿Qué hechos pueden afirmarse con fuerza?",
        "¿Qué hechos deben modularse porque son débiles o controvertidos?",
        "¿Qué prueba es crítica y debe protegerse?",
        "¿Qué testigo o documento conviene preparar primero?",
        "¿Qué excepción debe anticiparse?",
        "¿Qué escenario debe simularse antes de tomar una decisión?",
        "¿Qué punto no debe ir todavía al memorial por baja trazabilidad?",
    ]
    for p in preguntas:
        st.markdown(f"- ❓ {p}")

    st.markdown("---")
    st.caption(
        "**Nota:** Este sistema no reemplaza el criterio del abogado. "
        "Todas las conclusiones requieren revisión humana antes de ser utilizadas en litigio."
    )

# --- Footer ---
st.markdown("---")
st.markdown(
    "**Teoría del Caso Aumentada** | Ciencia de Datos - Ingeniería de Sistemas | "
    "Universidad de Pamplona 2026-1"
)
