import streamlit as st

st.set_page_config(page_title="Metodologia - Retail Analytics", layout="wide")

st.title("📖 Metodologia e Arquitetura do Projeto")
st.markdown("---")

# Seção 1: Visão Geral
st.header("🎯 Objetivo do Painel")
st.write("""
Este dashboard foi construído seguindo o conceito de **pirâmide de informações**: 
Iniciamos com indicadores macro (KPIs de faturamento e volume) no topo e permitimos o 
detalhamento progressivo (drill-down) até o nível de comportamento do consumidor e logística.
""")

with st.expander("🔍 Estratégia de Filtragem"):
    st.write("""
    O painel é totalmente reativo. O usuário pode filtrar toda a massa de dados por:
    - **Categoria de Produto**: Seleção múltipla via componentes interativos.
    - **Período Temporal**: Ajuste dinâmico dos últimos meses de operação.
    """)

# Seção 2: Origem dos Dados
st.header("🔌 Origem e Extração de Dados")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Fonte dos Dados")
    st.write("""
    Os dados originais foram extraídos da [FakeStoreAPI](https://fakestoreapi.com/docs). 
    A escolha por esta fonte teve como objetivo exercitar:
    - Conexão via **Protocolo HTTP**.
    - Consumo de APIs REST.
    - Tratamento de JSON aninhado para tabelas relacionais.
    """)

with col2:
    st.subheader("Enriquecimento")
    st.write("""
    Para simular um ambiente de produção real (Big Data), foi aplicado um multiplicador de **150x** na base de carrinhos, além da geração sintética de datas e status de compra, garantindo volume 
    para análises estatísticas e séries temporais de 6 meses.
    """)

# Seção 3: Tecnologia e Performance
st.header("🛠️ Stack Tecnológica")

c1, c2, c3 = st.columns(3)

with c1:
    st.image("https://duckdb.org/images/favicon.png", width=50)
    st.markdown("**DuckDB**")
    st.write("""
    Utilizado como banco de dados OLAP em memória. 
    Permite a execução de consultas SQL complexas diretamente em arquivos Parquet com 
    performance de milissegundos.
    """)

with c2:
    st.image("https://streamlit.io/images/brand/streamlit-mark-color.png", width=50)
    st.markdown("**Streamlit**")
    st.write("""
    Framework utilizado para o desenvolvimento do Frontend e das visualizações, 
    consolidando o domínio da linguagem **Python** para entrega de soluções de dados ponta a ponta.
    """)

with c3:
    st.image("https://altair-viz.github.io/_static/altair-logo-light.png", width=50)
    st.markdown("**Altair**")
    st.write("""
    Biblioteca de visualização declarativa para a criação de gráficos interativos e 
    estatísticos que compõem o BI.
    """)

# Seção 4: Modelagem de Dados
st.header("📊 Modelagem Relacional")
st.write("""
O ecossistema de dados baseia-se em três entidades principais:
1. **Users**: Informações cadastrais e geolocalização dos clientes.
2. **Products**: Catálogo, preços e avaliações técnicas.
3. **Carts**: Transações que conectam clientes aos produtos.
""")

st.info("""
**Lógica de Negócio**: Para mensurar o engajamento, realizamos um **JOIN** entre a base de 
`Users` e `Carts`. A contagem de pedidos válidos é feita filtrando status 'Completed' 
e agrupando pela chave primária do usuário, garantindo a integridade da métrica de Ticket Médio.
""")

st.markdown("---")
st.caption("Desenvolvido por Arthur P. Cidrao - 2026")