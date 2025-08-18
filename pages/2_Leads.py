import streamlit as st
import pandas as pd
from utils.supabase_client import get_table_data, insert_data, delete_data

st.title("📋 Leads")
st.subheader(
    "Gerenciamento de leads"
)

def rerun():
    try:
        st.rerun()
    except Exception:
        st.experimental_rerun()

colA, _ = st.columns([1, 3])
with colA:
    if st.button("🔄 Atualizar"):
        rerun()

# Dados
empreendimentos = pd.DataFrame(get_table_data("mais_emp_empreendimentos"))
leads = pd.DataFrame(get_table_data("mais_emp_lead"))

# Garantir colunas
for df, needed in [(leads, ["id_lead", "nome", "id_empreendimento", "objetivo", "forma_pagamento",
                            "renda_familiar", "potencial", "interesse_empreendimento", "created_at"]),
                   (empreendimentos, ["id_empreendimento", "nome"])]:
    for c in needed:
        if c not in df.columns:
            df[c] = None

# Montar visão amigável (sem IDs)
merged = leads.copy()
if not empreendimentos.empty:
    merged = merged.merge(
        empreendimentos[["id_empreendimento", "nome"]].rename(columns={"nome": "Empreendimento"}),
        on="id_empreendimento",
        how="left"
    )
else:
    merged["Empreendimento"] = None

merged["Nome"] = merged["nome"]

# Filtros
st.markdown("### 🔎 Filtros")
col1, col2, col3 = st.columns(3)
f_nome = col1.text_input("Nome")
emp_options = [""] + (sorted(list(empreendimentos["nome"].dropna().unique())) if not empreendimentos.empty else [])
f_emp = col2.selectbox("Empreendimento", emp_options)
f_pot = col3.selectbox("Potencial", ["", "Alto", "Médio", "Baixo"])

df_view = merged.copy()
if f_nome:
    df_view = df_view[df_view["Nome"].astype(str).str.contains(f_nome, case=False, na=False)]
if f_emp:
    df_view = df_view[df_view["Empreendimento"] == f_emp]
if f_pot:
    df_view = df_view[df_view["potencial"] == f_pot]

# Tabela amigável (sem IDs) + datas
cols_show = [
    "Nome", "Empreendimento", "objetivo", "forma_pagamento",
    "renda_familiar", "potencial", "interesse_empreendimento", "created_at"
]
df_show = df_view[cols_show] if not df_view.empty else pd.DataFrame(columns=cols_show)
df_show = df_show.rename(columns={
    "objetivo": "Objetivo",
    "forma_pagamento": "Forma de Pagamento",
    "renda_familiar": "Renda Familiar",
    "potencial": "Potencial",
    "interesse_empreendimento": "Interesse",
    "created_at": "Criado em"
})
if not df_show.empty:
    try:
        df_show["Criado em"] = pd.to_datetime(df_show["Criado em"], errors="coerce").dt.strftime("%d/%m/%Y")
    except Exception:
        pass
st.dataframe(df_show)

# Ocultar/Mostrar seções
colx, coly = st.columns(2)
hide_add = colx.checkbox("Ocultar: Registrar Novo Lead", value=False)
hide_del = coly.checkbox("Ocultar: Excluir Lead", value=False)

# Registrar
if not hide_add:
    st.markdown("### ➕ Registrar Novo Lead")
    with st.form("add_lead"):
        nome_lead = st.text_input("Nome")
        empreendimento_sel = st.selectbox(
            "Empreendimento (opcional)",
            [{"id_empreendimento": None, "nome": "Nenhum"}] + empreendimentos.to_dict("records"),
            format_func=lambda x: x.get("nome", "") if isinstance(x, dict) else ""
        )
        objetivo = st.radio("Objetivo", ["Moradia", "Investimento"])
        forma_pagamento = st.radio("Forma de Pagamento", ["À vista", "Financiamento"])
        renda_familiar = st.number_input("Renda Familiar (opcional)", min_value=0.0, step=0.01, format="%.2f")
        potencial = st.radio("Potencial", ["Alto", "Médio", "Baixo"])
        interesse = st.text_area("Interesse (opcional)")

        submitted = st.form_submit_button("Adicionar")
        if submitted:
            data_insert = {
                "nome": (nome_lead.strip() if nome_lead and nome_lead.strip() != "" else None),
                "id_usuario": None,
                "id_empreendimento": (
                    empreendimento_sel["id_empreendimento"]
                    if isinstance(empreendimento_sel, dict) and empreendimento_sel.get("id_empreendimento") is not None
                    else None
                ),
                "objetivo": objetivo if objetivo else None,
                "forma_pagamento": forma_pagamento if forma_pagamento else None,
                "renda_familiar": renda_familiar if renda_familiar > 0 else None,
                "potencial": potencial if potencial else None,
                "interesse_empreendimento": interesse if interesse else None,
            }
            insert_data("mais_emp_lead", data_insert)
            st.success("✅ Lead registrado com sucesso!")
            rerun()

# Excluir (filtro + select)
if not hide_del:
    st.markdown("### 🗑️ Excluir Lead")
    if not merged.empty:
        f_del = st.text_input("Filtrar (Nome ou Objetivo) para excluir")
        options = merged.copy()
        if f_del:
            mask = (
                options["Nome"].astype(str).str.contains(f_del, case=False, na=False) |
                options["objetivo"].astype(str).str.contains(f_del, case=False, na=False)
            )
            options = options[mask]
        if options.empty:
            st.info("Nenhum lead encontrado com o filtro informado.")
        else:
            selected = st.selectbox(
                "Selecione o Lead",
                options.to_dict("records"),
                format_func=lambda x: f"{x.get('Nome','(sem nome)')} - {x.get('objetivo','')}"
            )
            confirm = st.checkbox("Confirmo a exclusão permanente deste lead.")
            if st.button("Excluir Lead", disabled=not confirm):
                try:
                    from utils.supabase_client import get_table_data as _get
                    delete_data("mais_emp_lead", "id_lead", selected["id_lead"])
                    after = pd.DataFrame(_get("mais_emp_lead"))
                    if not after.empty and "id_lead" in after.columns and str(selected["id_lead"]) in set(after["id_lead"].astype(str)):
                        st.warning("⚠️ Exclusão solicitada, mas o registro ainda existe. Verifique RLS/constraints.")
                    else:
                        st.success("✅ Lead excluído com sucesso!")
                        rerun()
                except Exception as e:
                    st.error(f"Erro ao excluir lead: {e}")
    else:
        st.info("Nenhum lead cadastrado para excluir.")
