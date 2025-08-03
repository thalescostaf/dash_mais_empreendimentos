import streamlit as st

# Verifica se usuário está logado
if "usuario_logado" not in st.session_state or not st.session_state["usuario_logado"]:
    st.warning("⛔ Acesso negado. Por favor, faça login primeiro.")
    st.stop()

st.title("🔑 Menu Principal")
st.write("Bem-vindo à área principal do sistema.")

# ✅ Botão para navegar para a página de fluxo de caixa
if st.button("Ir para Fluxo de Caixa"):
    st.switch_page("pages/fluxo_caixa.py")
