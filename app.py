import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializar Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Verificar se o usuário está logado
if "usuario_logado" not in st.session_state:
    st.session_state["usuario_logado"] = False

# Mostrar página de login ou menu
if st.session_state["usuario_logado"]:
    # Se o usuário estiver logado, mostra o menu
    st.write("Bem-vindo, você está autenticado!")
    st.session_state["pagina"] = "menu"  # Marcar que está na página do menu
else:
    # Se o usuário não estiver logado, exibe o login
    st.set_page_config(page_title="Login - Dash", layout="centered")
    st.title("🔐 Login - Sistema Dash")

    email = st.text_input("Email")
    senha = st.text_input("Senha", type="password")
    botao_login = st.button("Entrar")

    if botao_login:
        try:
            # Tenta autenticar o usuário com email e senha
            usuario = supabase.auth.sign_in_with_password({"email": email, "password": senha})

            # Busca na tabela usuarios_dash se está aprovado
            dados = supabase.table("usuarios_dash").select("*").eq("email", email).execute()

            if len(dados.data) == 0:
                st.error("❌ Usuário não encontrado na base de dados.")
            elif not dados.data[0]['aprovado']:
                st.warning("⛔ Seu cadastro ainda não foi aprovado.")
            else:
                st.success(f"✅ Bem-vindo, {dados.data[0]['nome']}!")
                # Armazenar no session_state que o usuário está logado
                st.session_state["usuario_logado"] = True
                st.session_state["usuario"] = {
                    "id": dados.data[0]['id'],
                    "nome": dados.data[0]['nome']  # Se o nome foi configurado no Supabase
                }
                st.session_state["pagina"] = "menu"  # Marcar a página do menu
        except Exception as e:
            st.error("Erro ao autenticar. Verifique email/senha.")
            st.exception(e)

# Se estiver na página do menu, exibe a página
if "pagina" in st.session_state and st.session_state["pagina"] == "menu":
    st.write("Bem-vindo ao Menu Principal!")
    # Botões de navegação para outras páginas
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Ir para Lançamentos"):
            # Navega para a página de lançamentos
            st.switch_page("pages/lancamentos.py")
    
    with col2:
        if st.button("Ir para Métricas"):
            # Navega para a página de métricas
            st.switch_page("pages/metricas.py")
