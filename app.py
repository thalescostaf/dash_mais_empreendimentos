import streamlit as st

st.set_page_config(page_title="Painel Mais Empreendimentos", layout="wide")

st.title("📊 Painel Mais Empreendimentos")
st.subheader("Menu principal")
st.markdown("Navegue pelo menu lateral para acessar as páginas:")

st.markdown("""
- 📈 **Resumo** → visão geral do sistema  
- 📋 **Leads** → cadastro e exclusão de leads (sem edição)  
- 📅 **Agendamentos** → controle, edição e exclusão de reuniões  
- 🏢 **Empreendimentos** → cadastro, edição e exclusão de empreendimentos  
- 👤 **Usuários** → listagem e exclusão de usuários
""")
