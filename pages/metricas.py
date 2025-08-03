import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.express as px

# Carrega variáveis do .env
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Verifica se o usuário está logado
if "usuario_logado" not in st.session_state or not st.session_state["usuario_logado"]:
    st.warning("⛔ Acesso negado. Faça login primeiro.")
    st.stop()

# Verifica se o dicionário do usuário está carregado corretamente
usuario = st.session_state.get("usuario")
if not usuario or "id" not in usuario:
    st.error("⚠️ Erro ao carregar dados do usuário. Verifique se o login foi feito corretamente.")
    st.stop()

usuario_id = usuario["id"]

st.title("📊 Fluxo de Caixa - Métricas")

# Carregar todas as transações (sem filtrar por usuário)
res = supabase.table("fluxo_caixa_dash") \
    .select("*") \
    .execute()

transacoes = res.data

if not transacoes:
    st.info("Nenhuma transação registrada.")
else:
    df = pd.DataFrame(transacoes)
    df['data'] = pd.to_datetime(df['data']).dt.tz_localize(None).dt.date

    # Filtros
    st.subheader("🔍 Filtros")
    colf1, colf2 = st.columns(2)
    with colf1:
        data_inicio = st.date_input("Data inicial", value=None)
    with colf2:
        data_fim = st.date_input("Data final", value=None)

    descricao_filtro = st.text_input("Filtrar por descrição")
    tipo_filtro = st.selectbox("Filtrar por tipo", options=["todos", "entrada", "saida"])

    df_filtrado = df.copy()

    if data_inicio:
        df_filtrado = df_filtrado[df_filtrado['data'] >= data_inicio]
    if data_fim:
        df_filtrado = df_filtrado[df_filtrado['data'] <= data_fim]
    if descricao_filtro:
        df_filtrado = df_filtrado[df_filtrado['descricao'].str.contains(descricao_filtro, case=False, na=False)]
    if tipo_filtro != "todos":
        df_filtrado = df_filtrado[df_filtrado['tipo'] == tipo_filtro]

    # Calcular totais de entradas, saídas e saldo (baseado no filtro)
    total_entradas = df_filtrado[df_filtrado['tipo'] == 'entrada']['valor'].sum()
    total_saidas = df_filtrado[df_filtrado['tipo'] == 'saida']['valor'].sum()
    saldo = total_entradas - total_saidas

    # Exibir métricas
    st.subheader("💵 Resumo")
    st.write(f"**Total de Entradas**: R$ {total_entradas:.2f}")
    st.write(f"**Total de Saídas**: R$ {total_saidas:.2f}")
    st.write(f"**Saldo**: R$ {saldo:.2f}")

    # Exibir transações filtradas
    st.subheader("📋 Transações")
    for _, t in df_filtrado.iterrows():
        with st.expander(f"{t['descricao']} - R$ {t['valor']} ({t['tipo']}) - {t['data'].strftime('%d/%m/%Y')}"):
            col1, col2, col3 = st.columns([4, 2, 2])
            col1.markdown(f"**{t['descricao']}**")
            col2.markdown(f"💵 R$ {t['valor']:.2f}")
            col3.markdown(f"📅 {t['data'].strftime('%d/%m/%Y')}")

            if "usuario_id" in t:
                usuario_adicionador = supabase.table("usuarios_dash").select("nome").eq("id", t["usuario_id"]).execute().data
                if usuario_adicionador:
                    col3.markdown(f"👤 Adicionado por {usuario_adicionador[0]['nome']}")
                else:
                    col3.markdown("👤 Adicionado por [Desconhecido]")

    # Gráficos dinâmicos
    st.subheader("📊 Gráficos")

    # Gráfico de Barras: Entradas e Saídas por Data
    df_grouped = df_filtrado.groupby(['data', 'tipo']).agg({'valor': 'sum'}).reset_index()
    fig = px.bar(df_grouped, x='data', y='valor', color='tipo', 
                 labels={'data': 'Data', 'valor': 'Valor', 'tipo': 'Tipo'},
                 title='Entradas e Saídas por Data')
    st.plotly_chart(fig)

    # Gráfico de Linha: Evolução do Saldo
    df_filtrado['saldo_acumulado'] = df_filtrado.groupby('usuario_id')['valor'].cumsum()
    fig2 = px.line(df_filtrado, x='data', y='saldo_acumulado', 
                   title='Evolução do Saldo de Fluxo de Caixa ao Longo do Tempo',
                   labels={'data': 'Data', 'saldo_acumulado': 'Saldo Acumulado'})
    st.plotly_chart(fig2)

    # Gráfico de Pizza: Distribuição de Entradas e Saídas
    df_pie = df_filtrado.groupby('tipo').agg({'valor': 'sum'}).reset_index()
    fig3 = px.pie(df_pie, names='tipo', values='valor', title='Distribuição de Entradas e Saídas')
    st.plotly_chart(fig3)

    # Gráfico de Área: Entradas vs Saídas por Período
    fig4 = px.area(df_grouped, x='data', y='valor', color='tipo', 
                   title='Entradas vs Saídas por Período', 
                   labels={'data': 'Data', 'valor': 'Valor', 'tipo': 'Tipo'})
    st.plotly_chart(fig4)
