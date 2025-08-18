import streamlit as st
import pandas as pd
from uuid import uuid4
from utils.supabase_client import get_table_data, insert_data, update_data, delete_data, supabase

st.title("🏢 Empreendimentos")
st.subheader("Gerenciamento de empreendimentos.")

BUCKET_PDF = "empreendimentos-pdf"  # ajuste se usar outro nome

def rerun():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

# Botão de atualizar
colA, _ = st.columns([1, 3])
with colA:
    if st.button("🔄 Atualizar lista"):
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
filtro_nome = st.text_input("Nome", key="filtro_nome")
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

# ---------------- Helpers de upload ----------------
def upload_pdf_and_get_url(file, filename_hint: str) -> str | None:
    """Sobe o PDF ao bucket e retorna a URL pública."""
    if file is None:
        return None
    try:
        bytes_data = file.getvalue()  # Streamlit file_uploader
        # cria um caminho único (use o nome como prefixo para facilitar achar depois)
        prefix = filename_hint.strip().lower().replace(" ", "-") if filename_hint else "arquivo"
        object_path = f"{prefix}-{uuid4().hex}.pdf"

        # upload com upsert para evitar erro se existir (pouco provável)
        supabase.storage.from_(BUCKET_PDF).upload(
            path=object_path,
            file=bytes_data,
            file_options={"content-type": "application/pdf", "upsert": "true"}
        )

        public_url = supabase.storage.from_(BUCKET_PDF).get_public_url(object_path)
        return public_url
    except Exception as e:
        st.error(f"Erro no upload do PDF para o Storage: {e}")
        return None

# ============================================================
# ➕ Adicionar Empreendimento
# ============================================================
st.markdown("### ➕ Adicionar Empreendimento")
with st.form("add_empreendimento"):
    nome = st.text_input("Nome", key="add_nome")
    localizacao = st.text_input("Localização", key="add_localizacao")
    tipo = st.text_input("Tipo", key="add_tipo")
    link_tour_pc = st.text_input("Tour 360 (Computador) - URL", key="add_tour_pc")
    link_tour_mob = st.text_input("Tour 360 (Mobile) - URL", key="add_tour_mob")
    pdf_file = st.file_uploader("Anexar PDF (opcional)", type=["pdf"], key="add_pdf")

    submitted = st.form_submit_button("Adicionar", use_container_width=True)
    if submitted:
        try:
            # 1) Se houver PDF, sobe antes e pega a URL
            link_pdf_url = upload_pdf_and_get_url(pdf_file, nome)

            # 2) Insere incluindo link_pdf (se houver)
            insert_data("mais_emp_empreendimentos", {
                "nome": nome or None,
                "localizacao": localizacao or None,
                "tipo": tipo or None,
                "link_pdf": link_pdf_url or None,
                "link_tour_360_computador": link_tour_pc or None,
                "link_tour_360_mobile": link_tour_mob or None,
            })

            st.success("✅ Empreendimento adicionado com sucesso!")
            rerun()
        except Exception as e:
            st.error(f"Erro ao inserir: {e}")

# ============================================================
# ✏️ Editar Empreendimento
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
        nome_ed = st.text_input("Nome", selected.get("nome") or "", key="edit_nome")
        localizacao_ed = st.text_input("Localização", selected.get("localizacao") or "", key="edit_localizacao")
        tipo_ed = st.text_input("Tipo", selected.get("tipo") or "", key="edit_tipo")
        link_tour_pc_ed = st.text_input("Tour 360 (Computador) - URL", selected.get("link_tour_360_computador") or "", key="edit_tour_pc")
        link_tour_mob_ed = st.text_input("Tour 360 (Mobile) - URL", selected.get("link_tour_360_mobile") or "", key="edit_tour_mob")
        st.caption("Se anexar um novo PDF, o link será atualizado.")
        pdf_file_ed = st.file_uploader("Anexar novo PDF (opcional)", type=["pdf"], key="edit_pdf")

        submitted = st.form_submit_button("Salvar Alterações", use_container_width=True)
        if submitted:
            try:
                payload = {
                    "nome": nome_ed or None,
                    "localizacao": localizacao_ed or None,
                    "tipo": tipo_ed or None,
                    "link_tour_360_computador": link_tour_pc_ed or None,
                    "link_tour_360_mobile": link_tour_mob_ed or None,
                }

                # Se um novo PDF foi anexado, sobe e atualiza o link_pdf
                if pdf_file_ed is not None:
                    link_pdf_new = upload_pdf_and_get_url(pdf_file_ed, nome_ed or selected.get("nome") or "arquivo")
                    if link_pdf_new:
                        payload["link_pdf"] = link_pdf_new

                update_data("mais_emp_empreendimentos", "id_empreendimento", selected["id_empreendimento"], payload)

                st.success("✅ Empreendimento atualizado com sucesso!")
                rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")
else:
    st.info("Nenhum empreendimento para editar.")

# ============================================================
# 🗑️ Excluir Empreendimento
# ============================================================
st.markdown("### 🗑️ Excluir Empreendimento")
if not emps.empty:
    selected_del = st.selectbox(
        "Selecione",
        emps.to_dict("records"),
        format_func=lambda x: x.get("nome", ""),
        key="delete_select"  # evita IDs duplicados
    )
    confirm = st.checkbox("Confirmo a exclusão deste empreendimento.", key="delete_confirm")
    if st.button("Excluir Empreendimento", disabled=not confirm, key="delete_btn"):
        try:
            delete_data("mais_emp_empreendimentos", "id_empreendimento", selected_del["id_empreendimento"])
            after = pd.DataFrame(get_table_data("mais_emp_empreendimentos"))
            if not after.empty and "id_empreendimento" in after.columns and str(selected_del["id_empreendimento"]) in set(after["id_empreendimento"].astype(str)):
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
