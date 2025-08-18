import streamlit as st
import pandas as pd
from utils.supabase_client import get_table_data

st.title("👤 Usuários")
st.subheader("Lista de usuários Mais Empreendimentos")

def rerun():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

colA, _ = st.columns([1, 3])
with colA:
    if st.button("🔄 Atualizar"):
        rerun()

usuarios = pd.DataFrame(get_table_data("mais_emp_usuarios"))
for c in ["id_usuario", "nome", "telefone", "email", "created_at"]:
    if c not in usuarios.columns:
        usuarios[c] = None

st.markdown("### 🔎 Filtros")
col1, col2 = st.columns(2)
filtro_nome = col1.text_input("Nome")
filtro_email = col2.text_input("E-mail")

df = usuarios.copy()
if filtro_nome:
    df = df[df["nome"].astype(str).str.contains(filtro_nome, case=False, na=False)]
if filtro_email:
    df = df[df["email"].astype(str).str.contains(filtro_email, case=False, na=False)]

# Tabela amigável (sem IDs) + datas
df_show = df.rename(columns={
    "nome": "Nome",
    "telefone": "Telefone",
    "email": "E-mail",
    "created_at": "Criado em"
})
if not df_show.empty:
    try:
        df_show["Criado em"] = pd.to_datetime(df_show["Criado em"], errors="coerce").dt.strftime("%d/%m/%Y")
    except Exception:
        pass

st.dataframe(df_show[["Nome", "Telefone", "E-mail", "Criado em"]] if not df_show.empty else df_show)
