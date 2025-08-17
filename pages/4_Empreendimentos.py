import streamlit as st
import pandas as pd
from utils.supabase_client import get_table_data, insert_data, update_data, delete_data

st.title("🏢 Gestão de Empreendimentos")
st.subheader("Cadastro, consulta, edição e exclusão de empreendimentos")

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

empreendimentos = pd.DataFrame(get_table_data("mais_emp_empreendimentos"))

# --- Filtros
st.markdown("### 🔎 Filtros")
filtro_nome = st.text_input("Filtrar por nome do Empreendimento")
df = empreendimentos.copy()
if filtro_nome:
    df = df[df["nome"].str.contains(filtro_nome, case=False, na=False)]

st.dataframe(df)

# --- Adicionar Empreendimento
st.markdown("### ➕ Adicionar Empreendimento")
with st.form("add_empreendimento"):
    nome = st.text_input("Nome")
    localizacao = st.text_input("Localização")
    tipo = st.text_input("Tipo")
    link_pdf = st.text_input("Link PDF")
    link_tour_360 = st.text_input("Link Tour 360")
    submitted = st.form_submit_button("Adicionar")
    if submitted:
        insert_data("mais_emp_empreendimentos", {
            "nome": nome,
            "localizacao": localizacao,
            "tipo": tipo,
            "link_pdf": link_pdf,
            "link_tour_360": link_tour_360
        })
        st.success("✅ Empreendimento adicionado com sucesso!")
        rerun()

# --- Editar Empreendimento
st.markdown("### ✏️ Editar Empreendimento")
if not empreendimentos.empty:
    selected = st.selectbox("Selecione um empreendimento para editar", empreendimentos.to_dict("records"), format_func=lambda x: x.get("nome", ""))
    with st.form("edit_empreendimento"):
        nome = st.text_input("Nome", selected.get("nome", ""))
        localizacao = st.text_input("Localização", selected.get("localizacao", ""))
        tipo = st.text_input("Tipo", selected.get("tipo", ""))
        link_pdf = st.text_input("Link PDF", selected.get("link_pdf", ""))
        link_tour_360 = st.text_input("Link Tour 360", selected.get("link_tour_360", ""))
        submitted = st.form_submit_button("Salvar Alterações")
        if submitted:
            update_data("mais_emp_empreendimentos", "id_empreendimento", selected["id_empreendimento"], {
                "nome": nome,
                "localizacao": localizacao,
                "tipo": tipo,
                "link_pdf": link_pdf,
                "link_tour_360": link_tour_360
            })
            st.success("✅ Empreendimento atualizado com sucesso!")
            rerun()
else:
    st.info("Nenhum empreendimento para editar.")

# --- Excluir Empreendimento
st.markdown("### 🗑️ Excluir Empreendimento")
if not empreendimentos.empty:
    selected = st.selectbox("Selecione um empreendimento para excluir", empreendimentos.to_dict("records"), format_func=lambda x: x.get("nome", ""))
    if st.button("Excluir Empreendimento"):
        delete_data("mais_emp_empreendimentos", "id_empreendimento", selected["id_empreendimento"])
        st.success("✅ Empreendimento excluído com sucesso!")
        rerun()
else:
    st.info("Nenhum empreendimento para excluir.")
