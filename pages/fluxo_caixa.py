import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializar Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Verificar se o usuário está logado
if "usuario_logado" not in st.session_state or not st.session_state["usuario_logado"]:
    st.warning("⛔ Você precisa estar logado para acessar esta página.")
else:
    st.title("💰 Fluxo de Caixa")

    # Formulário para adicionar entrada/saída
    st.subheader("Adicionar Transação")

    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", min_value=0.01, step=0.01)
    tipo = st.radio("Tipo", ('entrada', 'saida'))
    botao_adicionar = st.button("Adicionar Transação")

    if botao_adicionar:
        if descricao and valor:
            # Salvar no banco de dados
            usuario_id = st.session_state["usuario"]["id"]
            dados = supabase.table("fluxo_caixa_dash").insert({
                "descricao": descricao,
                "valor": valor,
                "tipo": tipo,
                "usuario_id": usuario_id
            }).execute()

            if dados.status_code == 201:
                st.success("Transação adicionada com sucesso!")
            else:
                st.error("Erro ao adicionar transação.")
        else:
            st.error("Preencha todos os campos.")

    # Exibir fluxo de caixa
    st.subheader("Transações Recentes")
    transacoes = supabase.table("fluxo_caixa_dash").select("*").eq("usuario_id", st.session_state["usuario"]["id"]).execute()
    
    if transacoes.data:
        for transacao in transacoes.data:
            st.write(f"{transacao['descricao']} - {transacao['valor']} ({transacao['tipo']}) - {transacao['data']}")
    else:
        st.write("Nenhuma transação encontrada.")
