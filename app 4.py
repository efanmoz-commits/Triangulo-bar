import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gestão de Stock e Caixa", layout="wide", page_icon="🍻")

# 1. Opção de editar o nome do bar
st.sidebar.header("🏢 Configuração do Estabelecimento")
nome_bar = st.sidebar.text_input("Nome do Bar", value="Triângulo Bar")

st.title(f"🍻 {nome_bar} - Controlo de Stock e Caixa")
st.markdown("Gestão diária de stock, reposições, faturamento e caixa líquido efetivo.")

if 'df_stock' not in st.session_state:
    # Produtos base estruturados sem quantidades fixas de vendas/compras (zeradas para limpeza inicial)
    base_produtos = [
        ["2M", 12, 0, 0, 0, 620, 60],
        ["2M Lata", 24, 0, 0, 0, 1100, 55],
        ["Água da Namaacha", 24, 0, 0, 0, 370, 25],
        ["Bernini Garrafa", 24, 0, 0, 0, 1700, 85],
        ["Brutal", 24, 0, 0, 0, 1230, 60],
        ["Corona", 24, 0, 0, 0, 1600, 80],
        ["Gold", 24, 0, 0, 0, 1560, 0],
        ["Heineken Lata", 24, 0, 0, 0, 1350, 70],
        ["Heineken Txoti", 24, 0, 0, 0, 1540, 75],
        ["Impala", 12, 0, 0, 0, 480, 50],
        ["Lite", 24, 0, 0, 0, 1300, 65],
        ["MayFair", 24, 0, 0, 0, 1680, 80],
        ["Pretinha", 24, 0, 0, 0, 820, 50],
        ["Refreco", 24, 0, 0, 0, 370, 25],
        ["Savana", 24, 0, 0, 0, 1630, 80],
        ["Stella", 24, 0, 0, 0, 1450, 80],
        ["Sumo Compal", 12, 0, 0, 0, 580, 0],
        ["Txilar", 12, 0, 0, 0, 480, 50],
    ]
    
    # Acrescentar mais 10 espaços/linhas vazias extras
    for i in range(1, 11):
        base_produtos.append([f"Produto Vazio {i}", 24, 0, 0, 0, 0.0, 0.0])

    st.session_state.df_stock = pd.DataFrame(base_produtos, columns=[
        "Produto", "Unid_Caixa", "Estoque_Inicial_Cx", "Caixas_Repostas", 
        "Qtd_Vendida_Un", "Preco_Caixa", "Preco_Venda_Un"
    ])

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Configurações & Despesas")
dividas = st.sidebar.number_input("Dívidas / Fiados por Receber (MT)", value=0.0, step=50.0)
outras_despesas = st.sidebar.number_input("Outras Despesas / Saídas (MT)", value=0.0, step=10.0)

st.sidebar.markdown("---")
st.sidebar.header("➕ Adicionar Novo Produto")
with st.sidebar.form("form_novo_produto"):
    novo_nome = st.text_input("Nome do Produto")
    nova_un_cx = st.number_input("Unidades por Caixa", min_value=1, value=24)
    novo_estoque_cx = st.number_input("Estoque Inicial (Caixas)", min_value=0, value=0)
    novo_preco_cx = st.number_input("Preço da Caixa (MT)", min_value=0.0, value=1000.0)
    novo_preco_venda = st.number_input("Preço de Venda Unitário (MT)", min_value=0.0, value=50.0)
    submit_produto = st.form_submit_button("Adicionar à Lista")

    if submit_produto and novo_nome:
        novo_reg = pd.DataFrame([[novo_nome, nova_un_cx, novo_estoque_cx, 0, 0, novo_preco_cx, novo_preco_venda]], 
                                columns=st.session_state.df_stock.columns)
        st.session_state.df_stock = pd.concat([st.session_state.df_stock, novo_reg], ignore_index=True)
        st.success("Produto adicionado com sucesso!")

st.subheader("📦 Atualizar Stock e Vendas")
st.markdown("Altere diretamente as **Caixas Repostas (Compras)** e as **Unidades Vendidas** na tabela abaixo:")

edited_df = st.data_editor(st.session_state.df_stock, num_rows="dynamic", use_container_width=True)
st.session_state.df_stock = edited_df

edited_df["Custo_Total_Recargas"] = edited_df["Caixas_Repostas"] * edited_df["Preco_Caixa"]
edited_df["Preco_Custo_Un"] = edited_df["Preco_Caixa"] / edited_df["Unid_Caixa"]
edited_df["Valor_Vendido"] = edited_df["Qtd_Vendida_Un"] * edited_df["Preco_Venda_Un"]
edited_df["Lucro_Total"] = edited_df["Valor_Vendido"] - (edited_df["Qtd_Vendida_Un"] * edited_df["Preco_Custo_Un"])

def calc_final_stock(row):
    try:
        total_un = ((row["Estoque_Inicial_Cx"] + row["Caixas_Repostas"]) * row["Unid_Caixa"]) - row["Qtd_Vendida_Un"]
        cx = int(total_un // row["Unid_Caixa"])
        un = int(total_un % row["Unid_Caixa"])
        return f"{cx} Cx e {un} Un"
    except:
        return "0 Cx e 0 Un"

edited_df["Estoque_Final"] = edited_df.apply(calc_final_stock, axis=1)

total_faturamento = edited_df["Valor_Vendido"].sum()
total_recargas = edited_df["Custo_Total_Recargas"].sum()
total_lucro = edited_df["Lucro_Total"].sum()
caixa_liquido = total_faturamento - total_recargas - dividas - outras_despesas

st.markdown("---")
st.subheader("📊 Resumo Financeiro e Caixa Líquido")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Faturamento Bruto", f"{total_faturamento:.2f} MT")
col2.metric("Custo de Recargas", f"{total_recargas:.2f} MT")
col3.metric("Lucro Total Estimado", f"{total_lucro:.2f} MT")
col4.metric("Caixa Líquido Efetivo", f"{caixa_liquido:.2f} MT", delta="Dinheiro em Caixa")

st.markdown(f"""
- **Valor Total Bruto Vendido:** {total_faturamento:,.2f} MT
- **(-) Custo Total das Recargas (Novas Caixas):** {total_recargas:,.2f} MT
- **(-) Total de Dívidas / Fiados:** {dividas:,.2f} MT
- **(-) Outras Despesas:** {outras_despesas:,.2f} MT
- **(=) Caixa Líquido Efetivo Disponível:** **{caixa_liquido:,.2f} MT**
""")
