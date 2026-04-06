from database import LocalDatabase
import pandas as pd

db = LocalDatabase()

def get_total_sales_by_month(months_period: int = 6) -> pd.DataFrame:
    '''Vendas totais por mês e categoria para um período determinado.'''
    query = f"""
    SELECT
        strftime(date, '%Y-%m') AS month,
        p.category AS product_category,
        SUM(c.quantity) AS total_quantity_sold
    FROM
        carts AS c
    JOIN 
        products AS p ON c.productId = p.id
    WHERE 1=1
        AND date >= CURRENT_DATE - INTERVAL '{months_period} months'
        AND status = 'Completed'
    GROUP BY 
        ALL
    ORDER BY 
        1 DESC, 3 DESC
    """
    return db.execute_query(query)

def get_top_rated_products(min_rating: float = 4.0) -> pd.DataFrame:
    '''Lista de produtos mais bem avaliados.'''
    query = f"""
    SELECT
        title AS product_name,
        category AS product_category,
        rating.count AS rating_count,
        rating.rate AS rating_value
    FROM
        products
    WHERE 1=1
        AND rating.rate >= {min_rating}
    ORDER BY 
        rating.rate DESC
    """
    return db.execute_query(query)

def get_best_rated_categories() -> pd.DataFrame:
    '''Categorias mais bem avaliadas usando média ponderada (rate * count).'''
    query = """
    SELECT
        category AS Categoria,
        ROUND(SUM(rating.rate * rating.count) / SUM(rating.count) , 2) AS Nota,
        CAST(SUM(rating.count) AS INT64) AS "Reviews"
    FROM
        products
    WHERE 1=1
    GROUP BY 
        ALL
    ORDER BY 
        Nota DESC
    """
    return db.execute_query(query)

def get_customer_average_sales(months_period: int, categories: list) -> pd.DataFrame:
    '''Vendas médias por cliente filtradas por período e categoria de produto.'''
    
    # Função auxiliar para tratar aspas simples (evita erro em "women's clothing")
    def sql_list(items):
        if not items: return "('')"
        safe_items = [str(i).replace("'", "''") for i in items]
        return "('" + "','".join(safe_items) + "')"

    query = f"""
    SELECT
        u.id AS userId,
        u."name.firstname" || ' ' || u."name.lastname" AS user_name,
        COUNT(DISTINCT c.id) AS total_orders,
        SUM(c.quantity * p.price) / COUNT(DISTINCT c.id) AS average_ticket
    FROM
        carts AS c
    JOIN 
        users AS u ON c.userId = u.id
    JOIN 
        products AS p ON c.productId = p.id
    WHERE 1=1
        AND c.status = 'Completed'
        AND c.date >= CURRENT_DATE - INTERVAL '{months_period} months'
        AND p.category IN {sql_list(categories)}
    GROUP BY 
        u.id, user_name
    ORDER BY 
        average_ticket DESC
    """
    return db.execute_query(query)

def get_monthly_average_ticket() -> pd.DataFrame:
    '''Verifica o ticket médio geral da loja por mês.'''
    query = """
    SELECT
        strftime(date, '%Y-%m') AS month,
        SUM(c.quantity * p.price) / COUNT(DISTINCT c.id) AS monthly_avg_ticket
    FROM
        carts AS c
    JOIN 
        products AS p ON c.productId = p.id
    WHERE 1=1
        AND c.status = 'Completed'
    GROUP BY 
        1
    ORDER BY 
        1 DESC
    """
    return db.execute_query(query)

def get_purchase_status_percentage() -> pd.DataFrame:
    '''Porcentagem de status de compra: Completed vs Cancelled por mês.'''
    query = """
    SELECT
        strftime(date, '%Y-%m') AS month,
        status,
        COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY strftime(date, '%Y-%m')) AS percentage
    FROM
        carts
    WHERE 1=1
    GROUP BY 
        1, 2
    ORDER BY 
        1 DESC
    """
    return db.execute_query(query)

def get_user_locations() -> pd.DataFrame:
    '''Retorna localização dos usuários convertendo tipos para compatibilidade JSON.'''
    query = """
    SELECT
        id AS userId,
        "name.firstname" || ' ' || "name.lastname" AS user_name,
        CAST("address.geolocation.lat" AS FLOAT) AS latitude,
        CAST("address.geolocation.long" AS FLOAT) AS longitude,
        "address.city" AS city
    FROM
        users
    WHERE 1=1
        AND "address.geolocation.lat" IS NOT NULL
    """
    df = db.execute_query(query)
    
    # SOLUÇÃO PARA O ERRO: Converte explicitamente para float64 (compatível com JSON)
    df['latitude'] = df['latitude'].astype(float)
    df['longitude'] = df['longitude'].astype(float)
    
    return df



def get_monthly_revenue_report(months_period: int, categories: list) -> pd.DataFrame:
    '''Retorna o Faturamento Total por mês filtrado por Categoria, Cliente e Produto.'''
    
    # Função auxiliar para tratar aspas simples em listas de strings
    def sql_list(items):
        if not items: return "('')"
        safe_items = [str(i).replace("'", "''") for i in items]
        return "('" + "','".join(safe_items) + "')"
    
    query = f"""
    SELECT
        strftime(c.date, '%Y-%m') AS month,
        SUM(c.quantity * p.price) AS total_revenue
    FROM
        carts AS c
    JOIN 
        products AS p ON c.productId = p.id
    JOIN
        users AS u ON c.userId = u.id
    WHERE 1=1
        AND c.date >= CURRENT_DATE - INTERVAL '{months_period} months'
        AND p.category IN {sql_list(categories)}
        AND c.status = 'Completed'
    GROUP BY 1
    ORDER BY 1
    """
    return db.execute_query(query)


def get_filtered_metrics(months_period: int, categories: list) -> pd.DataFrame:
    '''Métricas base com filtros de Categoria, Usuário e Produto.'''
    
    # Utilitário para criar filtros SQL seguros
    def sql_list(items):
        safe_items = [str(i).replace("'", "''") for i in items]
        return "('" + "','".join(safe_items) + "')"

    query = f"""
    SELECT
        CASE
            WHEN c.status = 'Completed' THEN 'Venda Efetivada'
            ELSE 'Venda Cancelada'
        END AS status,
        SUM(c.quantity * p.price) as revenue,
        COUNT(DISTINCT c.id) as order_count,
        SUM(c.quantity) as total_items
    FROM carts AS c
    JOIN products AS p ON c.productId = p.id
    JOIN users AS u ON c.userId = u.id
    WHERE c.date >= CURRENT_DATE - INTERVAL '{months_period} months'
      AND p.category IN {sql_list(categories)}
    GROUP BY 1
    """
    return db.execute_query(query)



def get_user_consumption_pattern(months_period: int, categories: list) -> pd.DataFrame:
    '''Tabela de padrão de consumo: Usuário, Categoria e Qtd.'''
    safe_categories = [c.replace("'", "''") for c in categories]
    cat_filter = "('" + "','".join(safe_categories) + "')"
    query = f"""
    SELECT
        u."name.firstname" || ' ' || u."name.lastname" AS "Nome do Usuário",
        p.category AS "Categoria",
        SUM(c.quantity) AS "Qtd Comprada",
        SUM(c.quantity * p.price) AS "Valor Total"
    FROM carts c
    JOIN users u ON c.userId = u.id
    JOIN products p ON c.productId = p.id
    WHERE c.date >= CURRENT_DATE - INTERVAL '{months_period} months'
      AND p.category IN {cat_filter}
      AND c.status = 'Completed'
    GROUP BY 1, 2
    ORDER BY 3 DESC
    """
    return db.execute_query(query)

def get_product_performance_table(months_period: int, categories: list) -> pd.DataFrame:
    '''Tabela de performance detalhada com nomes em português.'''
    safe_categories = [c.replace("'", "''") for c in categories]
    cat_filter = "('" + "','".join(safe_categories) + "')"
    query = f"""
    SELECT
        strftime(c.date, '%Y-%m') AS "Mês",
        p.category AS "Categoria",
        p.title AS "Produto",
        SUM(c.quantity) AS "Qtd Vendida",
        SUM(c.quantity * p.price) AS "Valor Vendido"
    FROM carts c
    JOIN products p ON c.productId = p.id
    WHERE c.date >= CURRENT_DATE - INTERVAL '{months_period} months'
      AND p.category IN {cat_filter}
    GROUP BY 1, 2, 3
    ORDER BY 1 DESC, 5 DESC
    """
    return db.execute_query(query)