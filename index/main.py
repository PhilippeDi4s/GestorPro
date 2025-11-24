from config.config_bd import conectar_bd
from mysql.connector import Error
from datetime import datetime
from index.crud_cargos import JanelaCargos
from index.crud_funcionarios import JanelaFuncionarios

import tkinter as tk
from tkinter import ttk  
from tkinter import messagebox

class Main:
    
    def __init__(self, root):
        
        # --- Configuração da Janela Principal ---
        self.root = root 
        self.root.title("Gestorpro")
        self.root.geometry("1000x600") 
        
        nav_header = tk.Frame(root, padx=20, pady=20)
        nav_header.pack()
        
        tk.Button(nav_header, text="Gerenciar Cargos", width=25, command=self.abrir_cargos).pack(pady=10)
        tk.Button(nav_header, text="Gerenciar Funcionários",  width=25, command=self.abrir_funcionarios).pack(pady=10)

    def abrir_cargos(self):
        JanelaCargos(self.root)
        
    def abrir_funcionarios(self):
        JanelaFuncionarios(self.root)



# --- 4. Ponto de Entrada do Script ---
if __name__ == "__main__":
    # Testa a conexão com o BD antes de abrir a janela
    conexao_teste = conectar_bd()
    if conexao_teste:
        # Fecha a conexão de teste
        conexao_teste.close()
        
        # --- Inicialização do Tkinter ---
        
        # 1. Cria a janela principal da aplicação. É a "raiz" (root) de tudo.
        root = tk.Tk()
        
        # 2. Cria uma instância da nossa classe AplicacaoCRUD.
        #    Isso chama o método __init__ e passa a janela 'root' para ele.
        #    Nesse momento, todos os widgets (botões, campos, etc.) são criados.
        app = Main(root)
        
        # 3. Inicia o "loop principal" (event loop) do Tkinter.
        #    O programa fica aqui, "escutando" por eventos (cliques,
        #    teclas, etc.) até que a janela seja fechada pelo usuário.
        root.mainloop()
    else:
        # Se a conexão inicial falhou, o programa nem abre a GUI
        # (a função conectar_bd() já mostrou o pop-up de erro).
        print("Erro fatal: Não foi possível conectar ao banco de dados.")
 