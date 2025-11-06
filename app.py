import streamlit as st
import pandas as pd
import io
import plotly.express as px
from typing import Optional
from datetime import datetime, timedelta

# Imports dos serviços
from services.api_client import get_wms_client
from services.data_processor import process_agendamentos_data, create_agendamentos_summary, filter_agendamentos

# Imports dos módulos core
from src.core.utils import get_base64_image
from src.core.config import PAGE_TITLE, PAGE_ICON

# Configuração da página
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide"
)

# Carrega a imagem de fundo
background_image = get_base64_image("assets/background.png")

# Estilo CSS personalizado
st.markdown(f"""
    <style>
        /* Imagem de fundo */
        .stApp {{
            background-image: url("data:image/png;base64,{background_image}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* Sidebar com fundo branco */
        section[data-testid="stSidebar"] {{
            background-color: white;
        }}
        
        /* Container principal - UM ÚNICO BLOCO BRANCO */
        .block-container {{
            background-color: white;
            padding: 2rem;
            margin: 2rem auto;
            border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            max-width: 98%;
        }}
        
        /* Remove padding extra */
        .main {{
            padding: 0;
        }}
        
        /* Centraliza o título */
        h1 {{
            text-align: center;
        }}
        
        /* Ajusta tamanho dos títulos e valores das métricas */
        div[data-testid="stMetric"] label {{
            font-size: 1.2rem !important;
            font-weight: 600 !important;
        }}
        
        div[data-testid="stMetric"] div[data-testid="stMetricValue"] {{
            font-size: 2rem !important;
        }}
        
        /* Botões */
        div.stButton > button {{
            width: 100%;
        }}
    </style>
""", unsafe_allow_html=True)

def carregar_agendamentos():
    """
    Carrega todos os agendamentos disponíveis da API WMS
    """
    client = get_wms_client()
    try:
        # Busca todos os dados da API
        dados_brutos = client.get_agendamentos(todos=True)
        if not dados_brutos:
            return pd.DataFrame()
        
        # Processa os dados
        return process_agendamentos_data(dados_brutos)
    except Exception as e:
        st.error(f"❌ Erro ao carregar agendamentos: {str(e)}")
        return pd.DataFrame()

def main():
    # Cabeçalho
    st.title("🚚 WMS SIGMA - Agendamentos de Materiais")
    
    # Carrega dados automaticamente na primeira vez
    if 'df_original' not in st.session_state:
        # Cria um placeholder para as mensagens
        message_placeholder = st.empty()
        with message_placeholder.container():
            with st.spinner("Carregando dados da API..."):
                df_all = carregar_agendamentos()
                if df_all is not None and not df_all.empty:
                    # Garantir tipagem correta de data
                    if 'Data Agendamento' in df_all.columns:
                        df_all['Data Agendamento'] = pd.to_datetime(df_all['Data Agendamento'], errors='coerce')
                    st.session_state['df_original'] = df_all
                else:
                    st.session_state['df_original'] = pd.DataFrame()
        
        # Aguarda 3 segundos e limpa as mensagens
        import time
        time.sleep(3)
        message_placeholder.empty()
    
    # Sidebar com filtros
    with st.sidebar:
        # Filtros de data (agora filtram o DataFrame, não a API)
        st.subheader("📅 Período")
        col1, col2 = st.columns(2)
        with col1:
            data_inicio = st.date_input(
                "Data Inicial",
                datetime(2025, 1, 1)
            )
        with col2:
            data_fim = st.date_input(
                "Data Final",
                datetime.now()
            )

        # Remove o subheader "Filtros Adicionais"
        # Opções de filtros mantidas sem o texto
        if 'df_original' in st.session_state and not st.session_state['df_original'].empty:
            df_orig = st.session_state['df_original']
            status_options = ["Todos"] + sorted(df_orig['Status da Entrega'].dropna().unique().tolist()) if 'Status da Entrega' in df_orig.columns else ["Todos"]
            galpao_options = ["Todos"] + sorted(df_orig['Depósito'].dropna().unique().tolist()) if 'Depósito' in df_orig.columns else ["Todos"]
        else:
            status_options = ["Todos"] + ["AGENDADO", "CONFIRMADO", "CANCELADO", "FINALIZADO"]
            galpao_options = ["Todos"]

        filtro_status = st.selectbox(
            "Status",
            status_options
        )

        filtro_galpao = st.selectbox(
            "Depósito",
            galpao_options
        )

        filtro_transportadora = st.text_input(
            "Transportadora",
            placeholder="Digite para filtrar..."
        )

        # Botão para atualizar dados manualmente (puxa TODOS os registros da API)
        st.markdown("---")
        if st.button("🔄 Atualizar Dados", width="stretch"):
            with st.spinner("Buscando todos os agendamentos disponíveis..."):
                df_all = carregar_agendamentos()
                if df_all is None or df_all.empty:
                    st.warning("⚠️ Nenhum dado encontrado na API")
                else:
                    # Garantir tipagem correta de data
                    if 'Data Agendamento' in df_all.columns:
                        df_all['Data Agendamento'] = pd.to_datetime(df_all['Data Agendamento'], errors='coerce')
                    st.session_state['df_original'] = df_all
                    st.success(f"✅ {len(df_all)} registros carregados!")
    
    # Conteúdo principal
    # Verifica se já carregamos os dados
    if 'df_original' not in st.session_state or st.session_state['df_original'].empty:
        st.warning("⚠️ Nenhum dado disponível. Tente atualizar usando o botão na barra lateral.")
        return

    # DataFrame completo em memória
    df_original = st.session_state['df_original']

    # Garante que coluna de data está no formato datetime (usando nome renomeado)
    if 'Data Agendamento' in df_original.columns and not pd.api.types.is_datetime64_any_dtype(df_original['Data Agendamento']):
        df_original['Data Agendamento'] = pd.to_datetime(df_original['Data Agendamento'], errors='coerce')

    # Aplica filtros no DataFrame em memória
    df_filtrado = df_original.copy()

    # Filtro de período (usa apenas data)
    if 'Data Agendamento' in df_filtrado.columns:
        mask = (
            (df_filtrado['Data Agendamento'].dt.date >= data_inicio) &
            (df_filtrado['Data Agendamento'].dt.date <= data_fim)
        )
        df_filtrado = df_filtrado[mask]

    # Filtro de status
    if filtro_status and filtro_status != "Todos" and 'Status da Entrega' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Status da Entrega'] == filtro_status]

    # Filtro de galpão
    if filtro_galpao and filtro_galpao != "Todos" and 'Depósito' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Depósito'] == filtro_galpao]

    # Filtro de transportadora (texto)
    if filtro_transportadora:
        if 'Transportadora' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                df_filtrado['Transportadora'].str.contains(filtro_transportadora, case=False, na=False)
            ]

    # Se não houver registros após filtros, avisar e terminar
    if df_filtrado is None or df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado com os filtros aplicados")
        return

    # Adiciona os botões de exportação na sidebar (para o DataFrame filtrado)
    with st.sidebar:
        st.markdown("---")
        st.subheader("📥 Exportar")
        csv_bytes = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV",
            csv_bytes,
            "agendamentos.csv",
            "text/csv",
            width="stretch"
        )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Agendamentos')

        st.download_button(
            "📥 Download Excel",
            buffer.getvalue(),
            "agendamentos.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )

    # Tabs: Gráficos e Dados
    tab_graficos, tab_dados = st.tabs(["📊 Gráficos", "📋 Dados"])

    with tab_graficos:
        # Métricas principais (uso defensivo .get() para evitar KeyError)
        resumo = create_agendamentos_summary(df_filtrado)
        
        st.subheader("📈 Visão Geral")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**Total de Pedidos**")
            st.markdown(f"### {resumo.get('total_pedidos', 0)}")
        with col2:
            st.markdown("**Pedidos por Status**")
            status_counts = resumo.get('status_counts', {})
            if status_counts:
                for status, qtd in status_counts.items():
                    st.write(f"**{status}:** {qtd}")
            else:
                st.write("N/A")
        with col3:
            st.markdown("**Último Agendamento**")
            data_recente = resumo.get('data_recente')
            if data_recente and pd.notna(data_recente):
                st.markdown(f"### {data_recente.strftime('%d/%m/%Y')}")
            else:
                st.markdown("### N/A")
        
        st.markdown("---")
        
        # Gráficos
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.subheader("📊 Distribuição por Status")
            if status_counts:
                # Gráfico de pizza para status
                import plotly.express as px
                fig_status = px.pie(
                    names=list(status_counts.keys()),
                    values=list(status_counts.values()),
                    title="Status dos Pedidos"
                )
                st.plotly_chart(fig_status, width="stretch")
        
        with col_graf2:
            st.subheader("📦 Pedidos por Depósito")
            if 'Depósito' in df_filtrado.columns:
                deposito_counts = df_filtrado['Depósito'].value_counts()
                fig_deposito = px.bar(
                    x=deposito_counts.index,
                    y=deposito_counts.values,
                    title="Quantidade por Depósito",
                    labels={'x': 'Depósito', 'y': 'Quantidade'}
                )
                st.plotly_chart(fig_deposito, width="stretch")
        
        # Segunda linha de gráficos
        col_graf3, col_graf4 = st.columns(2)
        
        with col_graf3:
            st.subheader("📅 Pedidos ao Longo do Tempo")
            if 'Data Agendamento' in df_filtrado.columns:
                df_temp = df_filtrado.copy()
                df_temp['Data'] = pd.to_datetime(df_temp['Data Agendamento']).dt.date
                pedidos_por_dia = df_temp.groupby('Data').size().reset_index(name='Quantidade')
                fig_tempo = px.line(
                    pedidos_por_dia,
                    x='Data',
                    y='Quantidade',
                    title="Evolução de Pedidos"
                )
                st.plotly_chart(fig_tempo, width="stretch")
        
        with col_graf4:
            st.subheader("📦 Top 5 Materiais")
            if 'Descrição do Material' in df_filtrado.columns:
                # Filtra valores nulos e vazios antes de contar
                df_material = df_filtrado[
                    df_filtrado['Descrição do Material'].notna() & 
                    (df_filtrado['Descrição do Material'] != '') &
                    (df_filtrado['Descrição do Material'] != 'None')
                ]
                if not df_material.empty:
                    material_counts = df_material['Descrição do Material'].value_counts().head(5)
                    fig_material = px.bar(
                        x=material_counts.values,
                        y=material_counts.index,
                        orientation='h',
                        title="Top 5 Materiais Mais Agendados",
                        labels={'x': 'Quantidade', 'y': 'Material'}
                    )
                    st.plotly_chart(fig_material, width="stretch")
                else:
                    st.info("Nenhum material com descrição disponível")

    with tab_dados:
        # Exibe o DataFrame filtrado atual
        st.subheader("Resultados")
        st.dataframe(
            df_filtrado,
            width="stretch",
            column_config={
                "Data Agendamento": st.column_config.DatetimeColumn("Data Agendamento"),
                "Status da Entrega": st.column_config.TextColumn("Status da Entrega"),
                "Depósito": st.column_config.TextColumn("Depósito"),
                "Transportadora": st.column_config.TextColumn("Transportadora"),
                "Peso (kg)": st.column_config.NumberColumn("Peso (kg)", format="%.2f"),
                "Quantidade de Volume": st.column_config.NumberColumn("Quantidade de Volume")
            }
        )
    # export buttons removed from tabs - available in sidebar

if __name__ == "__main__":
    main()