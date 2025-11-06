import requests
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime

class WMSAPIClient:
    def __init__(self, base_url: Optional[str] = None, login: Optional[str] = None, password: Optional[str] = None):
        # Tenta usar as credenciais fornecidas, senão usa as do Streamlit
        self.base_url = base_url or st.secrets["api_wms"]["BASE_URL"]
        self.login = login or st.secrets["api_wms"]["LOGIN"]
        self.password = password or st.secrets["api_wms"]["PASSWORD"]
        self.token = None
        self.token_expiry = None
        self.session = requests.Session()
        
        # Headers padrão
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Streamlit-SABESP/1.0"
        })
    
    def _is_token_valid(self) -> bool:
        """Verifica se o token ainda é válido (25 minutos)"""
        if not self.token or not self.token_expiry:
            return False
        
        # Verifica se o token expirou (25 minutos de validade)
        return datetime.now().timestamp() < self.token_expiry
    
    def _login(self) -> bool:
        """Faz login e obtém token JWT"""
        try:
            login_url = f"{self.base_url}/login"
            payload = {
                "login": self.login,
                "password": self.password
            }
            
            response = self.session.post(login_url, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("autenticacao") and data.get("token"):
                self.token = data["token"]
                # Define expiração para 25 minutos a partir de agora
                self.token_expiry = datetime.now().timestamp() + (25 * 60)
                
                # Atualiza headers com o token
                self.session.headers.update({
                    "Authorization": self.token
                })
                
                st.success("✅ Autenticado com sucesso na API WMS")
                
                # Limpa a mensagem após 2 segundos
                import time
                time.sleep(2)
                
                return True
            else:
                st.error("❌ Falha na autenticação")
                return False
                
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Erro de conexão: {e}")
            return False
        except Exception as e:
            st.error(f"❌ Erro inesperado: {e}")
            return False
    
    def _ensure_authenticated(self) -> bool:
        """Garante que temos um token válido"""
        if not self._is_token_valid():
            return self._login()
        return True
    
    def get_agendamentos(self, data_consulta: Optional[str] = None, todos: bool = False) -> List[Dict[str, Any]]:
        """
        Busca agendamentos da API WMS
        
        Args:
            data_consulta: String no formato "dd.mm.aaaa - dd.mm.aaaa"
                         Se None e todos=False, retorna agendamentos do dia atual
            todos: Se True, retorna todos os agendamentos independente da data
                  
        Returns:
            List[Dict[str, Any]]: Lista de agendamentos. Lista vazia se houver erro.
        """
        if not self._ensure_authenticated():
            st.error("❌ Falha na autenticação")
            return []
            
        # Determina o período de consulta
        try:
            if todos:
                # Para todos os agendamentos, não enviamos data
                data_consulta = ""
                # st.info("🔍 Buscando todos os agendamentos disponíveis...")
            elif not data_consulta:
                # Se não especificou data e não pediu todos, usa data atual
                hoje = datetime.now().strftime("%d.%m.%Y")
                data_consulta = f"{hoje} - {hoje}"
                # st.info(f"🔍 Buscando agendamentos do dia {hoje}...")
            else:
                # Validar formato da data fornecida
                try:
                    inicio, fim = data_consulta.split(" - ")
                    data_inicio = datetime.strptime(inicio, "%d.%m.%Y")
                    data_fim = datetime.strptime(fim, "%d.%m.%Y")
                    
                    # Verifica se a data final não é menor que a inicial
                    if data_fim < data_inicio:
                        st.error("❌ Data final não pode ser menor que a data inicial")
                        return []
                        
                    # st.info(f"🔍 Buscando agendamentos de {inicio} até {fim}...")
                except ValueError:
                    st.error("❌ Formato de data inválido. Use: dd.mm.aaaa - dd.mm.aaaa")
                    return []
        except Exception as e:
            st.error(f"❌ Erro ao processar datas: {str(e)}")
            return []
        
        try:
            endpoint = f"{self.base_url}/agendamento/lista"
            # Se não tem data_consulta, não inclui no payload
            payload = {}
            if data_consulta:
                payload["diconsulta"] = data_consulta
            
            response = self.session.post(endpoint, json=payload, timeout=30)
            
            # Verifica o código de status primeiro
            if response.status_code != 200:
                st.error(f"❌ Erro na API: Status {response.status_code}")
                if response.text:
                    st.error(f"Detalhes: {response.text}")
                return []
            
            # Processa a resposta
            try:
                data = response.json()
                
                # Processa baseado no tipo da resposta
                if isinstance(data, list):
                    agendamentos = data
                elif isinstance(data, dict):
                    agendamentos = data.get("agendamentos", [])
                    if not isinstance(agendamentos, list):
                        st.error("❌ Campo 'agendamentos' não é uma lista")
                        return []
                else:
                    st.error("❌ Formato de resposta inválido")
                    return []
                
                # Valida e retorna os agendamentos
                if not agendamentos:
                    st.warning("⚠️ Nenhum agendamento encontrado no período")
                # else:
                #     st.success(f"✅ {len(agendamentos)} agendamentos encontrados")
                
                return agendamentos
                
            except ValueError as e:
                st.error(f"❌ Erro ao decodificar JSON da resposta: {str(e)}")
                return []
            except Exception as e:
                st.error(f"❌ Erro ao processar resposta: {str(e)}")
                return []
                
        except requests.exceptions.Timeout:
            st.error("⏰ Timeout na requisição à API WMS (30s)")
            return []
        except requests.exceptions.ConnectionError as e:
            st.error(f"🔌 Erro de conexão com a API WMS: {str(e)}")
            return []
        except Exception as e:
            st.error(f"❌ Erro inesperado ao fazer requisição: {str(e)}")
            return []
    
    def test_connection(self) -> bool:
        """Testa a conexão com a API"""
        return self._login()

# Factory function com cache
@st.cache_resource
def get_wms_client():
    """Retorna uma instância do cliente WMS (cacheada)"""
    return WMSAPIClient()

