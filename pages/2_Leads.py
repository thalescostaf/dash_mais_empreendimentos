import streamlit as st
import pandas as pd
from utils.supabase_client import get_table_data, insert_data, delete_data

st.title("📋 Gestão de Leads")
st.subheader("Cadastro, filtros e exclusão de leads (IDs ocultos)")

def rerun():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

# Botão de atualizar
colA, colB = st.columns([1, 3])
with colA:
    if st.button("🔄 Atualizar lista"):
        rerun()

# Dados base
usuarios = pd.DataFrame(get_table_data("mais_emp_usuarios"))
empreendimentos = pd.DataFrame(get_table_data("mais_emp_empreendimentos"))
leads = pd.DataFrame(get_table_data("mais_emp_lead"))

# Merge para exibir nomes amigáveis (ocultando IDs)
merged = leads.copy()
if not leads.empty:
    merged = merged.merge(
        usuarios[["id_usuario", "nome"]].rename(columns={"nome": "Nome do Lead"}),
        left_on="id_usuario", right_on="id_usuario", how="left"
    ).merge(
        empreendimentos[["id_empreendimento", "nome"]].rename(columns={"nome": "Empreendimento"}),
        left_on="id_empreendimento", right_on="id_empreendimento", how="left"
    )

# --- Filtros: Nome, Empreendimento, Potencial
st.markdown("### 🔎 Filtros")
col1, col2, col3 = st.columns(3)
f_nome = col1.text_input("Filtrar por Nome do Lead")
emp_options = [""] + sorted(list(empreendimentos["nome"].dropna().unique())) if not empreendimentos.empty else [""]
f_emp = col2.selectbox("Filtrar por Empreendimento", emp_options)
pot_options = ["", "Alto", "Médio", "Baixo"]
f_pot = col3.selectbox("Filtrar por Potencial", pot_options)

df_view = merged.copy()
if f_nome:
    df_view = df_view[df_view["Nome do Lead"].str.contains(f_nome, case=False, na=False)]
if f_emp:
    df_view = df_view[df_view["Empreendimento"] == f_emp]
if f_pot:
    df_view = df_view[df_view["potencial"] == f_pot]

# Exibir tabela com colunas amigáveis (sem IDs)
cols_show = ["Nome do Lead", "Empreendimento", "objetivo", "forma_pagamento",
             "renda_familiar", "potencial", "interesse_empreendimento", "created_at"]
df_show = df_view[cols_show] if not df_view.empty else pd.DataFrame(columns=cols_show)
df_show = df_show.rename(columns={
    "objetivo": "Objetivo",
    "forma_pagamento": "Forma de Pagamento",
    "renda_familiar": "Renda Familiar",
    "potencial": "Potencial",
    "interesse_empreendimento": "Interesse",
    "created_at": "Criado em"
})
st.dataframe(df_show)

# --- Adicionar Lead
st.markdown("### ➕ Registrar Novo Lead")
with st.form("add_lead"):
    usuario_sel = st.selectbox("Usuário (Nome do Lead)", usuarios.to_dict("records"), format_func=lambda x: x.get("nome", ""))
    empreendimento_sel = st.selectbox("Empreendimento", empreendimentos.to_dict("records"), format_func=lambda x: x.get("nome", ""))
    objetivo = st.selectbox("Objetivo", ["Moradia", "Investimento"])
    forma_pagamento = st.selectbox("Forma de Pagamento", ["À vista", "Financiamento"])
    renda_familiar = st.number_input("Renda Familiar", min_value=0.0, step=0.01)
    potencial = st.selectbox("Potencial", ["Alto", "Médio", "Baixo"])
    interesse = st.text_area("Interesse")
    submitted = st.form_submit_button("Adicionar")
    if submitted:
        insert_data("mais_emp_lead", {
            "id_usuario": usuario_sel["id_usuario"],
            "id_empreendimento": empreendimento_sel["id_empreendimento"],
            "objetivo": objetivo,
            "forma_pagamento": forma_pagamento,
            "renda_familiar": renda_familiar,
            "potencial": potencial,
            "interesse_empreendimento": interesse
        })
        st.success("✅ Lead registrado com sucesso!")
        rerun()

# --- Excluir Lead (mostrar 'Nome do Lead - Objetivo' no seletor)
st.markdown("### 🗑️ Excluir Lead")
if not merged.empty:
    options = merged.to_dict("records")
    selected = st.selectbox(
        "Selecione um Lead para excluir",
        options,
        format_func=lambda x: f"{x.get('Nome do Lead','(sem nome)')} - {x.get('objetivo','')}"
    )
    if st.button("Excluir Lead"):
        delete_data("mais_emp_lead", "id_lead", selected["id_lead"])
        st.success("✅ Lead excluído com sucesso!")
        rerun()
else:
    st.info("Nenhum lead cadastrado para excluir.")
