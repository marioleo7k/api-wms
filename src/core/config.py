"""
Configurações centralizadas do aplicativo WMS SIGMA
"""

# Configurações de página
PAGE_TITLE = "WMS SIGMA - SABESP"
PAGE_ICON = "assets/favicon.ico"
LAYOUT = "wide"

# Configurações de data
DEFAULT_START_DATE_YEAR = 2025
DEFAULT_START_DATE_MONTH = 1
DEFAULT_START_DATE_DAY = 1

# Configurações de timeout
API_TIMEOUT = 30  # segundos
TOKEN_EXPIRY_MINUTES = 25

# Configurações de UI
CONTAINER_MAX_WIDTH = "98%"
CONTAINER_PADDING = "2rem"
CONTAINER_MARGIN = "2rem auto"
CONTAINER_BORDER_RADIUS = "15px"

# Mensagens
MSG_NO_DATA = "⚠️ Nenhum dado disponível. Tente atualizar usando o botão na barra lateral."
MSG_LOADING = "Carregando dados da API..."
MSG_NO_RESULTS = "⚠️ Nenhum registro encontrado com os filtros aplicados"

# Configurações de gráficos
CHART_HEIGHT = 400
TOP_N_MATERIALS = 5

# Status padrão (caso não haja dados carregados)
DEFAULT_STATUS_OPTIONS = ["AGENDADO", "CONFIRMADO", "CANCELADO", "FINALIZADO"]
