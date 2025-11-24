import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'F&rradura01',
    'database': 'GestorPro_BD'
}

def conectar_bd():
    """
    Tenta se conectar ao banco de dados e retorna a conexão.
    Retorna None se ocorrer erro.
    """
    try:
        conexao = mysql.connector.connect(**DB_CONFIG)
        return conexao
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None
