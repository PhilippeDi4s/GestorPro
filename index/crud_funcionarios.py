from datetime import datetime
from config.config_bd import conectar_bd
from mysql.connector import Error
import re
import tkinter as tk
from tkinter import ttk  # 'themed tk' para widgets mais modernos
from tkinter import messagebox # Para pop-ups de confirmação e erro

# -----------------------------
# CONVERSORES DE DATA
# -----------------------------

def converter_para_mysql(data_br):
    try:
        return datetime.strptime(data_br, "%d/%m/%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None

def converter_para_br(data_mysql):
    try:
        return datetime.strptime(data_mysql, "%Y-%m-%d").strftime("%d/%m/%Y")
    except ValueError:
        return ""
        

# -----------------------------
# VALIDAÇÃO DE CPF
# -----------------------------

def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(i))
        digito = ((soma * 10) % 11) % 10
        if digito != int(cpf[i]):
            return False

    return True


# -----------------------------
# VALIDAÇÃO DE TELEFONE
# -----------------------------

def validar_telefone(telefone):
    telefone = ''.join(filter(str.isdigit, telefone))
    return 10 <= len(telefone) <= 11


# -----------------------------
# VALIDAÇÃO DE DATAS
# -----------------------------

def validar_datas(data_adm_br, data_term_br):
    data_adm = converter_para_mysql(data_adm_br)
    if not data_adm:
        return False, "Data de admissão inválida! Use o formato DD/MM/AAAA."

    if data_term_br:
        data_term = converter_para_mysql(data_term_br)
        if not data_term:
            return False, "Data de término inválida! Use o formato DD/MM/AAAA."

        if datetime.strptime(data_term, "%Y-%m-%d") < datetime.strptime(data_adm, "%Y-%m-%d"):
            return False, "A data de término não pode ser anterior à data de admissão."

    return True, ""

# -----------------------------
# VALIDAÇÃO DE NOME
# -----------------------------
def validar_nome(nome):
    """Valida nomes com acentos."""
    if len(nome.strip()) < 2:
        return False
    
    return all(c.isalpha() or c == " " for c in nome)

# -----------------------------
# VALIDAÇÃO DE EMAIL
# -----------------------------
def validar_email(email):
    """Valida um e-mail simples usando regex."""
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email) is not None

# -----------------------------
# VALIDAÇÃO DE SALÁRIO
# -----------------------------
def validar_salario(salario):
    # Aceitar vírgula como separador decimal
    if isinstance(salario, str):
        salario = salario.replace(",", ".")

    try:
        valor = float(salario)
        if valor <= 0:
            return False
        return True
    except ValueError:
        return False

# --- CREATE (Criar) ---
def inserir_funcionario(cargo_id, nome, email, cpf, telefone, data_admissao, data_termino, salario, ativo):

    # -------------------------
    # VALIDAR CPF
    # -------------------------
    if not validar_cpf(cpf):
        return False, "CPF inválido! Verifique e tente novamente."

    # -------------------------
    # VALIDAR TELEFONE
    # -------------------------
    if not validar_telefone(telefone):
        return False, "Telefone inválido! Deve ter 10 ou 11 dígitos."

    # -------------------------
    # VALIDAR NOME
    # -------------------------
    if not validar_nome(nome):
        return False, "Nome inválido! Digite apenas letras e espaços."

    # -------------------------
    # VALIDAR EMAIL
    # -------------------------
    if not validar_email(email):
        return False, "E-mail inválido! Exemplo válido: nome@dominio.com"
    
    # -------------------------
    # VALIDAR SALÁRIO
    # -------------------------
    if not validar_salario(salario):
        return False, "Salário inválido! Informe um valor numérico maior que zero."


    # -------------------------
    # VALIDAR DATAS
    # -------------------------
    ok, erro = validar_datas(data_admissao, data_termino)
    if not ok:
        return False, erro

    # Converter para formato MySQL
    data_admissao = converter_para_mysql(data_admissao)
    data_termino = converter_para_mysql(data_termino) if data_termino else None

    # -------------------------
    # QUERY
    # -------------------------
    query = """
        INSERT INTO funcionario 
        (cargo_id, nome, email, cpf, telefone, data_admissao, data_termino, salario, ativo) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    conexao = conectar_bd()
    if conexao:
        try:
            cursor = conexao.cursor()
            salario = float(str(salario).replace(",", "."))
            cursor.execute(query, (
                cargo_id, nome, email, cpf, telefone,
                data_admissao, data_termino, salario, ativo
            ))
            conexao.commit()

            return True, f"\n-> Funcionário '{nome}' adicionado com sucesso (ID: {cursor.lastrowid})."

        except Error as e:
            return False, f"Erro ao inserir dados: {e}"

        finally:
            cursor.close()
            conexao.close()

    return False, "Falha ao conectar no banco de dados."


# --- READ (Ler/Consultar) ---
def listar_funcionarios():
    query = "SELECT funcionario_id, cargo_id, nome, email, cpf, telefone, data_admissao, data_termino, salario, IF (ativo = 1, 'Sim', 'Não') AS ativo FROM funcionario"
    
    conexao = conectar_bd()
    if conexao:
        try:
            # dictionary=True faz o resultado vir como um dicionário (chave: valor)
            cursor = conexao.cursor(dictionary=True)
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados 
        except Error as e:
            messagebox.showerror("Erro de Leitura", f"Erro ao listar dados: {e}")
            return None
        finally:
            cursor.close()
            conexao.close()
    return None

# --- UPDATE (Atualizar) ---
def atualizar_funcionario(funcionario_id, novo_cargo_id, novo_nome, novo_email, novo_cpf,
                          novo_telefone, novo_data_admissao, novo_data_termino,
                          novo_salario, novo_ativo):

    # -------------------------
    # VALIDAR CAMPOS OPCIONAIS
    # -------------------------

    if novo_nome is not None and not validar_nome(novo_nome):
        return False, "Nome inválido! Use apenas letras e espaços."

    if novo_email is not None and not validar_email(novo_email):
        return False, "E-mail inválido! Exemplo: nome@dominio.com"

    if novo_cpf is not None and not validar_cpf(novo_cpf):
        return False, "CPF inválido! Verifique e tente novamente."

    if novo_telefone is not None and not validar_telefone(novo_telefone):
        return False, "Telefone inválido! Deve ter 10 ou 11 dígitos."
    
    if novo_salario is not None and not validar_salario(novo_salario):
        return False, "Salário inválido! Informe um valor numérico maior que zero."

    # -------------------------
    # VALIDAR DATAS (somente se o usuário enviou novas datas)
    # -------------------------
    if novo_data_admissao is not None or novo_data_termino is not None:

        ok, erro = validar_datas(novo_data_admissao or "", novo_data_termino or "")
        if not ok:
            return False, erro

        # Converter para MySQL
        if novo_data_admissao is not None:
            novo_data_admissao = converter_para_mysql(novo_data_admissao)

        if novo_data_termino:
            novo_data_termino = converter_para_mysql(novo_data_termino)


    conexao = conectar_bd()
    if not conexao:
        return False, "Falha ao conectar no banco de dados."

    try:
        cursor = conexao.cursor(dictionary=True)

        # 1) Buscar valores atuais
        cursor.execute("SELECT * FROM funcionario WHERE funcionario_id = %s", (funcionario_id,))
        funcionario_atual = cursor.fetchone()

        if not funcionario_atual:
            return False, f"Nenhum Funcionário encontrado com ID {funcionario_id}."

        # 2) Escolher valores finais
        cargo_final = funcionario_atual["cargo_id"] if novo_cargo_id is None else novo_cargo_id
        nome_final = funcionario_atual["nome"] if novo_nome is None else novo_nome
        email_final = funcionario_atual["email"] if novo_email is None else novo_email
        cpf_final = funcionario_atual["cpf"] if novo_cpf is None else novo_cpf
        telefone_final = funcionario_atual["telefone"] if novo_telefone is None else novo_telefone
        admissao_final = funcionario_atual["data_admissao"] if novo_data_admissao is None else novo_data_admissao
        termino_final = funcionario_atual["data_termino"] if novo_data_termino is None else novo_data_termino
        salario_final = funcionario_atual["salario"] if novo_salario is None else novo_salario
        ativo_final = funcionario_atual["ativo"] if novo_ativo is None else novo_ativo

        # 3) Executar UPDATE
        query = """
            UPDATE funcionario
            SET cargo_id = %s,
                nome = %s,
                email = %s,
                cpf = %s,
                telefone = %s,
                data_admissao = %s,
                data_termino = %s,
                salario = %s,
                ativo = %s
            WHERE funcionario_id = %s
        """

        params = (
            cargo_final,
            nome_final,
            email_final,
            cpf_final,
            telefone_final,
            admissao_final,
            termino_final,
            salario_final,
            ativo_final,
            funcionario_id
        )
        salario_final = float(str(salario_final).replace(",", "."))
        cursor.execute(query, params)
        conexao.commit()

        return True, f"Funcionário {nome_final} atualizado com sucesso."

    except Error as e:
        return False, f"Erro ao atualizar: {e}"

    finally:
        cursor.close()
        conexao.close()




# --- DELETE (Deletar) ---
def deletar_funcionario(funcionario_id):
    query = "DELETE FROM funcionario WHERE funcionario_id = %s"
    conexao = conectar_bd()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(query, (funcionario_id,))
            conexao.commit()

            if cursor.rowcount == 0:
                return False, f"Nenhum Funcionário encontrado com esse id {funcionario_id}."
            else:
                return True, f"Funcionário {funcionario_id} foi deletado com sucesso."
        except Error as e:
            return False, f"Erro ao deletar dados: {e}"
        finally:
            cursor.close()
            conexao.close()
    return False, "Falha ao conectar no banco de dados."

def relatorio_funcionarios_por_cargo():
    query = """
        SELECT c.cargo_nome AS cargo, COUNT(f.funcionario_id) AS quantidade
        FROM funcionario f
        JOIN cargo c ON f.cargo_id = c.cargo_id
        GROUP BY f.cargo_id
        ORDER BY quantidade DESC;
    """

    conexao = conectar_bd()
    if not conexao:
        return None

    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()

    except Error as e:
        print("Erro ao gerar relatório:", e)
        return None

    finally:
        cursor.close()
        conexao.close()


class JanelaFuncionarios:
    
    # O método __init__ é o "construtor" da classe. 
    # É executado automaticamente quando um novo objeto AplicacaoCRUD é criado.
    # 'root' é a janela principal da aplicação, que é passada como argumento.
    def __init__(self, master):
        
        # --- Configuração da Janela Principal ---
        self.root = tk.Toplevel(master) 
        self.root.title("Gerenciador de Funcionários (CRUD)")
        self.root.geometry("1000x600") 
        
        
        

        # --- Frame para os campos de entrada (Formulário) ---
        frame_formulario = ttk.LabelFrame(self.root, text="Formulário de Funcionários")
        frame_formulario.pack(padx=10, pady=10, fill="x")
        
        # --- Widgets dentro do Frame do Formulário (usando .grid()) ---
        ttk.Label(frame_formulario, text="Nome:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_nome = ttk.Entry(frame_formulario, width=40)
        self.entry_nome.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="ID Cargo:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_idCargo = ttk.Entry(frame_formulario)
        self.entry_idCargo.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="ID (p/Atualizar/Deletar):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_id = ttk.Entry(frame_formulario)
        self.entry_id.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="Email:").grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.entry_email = ttk.Entry(frame_formulario)
        self.entry_email.grid(row=0, column=4, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="CPF:").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        self.entry_cpf = ttk.Entry(frame_formulario)
        self.entry_cpf.grid(row=1, column=4, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="Telefone:").grid(row=2, column=3, padx=5, pady=5, sticky="w")
        self.entry_telefone = ttk.Entry(frame_formulario)
        self.entry_telefone.grid(row=2, column=4, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="Salário:").grid(row=0, column=6, padx=5, pady=5, sticky="w")
        self.entry_salario = ttk.Entry(frame_formulario)
        self.entry_salario.grid(row=0, column=7, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="Data Admissão dd/mm/aaaa:").grid(row=1, column=6, padx=5, pady=5, sticky="w")
        self.entry_admissao = ttk.Entry(frame_formulario)
        self.entry_admissao.grid(row=1, column=7, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="Data Término dd/mm/aaaa:").grid(row=2, column=6, padx=5, pady=5, sticky="w")
        self.entry_termino = ttk.Entry(frame_formulario)
        self.entry_termino.grid(row=2, column=7, padx=5, pady=5)
        
        ttk.Label(frame_formulario, text="Usuário está ativo? (S/N)").grid(row=0, column=8, padx=5, pady=5, sticky="w")
        self.entry_ativo = ttk.Entry(frame_formulario)
        self.entry_ativo.grid(row=0, column=9, padx=5, pady=5)

        


        
        # --- Frame para os Botões ---
        
        frame_botoes = ttk.Frame(self.root)
        frame_botoes.pack(pady=5)

        self.btn_adicionar = ttk.Button(frame_botoes, text="Adicionar", command=self.adicionar_funcionario_gui)
        self.btn_adicionar.grid(row=0, column=0, padx=5)
        
        self.btn_deletar = ttk.Button(frame_botoes, text="Deletar", command=self.deletar_funcionario_gui)
        self.btn_deletar.grid(row=0, column=1, padx=5)
        
        self.btn_atualizar = ttk.Button(frame_botoes, text="Atualizar", command=self.atualizar_funcionario_gui)
        self.btn_atualizar.grid(row=0, column=2, padx=5)
        
        self.btn_atualizar = ttk.Button(frame_botoes, text="Relatório", command=self.janela_relatorio_funcionarios)
        self.btn_atualizar.grid(row=0, column=3, padx=5)

        # --- Frame para a Lista (Treeview) ---
        
        frame_lista = ttk.LabelFrame(self.root, text="Lista de Funcionários")
        frame_lista.pack(padx=10, pady=10, fill="both", expand=True)

        colunas = ('ID', 'Cargo ID', 'Nome', 'Email', 'CPF', 'Telefone', 'Data Admissão', 'Data Término', 'Salário', 'Está ativo?')
        
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
        self.status_label = ttk.Label(self.root, text="Pronto.", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # --- Carregar dados iniciais ---     
        self.atualizar_treeview()

    # --- Funções de Callback (Ações da GUI) ---

    def atualizar_treeview(self):
        
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        funcionarios = listar_funcionarios()
        if funcionarios:
            for funcionario in funcionarios:
                self.tree.insert('', tk.END, values=(
                    funcionario['funcionario_id'],
                    funcionario['cargo_id'],
                    funcionario['nome'],
                    funcionario['email'],
                    funcionario['cpf'],
                    funcionario['telefone'],
                    funcionario['data_admissao'],
                    funcionario['data_termino'],
                    funcionario['salario'],
                    funcionario['ativo']
                ))

    def limpar_campos(self):
        """Limpa todos os campos de entrada do formulário."""
        self.entry_nome.delete(0, tk.END)
        self.entry_idCargo.delete(0, tk.END)
        self.entry_id.delete(0, tk.END)
        self.entry_telefone.delete(0, tk.END)
        self.entry_cpf.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        self.entry_admissao.delete(0, tk.END)
        self.entry_termino.delete(0, tk.END)
        self.entry_salario.delete(0, tk.END)
        self.entry_ativo.delete(0, tk.END)
        
        
    def on_tree_select(self, event):
        """Preenche os campos quando um item da lista é selecionado."""
        try:
            item_selecionado = self.tree.focus()
            
            if not item_selecionado:
                return
            valores = self.tree.item(item_selecionado, 'values')
            
            self.limpar_campos()
            
            self.entry_id.insert(0, valores[0])
            self.entry_idCargo.insert(0, valores[1])
            self.entry_nome.insert(0, valores[2])
            self.entry_email.insert(0, valores[3])
            self.entry_cpf.insert(0, valores[4])
            self.entry_telefone.insert(0, valores[5])
            self.entry_admissao.insert(0, valores[6])
            self.entry_termino.insert(0, valores[7])
            self.entry_salario.insert(0, valores[8])
            self.entry_ativo.insert(0, valores[9])
            
            self.status_label.config(text=f"Funcionário ID {valores[0]} selecionado.")
        except Exception as e:
            self.status_label.config(text=f"Erro ao selecionar: {e}")
    
    # def buscar_nome_por_id(self, id_cargo):
    #     return self.nome_cargos.get(id_cargo, None)

    def adicionar_funcionario_gui(self):
        """Coleta dados dos campos e chama a função de inserir."""
        
        # 'get()': Pega o texto atual da caixa de entrada.
        # 'strip()': Remove espaços em branco do início e do fim.
        id_cargo = self.entry_idCargo.get().strip()
        nome = self.entry_nome.get().strip()
        email = self.entry_email.get().strip()
        cpf = self.entry_cpf.get().strip()
        telefone = self.entry_telefone.get().strip()
        admissao = self.entry_admissao.get().strip()
        termino = self.entry_termino.get().strip()
        salario = self.entry_salario.get().strip()
        ativo = self.entry_ativo.get().strip().upper()
        

        # Validação simples
        if not all([id_cargo, nome, email, cpf, telefone, admissao, salario, ativo]):
            messagebox.showwarning("Campos Vazios", "Todos os campos (exceto ID) devem ser preenchidos.")
            return 
        
        if ativo == "S" or ativo == "SIM":
            ativo = 1
        elif ativo == "N" or ativo == "NÃO" or ativo == "NAO":
            ativo = 0
        else:
            messagebox.showwarning("Valor incorreto","'Ativo' só aceita os valores S/N ou Sim/Não")
            return

        # Chama a função do CRUD (da Seção 2)
        sucesso, mensagem = inserir_funcionario(id_cargo, nome, email, cpf, telefone, admissao, termino, salario, ativo)
        
        if sucesso:
            # 'messagebox.showinfo()': Exibe um pop-up de INFORMAÇÃO.
            messagebox.showinfo("Sucesso", mensagem)
            self.atualizar_treeview() # ATUALIZA a lista na tela
            self.limpar_campos()      # Limpa o formulário
        else:
            messagebox.showerror("Erro ao Adicionar", mensagem)
        
        # Atualiza a barra de status com o resultado.
        self.status_label.config(text=mensagem)
        
        
    def atualizar_funcionario_gui(self):
        try:
            funcionario_id = int(self.entry_id.get().strip())
        except ValueError:
            messagebox.showerror("Erro", "O ID deve ser um número inteiro.")
            return
        
        novo_idCargo = self.entry_idCargo.get().strip()
        novo_nome = self.entry_nome.get().strip()
        novo_email = self.entry_email.get().strip()
        novo_cpf = self.entry_cpf.get().strip()
        novo_telefone = self.entry_telefone.get().strip()
        novo_admissao = self.entry_admissao.get().strip()
        novo_termino = self.entry_termino.get().strip()
        novo_salario = self.entry_salario.get().strip()
        novo_ativo = self.entry_ativo.get().strip().upper()


        # ---- Cargo ID ----
        if novo_idCargo == "":
            novo_idCargo = None
        else:
            try:
                novo_idCargo = int(novo_idCargo)
            except ValueError:
                messagebox.showerror("Erro", "O ID do cargo deve ser numérico.")
                return

        # ---- Nome ----
        if novo_nome == "":
            novo_nome = None

        # ---- Email ----
        if novo_email == "":
            novo_email = None

        # ---- CPF ----
        if novo_cpf == "":
            novo_cpf = None

        # ---- Telefone ----
        if novo_telefone == "":
            novo_telefone = None

        # ---- Data de Admissão ----
        if novo_admissao == "":
            novo_admissao = None  # mantém no BD
        else:
            # opcional: validar formato YYYY-MM-DD
            try:
                str(novo_admissao)
            except:
                messagebox.showerror("Erro", "Data de admissão inválida.")
                return

        # ---- Data de Término ----
        if novo_termino == "":
            novo_termino = None
        else:
            try:
                str(novo_termino)
            except:
                messagebox.showerror("Erro", "Data de término inválida.")
                return

        # ---- Salário ----
        if novo_salario == "":
            novo_salario = None
        else:
            try:
                novo_salario = float(novo_salario)
            except ValueError:
                messagebox.showerror("Erro", "O salário deve ser numérico.")
                return

        # ---- Ativo (S/N ou 1/0) ----
        if novo_ativo == "":
            novo_ativo = None
        elif novo_ativo in ("S", "SIM", "1"):
            novo_ativo = 1
        elif novo_ativo in ("N", "NAO", "NÃO", "0"):
            novo_ativo = 0
        else:
            messagebox.showerror("Erro", "Campo 'Ativo' deve ser S/N ou 1/0.")
            return

        # ---- Chama a função de atualização real ----
        sucesso, mensagem = atualizar_funcionario(
            funcionario_id,
            novo_idCargo,
            novo_nome,
            novo_email,
            novo_cpf,
            novo_telefone,
            novo_admissao,
            novo_termino,
            novo_salario,
            novo_ativo
        )

        # ---- Retorno para o usuário ----
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            self.atualizar_treeview()
            self.limpar_campos()
        else:
            messagebox.showerror("Erro", mensagem)


    def deletar_funcionario_gui(self):
        """Coleta o ID do campo e pede confirmação para deletar."""
        id_str = self.entry_id.get().strip()

        
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
        if messagebox.askyesno("Confirmar Exclusão", f"Tem CERTEZA que deseja deletar o Funcionário: {id}?"):
            
            # Só executa se o usuário confirmou
            sucesso, mensagem = deletar_funcionario(id)
            
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
    def janela_relatorio_funcionarios(self):
        dados = relatorio_funcionarios_por_cargo()

        if not dados:
            messagebox.showerror("Erro", "Não foi possível gerar o relatório.")
            return

        janela = tk.Toplevel(self.root)
        janela.title("Relatório: Funcionários por Cargo")
        janela.geometry("450x400")

        frame = ttk.LabelFrame(janela, text="Funcionários por Cargo")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        colunas = ("Cargo", "Quantidade")

        tree = ttk.Treeview(frame, columns=colunas, show="headings")
        tree.heading("Cargo", text="Cargo")
        tree.heading("Quantidade", text="Quantidade")

        tree.column("Cargo", width=250)
        tree.column("Quantidade", width=120, anchor="center")

        tree.pack(fill="both", expand=True)

        for linha in dados:
            tree.insert("", tk.END, values=(linha["cargo"], linha["quantidade"]))




 