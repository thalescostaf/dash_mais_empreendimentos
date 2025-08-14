# app.py
import os
import streamlit as st
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
import plotly.express as px

# Carrega variáveis do .env
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Conecta ao Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Painel Mais Emp", layout="wide")
st.title("📊 Painel Mais Emp")

# Função para buscar dados
@st.cache_data
def get_table_data(table_name):
    data = supabase.table(table_name).select("*").execute()
    return pd.DataFrame(data.data)

# Funções para inserir e atualizar
def insert_data(table_name, data_dict):
    return supabase.table(table_name).insert(data_dict).execute()

def update_data(table_name, row_id_name, row_id_value, data_dict):
    return supabase.table(table_name).update(data_dict).eq(row_id_name, row_id_value).execute()

# Sidebar
aba = st.sidebar.radio("📌 Escolha a tabela:", 
    ["Usuários", "Empreendimentos", "Leads", "Agendamentos"])

# Carregar dados auxiliares para dropdowns
usuarios_df = get_table_data("mais_emp_usuarios")
empreendimentos_df = get_table_data("mais_emp_empreendimentos")

# --------------------------
# Usuários (somente leitura)
# --------------------------
if aba == "Usuários":
    st.header("👤 Usuários")
    df = usuarios_df
    st.dataframe(df)

# --------------------------
# Empreendimentos
# --------------------------
elif aba == "Empreendimentos":
    st.header("🏢 Empreendimentos")
    df = empreendimentos_df
    st.dataframe(df)

    st.subheader("➕ Adicionar Empreendimento")
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
            st.success("Empreendimento adicionado com sucesso!")

    st.subheader("✏️ Editar Empreendimento")
    if not df.empty:
        selected = st.selectbox("Selecione para editar", df.to_dict("records"), format_func=lambda x: x["nome"])
        with st.form("edit_empreendimento"):
            nome = st.text_input("Nome", selected["nome"])
            localizacao = st.text_input("Localização", selected["localizacao"])
            tipo = st.text_input("Tipo", selected["tipo"])
            link_pdf = st.text_input("Link PDF", selected["link_pdf"])
            link_tour_360 = st.text_input("Link Tour 360", selected["link_tour_360"])
            submitted = st.form_submit_button("Salvar Alterações")
            if submitted:
                update_data("mais_emp_empreendimentos", "id_empreendimento", selected["id_empreendimento"], {
                    "nome": nome,
                    "localizacao": localizacao,
                    "tipo": tipo,
                    "link_pdf": link_pdf,
                    "link_tour_360": link_tour_360
                })
                st.success("Empreendimento atualizado!")

# --------------------------
# Leads
# --------------------------
elif aba == "Leads":
    st.header("📋 Leads")
    df = get_table_data("mais_emp_lead")
    st.dataframe(df)

    st.subheader("➕ Registrar Lead")
    with st.form("add_lead"):
        usuario_sel = st.selectbox("Usuário", usuarios_df.to_dict("records"), format_func=lambda x: x["nome"])
        empreendimento_sel = st.selectbox("Empreendimento", empreendimentos_df.to_dict("records"), format_func=lambda x: x["nome"])
        objetivo = st.text_input("Objetivo")
        forma_pagamento = st.text_input("Forma de Pagamento")
        renda_familiar = st.number_input("Renda Familiar", min_value=0.0, step=0.01)
        potencial = st.text_input("Potencial")
        interesse_empreendimento = st.text_area("Interesse")
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            insert_data("mais_emp_lead", {
                "id_usuario": usuario_sel["id_usuario"],
                "id_empreendimento": empreendimento_sel["id_empreendimento"],
                "objetivo": objetivo,
                "forma_pagamento": forma_pagamento,
                "renda_familiar": renda_familiar,
                "potencial": potencial,
                "interesse_empreendimento": interesse_empreendimento
            })
            st.success("Lead registrado com sucesso!")

    st.subheader("✏️ Editar Lead")
    if not df.empty:
        selected = st.selectbox("Selecione para editar", df.to_dict("records"), format_func=lambda x: str(x["id_lead"]))
        with st.form("edit_lead"):
            usuario_sel = st.selectbox("Usuário", usuarios_df.to_dict("records"), index=usuarios_df.index[usuarios_df["id_usuario"] == selected["id_usuario"]][0], format_func=lambda x: x["nome"])
            empreendimento_sel = st.selectbox("Empreendimento", empreendimentos_df.to_dict("records"), index=empreendimentos_df.index[empreendimentos_df["id_empreendimento"] == selected["id_empreendimento"]][0], format_func=lambda x: x["nome"])
            objetivo = st.text_input("Objetivo", selected["objetivo"])
            forma_pagamento = st.text_input("Forma de Pagamento", selected["forma_pagamento"])
            renda_familiar = st.number_input("Renda Familiar", value=float(selected["renda_familiar"]), step=0.01)
            potencial = st.text_input("Potencial", selected["potencial"])
            interesse_empreendimento = st.text_area("Interesse", selected["interesse_empreendimento"])
            submitted = st.form_submit_button("Salvar Alterações")
            if submitted:
                update_data("mais_emp_lead", "id_lead", selected["id_lead"], {
                    "id_usuario": usuario_sel["id_usuario"],
                    "id_empreendimento": empreendimento_sel["id_empreendimento"],
                    "objetivo": objetivo,
                    "forma_pagamento": forma_pagamento,
                    "renda_familiar": renda_familiar,
                    "potencial": potencial,
                    "interesse_empreendimento": interesse_empreendimento
                })
                st.success("Lead atualizado!")

# --------------------------
# Agendamentos
# --------------------------
elif aba == "Agendamentos":
    st.header("📅 Agendamentos")
    df = get_table_data("mais_emp_agendamento")
    st.dataframe(df)

    st.subheader("➕ Registrar Agendamento")
    with st.form("add_agendamento"):
        usuario_sel = st.selectbox("Usuário", usuarios_df.to_dict("records"), format_func=lambda x: x["nome"])
        cliente_sel = st.selectbox("Cliente", usuarios_df.to_dict("records"), format_func=lambda x: x["nome"])
        tipo_evento = st.text_input("Tipo de Evento")
        data_evento = st.date_input("Data")
        horario = st.time_input("Horário")
        status = st.text_input("Status")
        negociacao = st.text_area("Negociação")
        submitted = st.form_submit_button("Adicionar")
        if submitted:
            insert_data("mais_emp_agendamento", {
                "id_usuario": usuario_sel["id_usuario"],
                "cliente_id": cliente_sel["id_usuario"],
                "tipo_evento": tipo_evento,
                "data": str(data_evento),
                "horario": str(horario),
                "status": status,
                "negociacao": negociacao
            })
            st.success("Agendamento registrado com sucesso!")

    st.subheader("✏️ Editar Agendamento")
    if not df.empty:
        selected = st.selectbox("Selecione para editar", df.to_dict("records"), format_func=lambda x: str(x["id_agendamento"]))
        with st.form("edit_agendamento"):
            usuario_sel = st.selectbox("Usuário", usuarios_df.to_dict("records"), index=usuarios_df.index[usuarios_df["id_usuario"] == selected["id_usuario"]][0], format_func=lambda x: x["nome"])
            cliente_sel = st.selectbox("Cliente", usuarios_df.to_dict("records"), index=usuarios_df.index[usuarios_df["id_usuario"] == selected["cliente_id"]][0], format_func=lambda x: x["nome"])
            tipo_evento = st.text_input("Tipo de Evento", selected["tipo_evento"])
            data_evento = st.date_input("Data", pd.to_datetime(selected["data"]).date())
            horario = st.time_input("Horário", pd.to_datetime(selected["horario"]).time())
            status = st.text_input("Status", selected["status"])
            negociacao = st.text_area("Negociação", selected["negociacao"])
            submitted = st.form_submit_button("Salvar Alterações")
            if submitted:
                update_data("mais_emp_agendamento", "id_agendamento", selected["id_agendamento"], {
                    "id_usuario": usuario_sel["id_usuario"],
                    "cliente_id": cliente_sel["id_usuario"],
                    "tipo_evento": tipo_evento,
                    "data": str(data_evento),
                    "horario": str(horario),
                    "status": status,
                    "negociacao": negociacao
                })
                st.success("Agendamento atualizado!")
