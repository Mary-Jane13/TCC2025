# gui.py

import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import FancyBboxPatch 
from matplotlib.figure import Figure
import numpy as np
import viz 
import os
from model import Disciplina

class App(tk.Tk):
    #Classe principal da aplicação, que herda de tk.Tk (a janela principal).
    def __init__(self, catalogo, nome_arquivo_xml):
        super().__init__()
        
        self.catalogo = catalogo
        self.nome_arquivo_xml = nome_arquivo_xml
        self.grafo_curso = None # Armazena o grafo

        self.title("Visualizador de Históricos Curriculares (TCC)")
        self.geometry("1600x900")

        try:
            self.state('zoomed')
        except tk.TclError:
            print("Não foi possível maximizar a janela.")

        # Estilo para o label de nome de disciplina (para quebra de linha)
        style = ttk.Style(self)
        style.configure('Wrappable.TLabel', wraplength=280)
        style.configure('Italic.TLabel', font=('Arial', 10, 'italic'))

        self.create_widgets()

    def create_widgets(self):
        #Cria e organiza todos os widgets na janela.
        
        # Frame principal
        # Divide a janela em duas partes: sidebar à direita, grafo à esquerda
        main_frame = ttk.Frame(self)
        main_frame.pack(side="top", fill="both", expand=True)

        # A barra lateral
        # Criada com widgets Tkinter reais
        self.sidebar_frame = ttk.Frame(main_frame, width=300, padding=10, relief="sunken")
        self.sidebar_frame.pack(side="right", fill="y")
        self.sidebar_frame.pack_propagate(False) 

        # O CONTEUDO DA BARRA LATERAL AQUII
        
        # Título
        ttk.Label(self.sidebar_frame, text="Informações", font=("Arial", 16, "bold")).pack(pady=5, anchor="w")

        # CATALOGO
        ttk.Label(self.sidebar_frame, text=f"Catálogo:", font=("Arial", 11, "bold")).pack(pady=(10, 0), anchor="w")
        ttk.Label(self.sidebar_frame, text=f"{self.nome_arquivo_xml}", foreground="darkblue", style='Italic.TLabel').pack(anchor="w")

        # estatisticas
        print("GUI: Gerando grafo do catálogo...")
        self.grafo_curso = viz.criar_grafo_do_catalogo(self.catalogo)
        
        ttk.Label(self.sidebar_frame, text="Estatísticas:", font=("Arial", 11, "bold")).pack(pady=(20, 0), anchor="w")
        ttk.Label(self.sidebar_frame, text=f"Disciplinas: {len(self.grafo_curso.nodes())}").pack(anchor="w")

        # Separador
        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", pady=20)

        # info das disciplinas (inetrativo)
        ttk.Label(self.sidebar_frame, text="Disciplina Selecionada:", font=("Arial", 11, "bold")).pack(anchor="w")
        
        # Armazenar referências a estes labels pra poder atualizá-los
        self.lbl_nome_disciplina = ttk.Label(self.sidebar_frame, text="Nenhuma", font=("Arial", 10, "bold"), style='Wrappable.TLabel')
        self.lbl_nome_disciplina.pack(pady=5, anchor="w")
        
        self.lbl_id_disciplina = ttk.Label(self.sidebar_frame, text="ID: N/A")
        self.lbl_id_disciplina.pack(anchor="w")
        
        self.lbl_creditos_disciplina = ttk.Label(self.sidebar_frame, text="Créditos: N/A")
        self.lbl_creditos_disciplina.pack(anchor="w")
        
        # Separador
        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", pady=20)
        
        # legenda mapa de calor
        self.create_heatmap_legend()

        # O FRAME DO GRAFO AQUII
        graph_frame = ttk.Frame(main_frame)
        graph_frame.pack(side="left", fill="both", expand=True)

        # GERAR FIGURA COM O MATPLOTLIB
        figura_matplotlib = viz.desenhar_grafo_em_camadas(self.grafo_curso, self.catalogo)
        print("GUI: Figura do grafo gerada.")

        # Embutir a Figura no Canvas do tkinter
        self.canvas = FigureCanvasTkAgg(figura_matplotlib, master=graph_frame)
        self.canvas.draw()
        
        # dicionar a Barra de Ferramentas do Matplotlib
        toolbar = NavigationToolbar2Tk(self.canvas, graph_frame)
        toolbar.update()
        toolbar.pack(side="top", fill="x")
        
        # poicinar o Canvas
        widget_canvas = self.canvas.get_tk_widget()
        widget_canvas.pack(side="top", fill="both", expand=True)

        #conectar o evento de clique
        self.canvas.mpl_connect('pick_event', self.on_pick)

    def create_heatmap_legend(self):
        #Cria a legenda do mapa de calor na barra lateral.
        ttk.Label(self.sidebar_frame, text="Mapa de Calor:", font=("Arial", 11, "bold")).pack(pady=(0, 5), anchor="w")
        
        # Cria um novo Figure e Canvas do Matplotlib SÓ para a legenda
        fig_legenda = Figure(figsize=(2.8, 0.6), dpi=100)
        fig_legenda.set_facecolor('#f0f0f0') # Cor de fundo do Tkinter
        ax_legenda = fig_legenda.add_subplot(111)
        ax_legenda.axis('off') # Remove eixos
        
        notas_legenda = np.linspace(0, 10, 6)
        cores_legenda = [viz.map_nota_para_cor(n) for n in notas_legenda]

        for i, (nota, cor) in enumerate(zip(notas_legenda, cores_legenda)):
            x_pos = 0.05 + (i * 0.15)
            ax_legenda.add_patch(FancyBboxPatch(
                (x_pos, 0.4), 0.1, 0.4,
                boxstyle="round,pad=0.01", facecolor=cor, edgecolor='black', linewidth=0.5
            ))
            # Desenha o texto da nota
            ax_legenda.text(x_pos + 0.05, 0.2, f"{nota:.1f}", 
                            ha='center', va='top', fontsize=9)

        # Embuti o canvas da legenda na barra lateral
        canvas_legenda = FigureCanvasTkAgg(fig_legenda, master=self.sidebar_frame)
        canvas_legenda.draw()
        canvas_legenda.get_tk_widget().pack(fill="x", anchor="w")
    


    def on_pick(self, event):
        """
        a função é chamada sempre que um item "clicável" (picker=True)
        no canvas do Matplotlib é clicado.
        """
        artist = event.artist
        node_id = artist.get_gid() # Pega o ID

        if node_id:
            print(f"Clique detectado no nó: {node_id}")
            disciplina = self.catalogo.get_disciplina(node_id)
            if disciplina:
                # Chama a função para atualizar a barra lateral
                self.update_sidebar(disciplina)
            else:
                print(f"Erro: Nó {node_id} clicado, mas não encontrado no catálogo.")

    def update_sidebar(self, disciplina: Disciplina):
        # Atualiza os labels na barra lateral com as informações da disciplina.
        self.lbl_nome_disciplina.config(text=f"{disciplina.nome}")
        self.lbl_id_disciplina.config(text=f"ID: {disciplina.codigo}")
        self.lbl_creditos_disciplina.config(text=f"Créditos: {disciplina.creditos}")
