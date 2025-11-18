-- Improved schema for management & sales app
-- Created: 2025-11-11
CREATE SCHEMA IF NOT EXISTS `mydb` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `mydb`;

CREATE DATABASE GestorPro_BD;
USE GestorPro_BD;

-- -------------------------------
-- Table: cargo (roles)
-- -------------------------------
CREATE TABLE IF NOT EXISTS cargo (
  cargo_id INT NOT NULL AUTO_INCREMENT,
  cargo_nome VARCHAR(45) NOT NULL,
  pode_gerenciar_estoque TINYINT(1) NOT NULL DEFAULT 0,
  pode_fazer_vendas TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (cargo_id),
  UNIQUE KEY uk_cargo_nome (cargo_nome)
) ENGINE=InnoDB;

-- -------------------------------
-- Table: funcionario (employees)
-- -------------------------------
CREATE TABLE IF NOT EXISTS funcionario (
  funcionario_id INT NOT NULL AUTO_INCREMENT,
  cargo_id INT NOT NULL,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL,
  cpf VARCHAR(20) NOT NULL,
  telefone VARCHAR(20) NULL,
  data_admissao DATE NOT NULL,
  data_termino DATE NULL,
  salario DECIMAL(10,2) NULL,
  ativo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (funcionario_id),
  UNIQUE KEY uk_funcionario_cpf (cpf),
  UNIQUE KEY uk_funcionario_email (email),
  INDEX idx_funcionario_cargo (cargo_id),
  CONSTRAINT fk_funcionario_cargo FOREIGN KEY (cargo_id)
    REFERENCES cargo (cargo_id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -------------------------------
-- Table: usuario (authentication / app users)
-- -------------------------------
CREATE TABLE IF NOT EXISTS usuario (
  usuario_id INT NOT NULL AUTO_INCREMENT,
  funcionario_id INT NOT NULL,
  login VARCHAR(50) NOT NULL,
  senha_hash VARCHAR(255) NOT NULL,
  criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  ativo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (usuario_id),
  UNIQUE KEY uk_usuario_login (login),
  UNIQUE KEY uk_usuario_funcionario (funcionario_id),
  CONSTRAINT fk_usuario_funcionario FOREIGN KEY (funcionario_id)
    REFERENCES funcionario (funcionario_id)
    ON UPDATE RESTRICT
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- -------------------------------
-- Table: estoque (warehouses / storages)
-- -------------------------------
CREATE TABLE IF NOT EXISTS estoque (
  estoque_id INT NOT NULL AUTO_INCREMENT,
  descricao VARCHAR(100) NOT NULL,
  tipo_estoque VARCHAR(45) NULL,
  capacidade_maxima INT NULL,
  PRIMARY KEY (estoque_id)
) ENGINE=InnoDB;

-- -------------------------------
-- Table: gerencia_estoque (history of stock managers)
-- -------------------------------
CREATE TABLE IF NOT EXISTS gerencia_estoque (
  gerencia_id INT NOT NULL AUTO_INCREMENT,
  estoque_id INT NOT NULL,
  funcionario_id INT NOT NULL,
  data_inicio DATE NOT NULL,
  data_fim DATE NULL,
  papel ENUM('responsavel','assistente') NOT NULL DEFAULT 'responsavel',
  ativo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (gerencia_id),
  INDEX idx_gest_estoque_estoque (estoque_id),
  INDEX idx_gest_estoque_func (funcionario_id),
  CONSTRAINT fk_gest_estoque_estoque FOREIGN KEY (estoque_id)
    REFERENCES estoque (estoque_id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT,
  CONSTRAINT fk_gest_estoque_funcionario FOREIGN KEY (funcionario_id)
    REFERENCES funcionario (funcionario_id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -------------------------------
-- Table: categoria (product categories)
-- -------------------------------
CREATE TABLE IF NOT EXISTS categoria (
  categoria_id INT NOT NULL AUTO_INCREMENT,
  categoria_nome VARCHAR(80) NULL,
  categoria_descricao VARCHAR(255) NULL,
  PRIMARY KEY (categoria_id),
  UNIQUE KEY uk_categoria_nome (categoria_nome)
) ENGINE=InnoDB;

-- -------------------------------
-- Table: produto (products)
-- -------------------------------
CREATE TABLE IF NOT EXISTS produto (
  produto_id INT NOT NULL AUTO_INCREMENT,
  categoria_id INT NULL,
  sku VARCHAR(50) NULL, 			#código alfanumérico único que cada empresa cria para identificar e gerenciar seus produtos internamente
  nome VARCHAR(150) NOT NULL,
  descricao TEXT NULL,				#Up to 65,535 characters 
  preco_venda DECIMAL(10,2) NOT NULL,
  custo_medio DECIMAL(10,2) NULL,
  peso DECIMAL(10,3) NULL,
  ativo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (produto_id),
  UNIQUE KEY uk_produto_sku (sku),
  INDEX idx_produto_categoria (categoria_id),
  CONSTRAINT fk_produto_categoria FOREIGN KEY (categoria_id)
    REFERENCES categoria (categoria_id)
    ON UPDATE RESTRICT
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- -------------------------------
-- Table: especificacao (product specifications)
-- -------------------------------
CREATE TABLE IF NOT EXISTS especificacao (
  especificacao_id INT NOT NULL AUTO_INCREMENT,
  produto_id INT NOT NULL,
  nome_atributo VARCHAR(100) NULL,				#Cor, volume, diâmetro, material, etc
  valor_atributo VARCHAR(100) NULL,				#Branco, 18, 50, etc
  unidade_medida VARCHAR(45) NULL,				#L, mm, m, etc
  PRIMARY KEY (especificacao_id),
  INDEX idx_espec_produto (produto_id),
  CONSTRAINT fk_especificacao_produto FOREIGN KEY (produto_id)
    REFERENCES produto (produto_id)
    ON UPDATE RESTRICT
    ON DELETE CASCADE
) ENGINE=InnoDB;

-- -------------------------------
-- Table: fornecedor (suppliers)
-- -------------------------------
CREATE TABLE IF NOT EXISTS fornecedor (
  fornecedor_id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(150) NOT NULL,
  telefone VARCHAR(20) NULL,
  cnpj VARCHAR(20) NULL,
  email VARCHAR(100) NULL,
  endereco VARCHAR(255) NULL,
  descricao TEXT NULL,
  PRIMARY KEY (fornecedor_id),
  UNIQUE KEY uk_fornecedor_cnpj (cnpj),
  UNIQUE KEY uk_fornecedor_email (email)
) ENGINE=InnoDB;

-- -------------------------------
-- Table: fornecedor_produto (supplier - product)
-- -------------------------------
CREATE TABLE IF NOT EXISTS fornecedor_produto (
  fornecedor_id INT NOT NULL,
  produto_id INT NOT NULL,
  unidade_compra VARCHAR(45) NULL,	#Caixa, peça, pacote, KIT, etc
  custo_unitario DECIMAL(10,2) NOT NULL,
  data_ultimo_custo DATE NOT NULL DEFAULT (CURRENT_DATE),
  PRIMARY KEY (fornecedor_id, produto_id),
  INDEX idx_fornecedor_produto_produto (produto_id),
  INDEX idx_fornecedor_produto_fornecedor (fornecedor_id),
  CONSTRAINT fk_fornecedor_produto_fornecedor FOREIGN KEY (fornecedor_id)
    REFERENCES fornecedor (fornecedor_id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT,
  CONSTRAINT fk_fornecedor_produto_produto FOREIGN KEY (produto_id)
    REFERENCES produto (produto_id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -------------------------------
-- Table: lote (batches)
-- -------------------------------
CREATE TABLE IF NOT EXISTS lote (
  lote_id INT NOT NULL AUTO_INCREMENT,
  estoque_id INT NOT NULL,
  produto_id INT NOT NULL,
  data_aquisicao DATE NOT NULL,
  quantidade_inicial INT NOT NULL,
  quantidade_atual INT NOT NULL,
  observacoes VARCHAR(255) NULL,
  PRIMARY KEY (lote_id),
  INDEX idx_lote_estoque (estoque_id),
  INDEX idx_lote_produto (produto_id),
  CONSTRAINT fk_lote_estoque FOREIGN KEY (estoque_id)
    REFERENCES estoque (estoque_id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT,
  CONSTRAINT fk_lote_produto FOREIGN KEY (produto_id)
    REFERENCES produto (produto_id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT
) ENGINE=InnoDB;

-- -------------------------------
-- Table: movimentacao_estoque (stock movements)
-- -------------------------------
CREATE TABLE IF NOT EXISTS movimentacao_estoque (
  movimentacao_id INT NOT NULL AUTO_INCREMENT,
  lote_id INT NOT NULL,
  tipo ENUM('entrada','saida','ajuste','perda','devolucao') NOT NULL,
  quantidade INT NOT NULL,
  motivo VARCHAR(255) NULL,
  data_movimentacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  funcionario_id INT NULL,
  PRIMARY KEY (movimentacao_id),
  INDEX idx_mov_lote (lote_id),
  INDEX idx_mov_func (funcionario_id),
  CONSTRAINT fk_mov_lote FOREIGN KEY (lote_id)
    REFERENCES lote (lote_id)
    ON UPDATE RESTRICT
    ON DELETE RESTRICT,
  CONSTRAINT fk_mov_func FOREIGN KEY (funcionario_id)
    REFERENCES funcionario (funcionario_id)
    ON UPDATE RESTRICT
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- =====================================================
-- TABELA PRINCIPAL DE VENDAS
-- =====================================================
CREATE TABLE venda (											#É a venda “viva”, ainda sendo processada.
  venda_id INT AUTO_INCREMENT PRIMARY KEY,
  funcionario_id INT NOT NULL,
  metodo_pagamento ENUM('DINHEIRO','CARTAO','PIX','OUTRO') NOT NULL,
  total_venda DECIMAL(10,2) NOT NULL,
  data_venda DATETIME DEFAULT CURRENT_TIMESTAMP,
  status ENUM('ABERTA','CONCLUIDA','CANCELADA') DEFAULT 'ABERTA',
  CONSTRAINT fk_venda_funcionario FOREIGN KEY (funcionario_id)
    REFERENCES funcionario(funcionario_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

-- =====================================================
-- ITENS DA VENDA
-- =====================================================
CREATE TABLE venda_item (										#Os produtos que o funcionário adiciona à venda.
  venda_item_id INT AUTO_INCREMENT PRIMARY KEY,
  venda_id INT NOT NULL,
  produto_id INT NOT NULL,
  quantidade INT NOT NULL,
  preco_unitario DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_venda_item_venda FOREIGN KEY (venda_id)
    REFERENCES venda(venda_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_venda_item_produto FOREIGN KEY (produto_id)
    REFERENCES produto(produto_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

-- =====================================================
-- HISTÓRICO DE VENDAS (CABEÇALHO)
-- =====================================================
CREATE TABLE historico_venda (									#Uma CÓPIA da venda quando ela é concluída ou cancelada.
  historico_id INT AUTO_INCREMENT PRIMARY KEY,
  venda_id INT NOT NULL,
  funcionario_id INT NOT NULL,
  metodo_pagamento ENUM('DINHEIRO','CARTAO','PIX','OUTRO') NOT NULL,
  total_venda DECIMAL(10,2) NOT NULL,
  data_venda DATETIME NOT NULL,
  data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
  status ENUM('CONCLUIDA','CANCELADA') NOT NULL,
  CONSTRAINT fk_historico_venda_funcionario FOREIGN KEY (funcionario_id)
    REFERENCES funcionario(funcionario_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;

-- =====================================================
-- HISTÓRICO DE ITENS DA VENDA
-- =====================================================
CREATE TABLE historico_venda_item (
  historico_item_id INT AUTO_INCREMENT PRIMARY KEY,
  historico_venda_id INT NOT NULL,
  produto_id INT NOT NULL,
  quantidade INT NOT NULL,
  preco_unitario DECIMAL(10,2) NOT NULL,
  subtotal DECIMAL(10,2) NOT NULL,
  CONSTRAINT fk_hist_item_hist_venda FOREIGN KEY (historico_venda_id)
    REFERENCES historico_venda(historico_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_hist_item_produto FOREIGN KEY (produto_id)
    REFERENCES produto(produto_id)
    ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE = InnoDB;