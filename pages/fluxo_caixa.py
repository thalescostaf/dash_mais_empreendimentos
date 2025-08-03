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

st.title("💰 Fluxo de Caixa")

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
            # Verificar se a resposta foi bem-sucedida
            if response.data:
                st.success("✅ Transação salva com sucesso!")
            else:
                st.error("❌ Erro ao salvar transação.")
        else:
            st.warning("Preencha todos os campos.")

# Exibir todas as transações
st.subheader("📋 Suas Transações")
res = supabase.table("fluxo_caixa_dash") \
    .select("*") \
    .order("data", desc=True) \
    .execute()

transacoes = res.data

if not transacoes:
    st.info("Nenhuma transação registrada.")
else:
    for t in transacoes:
        with st.expander(f"{t['descricao']} - R$ {t['valor']} ({t['tipo']}) - {t['data'][:10]}"):
            col1, col2, col3 = st.columns([4, 2, 2])
            
            # Exibe as transações, mostrando quem adicionou
            col1.markdown(f"**{t['descricao']}**")
            col2.markdown(f"💵 R$ {t['valor']:.2f}")
            col3.markdown(f"📅 {t['data'][:10]}")
            
            # Exibir nome do usuário que adicionou a transação
            if "usuario_id" in t:
                usuario_adicionador = supabase.table("usuarios_dash").select("nome").eq("id", t["usuario_id"]).execute().data
                if usuario_adicionador:
                    col3.markdown(f"👤 Adicionado por {usuario_adicionador[0]['nome']}")
                else:
                    col3.markdown("👤 Adicionado por [Desconhecido]")

            # Edição e exclusão
            with st.expander("🛠️ Editar ou Excluir"):
                nova_descricao = st.text_input("Descrição", value=t["descricao"], key=f"desc_{t['id']}")
                novo_valor = st.number_input("Valor", value=float(t["valor"]), min_value=0.01, step=0.01, key=f"valor_{t['id']}")
                novo_tipo = st.radio("Tipo", ["entrada", "saida"], index=0 if t["tipo"] == "entrada" else 1, key=f"tipo_{t['id']}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Atualizar", key=f"atualizar_{t['id']}"):
                        update = supabase.table("fluxo_caixa_dash").update({
                            "descricao": nova_descricao,
                            "valor": novo_valor,
                            "tipo": novo_tipo
                        }).eq("id", t["id"]).execute()
                        # Verificar se a resposta da atualização foi bem-sucedida
                        if update.data:
                            st.success("Atualizado com sucesso.")
                        else:
                            st.error("Erro ao atualizar transação.")
                with col2:
                    if st.button("🗑️ Excluir", key=f"excluir_{t['id']}"):
                        delete = supabase.table("fluxo_caixa_dash").delete().eq("id", t["id"]).execute()
                        # Verificar se a resposta da exclusão foi bem-sucedida
                        if delete.data:
                            st.success("Excluído com sucesso.")
                        else:
                            st.error("Erro ao excluir transação.")
