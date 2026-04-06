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
        category AS product_category,
        SUM(rating.rate * rating.count) / SUM(rating.count) AS weighted_rating_avg,
        SUM(rating.count) AS total_reviews
    FROM
        products
    WHERE 1=1
    GROUP BY 
        ALL
    ORDER BY 
        weighted_rating_avg DESC
    """
    return db.execute_query(query)

def get_customer_average_sales() -> pd.DataFrame:
    '''Vendas médias por cliente: quantidade de compras e ticket médio.'''
    query = """
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
    GROUP BY 
        ALL
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
    '''Retorna o Faturamento Total por mês com escape de aspas.'''
    
    safe_categories = [c.replace("'", "''") for c in categories]
    cat_filter = "('" + "','".join(safe_categories) + "')"
    
    query = f"""
    SELECT
        strftime(c.date, '%Y-%m') AS month,
        SUM(c.quantity * p.price) AS total_revenue
    FROM
        carts AS c
    JOIN 
        products AS p ON c.productId = p.id
    WHERE 1=1
        AND c.date >= CURRENT_DATE - INTERVAL '{months_period} months'
        AND p.category IN {cat_filter}
        AND c.status = 'Completed'
    GROUP BY 1
    ORDER BY 1
    """
    return db.execute_query(query)


def get_filtered_metrics(months_period: int, categories: list) -> pd.DataFrame:
    '''Métricas base com escape de aspas.'''
    
    safe_categories = [c.replace("'", "''") for c in categories]
    cat_filter = "('" + "','".join(safe_categories) + "')"
    
    query = f"""
    SELECT
        status,
        SUM(c.quantity * p.price) as revenue,
        COUNT(DISTINCT c.id) as order_count
    FROM
        carts AS c
    JOIN 
        products AS p ON c.productId = p.id
    WHERE 1=1
        AND c.date >= CURRENT_DATE - INTERVAL '{months_period} months'
        AND p.category IN {cat_filter}
    GROUP BY status
    """
    return db.execute_query(query)