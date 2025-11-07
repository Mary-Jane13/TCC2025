# main.py

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from model import Catalogo
import gui 


def selecionar_arquivos():
    root = tk.Tk()
    root.withdraw()  # Esconde a janela principal
    
    print("Selecione o arquivo XML do catálogo...")
    caminho_xml = filedialog.askopenfilename(
        title="Selecione o arquivo XML do catálogo",
        filetypes=[("Arquivos XML", "*.xml"), ("Todos os arquivos", "*.*")]
    )
    
    if not caminho_xml:
        print("Nenhum arquivo XML selecionado. Encerrando.")
        return None, None
    
    print("Selecione o arquivo CSV com os dados dos alunos...")
    caminho_csv = filedialog.askopenfilename(
        title="Selecione o arquivo CSV com os dados dos alunos",
        filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")]
    )
    
    if not caminho_csv:
        print("Nenhum arquivo CSV selecionado. Encerrando.")
        return None, None
    
    root.destroy()
    return caminho_xml, caminho_csv


def main():
    print("=== Sistema de Visualização de Históricos Curriculares ===")
    
    # --- 1. Seleção dos arquivos via interface gráfica ---
    caminho_xml, caminho_csv = selecionar_arquivos()
    
    if not caminho_xml or not caminho_csv:
        return

    # Verifica se os arquivos existem
    if not (os.path.exists(caminho_xml) and os.path.exists(caminho_csv)):
        print(f"Erro: Não foi possível encontrar os arquivos selecionados.")
        input("Pressione Enter para sair.")
        return

    # --- 2. Carregamento dos dados ---
    print(f"\nCarregando dados...")
    print(f"XML: {os.path.basename(caminho_xml)}")
    print(f"CSV: {os.path.basename(caminho_csv)}")
    
    catalogo = Catalogo()
    catalogo.carregar_dados(caminho_xml, caminho_csv)
    
    print("\n--- Resumo da Carga ---")
    print(catalogo)  # Mostra o __repr__ do catálogo
    print("-------------------------")
    print("Iniciando a interface gráfica...")

    # --- 3. Iniciar a Aplicação Gráfica ---
    # Extrai apenas o nome do arquivo para passar para a GUI
    nome_xml = os.path.basename(caminho_xml)
    
    app = gui.App(catalogo, nome_xml)
    
    app.mainloop()
    
    print("Aplicação gráfica fechada. Programa encerrado.")


if __name__ == '__main__':
    main()
