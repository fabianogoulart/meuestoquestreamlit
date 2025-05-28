import streamlit as st
import pandas as pd
from datetime import datetime
import json
import os

class SistemaEstoque:
    def __init__(self):
        self.caminho_arquivo = "estoque.json"
        self.carregar_dados()

    def carregar_dados(self):
        if os.path.exists(self.caminho_arquivo):
            with open(self.caminho_arquivo, 'r') as arquivo:
                self.estoque = json.load(arquivo)
        else:
            self.estoque = []

    def salvar_dados(self):
        with open(self.caminho_arquivo, 'w') as arquivo:
            json.dump(self.estoque, arquivo)

    def adicionar_item(self, codigo, nome, quantidade, preco, estoque_minimo):
        item = {
            'codigo': codigo,
            'nome': nome,
            'quantidade': quantidade,
            'preco': preco,
            'estoque_minimo': estoque_minimo,
            'ultima_atualizacao': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.estoque.append(item)
        self.salvar_dados()

    def atualizar_quantidade(self, codigo, alteracao_quantidade):
        for item in self.estoque:
            if item['codigo'] == codigo:
                item['quantidade'] += alteracao_quantidade
                item['ultima_atualizacao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.salvar_dados()
                return True
        return False

    def remover_item_por_codigo(self, codigo):
        antes = len(self.estoque)
        self.estoque = [item for item in self.estoque if item['codigo'] != codigo]
        self.salvar_dados()
        return len(self.estoque) < antes

    def remover_item_por_nome(self, nome):
        antes = len(self.estoque)
        self.estoque = [item for item in self.estoque if item['nome'] != nome]
        self.salvar_dados()
        return len(self.estoque) < antes

def main():
    st.set_page_config(page_title="Sistema de Controle de Estoque", layout="wide")
    
    sistema = SistemaEstoque()
    
    st.title("Sistema de Controle de Estoque")
    
    menu = st.sidebar.selectbox(
        "Menu",
        ["Cadastrar Produto", "Movimento de Estoque", "Visualizar Estoque", "Remover Produto"]
    )
    
    if menu == "Cadastrar Produto":
        st.header("Cadastrar Novo Produto")
        
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código do Produto")
            nome = st.text_input("Nome do Produto")
            quantidade = st.number_input("Quantidade Inicial", min_value=0)
        
        with col2:
            preco = st.number_input("Preço Unitário", min_value=0.0)
            estoque_minimo = st.number_input("Estoque Mínimo", min_value=0)
        
        if st.button("Cadastrar"):
            if codigo and nome:
                sistema.adicionar_item(codigo, nome, quantidade, preco, estoque_minimo)
                st.success("Produto cadastrado com sucesso!")
            else:
                st.error("Preencha todos os campos obrigatórios!")

    elif menu == "Movimento de Estoque":
        st.header("Movimento de Estoque")
        
        itens = pd.DataFrame(sistema.estoque)
        if not itens.empty:
            codigo_selecionado = st.selectbox("Selecione o Produto", itens['codigo'].tolist())
            operacao = st.radio("Operação", ["Entrada", "Saída"])
            quantidade = st.number_input("Quantidade", min_value=1)
            
            if st.button("Confirmar Movimento"):
                alteracao_quantidade = quantidade if operacao == "Entrada" else -quantidade
                if sistema.atualizar_quantidade(codigo_selecionado, alteracao_quantidade):
                    st.success("Movimento registrado com sucesso!")
                else:
                    st.error("Erro ao atualizar estoque!")
        else:
            st.warning("Nenhum produto cadastrado!")

    elif menu == "Remover Produto":
        st.header("Remover Produto")
        
        if sistema.estoque:
            df = pd.DataFrame(sistema.estoque)
            metodo = st.radio("Remover por:", ["Código", "Nome"])
            
            if metodo == "Código":
                codigo_remover = st.selectbox("Selecione o código do produto", df['codigo'].tolist())
                if st.button("Remover"):
                    if sistema.remover_item_por_codigo(codigo_remover):
                        st.success("Produto removido com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao remover produto!")
            else:
                nome_remover = st.selectbox("Selecione o nome do produto", df['nome'].tolist())
                if st.button("Remover"):
                    if sistema.remover_item_por_nome(nome_remover):
                        st.success("Produto removido com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao remover produto!")
        else:
            st.warning("Nenhum produto cadastrado!")

    else:  # Visualizar Estoque
        st.header("Estoque Atual")
        
        if sistema.estoque:
            df = pd.DataFrame(sistema.estoque)
            
            # Alertas de estoque baixo
            estoque_baixo = df[df['quantidade'] <= df['estoque_minimo']]
            if not estoque_baixo.empty:
                st.warning("Produtos com estoque baixo:")
                st.dataframe(estoque_baixo[['codigo', 'nome', 'quantidade', 'estoque_minimo']])
            
            # Valor total do estoque
            valor_total = (df['quantidade'] * df['preco']).sum()
            st.metric("Valor Total do Estoque", f"R$ {valor_total:.2f}")
            
            # Tabela completa
            st.subheader("Lista de Produtos")
            st.dataframe(df)
        else:
            st.info("Nenhum produto cadastrado no sistema!")

if __name__ == "__main__":
    main()