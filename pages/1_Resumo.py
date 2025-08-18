import streamlit as st
import pandas as pd
import plotly.express as px
from utils.supabase_client import get_table_data

st.title("📈 Resumo do Sistema")
st.subheader("📊 Visão geral com métricas e gráficos")

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

# Leads por Empreendimento (usa nome amigável)
st.subheader("📋 Leads por Empreendimento")
if not leads.empty:
    df = leads.copy()
    if "id_empreendimento" not in df.columns:
        df["id_empreendimento"] = None

    if not empreendimentos.empty:
        df = df.merge(
            empreendimentos[["id_empreendimento", "nome"]].rename(columns={"nome": "Empreendimento"}),
            on="id_empreendimento",
            how="left"
        )
    else:
        df["Empreendimento"] = None

    df["Empreendimento"] = df["Empreendimento"].fillna("Sem vínculo")

    agg = df.groupby("Empreendimento", dropna=False).size().reset_index(name="Leads")
    if not agg.empty and "Empreendimento" in agg.columns:
        fig = px.bar(agg, x="Empreendimento", y="Leads", title="Leads por Empreendimento")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem dados de leads para exibir.")
else:
    st.info("Sem dados de leads para exibir.")
