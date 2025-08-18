import streamlit as st
import pandas as pd
from utils.supabase_client import get_table_data, insert_data, update_data, delete_data

st.title("🏢 Empreendimentos")
st.subheader("Gerenciar empreendimentos.")

def rerun():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

# Botão de atualizar
colA, _ = st.columns([1, 3])
with colA:
    if st.button("🔄 Atualizar"):
        rerun()

# Carregar dados
emps = pd.DataFrame(get_table_data("mais_emp_empreendimentos"))

# Garantir colunas do schema novo
for c in [
    "id_empreendimento",
    "nome",
    "localizacao",
    "tipo",
    "link_pdf",
    "link_tour_360_computador",
    "link_tour_360_mobile",
]:
    if c not in emps.columns:
        emps[c] = None

# ---------------- Filtros ----------------
st.markdown("### 🔎 Filtros")
filtro_nome = st.text_input("Nome")
df = emps.copy()
if filtro_nome:
    df = df[df["nome"].astype(str).str.contains(filtro_nome, case=False, na=False)]

# ---------------- Tabela amigável (sem IDs) ----------------
df_show = df.rename(columns={
    "nome": "Nome",
    "localizacao": "Localização",
    "tipo": "Tipo",
    "link_pdf": "Link PDF",
    "link_tour_360_computador": "Tour 360 (Computador)",
    "link_tour_360_mobile": "Tour 360 (Mobile)",
})
cols_listagem = ["Nome", "Localização", "Tipo", "Link PDF", "Tour 360 (Computador)", "Tour 360 (Mobile)"]
st.dataframe(df_show[cols_listagem] if not df_show.empty else df_show)

# ============================================================
# ➕ Adicionar Empreendimento
# - Link PDF: agora é upload (opcional). Ainda não salva no Supabase.
# ============================================================
st.markdown("### ➕ Adicionar Empreendimento")
with st.form("add_empreendimento"):
    nome = st.text_input("Nome")
    localizacao = st.text_input("Localização")
    tipo = st.text_input("Tipo")
    link_tour_pc = st.text_input("Tour 360 (Computador) - URL")
    link_tour_mob = st.text_input("Tour 360 (Mobile) - URL")
    pdf_file = st.file_uploader("Anexar PDF (opcional)", type=["pdf"], key="pdf_add")

    submitted = st.form_submit_button("Adicionar")
    if submitted:
        try:
            # Observação: por ora não salvamos o PDF no Supabase;
            # você pode integrar com Google Drive / Supabase Storage depois.
            insert_data("mais_emp_empreendimentos", {
                "nome": nome or None,
                "localizacao": localizacao or None,
                "tipo": tipo or None,
                "link_tour_360_computador": link_tour_pc or None,
                "link_tour_360_mobile": link_tour_mob or None,
                # Não vamos gravar link_pdf por enquanto
                # "link_pdf": None,
            })
            if pdf_file is not None:
                st.info("📎 PDF anexado localmente nesta sessão, mas ainda não está sendo enviado a nenhum storage.")
            st.success("✅ Empreendimento adicionado com sucesso!")
            rerun()
        except Exception as e:
            st.error(f"Erro ao inserir: {e}")

# ============================================================
# ✏️ Editar Empreendimento
# - Atualiza campos do schema novo.
# - Upload de PDF (opcional) — ainda não salva em storage.
# - Corrigido erro de IDs duplicados com key="edit_select".
# ============================================================
st.markdown("### ✏️ Editar Empreendimento")
if not emps.empty:
    selected = st.selectbox(
        "Selecione",
        emps.to_dict("records"),
        format_func=lambda x: x.get("nome", ""),
        key="edit_select"  # evita StreamlitDuplicateElementId
    )
    with st.form("edit_empreendimento"):
        nome_ed = st.text_input("Nome", selected.get("nome") or "")
        localizacao_ed = st.text_input("Localização", selected.get("localizacao") or "")
        tipo_ed = st.text_input("Tipo", selected.get("tipo") or "")
        link_tour_pc_ed = st.text_input("Tour 360 (Computador) - URL", selected.get("link_tour_360_computador") or "")
        link_tour_mob_ed = st.text_input("Tour 360 (Mobile) - URL", selected.get("link_tour_360_mobile") or "")
        pdf_file_ed = st.file_uploader("Anexar novo PDF (opcional)", type=["pdf"], key="pdf_edit")
        submitted = st.form_submit_button("Salvar Alterações")
        if submitted:
            try:
                update_data("mais_emp_empreendimentos", "id_empreendimento", selected["id_empreendimento"], {
                    "nome": nome_ed or None,
                    "localizacao": localizacao_ed or None,
                    "tipo": tipo_ed or None,
                    "link_tour_360_computador": link_tour_pc_ed or None,
                    "link_tour_360_mobile": link_tour_mob_ed or None,
                    # não mexemos em link_pdf aqui (continua sem gravar)
                })
                if pdf_file_ed is not None:
                    st.info("📎 PDF anexado localmente nesta sessão, mas ainda não está sendo enviado a nenhum storage.")
                st.success("✅ Empreendimento atualizado com sucesso!")
                rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")
else:
    st.info("Nenhum empreendimento para editar.")

# ============================================================
# 🗑️ Excluir Empreendimento
# - Corrigido erro de IDs duplicados com key="delete_select".
# ============================================================
st.markdown("### 🗑️ Excluir Empreendimento")
if not emps.empty:
    selected = st.selectbox(
        "Selecione",
        emps.to_dict("records"),
        format_func=lambda x: x.get("nome", ""),
        key="delete_select"  # evita StreamlitDuplicateElementId
    )
    confirm = st.checkbox("Confirmo a exclusão deste empreendimento.")
    if st.button("Excluir Empreendimento", disabled=not confirm, key="delete_btn"):
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
            st.error(f"Erro ao excluir (possível vínculo em Leads): {e}")
else:
    st.info("Nenhum empreendimento para excluir.")
