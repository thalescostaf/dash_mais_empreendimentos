import streamlit as st
import pandas as pd
from utils.supabase_client import get_table_data, insert_data, update_data, delete_data

st.title("📅 Gestão de Agendamentos")
st.subheader("Registro, consulta, edição e exclusão de reuniões e visitas")

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
agendamentos_raw = pd.DataFrame(get_table_data("mais_emp_agendamento"))

# Construir visão com nomes (usuario e cliente)
ag_view = agendamentos_raw.copy()
if not ag_view.empty:
    ag_view = ag_view.merge(
        usuarios[["id_usuario", "nome"]].rename(columns={"nome": "Usuário"}),
        left_on="id_usuario", right_on="id_usuario", how="left"
    ).merge(
        usuarios[["id_usuario", "nome"]].rename(columns={"id_usuario": "cliente_id", "nome": "Cliente"}),
        on="cliente_id", how="left"
    )

# --- Filtros
st.markdown("### 🔎 Filtros")
col1, col2, col3 = st.columns(3)
f_status = col1.text_input("Filtrar por Status")
f_data = col2.date_input("Filtrar por Data", value=None)
f_usuario = col3.text_input("Filtrar por Usuário/Cliente")

df_view = ag_view.copy()
if f_status:
    df_view = df_view[df_view["status"].str.contains(f_status, case=False, na=False)]
if f_data:
    df_view = df_view[df_view["data"] == str(f_data)]
if f_usuario:
    mask = (
        df_view["Usuário"].str.contains(f_usuario, case=False, na=False) |
        df_view["Cliente"].str.contains(f_usuario, case=False, na=False)
    )
    df_view = df_view[mask]

cols_show = ["Usuário", "Cliente", "tipo_evento", "data", "horario", "status", "negociacao", "created_at"]
df_show = df_view[cols_show] if not df_view.empty else pd.DataFrame(columns=cols_show)
df_show = df_show.rename(columns={
    "tipo_evento": "Tipo de Evento",
    "data": "Data",
    "horario": "Horário",
    "status": "Status",
    "negociacao": "Negociação",
    "created_at": "Criado em"
})
st.dataframe(df_show)

# --- Adicionar Agendamento
st.markdown("### ➕ Registrar Agendamento")
with st.form("add_agendamento"):
    usuario_sel = st.selectbox("Usuário", usuarios.to_dict("records"), format_func=lambda x: x.get("nome", ""))
    cliente_sel = st.selectbox("Cliente", usuarios.to_dict("records"), format_func=lambda x: x.get("nome", ""))
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
        st.success("✅ Agendamento registrado com sucesso!")
        rerun()

# --- Editar Agendamento
st.markdown("### ✏️ Editar Agendamento")
if not agendamentos_raw.empty:
    selected = st.selectbox(
        "Selecione um agendamento para editar",
        agendamentos_raw.to_dict("records"),
        format_func=lambda x: f"{x.get('tipo_evento','')} - {x.get('data','')}"
    )
    with st.form("edit_agendamento"):
        # índices seguros
        try:
            idx_user = usuarios.index[usuarios["id_usuario"] == selected["id_usuario"]][0]
        except Exception:
            idx_user = 0
        try:
            idx_cliente = usuarios.index[usuarios["id_usuario"] == selected["cliente_id"]][0]
        except Exception:
            idx_cliente = 0

        usuario_sel = st.selectbox("Usuário", usuarios.to_dict("records"), index=idx_user, format_func=lambda x: x.get("nome", ""))
        cliente_sel = st.selectbox("Cliente", usuarios.to_dict("records"), index=idx_cliente, format_func=lambda x: x.get("nome", ""))
        tipo_evento = st.text_input("Tipo de Evento", selected.get("tipo_evento", ""))
        # data/horário defensivos
        d_default = pd.to_datetime(selected.get("data", None)).date() if selected.get("data") else None
        h_default = pd.to_datetime(selected.get("horario", None)).time() if selected.get("horario") else None
        data_evento = st.date_input("Data", d_default)
        horario = st.time_input("Horário", h_default)
        status = st.text_input("Status", selected.get("status", ""))
        negociacao = st.text_area("Negociação", selected.get("negociacao", ""))
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
            st.success("✅ Agendamento atualizado com sucesso!")
            rerun()
else:
    st.info("Nenhum agendamento para editar.")

# --- Excluir Agendamento
st.markdown("### 🗑️ Excluir Agendamento")
if not agendamentos_raw.empty:
    selected = st.selectbox(
        "Selecione um agendamento para excluir",
        ag_view.to_dict("records") if not ag_view.empty else agendamentos_raw.to_dict("records"),
        format_func=lambda x: f"{x.get('Cliente', 'Cliente')} - {x.get('tipo_evento','')} - {x.get('data','')}"
    )
    if st.button("Excluir Agendamento"):
        delete_data("mais_emp_agendamento", "id_agendamento", selected["id_agendamento"])
        st.success("✅ Agendamento excluído com sucesso!")
        rerun()
else:
    st.info("Nenhum agendamento para excluir.")
