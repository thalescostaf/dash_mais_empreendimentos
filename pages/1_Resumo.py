import streamlit as st
import pandas as pd
import plotly.express as px
from utils.supabase_client import get_table_data

st.title("📈 Resumo do Sistema")
st.subheader("📊 Visão geral com métricas e gráficos")

# Carregar dados
usuarios = pd.DataFrame(get_table_data("mais_emp_usuarios"))
empreendimentos = pd.DataFrame(get_table_data("mais_emp_empreendimentos"))
leads = pd.DataFrame(get_table_data("mais_emp_lead"))
agendamentos = pd.DataFrame(get_table_data("mais_emp_agendamento"))

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Usuários", len(usuarios))
col2.metric("Empreendimentos", len(empreendimentos))
col3.metric("Leads", len(leads))
col4.metric("Agendamentos", len(agendamentos))

st.markdown("---")

# Leads por Empreendimento (nome amigável)
st.subheader("📋 Leads por Empreendimento")
if not leads.empty and not empreendimentos.empty:
    merged = leads.merge(
        empreendimentos[["id_empreendimento", "nome"]],
        on="id_empreendimento", how="left"
    ).rename(columns={"nome": "Empreendimento"})
    fig = px.histogram(merged, x="Empreendimento", title="Distribuição de Leads por Empreendimento")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Sem dados de leads para exibir.")
