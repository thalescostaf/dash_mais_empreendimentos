import streamlit as st
import pandas as pd
from utils.supabase_client import get_table_data, insert_data, update_data, delete_data

st.title("🏢 Empreendimentos")
st.subheader("Gerenciar empreendimentos")

def rerun():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

colA, _ = st.columns([1, 3])
with colA:
    if st.button("🔄 Atualizar"):
        rerun()

emps = pd.DataFrame(get_table_data("mais_emp_empreendimentos"))
for c in ["id_empreendimento", "nome", "localizacao", "tipo", "link_pdf", "link_tour_360"]:
    if c not in emps.columns:
        emps[c] = None

# Filtros
st.markdown("### 🔎 Filtros")
filtro_nome = st.text_input("Nome")
df = emps.copy()
if filtro_nome:
    df = df[df["nome"].astype(str).str.contains(filtro_nome, case=False, na=False)]

# Tabela amigável (sem IDs)
df_show = df.rename(columns={
    "nome": "Nome",
    "localizacao": "Localização",
    "tipo": "Tipo",
    "link_pdf": "Link PDF",
    "link_tour_360": "Link Tour 360",
})
st.dataframe(df_show[["Nome", "Localização", "Tipo", "Link PDF", "Link Tour 360"]] if not df_show.empty else df_show)

# ➕ Adicionar
st.markdown("### ➕ Adicionar Empreendimento")
with st.form("add_empreendimento"):
    nome = st.text_input("Nome")
    localizacao = st.text_input("Localização")
    tipo = st.text_input("Tipo")
    link_pdf = st.text_input("Link PDF")
    link_tour_360 = st.text_input("Link Tour 360")
    submitted = st.form_submit_button("Adicionar")
    if submitted:
        try:
            insert_data("mais_emp_empreendimentos", {
                "nome": nome or None,
                "localizacao": localizacao or None,
                "tipo": tipo or None,
                "link_pdf": link_pdf or None,
                "link_tour_360": link_tour_360 or None
            })
            st.success("✅ Empreendimento adicionado com sucesso!")
            rerun()
        except Exception as e:
            st.error(f"Erro ao inserir: {e}")

# ✏️ Editar
st.markdown("### ✏️ Editar Empreendimento")
if not emps.empty:
    selected = st.selectbox("Selecione", emps.to_dict("records"), format_func=lambda x: x.get("nome", ""))
    with st.form("edit_empreendimento"):
        nome = st.text_input("Nome", selected.get("nome") or "")
        localizacao = st.text_input("Localização", selected.get("localizacao") or "")
        tipo = st.text_input("Tipo", selected.get("tipo") or "")
        link_pdf = st.text_input("Link PDF", selected.get("link_pdf") or "")
        link_tour_360 = st.text_input("Link Tour 360", selected.get("link_tour_360") or "")
        submitted = st.form_submit_button("Salvar Alterações")
        if submitted:
            try:
                update_data("mais_emp_empreendimentos", "id_empreendimento", selected["id_empreendimento"], {
                    "nome": nome or None,
                    "localizacao": localizacao or None,
                    "tipo": tipo or None,
                    "link_pdf": link_pdf or None,
                    "link_tour_360": link_tour_360 or None
                })
                st.success("✅ Empreendimento atualizado com sucesso!")
                rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")
else:
    st.info("Nenhum empreendimento para editar.")

# 🗑️ Excluir (com validação pós-delete)
st.markdown("### 🗑️ Excluir Empreendimento")
if not emps.empty:
    selected = st.selectbox("Selecione", emps.to_dict("records"), format_func=lambda x: x.get("nome", ""))
    confirm = st.checkbox("Confirmo a exclusão deste empreendimento.")
    if st.button("Excluir Empreendimento", disabled=not confirm):
        try:
            delete_data("mais_emp_empreendimentos", "id_empreendimento", selected["id_empreendimento"])
            after = pd.DataFrame(get_table_data("mais_emp_empreendimentos"))
            if not after.empty and "id_empreendimento" in after.columns and str(selected["id_empreendimento"]) in set(after["id_empreendimento"].astype(str)):
                st.warning(
                    "⚠️ Exclusão solicitada, mas o registro ainda existe. "
                    "Se houver Leads vinculados, configure FK como ON DELETE SET NULL/CASCADE, ou remova/reatribua os Leads."
                )
            else:
                st.success("✅ Empreendimento excluído com sucesso!")
                rerun()
        except Exception as e:
            st.error(f"Erro ao excluir (provável vínculo em Leads): {e}")
else:
    st.info("Nenhum empreendimento para excluir.")
