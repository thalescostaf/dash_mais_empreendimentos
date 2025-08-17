import streamlit as st
import pandas as pd
from utils.supabase_client import get_table_data, delete_data

st.title("👤 Usuários")
st.subheader("Listagem com filtros e exclusão (sem edição)")

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

usuarios = pd.DataFrame(get_table_data("mais_emp_usuarios"))

# --- Filtros
st.markdown("### 🔎 Filtros")
col1, col2 = st.columns(2)
filtro_nome = col1.text_input("Filtrar por nome")
filtro_email = col2.text_input("Filtrar por e-mail")

df = usuarios.copy()
if filtro_nome:
    df = df[df["nome"].str.contains(filtro_nome, case=False, na=False)]
if filtro_email:
    df = df[df["email"].str.contains(filtro_email, case=False, na=False)]

st.dataframe(df)

# --- Excluir Usuário
st.markdown("### 🗑️ Excluir Usuário")
if not usuarios.empty:
    selected = st.selectbox("Selecione um usuário para excluir", usuarios.to_dict("records"), format_func=lambda x: x.get("nome", "") or str(x.get("id_usuario", "")))
    if st.button("Excluir Usuário"):
        delete_data("mais_emp_usuarios", "id_usuario", selected["id_usuario"])
        st.success("✅ Usuário excluído com sucesso!")
        rerun()
else:
    st.info("Nenhum usuário para excluir.")
