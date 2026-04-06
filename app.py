import streamlit as st
import queries, charts

st.set_page_config(page_title="Análises Varejo", layout="wide")

# --- SIDEBAR / FILTROS ---
st.sidebar.title("🎯 Navegação")
# Botão para ir para a página de metodologia
if st.sidebar.button("📖 Ver Metodologia", use_container_width=True):
    st.switch_page("pages/metodologia.py")

st.sidebar.markdown("---")
st.sidebar.title("Filtros Estratégicos")
periodo = st.sidebar.slider("Meses", 1, 6, 6)

# Carregamento inicial para pegar os nomes das categorias
df_init = queries.get_total_sales_by_month(6)
categorias_disponiveis = df_init['product_category'].unique().tolist()

selecao_pills = st.sidebar.pills(
    "Categorias", 
    categorias_disponiveis, 
    selection_mode="multi", 
    default=None
)

if not selecao_pills:
    selecao_categorias = categorias_disponiveis
else:
    selecao_categorias = selecao_pills

# --- CARREGAMENTO DE DADOS ---
df_metricas = queries.get_filtered_metrics(periodo, selecao_categorias)
df_faturamento = queries.get_monthly_revenue_report(periodo, selecao_categorias)
df_vendas_cat = queries.get_total_sales_by_month(periodo)
df_vendas_cat = df_vendas_cat[df_vendas_cat['product_category'].isin(selecao_categorias)]

# --- CÁLCULOS DOS KPIs ---
if not df_metricas.empty and 'status' in df_metricas.columns:
    vendas_sucesso = df_metricas[df_metricas['status'] == 'Venda Efetivada']
    receita_total = vendas_sucesso['revenue'].sum()
    qtd_pedidos = vendas_sucesso['order_count'].sum()
else:
    receita_total = 0
    qtd_pedidos = 0

total_itens = df_vendas_cat['total_quantity_sold'].sum()
ticket_medio = receita_total / qtd_pedidos if qtd_pedidos > 0 else 0
itens_por_carrinho = total_itens / qtd_pedidos if qtd_pedidos > 0 else 0

st.title("📊 BI - Dashboard Comercial de Varejo")

st.write("Dashboard de análise comercial construído a partir da API de dados gratuita: https://fakestoreapi.com/docs")
st.write("Os dados foram enriquecidos e estruturados para fornecer insights valiosos sobre vendas, clientes e produtos. " \
"Os dados são fictícios e destinados apenas para fins de demonstração.")

# --- LINHA 1: KPIs (4 COLUNAS) ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Valor Total Vendido", f"R$ {receita_total:,.2f}")
m2.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
m3.metric("Total de Itens", f"{total_itens:,.0f}")
m4.metric("Média Itens/Carrinho", f"{itens_por_carrinho:.2f}")

st.markdown("---")

# --- LINHA 2: FINANCEIRO E STATUS (2 COLUNAS) ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Valor Vendido por Mês")
    if not df_faturamento.empty:
        st.altair_chart(charts.plot_line_chart(df_faturamento, 'month', 'total_revenue', None, "Mês", "Receita", "Evolução Financeira"), width="stretch")
with c2:
    st.subheader("Status dos Carrinhos")
    if not df_metricas.empty:
        st.altair_chart(charts.plot_donut_chart(df_metricas, 'order_count', 'status', "Conversão de Vendas"), width="stretch")

st.markdown("---")

# --- LINHA 3: CATEGORIAS E PERFORMANCE (2 COLUNAS) ---
c3, c4 = st.columns(2)
with c3:
    st.subheader("Qtd de Vendas por Categoria")
    st.altair_chart(charts.plot_line_chart(df_vendas_cat, 'month', 'total_quantity_sold', 'product_category', "Mês", "Qtd", "Volume por Categoria"), width="stretch")
with c4:
    st.subheader("Performance de Produtos")
    df_perf = queries.get_product_performance_table(periodo, selecao_categorias)
    
    df_perf_sorted = df_perf.sort_values(by='Valor Vendido', ascending=False)
    
    st.dataframe(
        df_perf_sorted.style.background_gradient(cmap='Blues', subset=['Valor Vendido']), 
        width="stretch"
    )

st.markdown("---")

# --- LINHA 4: CLIENTES E MAPA (2 COLUNAS) ---
c5, c6 = st.columns(2)
with c5:
    st.subheader("Top 10 Clientes (Ticket Médio)")
    df_clientes = queries.get_customer_average_sales(periodo, selecao_categorias).head(10)
    st.altair_chart(charts.plot_bar_chart(df_clientes, 'average_ticket', 'user_name', "Ticket (R$)", "Cliente", "Maiores Gastadores"), width="stretch")
with c6:
    st.subheader("📍 Mapa Logístico")
    df_mapa = queries.get_user_locations()
    df_mapa['latitude'] = df_mapa['latitude'].astype(float)
    df_mapa['longitude'] = df_mapa['longitude'].astype(float)
    st.map(df_mapa, latitude='latitude', longitude='longitude', size=20)

    st.write("**Observação:** O mapa acima é uma representação fictícia baseada em dados de localização " \
    "gerados aleatoriamente para os usuários. Ele serve apenas para fins ilustrativos e não reflete " \
    "localizações reais dos clientes."
    )

st.markdown("---")

# --- LINHA 5: PADRÃO E QUALIDADE (2 COLUNAS) ---
c7, c8 = st.columns(2)
with c7:
    st.subheader("Padrão de Consumo")
    st.dataframe(queries.get_user_consumption_pattern(periodo, selecao_categorias), width="stretch")
with c8:
    st.subheader("Categorias Mais Bem Avaliadas")
    st.table(queries.get_best_rated_categories())