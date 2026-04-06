import streamlit as st
import queries
import charts

# Configuração da Página
st.set_page_config(
    page_title="vendas online", 
    layout="wide"
)

# --- SIDEBAR / FILTROS GLOBAIS ---
st.sidebar.title("Filtros Globais")

# 1. Filtro de Período (Slider)
periodo = st.sidebar.slider("Período de Análise (Meses)", 1, 12, 6)

# Carregamento de dados para filtros dinâmicos
df_vendas_base = queries.get_total_sales_by_month(periodo)
categorias_disponiveis = df_vendas_base['product_category'].unique().tolist()

# 2. Filtro de Categorias (Pills)
st.sidebar.write("Filtrar por Categoria:")
selecao_categorias = st.sidebar.pills(
    "Categorias", 
    categorias_disponiveis, 
    selection_mode="multi", 
    default=categorias_disponiveis
)

# Aplicar filtro de categoria no dataframe de vendas
df_vendas_filtrado = df_vendas_base[df_vendas_base['product_category'].isin(selecao_categorias)]

# --- LAYOUT DO DASHBOARD ---
st.title("📊 Dashboard Comercial - Análise de Vendas Online")
st.markdown("---")

# Métricas Rápidas (KPIs)
col1, col2, col3 = st.columns(3)
with col1:
    total_itens = df_vendas_filtrado['total_quantity_sold'].sum()
    st.metric("Total de Itens Vendidos", f"{total_itens:,}")

with col2:
    df_ticket = queries.get_monthly_average_ticket()
    avg_ticket = df_ticket['monthly_avg_ticket'].mean()
    st.metric("Ticket Médio (Geral)", f"R$ {avg_ticket:.2f}")

with col3:
    df_status_base = queries.get_purchase_status_percentage()
    # Filtrando a média de sucesso apenas para os meses no período
    taxa_sucesso = df_status_base[df_status_base['status'] == 'Completed']['percentage'].mean()
    st.metric("Taxa de Conversão", f"{taxa_sucesso:.1f}%")

st.markdown("---")

# Linha 1: Séries Temporais e Heatmap
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Evolução de Vendas por Categoria")
    fig_vendas = charts.plot_line_chart(
        df_vendas_filtrado, 'month', 'total_quantity_sold', 'product_category',
        "Mês da Venda", "Qtd Vendida", "Volume de Vendas Mensal"
    )
    # Atualizado para a nova sintaxe de 2026
    st.altair_chart(fig_vendas, width="stretch")

with c2:
    st.subheader("Tabela de Performance")
    # Tabela com Mapa de Calor (Estilização Pandas)
    st.dataframe(
        df_vendas_filtrado.style.background_gradient(cmap='Greens', subset=['total_quantity_sold']),
        width="stretch"
    )

st.markdown("---")

# Linha 2: Maiores Clientes e Mapa Logístico
c3, c4 = st.columns(2)

with c3:
    st.subheader("Top 10 Clientes (Maior Ticket)")
    df_clientes = queries.get_customer_average_sales().head(10)
    fig_clientes = charts.plot_bar_chart(
        df_clientes, 'average_ticket', 'user_name',
        "Ticket Médio (R$)", "Cliente", "Maiores Gastadores"
    )
    st.altair_chart(fig_clientes, width="stretch")

with c4:
    st.subheader("📍 Localização de Clientes (Logística)")
    df_mapa = queries.get_user_locations()
    
    # Camada de segurança para garantir que lat/lon sejam float64 (evita erro de JSON)
    df_mapa['latitude'] = df_mapa['latitude'].astype(float)
    df_mapa['longitude'] = df_mapa['longitude'].astype(float)
    
    # O Streamlit utiliza DeckGL internamente para o st.map
    st.map(df_mapa, latitude='latitude', longitude='longitude', size=20, color='#ff4b4b')
    st.caption("Insight: Concentração geográfica para expansão de galpões logísticos.")

# Linha 3: Qualidade e Status
st.markdown("---")
c5, c6 = st.columns(2)

with c5:
    st.subheader("Categorias Mais Bem Avaliadas")
    df_cat = queries.get_best_rated_categories()
    st.dataframe(df_cat, width="stretch")

with c6:
    st.subheader("Status de Compra por Mês (%)")
    df_status = queries.get_purchase_status_percentage()
    fig_status = charts.plot_line_chart(
        df_status, 'month', 'percentage', 'status',
        "Mês", "Porcentagem (%)", "Completed vs Cancelled"
    )
    st.altair_chart(fig_status, width="stretch")