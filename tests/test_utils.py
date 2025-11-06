"""
Testes unitários para utils.py
"""
import pytest
import pandas as pd
from datetime import datetime
from utils import (
    format_date_br,
    format_number,
    safe_get_column_values,
    remove_null_values
)


def test_format_date_br():
    """Testa formatação de data brasileira"""
    date = datetime(2025, 1, 15)
    assert format_date_br(date) == "15/01/2025"
    assert format_date_br(None) == "N/A"
    assert format_date_br(pd.NaT) == "N/A"


def test_format_number():
    """Testa formatação de números"""
    assert format_number(1000.50) == "1.000,50"
    assert format_number(1000000) == "1.000.000,00"
    assert format_number(None) == "N/A"


def test_safe_get_column_values():
    """Testa obtenção segura de valores de coluna"""
    df = pd.DataFrame({
        'status': ['A', 'B', 'A', 'C'],
        'valor': [1, 2, 3, 4]
    })
    
    result = safe_get_column_values(df, 'status')
    assert result == ['A', 'B', 'C']
    
    result = safe_get_column_values(df, 'inexistente', ['default'])
    assert result == ['default']


def test_remove_null_values():
    """Testa remoção de valores nulos"""
    df = pd.DataFrame({
        'col': ['A', None, '', 'None', 'B']
    })
    
    result = remove_null_values(df, 'col')
    assert len(result) == 2
    assert list(result['col']) == ['A', 'B']


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
