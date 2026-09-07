
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Triângulo Bar - Gestão de Stock", layout="wide", page_icon="🍻")

st.title("🍻 Triângulo Bar - Controlo de Stock e Caixa")
st.markdown("Gestão diária de stock, reposições, faturamento e caixa líquido efetivo.")

# Initialize default product data if not in session state
if 'df_stock' not in st.session_state:
    data = [
        ["2M", 12, 8, 0, 79, 620, 60],
        ["2M Lata", 24, 1, 0, 0, 1100, 55],
        ["Água da Namaacha", 24, 1, 0, 1, 370, 25],
        ["Bernini Garrafa", 24, 1, 0, 0, 1700, 85],
        ["Brutal", 24, 2, 0, 0, 1230, 60],
        ["Corona", 24, 3, 0, 4, 1600, 80],
        ["Gold", 24, 0, 0, 0, 1560, 0],
        ["Heineken Lata", 24, 1, 0, 0, 1350, 70],
        ["Heineken Txoti", 24, 1, 0, 7, 1540, 75],
        ["Impala", 12, 8, 0, 33, 480, 50],
        ["Lite", 24, 1, 0, 9, 1300, 65],
        ["MayFair", 24, 1, 0, 16, 1680, 80],
        ["Pretinha", 24, 2, 0, 11, 820, 50],
        ["Refreco", 24, 1, 0, 23, 370, 25],
        ["Savana", 24, 2, 0, 7, 1630, 80],
        ["Stella", 24, 1, 0, 0, 1450, 80],
        ["Sumo Compal", 12, 0, 0, 0, 580, 0],
        ["Txilar", 12, 4, 0, 19, 480, 50],
    ]
    st.session_state.df_stock = pd.DataFrame(data, columns=[
        "Produto", "Unid_Caixa", "Estoque_Inicial_Cx", "Caixas_Repostas", 
        "Qtd_Vendida_Un", "Preco_Caixa", "Preco_Venda_Un"
    ])

df = st.session_state.df_stock

st.sidebar.header("⚙️ Configurações & Despesas")
dividas = st.sidebar.number_input("Dívidas / Fiados por Receber (MT)", value=1885.0, step=50.0)
outras_despesas = st.sidebar.number_input("Outras Despesas / Saídas (MT)", value=150.0, step=10.0)

st.subheader("📦 Atualizar Stock e Vendas")
st.markdown("Altere diretamente as **Caixas Repostas (Compras)** e as **Unidades Vendidas** na tabela abaixo:")

edited_df = st.data_editor(df, num_rows="fixed", use_container_width=True)
st.session_state.df_stock = edited_df

# Calculations
edited_df["Custo_Total_Recargas"] = edited_df["Caixas_Repostas"] * edited_df["Preco_Caixa"]
edited_df["Preco_Custo_Un"] = edited_df["Preco_Caixa"] / edited_df["Unid_Caixa"]
edited_df["Valor_Vendido"] = edited_df["Qtd_Vendida_Un"] * edited_df["Preco_Venda_Un"]
edited_df["Lucro_Total"] = edited_df["Valor_Vendido"] - (edited_df["Qtd_Vendida_Un"] * edited_df["Preco_Custo_Un"])

# Final stock expression
def calc_final_stock(row):
    total_un = ((row["Estoque_Inicial_Cx"] + row["Caixas_Repostas"]) * row["Unid_Caixa"]) - row["Qtd_Vendida_Un"]
    cx = int(total_un // row["Unid_Caixa"])
    un = int(total_un % row["Unid_Caixa"])
    return f"{cx} Cx e {un} Un"

edited_df["Estoque_Final"] = edited_df.apply(calc_final_stock, axis=1)

# Totals
total_faturamento = edited_df["Valor_Vendido"].sum()
total_recargas = edited_df["Custo_Total_Recargas"].sum()
total_lucro = edited_df["Lucro_Total"].sum()
caixa_liquido = total_faturamento - total_recargas - dividas - outras_despesas

st.markdown("---")
st.subheader("📊 Resumo Financeiro e Caixa Líquido")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento Bruto", f"{total_faturamento:,.2f} MT")
col2.metric("Custo de Recargas", f"{total_recargas:,.2f} MT")
col3.metric("Lucro Total Estimado", f"{total_lucro:,.2f} MT")
col4.metric("Caixa Líquido Efetivo", f"{caixa_liquido:,.2f} MT", delta="Dinheiro em Caixa")

st.markdown(f"""
- **Valor Total Bruto Vendido:** {total_faturamento:,.2f} MT
- **(-) Custo Total das Recargas (Novas Caixas):** {total_recargas:,.2f} MT *(subtraído automaticamente do caixa)*
- **(-) Total de Dívidas / Fiados:** {dividas:,.2f} MT
- **(-) Outras Despesas:** {outras_despesas:,.2f} MT
- **(=) Caixa Líquido Efetivo Disponível:** **{caixa_liquido:,.2f} MT**
""")
