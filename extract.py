import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Configurações Globais
BASE_URL = "https://fakestoreapi.com"
DATA_DIR = "data"

# documentation = "https://fakestoreapi.com/docs"

# Constantes para garantir Integridade Referencial
TOTAL_USERS = 100    # Criaremos 100 usuários únicos
TOTAL_PRODUCTS = 20  # A API FakeStore possui 20 produtos fixos

def fetch_data(endpoint: str) -> list:
    '''Faz a requisição GET para a API e retorna uma lista de dados.'''
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise Exception(f"Erro ao acessar {endpoint}: {e}")

def products_to_parquet() -> pd.DataFrame:
    '''Extrai produtos originais. Mantemos os 20 originais para ter fotos e categorias reais.'''
    print("-> Extraindo Produtos...")
    data = fetch_data("products")
    df = pd.DataFrame(data)
    
    # Salva os produtos originais (IDs 1 a 20)
    df.to_parquet(f"{DATA_DIR}/products.parquet", index=False)
    return df

def users_to_parquet() -> pd.DataFrame:
    '''Gera uma base de usuários consistente com dados completos.'''
    print(f"-> Gerando {TOTAL_USERS} Usuários com integridade...")
    data = fetch_data("users")
    df_base = pd.json_normalize(data)
    
    # Multiplica a base para atingir o TOTAL_USERS
    multiplier = (TOTAL_USERS // len(df_base)) + 1
    df_users = pd.concat([df_base] * multiplier, ignore_index=True).iloc[:TOTAL_USERS].copy()
    
    # Atribui IDs sequenciais e customiza dados para serem únicos
    df_users['id'] = range(1, TOTAL_USERS + 1)
    df_users['email'] = df_users['id'].apply(lambda x: f"user_{x}@email.com.br")
    df_users['username'] = df_users['id'].apply(lambda x: f"usuario_varejo_{x}")
    
    # Ajusta nomes para diferenciar os registros clonados
    df_users['name.firstname'] = df_users['name.firstname'] + " " + df_users['id'].astype(str)
    
    df_users.to_parquet(f"{DATA_DIR}/users.parquet", index=False)
    return df_users

def carts_to_parquet(multiplier: int = 50) -> pd.DataFrame:
    '''Gera massa de vendas aleatória garantindo que UserID e ProductID existam.'''
    print(f"-> Gerando Massa de Vendas (Multiplicador: {multiplier})...")
    carts_raw = fetch_data("carts")
    df_base = pd.DataFrame(carts_raw)
    
    # 1. Expandir volume de linhas
    df_carts = pd.concat([df_base] * multiplier, ignore_index=True)
    df_carts = df_carts.explode('products').reset_index(drop=True)
    
    # 2. Gerar IDs únicos para cada venda
    df_carts['id'] = range(1, len(df_carts) + 1)

    # 3. GARANTIR INTEGRIDADE: IDs de usuários e produtos que EXISTEM nas outras tabelas
    df_carts['userId'] = np.random.randint(1, TOTAL_USERS + 1, size=len(df_carts))
    df_carts['productId'] = np.random.randint(1, TOTAL_PRODUCTS + 1, size=len(df_carts))
    
    # 4. Dados aleatórios de transação
    df_carts['quantity'] = np.random.randint(1, 6, size=len(df_carts)) # Entre 1 e 5 itens
    
    # Datas aleatórias nos últimos 4 meses
    end_date = datetime.now()
    df_carts['date'] = [
        end_date - timedelta(days=np.random.randint(0, 180), 
                             hours=np.random.randint(0, 24),
                             minutes=np.random.randint(0, 60))
        for _ in range(len(df_carts))
    ]
    
    # Status da compra (70% Sucesso / 30% Cancelado)
    df_carts['status'] = np.random.choice(
        ['Completed', 'Cancelled'], 
        size=len(df_carts), 
        p=[0.7, 0.3]
    )
    
    # 5. Limpeza de colunas desnecessárias
    df_carts = df_carts[['id', 'userId', 'productId', 'date', 'quantity', 'status']]
    
    df_carts.to_parquet(f"{DATA_DIR}/carts.parquet", index=False)
    print(f"-> Sucesso! {len(df_carts)} linhas de vendas geradas.")
    return df_carts

def run_extraction():
    '''Executa o pipeline completo.'''
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Diretório {DATA_DIR} criado.")

    print("--- INICIANDO EXTRAÇÃO E GERAÇÃO DE DADOS ---")
    products_to_parquet()
    users_to_parquet()
    carts_to_parquet(multiplier=150) # Gera aprox. 3600 linhas de vendas
    print("--- PROCESSO CONCLUÍDO COM SUCESSO ---")

if __name__ == "__main__":
    run_extraction()