import streamlit as st
import pandas as pd
import io
import plotly.express as px
from datetime import datetime

# Imports dos serviços
from services.api_client import get_wms_client
from services.data_processor import process_agendamentos_data, create_agendamentos_summary

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
        dados_brutos = client.get_agendamentos(todos=True)
        if not dados_brutos:
            return pd.DataFrame()
        return process_agendamentos_data(dados_brutos)
    except Exception as e:
        st.error(f"❌ Erro ao carregar agendamentos: {str(e)}")
        return pd.DataFrame()

def main():
    st.title("🚚 WMS SIGMA - Agendamentos de Materiais")
    
    if 'df_original' not in st.session_state:
        message_placeholder = st.empty()
        with message_placeholder.container():
            with st.spinner("Carregando dados da API..."):
                df_all = carregar_agendamentos()
                if df_all is not None and not df_all.empty:
                    if 'Data Agendamento' in df_all.columns:
                        df_all['Data Agendamento'] = pd.to_datetime(df_all['Data Agendamento'], errors='coerce')
                    st.session_state['df_original'] = df_all
                else:
                    st.session_state['df_original'] = pd.DataFrame()
        import time
        time.sleep(3)
        message_placeholder.empty()
    
    with st.sidebar:
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

        if 'df_original' in st.session_state and not st.session_state['df_original'].empty:
            df_orig = st.session_state['df_original']
            status_options = ["Todos"] + sorted(df_orig['Status da Entrega'].dropna().unique().tolist()) if 'Status da Entrega' in df_orig.columns else ["Todos"]
            galpao_options = ["Todos"] + sorted(df_orig['Depósito'].dropna().unique().tolist()) if 'Depósito' in df_orig.columns else ["Todos"]
        else:
            status_options = ["Todos", "AGENDADO", "CONFIRMADO", "CANCELADO", "FINALIZADO"]
            galpao_options = ["Todos"]

        filtro_status = st.selectbox("Status", status_options)
        filtro_galpao = st.selectbox("Depósito", galpao_options)
        filtro_transportadora = st.text_input("Transportadora", placeholder="Digite para filtrar...")

        st.markdown("---")
        if st.button("🔄 Atualizar Dados", width='stretch'):
            with st.spinner("Buscando todos os agendamentos disponíveis..."):
                df_all = carregar_agendamentos()
                if df_all is None or df_all.empty:
                    st.warning("⚠️ Nenhum dado encontrado na API")
                else:
                    if 'Data Agendamento' in df_all.columns:
                        df_all['Data Agendamento'] = pd.to_datetime(df_all['Data Agendamento'], errors='coerce')
                    st.session_state['df_original'] = df_all
                    st.success(f"✅ {len(df_all)} registros carregados!")
    
    if 'df_original' not in st.session_state or st.session_state['df_original'].empty:
        st.warning("⚠️ Nenhum dado disponível. Tente atualizar usando o botão na barra lateral.")
        return

    df_original = st.session_state['df_original']

    if 'Data Agendamento' in df_original.columns and not pd.api.types.is_datetime64_any_dtype(df_original['Data Agendamento']):
        df_original['Data Agendamento'] = pd.to_datetime(df_original['Data Agendamento'], errors='coerce')

    df_filtrado = df_original.copy()

    if 'Data Agendamento' in df_filtrado.columns:
        mask = (
            (df_filtrado['Data Agendamento'].dt.date >= data_inicio) &
            (df_filtrado['Data Agendamento'].dt.date <= data_fim)
        )
        df_filtrado = df_filtrado[mask]

    if filtro_status and filtro_status != "Todos" and 'Status da Entrega' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Status da Entrega'] == filtro_status]

    if filtro_galpao and filtro_galpao != "Todos" and 'Depósito' in df_filtrado.columns:
        df_filtrado = df_filtrado[df_filtrado['Depósito'] == filtro_galpao]

    if filtro_transportadora:
        if 'Transportadora' in df_filtrado.columns:
            df_filtrado = df_filtrado[
                df_filtrado['Transportadora'].str.contains(filtro_transportadora, case=False, na=False)
            ]

    if df_filtrado is None or df_filtrado.empty:
        st.warning("⚠️ Nenhum registro encontrado com os filtros aplicados")
        return

    with st.sidebar:
        st.markdown("---")
        st.subheader("📥 Exportar")
        csv_bytes = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download CSV",
            csv_bytes,
            "agendamentos.csv",
            "text/csv",
            width='stretch'
        )

        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name='Agendamentos')

        st.download_button(
            "📥 Download Excel",
            buffer.getvalue(),
            "agendamentos.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )

    tab_graficos, tab_dados, tab_calendario = st.tabs(["📊 Gráficos", "📋 Dados", "🗓️ Calendário"])

    with tab_graficos:
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
        
        col_graf1, col_graf2 = st.columns(2)
        
        with col_graf1:
            st.subheader("📊 Distribuição por Status")
            if status_counts:
                fig_status = px.pie(
                    names=list(status_counts.keys()),
                    values=list(status_counts.values()),
                    title="Status dos Pedidos"
                )
                fig_status.update_layout(margin=dict(l=10,r=10,t=50,b=10), legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5))
                st.plotly_chart(fig_status, config={'displayModeBar': False, 'responsive': True})
        
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
                fig_deposito.update_layout(margin=dict(l=10,r=10,t=50,b=10))
                st.plotly_chart(fig_deposito, config={'displayModeBar': False, 'responsive': True})
        
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
                fig_tempo.update_traces(line=dict(width=2))
                fig_tempo.update_layout(margin=dict(l=10,r=10,t=50,b=10))
                st.plotly_chart(fig_tempo, config={'displayModeBar': False, 'scrollZoom': True, 'responsive': True})
        
        with col_graf4:
            st.subheader("📦 Top 5 Materiais")
            if 'Descrição do Material' in df_filtrado.columns:
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
                    fig_material.update_layout(margin=dict(l=10,r=10,t=50,b=10))
                    st.plotly_chart(fig_material, config={'displayModeBar': False, 'responsive': True})
                else:
                    st.info("Nenhum material com descrição disponível")

    with tab_dados:
        st.subheader("Resultados")
        st.dataframe(
            df_filtrado,
            width='stretch',
            hide_index=True,
            column_config={
                "Data Agendamento": st.column_config.DatetimeColumn("Data Agendamento"),
                "Status da Entrega": st.column_config.TextColumn("Status da Entrega"),
                "Depósito": st.column_config.TextColumn("Depósito"),
                "Transportadora": st.column_config.TextColumn("Transportadora"),
                "Peso (kg)": st.column_config.NumberColumn("Peso (kg)", format="%.2f"),
                "Quantidade de Volume": st.column_config.NumberColumn("Quantidade de Volume")
            }
        )
    
    with tab_calendario:
        st.subheader("Visão de Calendário dos Agendamentos")
        if 'Data Agendamento' not in df_filtrado.columns:
            st.info("Coluna 'Data Agendamento' não disponível nos dados filtrados.")
        else:
            df_cal = df_filtrado.copy()
            df_cal['Data'] = pd.to_datetime(df_cal['Data Agendamento']).dt.date
            if df_cal['Data'].isna().all():
                st.warning("Sem datas válidas para exibir no calendário.")
            else:
                import calendar
                
                hoje = datetime.now().date()
                
                st.markdown("### 🔍 Filtros")
                col1, col2, col3, col4, col5, col6 = st.columns(6)
                
                anos_disponiveis = sorted({d.year for d in df_cal['Data'] if pd.notna(d)})
                nome_meses = {1:'Janeiro',2:'Fevereiro',3:'Março',4:'Abril',5:'Maio',6:'Junho',7:'Julho',8:'Agosto',9:'Setembro',10:'Outubro',11:'Novembro',12:'Dezembro'}
                depositos_disponiveis = ['Todos'] + sorted(df_cal['Depósito'].dropna().unique().tolist()) if 'Depósito' in df_cal.columns else ['Todos']
                
                ano_atual_idx = anos_disponiveis.index(hoje.year) if hoje.year in anos_disponiveis else len(anos_disponiveis)-1
                mes_atual_nome = nome_meses[hoje.month]
                
                with col1:
                    dia_sel = st.selectbox("📅 Dia", ['Todos'] + list(range(1, 32)), index=0)
                with col2:
                    mes_sel_idx = st.selectbox("📅 Mês", list(nome_meses.values()), index=list(nome_meses.values()).index(mes_atual_nome) if mes_atual_nome in list(nome_meses.values()) else 0)
                    mes_num = [k for k, v in nome_meses.items() if v == mes_sel_idx][0]
                with col3:
                    ano_sel = st.selectbox("📆 Ano", anos_disponiveis, index=ano_atual_idx)
                
                # Blindagem para o analisador e segurança em tempo de execução
                ano_sel = int(ano_sel) if ano_sel is not None else hoje.year
                mes_num = int(mes_num) if mes_num is not None else hoje.month
                with col4:
                    deposito_sel = st.selectbox("🏢 Depósito", depositos_disponiveis, index=0)
                with col5:
                    fornecedor_sel = st.text_input("🏭 Fornecedor", placeholder="Digite o fornecedor...")
                with col6:
                    codigo_material_sel = st.text_input("📦 Código Material", placeholder="Digite o código...")
                
                df_filtrado_cal = df_cal.copy()
                df_filtrado_cal = df_filtrado_cal[df_filtrado_cal['Data'].apply(lambda d: d.year == ano_sel and d.month == mes_num)]
                
                if dia_sel != 'Todos':
                    df_filtrado_cal = df_filtrado_cal[df_filtrado_cal['Data'].apply(lambda d: d.day == dia_sel)]
                
                if deposito_sel != 'Todos' and 'Depósito' in df_filtrado_cal.columns:
                    df_filtrado_cal = df_filtrado_cal[df_filtrado_cal['Depósito'] == deposito_sel]
                
                if fornecedor_sel and 'Fornecedor' in df_filtrado_cal.columns:
                    df_filtrado_cal = df_filtrado_cal[df_filtrado_cal['Fornecedor'].str.contains(fornecedor_sel, case=False, na=False)]
                
                if codigo_material_sel and 'Código do Material' in df_filtrado_cal.columns:
                    df_filtrado_cal = df_filtrado_cal[df_filtrado_cal['Código do Material'].astype(str).str.contains(codigo_material_sel, case=False, na=False)]
                
                counts_por_dia = df_filtrado_cal.groupby('Data').size().to_dict()
                
                total_filtrado = len(df_filtrado_cal)
                dias_com_ag = len(counts_por_dia)
                st.info(f"📊 **{total_filtrado}** agendamentos encontrados em **{dias_com_ag}** dias")
                
                st.markdown("---")
                
                cal = calendar.Calendar(firstweekday=0)
                semanas = cal.monthdayscalendar(ano_sel, mes_num)
                
                css_cal = """
                <style>
                table.calendario {
                    width:100%; 
                    border-collapse:collapse; 
                    table-layout:fixed;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    border-radius: 8px;
                    overflow: hidden;
                }
                table.calendario th {
                    background: linear-gradient(135deg, #005BAC 0%, #003d73 100%);
                    color: #fff; 
                    padding: 12px;
                    font-size: 0.9rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                table.calendario td {
                    border: 1px solid #e0e0e0; 
                    height: 90px; 
                    vertical-align: top; 
                    padding: 8px;
                    font-size: 0.85rem;
                    background: #fff;
                    transition: all 0.2s ease;
                }
                table.calendario td .dia {
                    font-weight: 700;
                    font-size: 1.1rem;
                    color: #333;
                    margin-bottom: 4px;
                }
                table.calendario td .badge {
                    display: inline-block;
                    background: #005BAC;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 12px;
                    font-size: 0.7rem;
                    font-weight: 600;
                    margin-top: 4px;
                }
                table.calendario td.empty {
                    background: #f5f5f5;
                    pointer-events: none;
                }
                table.calendario td.com-agendamento {
                    background: linear-gradient(135deg, #e6f2ff 0%, #cce5ff 100%);
                    cursor: pointer;
                    border-left: 3px solid #005BAC;
                }
                table.calendario td.com-agendamento:hover {
                    background: linear-gradient(135deg, #cce5ff 0%, #99ccff 100%);
                    transform: scale(1.02);
                    box-shadow: 0 4px 12px rgba(0,91,172,0.3);
                }
                table.calendario td.com-agendamento .dia {
                    color: #005BAC;
                }
                table.calendario td.hoje {
                    border: 2px solid #FF9800;
                    box-shadow: 0 0 10px rgba(255,152,0,0.3);
                }
                table.calendario td.fim-de-semana {
                    background: #fafafa;
                }
                </style>
                """
                
                html = [css_cal, '<table class="calendario">']
                html.append(f'<tr><th colspan="7" style="font-size:1.1rem; padding:16px;">{mes_sel_idx} / {ano_sel}</th></tr>')
                html.append('<tr>' + ''.join(f'<th>{d}</th>' for d in ['Seg','Ter','Qua','Qui','Sex','Sáb','Dom']) + '</tr>')
                
                hoje = datetime.now().date()
                
                for semana in semanas:
                    html.append('<tr>')
                    for idx, dia in enumerate(semana):
                        if dia == 0:
                            html.append('<td class="empty"></td>')
                        else:
                            data_atual = datetime(ano_sel, mes_num, dia).date()
                            qtd = counts_por_dia.get(data_atual, 0)
                            classes = []
                            if qtd > 0:
                                classes.append('com-agendamento')
                            if data_atual == hoje:
                                classes.append('hoje')
                            if idx >= 5:
                                classes.append('fim-de-semana')
                            cls = ' '.join(classes)
                            if qtd > 0:
                                html.append(f'<td class="{cls}"><div class="dia">{dia}</div><div class="badge">{qtd} agendamento{"s" if qtd > 1 else ""}</div></td>')
                            else:
                                html.append(f'<td class="{cls}"><div class="dia">{dia}</div></td>')
                    html.append('</tr>')
                html.append('</table>')
                st.markdown('\n'.join(html), unsafe_allow_html=True)
                
                st.markdown("---")
                
                if len(df_filtrado_cal) > 0:
                    st.markdown(f"### 📋 Agendamentos ({len(df_filtrado_cal)})")
                    st.dataframe(
                        df_filtrado_cal.drop(columns=['Data']),
                        width='stretch',
                        hide_index=True,
                        column_config={
                            "Data Agendamento": st.column_config.DatetimeColumn("Data/Hora", format="DD/MM/YYYY HH:mm"),
                            "Status da Entrega": st.column_config.TextColumn("Status"),
                            "Depósito": st.column_config.TextColumn("Depósito"),
                            "Transportadora": st.column_config.TextColumn("Transportadora"),
                            "Peso (kg)": st.column_config.NumberColumn("Peso (kg)", format="%.2f"),
                        }
                    )
                else:
                    st.info("📭 Nenhum agendamento encontrado com os filtros selecionados.")

if __name__ == "__main__":
    main()