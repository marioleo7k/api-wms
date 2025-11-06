"""
Funções utilitárias para o aplicativo WMS
"""
import base64
from typing import Optional
import pandas as pd
from datetime import datetime


def get_base64_image(image_path: str) -> str:
    """
    Converte uma imagem em string base64
    
    Args:
        image_path: Caminho para a imagem
        
    Returns:
        String base64 da imagem
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""


def format_date_br(date: Optional[datetime]) -> str:
    """
    Formata data no padrão brasileiro
    
    Args:
        date: Objeto datetime
        
    Returns:
        Data formatada como dd/mm/yyyy ou "N/A"
    """
    if date and pd.notna(date):
        return date.strftime('%d/%m/%Y')
    return "N/A"


def format_number(value: float, decimals: int = 2) -> str:
    """
    Formata número com separador de milhares
    
    Args:
        value: Valor numérico
        decimals: Número de casas decimais
        
    Returns:
        Número formatado
    """
    try:
        return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "N/A"


def safe_get_column_values(df: pd.DataFrame, column: str, default: list = None) -> list:
    """
    Obtém valores únicos de uma coluna de forma segura
    
    Args:
        df: DataFrame
        column: Nome da coluna
        default: Lista padrão se coluna não existir
        
    Returns:
        Lista de valores únicos
    """
    if default is None:
        default = []
    
    if column in df.columns:
        return sorted(df[column].dropna().unique().tolist())
    return default


def filter_dataframe_by_date(
    df: pd.DataFrame,
    date_column: str,
    start_date,
    end_date
) -> pd.DataFrame:
    """
    Filtra DataFrame por intervalo de datas
    
    Args:
        df: DataFrame a filtrar
        date_column: Nome da coluna de data
        start_date: Data inicial
        end_date: Data final
        
    Returns:
        DataFrame filtrado
    """
    if date_column not in df.columns:
        return df
    
    # Garante que a coluna está em formato datetime
    df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    
    # Filtra
    mask = (
        (df[date_column].dt.date >= start_date) &
        (df[date_column].dt.date <= end_date)
    )
    return df[mask]


def remove_null_values(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Remove valores nulos, vazios e 'None' de uma coluna
    
    Args:
        df: DataFrame
        column: Nome da coluna
        
    Returns:
        DataFrame filtrado
    """
    if column not in df.columns:
        return df
    
    return df[
        df[column].notna() & 
        (df[column] != '') &
        (df[column] != 'None')
    ]
