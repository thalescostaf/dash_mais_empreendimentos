import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
from datetime import datetime
import pandas as pd

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
    df = pd.DataFrame(transacoes)
    df['data'] = pd.to_datetime(df['data']).dt.tz_localize(None).dt.date

    st.subheader("🔍 Filtrar Transações")
    colf1, colf2 = st.columns(2)
    with colf1:
        data_inicio = st.date_input("Data inicial", value=None)
    with colf2:
        data_fim = st.date_input("Data final", value=None)

    descricao_filtro = st.text_input("Filtrar por descrição")
    tipo_filtro = st.selectbox("Filtrar por tipo", options=["todos", "entrada", "saida"])

    df_filtrado = df.copy()

    if data_inicio:
        df_filtrado = df_filtrado[df_filtrado['data'] >= data_inicio]
    if data_fim:
        df_filtrado = df_filtrado[df_filtrado['data'] <= data_fim]
    if descricao_filtro:
        df_filtrado = df_filtrado[df_filtrado['descricao'].str.contains(descricao_filtro, case=False, na=False)]
    if tipo_filtro != "todos":
        df_filtrado = df_filtrado[df_filtrado['tipo'] == tipo_filtro]

    for _, t in df_filtrado.iterrows():
        with st.expander(f"{t['descricao']} - R$ {t['valor']} ({t['tipo']}) - {t['data'].strftime('%d/%m/%Y')}"):
            col1, col2, col3 = st.columns([4, 2, 2])
            col1.markdown(f"**{t['descricao']}**")
            col2.markdown(f"💵 R$ {t['valor']:.2f}")
            col3.markdown(f"📅 {t['data'].strftime('%d/%m/%Y')}")

            if "usuario_id" in t:
                usuario_adicionador = supabase.table("usuarios_dash").select("nome").eq("id", t["usuario_id"]).execute().data
                if usuario_adicionador:
                    col3.markdown(f"👤 Adicionado por {usuario_adicionador[0]['nome']}")
                else:
                    col3.markdown("👤 Adicionado por [Desconhecido]")

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
                        if update.data:
                            st.success("Atualizado com sucesso.")
                        else:
                            st.error("Erro ao atualizar transação.")
                with col2:
                    if st.button("🗑️ Excluir", key=f"excluir_{t['id']}"):
                        delete = supabase.table("fluxo_caixa_dash").delete().eq("id", t["id"]).execute()
                        if delete.data:
                            st.success("Excluído com sucesso.")
                        else:
                            st.error("Erro ao excluir transação.")
