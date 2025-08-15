import streamlit as st
import time
import uuid
from supabase_client import supabase

st.set_page_config(page_title="MAIS EMPREENDIMENTOS", layout="wide")

# ========================================
# Tela inicial
# ========================================
st.title("MAIS EMPREENDIMENTOS")

with st.spinner('Construindo...'):
    time.sleep(1)
st.success("BEM VINDO!")
st.text("Bem vindo ao painel de gerenciamento de Leads")

# ========================================
# CRUD Empreendimentos
# ========================================
st.header("Gerenciar Empreendimentos")

# Formulário para adicionar empreendimento
with st.form("form_add_empreendimento", clear_on_submit=True):
    nome = st.text_input("Nome do Empreendimento")
    localizacao = st.text_input("Localização")
    tipo = st.text_input("Tipo")
    link_tour = st.text_input("Link Tour 360")
    pdf_file = st.file_uploader("Upload PDF", type=["pdf"])

    submit = st.form_submit_button("Adicionar")

    if submit:
        link_pdf = None
        if pdf_file is not None:
            file_name = f"{uuid.uuid4()}.pdf"
            res = supabase.storage.from_("empreendimentos").upload(file_name, pdf_file.getvalue())
            if "Key already exists" not in str(res):
                link_pdf = supabase.storage.from_("empreendimentos").get_public_url(file_name)

        supabase.table("mais_emp_empreendimentos").insert({
            "nome": nome,
            "localizacao": localizacao,
            "tipo": tipo,
            "link_pdf": link_pdf,
            "link_tour_360": link_tour
        }).execute()
        st.success("Empreendimento adicionado com sucesso!")
        st.experimental_rerun()

# Listagem de empreendimentos
st.subheader("Empreendimentos Cadastrados")
empreendimentos = supabase.table("mais_emp_empreendimentos").select("*").execute().data

for emp in empreendimentos:
    with st.expander(emp["nome"] or "Sem nome"):
        st.write(f"📍 Localização: {emp['localizacao']}")
        st.write(f"🏷 Tipo: {emp['tipo']}")
        if emp["link_pdf"]:
            st.markdown(f"[📄 PDF]({emp['link_pdf']})")
        if emp["link_tour_360"]:
            st.markdown(f"[🌐 Tour 360]({emp['link_tour_360']})")

        col1, col2 = st.columns(2)
        with col1:
            if st.button(f"Excluir", key=f"del_{emp['id_empreendimento']}"):
                supabase.table("mais_emp_empreendimentos").delete().eq("id_empreendimento", emp["id_empreendimento"]).execute()
                st.experimental_rerun()
        with col2:
            novo_nome = st.text_input("Novo nome", value=emp["nome"] or "", key=f"edit_nome_{emp['id_empreendimento']}")
            if st.button("Salvar", key=f"edit_{emp['id_empreendimento']}"):
                supabase.table("mais_emp_empreendimentos").update({
                    "nome": novo_nome
                }).eq("id_empreendimento", emp["id_empreendimento"]).execute()
                st.experimental_rerun()

# ========================================
# Espaço para Leads e Usuários
# ========================================
st.header("Gerenciar Leads (em breve)")
st.info("Área de filtros e listagem de leads será adicionada.")

st.header("Gerenciar Usuários (em breve)")
st.info("Área de filtros e listagem de usuários será adicionada.")
