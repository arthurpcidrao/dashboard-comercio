import duckdb
import pandas as pd
import os

class LocalDatabase:
    def __init__(self, db_path: str = "data/varejo.db"):
        self.db_path = db_path
        self._setup_database()

    def _get_connection(self):
        """Retorna uma conexão com o DuckDB."""
        return duckdb.connect(self.db_path)

    def _setup_database(self):
        """
        Cria as views iniciais apontando para os parquets. 
        Isso garante que as tabelas existam sempre que a classe for instanciada.
        """
        # Verifica se os arquivos existem antes de tentar criar as views
        files = {
            "products": "data/products.parquet",
            "users": "data/users.parquet",
            "carts": "data/carts.parquet"
        }
        
        with self._get_connection() as con:
            for table_name, file_path in files.items():
                if os.path.exists(file_path):
                    con.execute(f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM '{file_path}'")
            print("[DB] Views mapeadas com sucesso para os arquivos Parquet.")

    def execute_query(self, sql_query: str) -> pd.DataFrame:
        """
        Executa uma consulta SQL e retorna um DataFrame do Pandas.
        Abre e fecha a conexão automaticamente usando o contexto 'with'.
        """
        try:
            with self._get_connection() as con:
                df = con.execute(sql_query).df()
                return df
        except Exception as e:
            print(f"[DB Error] Falha ao executar query: {e}")
            return pd.DataFrame()


    