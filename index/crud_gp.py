# pip install mysql-connector-python
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# --- Importações da Interface Gráfica (GUI) ---
import tkinter as tk
from tkinter import ttk  # 'themed tk' para widgets mais modernos
from tkinter import messagebox # Para pop-ups de confirmação e erro

# --- 1. Configuração da Conexão com o Banco de Dados ---
# ATENÇÃO: Substitua pelos seus dados de login do MySQL.
DB_CONFIG = {
    'host': 'localhost',
    'port': 3307, 
    'user': 'root',
    'password': 'admin',
    'database': 'GestorPro_BD'
}

def conectar_bd():
    """
    Tenta se conectar ao banco de dados MySQL.
    Retorna o objeto de conexão ou None se falhar.
    """
    try:
        # O operador ** descompacta o dicionário DB_CONFIG
        conexao = mysql.connector.connect(**DB_CONFIG)
        return conexao
    except Error as e:
        # Em vez de printar, exibimos um erro gráfico
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao MySQL:\n{e}\n\nVerifique suas credenciais, porta e se o servidor está no ar.")
        return None

# --- 2. Funções do CRUD (A Lógica do Banco) ---
# MODIFICADAS para retornar mensagens em vez de printar no console.

# --- CREATE (Criar) ---
def inserir_cargo(nome, gerenciar_estoque, fazer_vendas):
    """
    Insere um novo cargo na tabela 'cargo'.
    """
    
    query = """
    INSERT INTO cargo (cargo_nome, pode_gerenciar_estoque, pode_fazer_vendas) 
    VALUES (%s, %s, %s)
    """
    
    conexao = conectar_bd()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(query, (nome, gerenciar_estoque, fazer_vendas))
            conexao.commit()
            return True, (f"\n-> Cargo '{nome}' criado com sucesso (ID: {cursor.lastrowid}).")
        except Error as e:
            return False, f"Erro ao inserir dados: {e}"
        finally:
            cursor.close()
            conexao.close()
    return False, "Falha ao conectar no banco de dados."

# --- READ (Ler/Consultar) ---
def listar_cargos():
    """Lista todos os alunos. Retorna uma lista de dicionários ou None se falhar."""
    query = "SELECT cargo_id, cargo_nome, IF (pode_gerenciar_estoque = 1, 'Sim', 'Não') AS pode_gerenciar_estoque, IF (pode_fazer_vendas = 1, 'Sim', 'Não') AS pode_fazer_vendas FROM cargo"
    
    conexao = conectar_bd()
    if conexao:
        try:
            # dictionary=True faz o resultado vir como um dicionário (chave: valor)
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados # Retorna a lista de alunos
        except Error as e:
            messagebox.showerror("Erro de Leitura", f"Erro ao listar dados: {e}")
            return None
        finally:
            cursor.close()
            conexao.close()
    return None

# --- UPDATE (Atualizar) ---
def atualizar_cidade(ra_aluno, nova_cidade):
    """Atualiza a cidade. Retorna (True, mensagem_sucesso) ou (False, mensagem_erro)."""
    query = "UPDATE aluno SET cidade = %s WHERE RA = %s"
    
    conexao = conectar_bd()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(query, (nova_cidade, ra_aluno))
            conexao.commit()
            
            if cursor.rowcount == 0:
                return False, f"Nenhum aluno encontrado com o RA {ra_aluno}."
            else:
                return True, f"Cidade do aluno RA {ra_aluno} atualizada com sucesso."
        except Error as e:
            return False, f"Erro ao atualizar dados: {e}"
        finally:
            cursor.close()
            conexao.close()
    return False, "Falha ao conectar no banco de dados."

# --- DELETE (Deletar) ---
def deletar_cargo(cargo_id):
    query = "DELETE FROM cargo WHERE cargo_id = %s"
    conexao = conectar_bd()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(query, (cargo_id,))
            conexao.commit()

            if cursor.rowcount == 0:
                return False, f"Nenhum cargo encontrado com esse id {cargo_id}."
            else:
                return True, f"Cargo {cargo_id} foi deletado com sucesso."
        except Error as e:
            return False, f"Erro ao deletar dados: {e}"
        finally:
            cursor.close()
            conexao.close()
    return False, "Falha ao conectar no banco de dados."

# --- 3. Classe da Aplicação GUI (Tkinter) ---
# Importações necessárias para a GUI
import tkinter as tk
from tkinter import ttk  # 'themed tk' para widgets com aparência mais moderna
from tkinter import messagebox # Para caixas de diálogo (pop-ups) de informação, erro, aviso

class AplicacaoCRUD:
    
    # O método __init__ é o "construtor" da classe. 
    # É executado automaticamente quando um novo objeto AplicacaoCRUD é criado.
    # 'root' é a janela principal da aplicação, que é passada como argumento.
    def __init__(self, root):
        
        # --- Configuração da Janela Principal ---
        self.root = root 
        self.root.title("Gerenciador de Cragos (CRUD)")
        self.root.geometry("1000x600") 
        
        # self.nome_cargos = {}

        # --- Frame para os campos de entrada (Formulário) ---
        frame_formulario = ttk.LabelFrame(root, text="Formulário de Cargos")
        frame_formulario.pack(padx=10, pady=10, fill="x")
        
        # --- Widgets dentro do Frame do Formulário (usando .grid()) ---
        ttk.Label(frame_formulario, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_nome = ttk.Entry(frame_formulario, width=40)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="ID:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_id = ttk.Entry(frame_formulario)
        self.entry_id.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="Pode gerenciar estoque? (S/N): ").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.entry_gerencia = ttk.Entry(frame_formulario)
        self.entry_gerencia.grid(row=0, column=4, padx=5, pady=5)

        ttk.Label(frame_formulario, text="Pode fazer vendas? (S/N):").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.entry_venda = ttk.Entry(frame_formulario)
        self.entry_venda.grid(row=1, column=4, padx=5, pady=5)


        
        # --- Frame para os Botões ---
        
        frame_botoes = ttk.Frame(root)
        frame_botoes.pack(pady=5)

        self.btn_adicionar = ttk.Button(frame_botoes, text="Adicionar", command=self.adicionar_cargo_gui)
        self.btn_adicionar.grid(row=0, column=0, padx=5)
        
        self.btn_deletar = ttk.Button(frame_botoes, text="Deletar", command=self.deletar_cargo_gui)
        self.btn_deletar.grid(row=0, column=1, padx=5)

        # --- Frame para a Lista (Treeview) ---
        
        frame_lista = ttk.LabelFrame(root, text="Lista de Cargos")
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        colunas = ('ID', 'Nome', 'Pode Gerenciar Estoque?', 'Pode Fazer Vendas?')
        
        self.tree = ttk.Treeview(frame_lista, columns=colunas, show='headings')

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != 'Nome' else 200) 

        # --- Barra de Rolagem (Scrollbar) ---
        
        scrollbar = ttk.Scrollbar(frame_lista, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # --- Barra de Status ---
        self.status_label = ttk.Label(root, text="Bem-vindo! Clique em um aluno para selecioná-lo ou preencha os campos para adicionar.", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Carregar dados iniciais ---     
        self.atualizar_treeview()

    # --- Funções de Callback (Ações da GUI) ---

    def atualizar_treeview(self):
        """Limpa e recarrega a lista de cargos no Treeview."""
        
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        cargos = listar_cargos()
        if cargos:
            for cargo in cargos:
                self.tree.insert('', tk.END, values=(
                    cargo['cargo_id'],
                    cargo['cargo_nome'],
                    cargo['pode_gerenciar_estoque'],
                    cargo['pode_fazer_vendas'],
                ))

    def limpar_campos(self):
        """Limpa todos os campos de entrada do formulário."""
        self.entry_nome.delete(0, tk.END)
        self.entry_id.delete(0, tk.END)
        self.entry_gerencia.delete(0, tk.END)
        self.entry_venda.delete(0, tk.END)
        
        
        self.status_label.config(text="Campos limpos. Pronto para adicionar.")

    def on_tree_select(self, event):
        """Preenche os campos quando um item da lista é selecionado."""
        try:
            item_selecionado = self.tree.focus()
            
            if not item_selecionado:
                return
            valores = self.tree.item(item_selecionado, 'values')
            
            self.limpar_campos()
            
            self.entry_id.insert(0, valores[0])
            self.entry_nome.insert(0, valores[1])
            self.entry_gerencia.insert(0, valores[2])
            self.entry_venda.insert(0, valores[3])
            
            self.status_label.config(text=f"Cargo ID {valores[0]} selecionado.")
        except Exception as e:
            self.status_label.config(text=f"Erro ao selecionar: {e}")
    
    # def buscar_nome_por_id(self, id_cargo):
    #     return self.nome_cargos.get(id_cargo, None)

    def adicionar_cargo_gui(self):
        """Coleta dados dos campos e chama a função de inserir."""
        
        # 'get()': Pega o texto atual da caixa de entrada.
        # 'strip()': Remove espaços em branco do início e do fim.
        nome = self.entry_nome.get().strip()
        gerencia = self.entry_gerencia.get().strip().upper()
        venda = self.entry_venda.get().strip().upper()
        

        # Validação simples
        if not all([nome, gerencia, venda]):
            messagebox.showwarning("Campos Vazios", "Todos os campos (exceto ID) devem ser preenchidos.")
            return 
        
        if gerencia == "S":
            gerencia = 1
        elif gerencia == "N":
            gerencia = 0
        else:
            messagebox.showwarning("'Pode Gerenciar Estoque' só aceita os valores S e N.")
            return
            
        if venda == "S":
            venda = 1
        elif venda == "N":
            venda = 0
        else:
            messagebox.showwarning("'Pode Fazer Vendas' só aceita os valores S e N.")
            return       

        # Chama a função do CRUD (da Seção 2)
        sucesso, mensagem = inserir_cargo(nome, gerencia, venda)
        
        if sucesso:
            # 'messagebox.showinfo()': Exibe um pop-up de INFORMAÇÃO.
            messagebox.showinfo("Sucesso", mensagem)
            self.atualizar_treeview() # ATUALIZA a lista na tela
            self.limpar_campos()      # Limpa o formulário
        else:
            messagebox.showerror("Erro ao Adicionar", mensagem)
        
        # Atualiza a barra de status com o resultado.
        self.status_label.config(text=mensagem)

    # def atualizar_aluno_gui(self):
    #     """Coleta o RA e a nova cidade para atualizar."""
    #     ra_str = self.entry_ra.get().strip()
    #     nova_cidade = self.entry_cidade.get().strip()
        
    #     if not ra_str or not nova_cidade:
    #         messagebox.showwarning("Campos Faltando", "O 'RA' e a 'Cidade' devem ser preenchidos para atualizar.")
    #         return

    #     try:
    #         ra = int(ra_str)
    #     except ValueError:
    #         messagebox.showerror("RA Inválido", "O RA deve ser um número.")
    #         return
            
    #     # Chama a função do CRUD
    #     sucesso, mensagem = atualizar_cidade(ra, nova_cidade)

    #     if sucesso:
    #         messagebox.showinfo("Sucesso", mensagem)
    #         self.atualizar_treeview()
    #         self.limpar_campos()
    #     else:
    #         messagebox.showerror("Erro ao Atualizar", mensagem)
        
    #     self.status_label.config(text=mensagem)


    def deletar_cargo_gui(self):
        """Coleta o ID do campo e pede confirmação para deletar."""
        id_str = self.entry_id.get().strip()
        nome_cargo = self.entry_nome.get().strip()

        
        if not id_str:
            messagebox.showwarning("ID Faltando", "O campo 'ID' deve ser preenchido para deletar.")
            return

        try:
            id = int(id_str)
        except ValueError:
            messagebox.showerror("ID Inválido", "O ID deve ser um número.")
            return
        # nome_cargo = self.buscar_nome_por_id(id)

        # 'messagebox.askyesno()': Exibe um pop-up de SIM/NÃO.
        # Retorna True se o usuário clicar em "Sim" e False se clicar em "Não".
        if messagebox.askyesno("Confirmar Exclusão", f"Tem CERTEZA que deseja deletar o cargo: {id}?"):
            
            # Só executa se o usuário confirmou
            sucesso, mensagem = deletar_cargo(id)
            
            if sucesso:
                messagebox.showinfo("Sucesso", mensagem)
                self.atualizar_treeview()
                self.limpar_campos()
            else:
                messagebox.showerror("Erro ao Deletar", mensagem)
            
            self.status_label.config(text=mensagem)
        else:
            # Se o usuário clicou em "Não"
            self.status_label.config(text="Operação de exclusão cancelada.")


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
        app = AplicacaoCRUD(root)
        
        # 3. Inicia o "loop principal" (event loop) do Tkinter.
        #    O programa fica aqui, "escutando" por eventos (cliques,
        #    teclas, etc.) até que a janela seja fechada pelo usuário.
        root.mainloop()
    else:
        # Se a conexão inicial falhou, o programa nem abre a GUI
        # (a função conectar_bd() já mostrou o pop-up de erro).
        print("Erro fatal: Não foi possível conectar ao banco de dados.")
