import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def draw_table(ax, x, y, title, fields, color='#f0f0f0'):
    ax.add_patch(plt.Rectangle((x, y - len(fields) - 1), 4, len(fields) + 1,
                               fill=True, color=color, edgecolor='black'))
    ax.text(x + 2, y, title, ha='center', va='bottom', fontsize=12, fontweight='bold')
    for i, field in enumerate(fields):
        style = 'italic' if 'PK' in field or 'FK' in field else 'normal'
        ax.text(x + 0.2, y - i - 1, field, ha='left', va='center', fontsize=10, style=style)

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_xlim(0, 20)
ax.set_ylim(0, 18)
ax.axis('off')

draw_table(ax, 2, 16, "mais_emp_usuarios", [
    "id_usuario (PK)", "nome", "telefone", "email", "created_at"
], color='#d1e7dd')

draw_table(ax, 8, 16, "mais_emp_empreendimentos", [
    "id_empreendimento (PK)", "nome", "localizacao", "tipo", "link_pdf", "link_tour_360"
], color='#e2e3e5')

draw_table(ax, 2, 8, "mais_emp_lead", [
    "id_lead (PK)", "id_usuario (FK)", "id_empreendimento (FK)",
    "objetivo", "forma_pagamento", "renda_familiar", "potencial", "interesse_empreendimento", "created_at"
], color='#fff3cd')

draw_table(ax, 10, 8, "mais_emp_agendamento", [
    "id_agendamento (PK)", "id_usuario (FK)", "cliente_id (FK)",
    "tipo_evento", "data", "horario", "status", "negociacao", "created_at"
], color='#fde2e2')

def draw_arrow(x1, y1, x2, y2, text=None):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='black'))
    if text:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.2, text, ha='center', fontsize=9, style='italic')

draw_arrow(4, 15, 4, 10, "1:N")  # usuarios -> leads
draw_arrow(10, 15, 6, 10, "1:N")  # empreendimentos -> leads
draw_arrow(4, 15, 11, 10, "1:N")  # usuarios -> agendamento (quem agenda)
draw_arrow(4, 14.5, 13, 10, "1:N")  # usuarios -> agendamento (cliente_id)

plt.tight_layout()
plt.show()
