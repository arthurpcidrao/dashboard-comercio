import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

BASE_URL = "https://fakestoreapi.com"

# documentation = "https://fakestoreapi.com/docs"


def fetch_data(endpoint: str) -> list:
    '''
    Função que faz a requisição GET para o endpoint geral, ou seja, uma lista de produtos, 
    usuários ou carrinhos. O endpoint é passado como argumento.
    '''
    response = requests.get(f"{BASE_URL}/{endpoint}")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Erro ao acessar {endpoint}: {response.status_code}")
    


def products_to_parquet() -> pd.DataFrame:
    '''
    Função que extrai os dados de produtos e salva em arquivos Parquet.
    '''
    print("Extraindo Produtos...")
    products_raw = fetch_data("products")
    df_products = pd.DataFrame(products_raw)
    df_products.to_parquet("data/products.parquet", index=False)
    
    return df_products



def users_to_parquet() -> pd.DataFrame:
    '''
    Função que extrai os dados de usuários e salva em arquivos Parquet.
    '''
    print("Extraindo Usuários...")
    users_raw = fetch_data("users")
    # O JSON de users é aninhado (address, name), precisamos normalizar
    df_users = pd.json_normalize(users_raw)
    df_users.to_parquet("data/users.parquet", index=False)
    
    return df_users



def carts_to_parquet() -> pd.DataFrame:
    '''
    Extrai carrinhos, explode produtos e gera dados sintéticos de data e status.
    '''
    print("Extraindo Carrinhos...")
    carts_raw = fetch_data("carts")
    df_carts = pd.DataFrame(carts_raw)
    
    # 1. Explode para ter uma linha por produto
    df_carts = df_carts.explode('products').reset_index(drop=True)
    
    # 2. Extrai productId e quantity do dicionário
    df_carts['productId'] = df_carts['products'].apply(lambda x: x.get('productId'))
    df_carts['quantity'] = df_carts['products'].apply(lambda x: x.get('quantity'))
    
    # 3. Lógica de Datas (Últimos 4 meses / 120 dias)
    end_date = datetime.now()
    df_carts['date'] = [
        end_date - timedelta(days=np.random.randint(0, 120), 
                             hours=np.random.randint(0, 24))
        for _ in range(len(df_carts))
    ]
    
    # 4. Lógica de Status (70% Completed / 30% Cancelled)
    df_carts['status'] = np.random.choice(
        ['Completed', 'Cancelled'], 
        size=len(df_carts), 
        p=[0.7, 0.3]
    )
    
    # 5. Limpeza e salvamento
    df_carts = df_carts.drop(columns=['products'])
    df_carts.to_parquet("data/carts.parquet", index=False)
    
    return df_carts


def run_extraction():

    df_products = products_to_parquet()

    df_users = users_to_parquet()

    df_carts = carts_to_parquet()
    print("Extração concluída com sucesso!")

    return df_products, df_users, df_carts




print("Iniciando extração de dados...")
df_products, df_users, df_carts = run_extraction()
print(df_products.all())
print()
print(df_users.head())
print()
print(df_carts.head())
print("Processo de extração finalizado.")


# print(fetch_data("products/1"))