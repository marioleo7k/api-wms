"""
Configuração de logging para o aplicativo
"""
import logging
import sys
from datetime import datetime

# Configuração básica de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Logger principal
logger = logging.getLogger('wms_sigma')


def log_api_call(endpoint: str, success: bool, records_count: int = 0):
    """
    Registra chamada à API
    
    Args:
        endpoint: Endpoint chamado
        success: Se foi bem-sucedida
        records_count: Número de registros retornados
    """
    if success:
        logger.info(f"API call successful - Endpoint: {endpoint}, Records: {records_count}")
    else:
        logger.error(f"API call failed - Endpoint: {endpoint}")


def log_error(error: Exception, context: str = ""):
    """
    Registra erro com contexto
    
    Args:
        error: Exceção ocorrida
        context: Contexto adicional
    """
    logger.error(f"Error in {context}: {str(error)}", exc_info=True)


def log_user_action(action: str, details: str = ""):
    """
    Registra ação do usuário
    
    Args:
        action: Ação realizada
        details: Detalhes adicionais
    """
    logger.info(f"User action - {action}: {details}")
