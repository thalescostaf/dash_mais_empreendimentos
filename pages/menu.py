import streamlit as st

# Verifica se usuário está logado
if "usuario_logado" not in st.session_state or not st.session_state["usuario_logado"]:
    st.warning("⛔ Acesso negado. Por favor, faça login primeiro.")
    st.stop()

st.title("🔑 Menu Principal")
st.write("Bem-vindo à área principal do sistema.")

# ✅ Botões para navegar para as páginas de Lançamentos e Métricas
col1, col2 = st.columns(2)

with col1:
    if st.button("Ir para Lançamentos"):
        # Navega para a página de lançamentos
        st.switch_page("pages/lancamentos.py")

with col2:
    if st.button("Ir para Métricas"):
        # Navega para a página de métricas
        st.switch_page("pages/metricas.py")
