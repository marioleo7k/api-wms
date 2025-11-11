# 🚚 WMS SIGMA - Sistema de Agendamentos de Materiais

Sistema de visualização e análise de agendamentos de materiais da SIGMA para SABESP, desenvolvido com Streamlit.

## 📋 Funcionalidades

- **Dashboard Interativo**: Visualização em tempo real dos agendamentos
- **Gráficos Analíticos**:
  - Distribuição por Status
  - Pedidos por Depósito
  - Evolução temporal
  - Top 5 Materiais mais agendados
- **Filtros Avançados**: Por data, status, depósito e transportadora
- **Exportação**: Download em CSV e Excel
- **Carregamento Automático**: Dados carregados automaticamente ao iniciar

## Documentação das Colunas da API

| Nome Original              | Nome Alterado                 | Tipagem   | Observação                                                                                         |
| -------------------------- | ----------------------------- | --------- | ---------------------------------------------------------------------------------------------------- |
| idagendamento              | ID                            | int/str   |                                                                                                      |
| galpao                     | Depósito                     | str       |                                                                                                      |
| dtcadastro                 | Data Cadastro                 | datetime  | Data que o fornecedor cadastrou a informação no sistema SIGMA                                      |
| dtconfirmacao              | Data Confirmação            | datetime  |                                                                                                      |
| cnpj                       | CNPJ                          | str       |                                                                                                      |
| razao                      | Fornecedor                    | str       |                                                                                                      |
| nome_transportadora        | Transportadora                | str       |                                                                                                      |
| transportadora             | Transportadora                | str       |                                                                                                      |
| placa                      | Placa do Veículo             | str       |                                                                                                      |
| cnh                        | CNH                           | str       |                                                                                                      |
| motorista                  | Motorista                     | str       |                                                                                                      |
| dtagendamento              | Data Agendamento              | datetime  | Data informada pelo fornecedor que ele pretende entregar o material                                  |
| dtalteracao                | Data Alteração              | datetime  | Data que teve alteração do registro da agenda                                                      |
| dtconfirmada               | Data Confirmada               | datetime  | Confirmação do almoxarifado, garantindo a data de agendamento e horário que o fornecedor informou |
| status                     | Status da Entrega             | str       |                                                                                                      |
| tipo_veiculo               | Tipo de Veículo              | str       |                                                                                                      |
| tipo_material              | Tipo de Material              | str       |                                                                                                      |
| qnt_volume                 | Quantidade de Volume          | int/float |                                                                                                      |
| peso                       | Peso (kg)                     | float     | Peso total da carga informado pelo fornecedor                                                        |
| usuario                    | Usuário                      | str       |                                                                                                      |
| observacao                 | Observação                  | str       |                                                                                                      |
| justificativa_cancelamento | Justificativa do Cancelamento | str       | Justificativa inserida pelo almoxarifado                                                             |
| pedidos                    | Pedidos                       | list      | Removida após expansão                                                                             |
| pedido_numero              | Documento de Compra           | str       |                                                                                                      |
| codigo_material            | Código do Material           | str       |                                                                                                      |
| material                   | Descrição do Material       | str       |                                                                                                      |
| quantidade_pedido          | Quantidade do Pedido          | int/float |                                                                                                      |

## Tecnologias

- **Streamlit** - Framework web
- **Pandas** - Manipulação de dados
- **Plotly** - Visualizações interativas
- **Requests** - Comunicação com API

## 📦 Instalação

1. Clone o repositório:

```bash
git clone <seu-repositorio>
cd api-wms
```

2. Crie e ative o ambiente virtual:

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure as credenciais em `.streamlit/secrets.toml`:

```toml
[api_wms]
BASE_URL = "https://sua-api.com"
LOGIN = "seu_login"
PASSWORD = "sua_senha"
```

## 🚀 Execução

```bash
streamlit run app.py
```

Acesse: http://localhost:8501

## 📁 Estrutura do Projeto

```
api-wms/
├── app.py                       # Aplicação principal
│
├── src/                         # Código fonte organizado
│   ├── core/                    # Funcionalidades centrais
│   │   ├── config.py           # Configurações do app
│   │   ├── utils.py            # Funções utilitárias
│   │   └── logger.py           # Sistema de logs
│   └── ui/                      # Interface de usuário
│       └── components.py       # Componentes visuais
│
├── services/                    # Camada de serviços
│   ├── api_client.py           # Cliente da API WMS
│   └── data_processor.py       # Processamento de dados
│
├── tests/                       # Testes unitários
│   ├── test_utils.py
│   └── test_data_processor.py
│
├── scripts/                     # Scripts de manutenção
├── assets/                      # Recursos estáticos
│   ├── favicon.ico             # Ícone do site
│   └── background.png          # Imagem de fundo
│
├── docs/                        # Documentação da API
├── logs/                        # Arquivos de log
├── .streamlit/                  # Configurações Streamlit
│   ├── config.toml
│   └── secrets.toml
│
├── requirements.txt             # Dependências
└── README.md                    # Este arquivo

```

## 🔒 Segurança

- Nunca commite o arquivo `secrets.toml`
- Use variáveis de ambiente em produção
- Token JWT com renovação automática (25 min)

## 📊 Uso

1. **Visualização**: Os dados são carregados automaticamente
2. **Filtros**: Use a sidebar para filtrar por período, status, depósito ou transportadora
3. **Gráficos**: Acesse a aba "📊 Gráficos" para análises visuais
4. **Dados**: Veja a tabela completa na aba "📋 Dados"
5. **Exportação**: Use os botões na sidebar para baixar os dados

## 📝 Licença

Este projeto está sob a licença especificada em LICENSE.md

## 👤 Autor

Para quaisquer dúvidas ou melhorias, contactar mariodasilva.sabesp@meetupconsultoria.com.br
