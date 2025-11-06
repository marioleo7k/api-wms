"""
Componentes de UI reutilizáveis
"""
import streamlit as st
import plotly.express as px
import pandas as pd
from typing import Dict, Optional


def render_metrics_card(title: str, value: str):
    """
    Renderiza um card de métrica customizado
    
    Args:
        title: Título da métrica
        value: Valor a exibir
    """
    st.markdown(f"**{title}**")
    st.markdown(f"### {value}")


def render_status_breakdown(status_counts: Dict[str, int]):
    """
    Renderiza breakdown de status
    
    Args:
        status_counts: Dicionário com status e contagens
    """
    st.markdown("**Pedidos por Status**")
    if status_counts:
        for status, qtd in status_counts.items():
            st.write(f"**{status}:** {qtd}")
    else:
        st.write("N/A")


def render_pie_chart(
    data: Dict[str, int],
    title: str,
    labels_name: str = "Status",
    values_name: str = "Quantidade"
):
    """
    Renderiza gráfico de pizza
    
    Args:
        data: Dicionário com dados
        title: Título do gráfico
        labels_name: Nome para labels
        values_name: Nome para valores
    """
    if not data:
        st.info("Nenhum dado disponível")
        return
    
    fig = px.pie(
        names=list(data.keys()),
        values=list(data.values()),
        title=title
    )
    st.plotly_chart(fig, width="stretch")


def render_bar_chart(
    x_data: list,
    y_data: list,
    title: str,
    x_label: str = "Categoria",
    y_label: str = "Quantidade",
    orientation: str = "v"
):
    """
    Renderiza gráfico de barras
    
    Args:
        x_data: Dados do eixo X
        y_data: Dados do eixo Y
        title: Título do gráfico
        x_label: Label do eixo X
        y_label: Label do eixo Y
        orientation: 'v' vertical ou 'h' horizontal
    """
    fig = px.bar(
        x=x_data,
        y=y_data,
        orientation=orientation,
        title=title,
        labels={'x': x_label, 'y': y_label}
    )
    st.plotly_chart(fig, width="stretch")


def render_line_chart(
    df: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str
):
    """
    Renderiza gráfico de linha
    
    Args:
        df: DataFrame com os dados
        x_column: Nome da coluna X
        y_column: Nome da coluna Y
        title: Título do gráfico
    """
    fig = px.line(
        df,
        x=x_column,
        y=y_column,
        title=title
    )
    st.plotly_chart(fig, width="stretch")


def render_export_buttons(df: pd.DataFrame, filename_base: str = "dados"):
    """
    Renderiza botões de exportação CSV e Excel
    
    Args:
        df: DataFrame para exportar
        filename_base: Nome base dos arquivos
    """
    import io
    
    st.markdown("---")
    st.subheader("📥 Exportar")
    
    # CSV
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download CSV",
        csv_bytes,
        f"{filename_base}.csv",
        "text/csv",
        width="stretch"
    )
    
    # Excel
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Dados')
    
    st.download_button(
        "📥 Download Excel",
        buffer.getvalue(),
        f"{filename_base}.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width="stretch"
    )


def render_filter_sidebar(
    df: pd.DataFrame,
    date_column: str,
    status_column: str,
    depot_column: str
):
    """
    Renderiza filtros na sidebar
    
    Args:
        df: DataFrame com os dados
        date_column: Nome da coluna de data
        status_column: Nome da coluna de status
        depot_column: Nome da coluna de depósito
        
    Returns:
        Tuple com (data_inicio, data_fim, filtro_status, filtro_depot, filtro_transportadora)
    """
    from datetime import datetime
    from ..core.config import DEFAULT_START_DATE_YEAR, DEFAULT_START_DATE_MONTH, DEFAULT_START_DATE_DAY
    
    st.subheader("📅 Período")
    col1, col2 = st.columns(2)
    
    with col1:
        data_inicio = st.date_input(
            "Data Inicial",
            datetime(DEFAULT_START_DATE_YEAR, DEFAULT_START_DATE_MONTH, DEFAULT_START_DATE_DAY)
        )
    with col2:
        data_fim = st.date_input(
            "Data Final",
            datetime.now()
        )
    
    # Opções de filtros
    if not df.empty:
        status_options = ["Todos"] + sorted(df[status_column].dropna().unique().tolist()) if status_column in df.columns else ["Todos"]
        depot_options = ["Todos"] + sorted(df[depot_column].dropna().unique().tolist()) if depot_column in df.columns else ["Todos"]
    else:
        from ..core.config import DEFAULT_STATUS_OPTIONS
        status_options = ["Todos"] + DEFAULT_STATUS_OPTIONS
        depot_options = ["Todos"]
    
    filtro_status = st.selectbox("Status", status_options)
    filtro_depot = st.selectbox("Depósito", depot_options)
    filtro_transportadora = st.text_input("Transportadora", placeholder="Digite para filtrar...")
    
    return data_inicio, data_fim, filtro_status, filtro_depot, filtro_transportadora
