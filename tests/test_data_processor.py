"""
Testes para data_processor.py
"""
import pytest
import pandas as pd
from services.data_processor import process_agendamentos_data, create_agendamentos_summary


def test_process_agendamentos_data_empty():
    """Testa processamento com dados vazios"""
    result = process_agendamentos_data([])
    assert result.empty


def test_process_agendamentos_data_single_dict():
    """Testa processamento com único dicionário"""
    data = {'idagendamento': 1, 'status': 'CONFIRMADO'}
    result = process_agendamentos_data(data)
    assert not result.empty
    assert 'ID' in result.columns


def test_create_agendamentos_summary_empty():
    """Testa criação de resumo com DataFrame vazio"""
    df = pd.DataFrame()
    result = create_agendamentos_summary(df)
    
    assert result['total_pedidos'] == 0
    assert result['status_counts'] == {}


def test_create_agendamentos_summary_with_data():
    """Testa criação de resumo com dados"""
    df = pd.DataFrame({
        'ID': [1, 2, 3],
        'Status da Entrega': ['Confirmado', 'Confirmado', 'Agendado'],
        'Data Agendamento': pd.to_datetime(['2025-01-01', '2025-01-02', '2025-01-03'])
    })
    
    result = create_agendamentos_summary(df)
    
    assert result['total_pedidos'] == 3
    assert 'Confirmado' in result['status_counts']
    assert result['status_counts']['Confirmado'] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
