# lançamentos.py

import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime

# Carrega variáveis do .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Verifica se o usuário está logado
if "usuario_logado" not in st.session_state or not st.session_state["usuario_logado"]:
    st.warning("⛔ Acesso negado. Faça login primeiro.")
    st.stop()

# Verifica se o dicionário do usuário está carregado corretamente
usuario = st.session_state.get("usuario")
if not usuario or "id" not in usuario:
    st.error("⚠️ Erro ao carregar dados do usuário. Verifique se o login foi feito corretamente.")
    st.stop()

usuario_id = usuario["id"]

st.title("💰 Fluxo de Caixa - Lançamentos")

# Formulário de nova transação
st.subheader("➕ Adicionar Transação")
with st.form("form_nova_transacao"):
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.01, step=0.01)
    tipo = st.radio("Tipo", ["entrada", "saida"], horizontal=True)
    submit = st.form_submit_button("Salvar")

    if submit:
        if descricao and valor:
            response = supabase.table("fluxo_caixa_dash").insert({
                "descricao": descricao,
                "valor": valor,
                "tipo": tipo,
                "usuario_id": usuario_id,
                "data": datetime.now().isoformat()
            }).execute()
            if response.data:
                st.success("✅ Transação salva com sucesso!")
            else:
                st.error("❌ Erro ao salvar transação.")
        else:
            st.warning("Preencha todos os campos.")
