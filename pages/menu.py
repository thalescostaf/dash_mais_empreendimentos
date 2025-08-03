import streamlit as st

# Verificar se o usuário está logado
if "usuario_logado" not in st.session_state or not st.session_state["usuario_logado"]:
    st.warning("⛔ Acesso negado. Por favor, faça login primeiro.")
else:
    st.title("🔑 Menu Principal")
    st.write("Bem-vindo à área principal do sistema.")

# Navegar para a página de fluxo de caixa
if st.button("Ir para Fluxo de Caixa"):
    st.session_state["pagina"] = "fluxo_caixa"
    st.experimental_rerun()  # Recarregar para mostrar a página de fluxo de caixa