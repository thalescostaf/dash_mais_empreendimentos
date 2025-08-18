import streamlit as st

st.set_page_config(page_title="Painel Mais Empreendimentos", layout="wide")

st.title("📊 Painel Mais Empreendimentos")
st.subheader("Menu principal")
st.markdown("Navegue pelo menu lateral para acessar as páginas:")

st.markdown("""
- 📈 **Resumo** → visão geral do sistema  
- 📋 **Leads** → visão geral dos leads 
- 📅 **Agendamentos** → agenda de reuniões
- 🏢 **Empreendimentos** → gerenciar empreendimentos
- 👤 **Usuários** → lista de usuários
""")
