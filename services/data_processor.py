import pandas as pd
import streamlit as st
from typing import Dict, List, Any
from datetime import datetime

def process_agendamentos_data(api_data: List[Dict]) -> pd.DataFrame:
    """
    Processa os dados de agendamentos da API WMS
    
    Args:
        api_data: Lista de agendamentos da API
        
    Returns:
        DataFrame com dados processados
    """
    # Garante que temos dados válidos
    if not api_data:
        return pd.DataFrame()
    
    try:
        # Se recebemos um único dicionário, converte para lista
        if isinstance(api_data, dict):
            api_data = [api_data]
        
        # Se não é uma lista neste ponto, retorna DataFrame vazio
        if not isinstance(api_data, list):
            st.error("❌ Formato de dados inválido")
            return pd.DataFrame()
            
        # Remove itens None ou vazios da lista
        api_data = [item for item in api_data if item]
        
        if not api_data:
            st.warning("⚠️ Nenhum dado válido encontrado")
            return pd.DataFrame()
            
        # Cria DataFrame principal
        df_main = pd.DataFrame(api_data)
        
        # Lista para armazenar dados expandidos (com pedidos)
        expanded_data = []
        
        for _, agendamento in df_main.iterrows():
            base_data = agendamento.to_dict()
            
            # Se não houver pedidos, adiciona uma linha
            if not agendamento.get('pedidos') or not isinstance(agendamento['pedidos'], list):
                expanded_data.append(base_data)
            else:
                # Expande os pedidos (uma linha por pedido)
                for pedido in agendamento['pedidos']:
                    combined_data = base_data.copy()
                    combined_data.update({
                        'pedido_numero': pedido.get('peiddo', ''),
                        'codigo_material': pedido.get('codigo', ''),
                        'material': pedido.get('material', ''),
                        'quantidade_pedido': pedido.get('quantidade', '')
                    })
                    expanded_data.append(combined_data)
        
        # Cria DataFrame final
        df_final = pd.DataFrame(expanded_data)
        
        # Processa colunas de data
        date_columns = ['dtcadastro', 'dtconfirmacao', 'dtagendamento', 'dtconfirmada']
        for col in date_columns:
            if col in df_final.columns:
                df_final[col] = pd.to_datetime(df_final[col], errors='coerce', dayfirst=True)
        
        # Converte colunas numéricas
        numeric_columns = ['qnt_volume', 'peso', 'quantidade_pedido']
        for col in numeric_columns:
            if col in df_final.columns:
                df_final[col] = pd.to_numeric(df_final[col], errors='coerce')
        
        # Ordena por data de agendamento
        if 'dtagendamento' in df_final.columns:
            df_final = df_final.sort_values('dtagendamento', ascending=False)
        
        # Renomeia colunas (adicione mais mapeamentos conforme necessário)
        rename_map = {
            'idagendamento': 'ID',
            'galpao': 'Depósito',
            'dtcadastro' : 'Data Cadastro',
            'dtconfirmacao' : 'Data Confirmação',
            'cnpj' : 'CNPJ',
            'razao' : 'Fornecedor',
            # Algumas cargas podem vir como 'transportadora' ou 'nome_transportadora'
            'nome_transportadora': 'Transportadora',
            'transportadora': 'Transportadora',
            'placa' : 'Placa do Veículo',
            'cnh' : 'CNH',
            'motorista' : 'Motorista',
            'dtagendamento': 'Data Agendamento',
            'dtalteracao': 'Data Alteração',
            'dtconfirmada': 'Data Confirmada',
            'status': 'Status da Entrega',
            'tipo_veiculo': 'Tipo de Veículo',
            'tipo_material': 'Tipo de Material',
            'qnt_volume': 'Quantidade de Volume',
            'peso': 'Peso (kg)',
            'usuario' : 'Usuário',
            'observacao' : 'Observação',
            'justificativa_cancelamento' : 'Justificativa do Cancelamento', 
            'pedidos' : 'Pedidos',
            'pedido_numero': 'Documento de Compra',
            'codigo_material': 'Código do Material',
            'material': 'Descrição do Material',
            'quantidade_pedido': 'Quantidade do Pedido'
        }
        df_final = df_final.rename(columns=rename_map)
        
        # Remove a coluna Pedidos pois já foi expandida em outras colunas
        df_final = df_final.drop(columns=['Pedidos'], errors='ignore')
        
        return df_final
        
    except Exception as e:
        st.error(f"❌ Erro ao processar dados: {e}")
        return pd.DataFrame()

def create_agendamentos_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Cria um resumo dos agendamentos
    
    Args:
        df: DataFrame com dados processados
        
    Returns:
        Dicionário com métricas de resumo
    """
    if df.empty:
        # Retorna um resumo padrão com zeros para evitar KeyError ao consumir o resultado
        return {
            'total_agendamentos': 0,
            'total_pedidos': 0,
            'galpoes_unicos': 0,
            'status_counts': {},
            'galpao_counts': {},
            'peso_total': 0,
            'volume_total': 0
        }
    
    summary = {
        'total_agendamentos': len(df['ID'].unique()) if 'ID' in df.columns else 0,
        'total_pedidos': len(df) if 'Documento de Compra' in df.columns else 0,
        'galpoes_unicos': df['Depósito'].nunique() if 'Depósito' in df.columns else 0,
        'status_counts': df['Status da Entrega'].value_counts().to_dict() if 'Status da Entrega' in df.columns else {},
        'galpao_counts': df['Depósito'].value_counts().to_dict() if 'Depósito' in df.columns else {},
        'peso_total': df['Peso (kg)'].sum() if 'Peso (kg)' in df.columns else 0,
        'volume_total': df['Quantidade de Volume'].sum() if 'Quantidade de Volume' in df.columns else 0,
        'data_recente': df['Data Agendamento'].max() if 'Data Agendamento' in df.columns else None
    }
    
    return summary

def filter_agendamentos(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """
    Filtra os agendamentos com base nos critérios
    
    Args:
        df: DataFrame com dados processados
        filters: Dicionário com filtros a aplicar
        
    Returns:
        DataFrame filtrado
    """
    filtered_df = df.copy()
    
    # Filtro por galpão
    if filters.get('galpao') and 'galpao' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['galpao'] == filters['galpao']]
    
    # Filtro por status
    if filters.get('status') and 'status' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['status'] == filters['status']]
    
    # Filtro por data (período)
    if filters.get('data_inicio') and 'dtagendamento' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['dtagendamento'] >= filters['data_inicio']]
    
    if filters.get('data_fim') and 'dtagendamento' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['dtagendamento'] <= filters['data_fim']]
    
    # Filtro por transportadora
    if filters.get('transportadora') and 'Transportadora' in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df['Transportadora'].str.contains(
                filters['transportadora'], case=False, na=False
            )
        ]
    
    return filtered_df