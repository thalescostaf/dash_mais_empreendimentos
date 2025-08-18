import streamlit as st
import pandas as pd
from utils.supabase_client import get_table_data, insert_data, update_data, delete_data

st.title("📅 Agendamentos")
st.subheader("Agenda de visitas e reuniões")

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
ag_raw = pd.DataFrame(get_table_data("mais_emp_agendamento"))

# Garantir colunas esperadas
for df, needed in [
    (ag_raw, ["id_agendamento", "id_usuario", "cliente_id", "tipo_evento", "data", "horario", "status", "negociacao", "created_at"]),
    (usuarios, ["id_usuario", "nome"])
]:
    for c in needed:
        if c not in df.columns:
            df[c] = None

# Se não houver usuários, evita quebra nos selects
if usuarios.empty:
    st.warning("Não há usuários cadastrados. Cadastre um usuário antes de criar/editar agendamentos.")
else:
    usuarios = usuarios.reset_index(drop=True)

# Visão amigável (sem IDs). Mantemos Usuário e Cliente na view, mas agora são a mesma pessoa
ag_view = ag_raw.copy()
if not ag_view.empty:
    ag_view = ag_view.merge(
        usuarios[["id_usuario", "nome"]].rename(columns={"nome": "Usuário"}),
        left_on="id_usuario", right_on="id_usuario", how="left"
    ).merge(
        usuarios[["id_usuario", "nome"]].rename(columns={"id_usuario": "cliente_id", "nome": "Cliente"}),
        on="cliente_id", how="left"
    )

# ---------------- Filtros ----------------
st.markdown("### 🔎 Filtros")
col1, col2, col3 = st.columns(3)
f_status = col1.text_input("Status")
f_data = col2.date_input("Data", value=None)
f_pessoa = col3.text_input("Nome (Usuário/Cliente)")

df_view = ag_view.copy()
if f_status:
    df_view = df_view[df_view["status"].astype(str).str.contains(f_status, case=False, na=False)]
if f_data:
    df_view = df_view[df_view["data"] == str(f_data)]
if f_pessoa:
    mask = (
        df_view["Usuário"].astype(str).str.contains(f_pessoa, case=False, na=False) |
        df_view["Cliente"].astype(str).str.contains(f_pessoa, case=False, na=False)
    )
    df_view = df_view[mask]

# ---------------- Tabela amigável ----------------
cols_show = ["Usuário", "Cliente", "tipo_evento", "data", "horario", "status", "negociacao", "created_at"]
df_show = df_view[cols_show] if not df_view.empty else pd.DataFrame(columns=cols_show)
df_show = df_show.rename(columns={
    "tipo_evento": "Tipo",
    "data": "Data",
    "horario": "Horário",
    "status": "Status",
    "negociacao": "Negociação",
    "created_at": "Criado em"
})
if not df_show.empty:
    try:
        df_show["Data"] = pd.to_datetime(df_show["Data"], errors="coerce").dt.strftime("%d/%m/%Y")
    except Exception:
        pass
    try:
        df_show["Criado em"] = pd.to_datetime(df_show["Criado em"], errors="coerce").dt.strftime("%d/%m/%Y")
    except Exception:
        pass
st.dataframe(df_show)

# ---------------- Adicionar ----------------
st.markdown("### ➕ Registrar Agendamento")
with st.form("add_agendamento"):
    usuario_sel = st.selectbox(
        "Usuário",
        usuarios.to_dict("records"),
        format_func=lambda x: x.get("nome", "") if isinstance(x, dict) else ""
    )

    tipo_evento = st.radio("Evento", ["Reunião", "Visita"])

    data_evento = st.date_input("Data")
    horario = st.time_input("Horário")
    negociacao = st.text_area("Negociação")

    submitted = st.form_submit_button("Adicionar")
    if submitted:
        try:
            uid = usuario_sel.get("id_usuario") if isinstance(usuario_sel, dict) else None
            insert_data("mais_emp_agendamento", {
                "id_usuario": uid,                 # usuário e cliente são o mesmo
                "cliente_id": uid,
                "tipo_evento": tipo_evento or None,
                "data": str(data_evento) if data_evento else None,
                "horario": str(horario) if horario else None,
                "status": "agendado",              # automático no cadastro
                "negociacao": negociacao or None
            })
            st.success("✅ Agendamento registrado como 'agendado'!")
            rerun()
        except Exception as e:
            st.error(f"Erro ao inserir: {e}")

# ---------------- Editar ----------------
st.markdown("### ✏️ Editar Agendamento")
if not ag_raw.empty:
    selected = st.selectbox(
        "Selecione",
        ag_raw.to_dict("records"),
        format_func=lambda x: f"{x.get('tipo_evento','')} - {x.get('data','')}"
    )

    def safe_index(df, col, val) -> int:
        try:
            # Garante int nativo (evita StreamlitAPIException: int64)
            return int(df.index[df[col] == val][0])
        except Exception:
            return 0

    with st.form("edit_agendamento"):
        # Apenas um usuário (igual para id_usuario e cliente_id)
        idx_user = safe_index(usuarios, "id_usuario", selected.get("id_usuario") or selected.get("cliente_id"))
        usuario_sel_ed = st.selectbox(
            "Usuário",
            usuarios.to_dict("records"),
            index=int(idx_user),  # garantir int nativo
            format_func=lambda x: x.get("nome", "") if isinstance(x, dict) else ""
        )

        # Tipo como radio
        tipo_atual = selected.get("tipo_evento") or "Visita"
        tipo_evento_ed = st.radio("Evento", ["Reunião", "Visita"], index=0 if tipo_atual == "Reunião" else 1)

        # Datas/horários defensivos
        d_default = pd.to_datetime(selected.get("data"), errors="coerce")
        t_default = pd.to_datetime(selected.get("horario"), errors="coerce")
        data_evento_ed = st.date_input("Data", None if pd.isna(d_default) else d_default.date())
        horario_ed = st.time_input("Horário", None if pd.isna(t_default) else t_default.time())

        # Status editável pelo admin: agendado ↔ realizada
        status_atual = selected.get("status") or "agendado"
        status_ed = st.radio("Status", ["agendado", "realizada"], index=0 if status_atual == "agendado" else 1)

        negociacao_ed = st.text_area("Negociação", selected.get("negociacao") or "")
        submitted = st.form_submit_button("Salvar Alterações")
        if submitted:
            try:
                uid = usuario_sel_ed.get("id_usuario") if isinstance(usuario_sel_ed, dict) else None
                update_data("mais_emp_agendamento", "id_agendamento", selected["id_agendamento"], {
                    "id_usuario": uid,
                    "cliente_id": uid,   # mesmo usuário
                    "tipo_evento": tipo_evento_ed or None,
                    "data": str(data_evento_ed) if data_evento_ed else None,
                    "horario": str(horario_ed) if horario_ed else None,
                    "status": status_ed or None,
                    "negociacao": negociacao_ed or None
                })
                st.success("✅ Agendamento atualizado!")
                rerun()
            except Exception as e:
                st.error(f"Erro ao atualizar: {e}")
else:
    st.info("Nenhum agendamento para editar.")

# ---------------- Excluir ----------------
st.markdown("### 🗑️ Excluir Agendamento")
if not ag_view.empty:
    selected = st.selectbox(
        "Selecione",
        ag_view.to_dict("records"),
        format_func=lambda x: f"{x.get('Cliente','Cliente')} - {x.get('tipo_evento','')} - {x.get('data','')}"
    )
    confirm = st.checkbox("Confirmo a exclusão deste agendamento.")
    if st.button("Excluir Agendamento", disabled=not confirm):
        try:
            delete_data("mais_emp_agendamento", "id_agendamento", selected["id_agendamento"])
            after = pd.DataFrame(get_table_data("mais_emp_agendamento"))
            if not after.empty and "id_agendamento" in after.columns and str(selected["id_agendamento"]) in set(after["id_agendamento"].astype(str)):
                st.warning("⚠️ Exclusão solicitada, mas o registro ainda existe. Verifique RLS/constraints.")
            else:
                st.success("✅ Agendamento excluído com sucesso!")
                rerun()
        except Exception as e:
            st.error(f"Erro ao excluir: {e}")
else:
    st.info("Nenhum agendamento para excluir.")
