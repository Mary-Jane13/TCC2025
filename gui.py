# gui.py - versão corrigida


import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.figure import Figure
import numpy as np
import viz 
import os
from model import Disciplina
import networkx as nx


class App(tk.Tk):
    def __init__(self, catalogo, nome_arquivo_xml):
        super().__init__()
        
        self.catalogo = catalogo
        self.nome_arquivo_xml = nome_arquivo_xml
        self.grafo_curso = None
        self.figura_atual = None
        self.estado_hover = None
        self.grafo_textos = {}
        self.grafo_setas = {}
        self.grafo_caixas = {}
        self.ordem_heatmap = 'decrescente'
        self.ra_sequencia = self.obter_ras_ordenados()
        
        # tem que inicializar os frames primeiro
        self.main_frame = None
        self.sidebar_frame = None
        self.graph_frame = None
        
        self.title("Visualizador de Históricos Curriculares (TCC)")
        self.geometry("1600x900")

        try:
            self.state('zoomed')
        except tk.TclError:
            print("Não foi possível maximizar a janela.")
        
        largura_barra = 220
        padding = 16
        wraplength = largura_barra - padding - 10

        style = ttk.Style(self)
        style.configure('Wrappable.TLabel', wraplength=wraplength)
        style.configure('Italic.TLabel', font=('Arial', 10, 'italic'))

        # Criar widgets imediatamente
        self.create_widgets()

    def obter_ras_ordenados(self):
        """Obtém lista ordenada de todos os RAs únicos do catálogo"""
        ras = set()
        for disciplina in self.catalogo.disciplinas.values():
            for registro in disciplina.registros:
                ras.add(registro['ra'])
        return sorted(ras)

    def create_widgets(self):
        # Criar frame principal
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(side="top", fill="both", expand=True)

        # Barra lateral
        self.sidebar_frame = ttk.Frame(self.main_frame, width=220, padding=10, relief="sunken")
        self.sidebar_frame.pack(side="right", fill="y")
        self.sidebar_frame.pack_propagate(False) 

        # Conteúdo da barra lateral
        ttk.Label(self.sidebar_frame, text="Informações", font=("Arial", 16, "bold")).pack(pady=5, anchor="w")
        ttk.Label(self.sidebar_frame, text=f"Currículo:", font=("Arial", 11, "bold")).pack(pady=(10, 0), anchor="w")
        ttk.Label(self.sidebar_frame, text=f"{self.nome_arquivo_xml}", foreground="darkblue", style='Italic.TLabel').pack(anchor="w")

        # Estatísticas
        print("GUI: Gerando grafo do catálogo...")
        self.grafo_curso = viz.criar_grafo_do_catalogo(self.catalogo)

        #pré-calcular grafo ponderado, fontes e sumidouros
        print("GUI: Pré-calculando grafo ponderado para caminhos longos...")
        self.grafo_ponderado = self.grafo_curso.copy()
        for u, v in self.grafo_ponderado.edges():
            self.grafo_ponderado[u][v]['weight'] = -1
        
        # Nós "fonte" (início do curso, sem pré-requisitos)
        self.sources = [n for n in self.grafo_curso.nodes() if self.grafo_curso.in_degree(n) == 0]
        # Nós "sumidouro" (fim de trilha, sem sucessores)
        self.sinks = [n for n in self.grafo_curso.nodes() if self.grafo_curso.out_degree(n) == 0]
        
        ttk.Label(self.sidebar_frame, text="Estatísticas:", font=("Arial", 11, "bold")).pack(pady=(20, 0), anchor="w")
        ttk.Label(self.sidebar_frame, text=f"Disciplinas: {len(self.grafo_curso.nodes())}").pack(anchor="w")
        ttk.Label(self.sidebar_frame, text=f"Alunos: {self.catalogo.total_alunos}").pack(anchor="w")

        # Controle de ordenação do mapa de calor
        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", pady=10)
        
        ttk.Label(self.sidebar_frame, text="Ordenar Mapa de Calor:", 
                 font=("Arial", 11, "bold")).pack(anchor="w")
        
        self.ordem_var = tk.StringVar(value=self.ordem_heatmap)
        ordem_combo = ttk.Combobox(self.sidebar_frame, textvariable=self.ordem_var,
                                  values=['decrescente', 'crescente', 'ra'],
                                  state='readonly', width=15)
        ordem_combo.pack(anchor="w", pady=(5, 15))
        ordem_combo.bind('<<ComboboxSelected>>', self.on_ordem_change)

        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", pady=10)

        # Info das disciplinas
        ttk.Label(self.sidebar_frame, text="Disciplina Selecionada:", font=("Arial", 11, "bold")).pack(anchor="w")
        
        self.lbl_nome_disciplina = ttk.Label(self.sidebar_frame, text="Nenhuma", font=("Arial", 10, "bold"), style='Wrappable.TLabel')
        self.lbl_nome_disciplina.pack(pady=3, anchor="w")
        
        self.lbl_id_disciplina = ttk.Label(self.sidebar_frame, text="ID: N/A")
        self.lbl_id_disciplina.pack(anchor="w")
        
        self.lbl_creditos_disciplina = ttk.Label(self.sidebar_frame, text="Créditos: N/A")
        self.lbl_creditos_disciplina.pack(anchor="w")
        
        ttk.Separator(self.sidebar_frame, orient="horizontal").pack(fill="x", pady=20)
        
        self.create_heatmap_legend()

        # Frame do grafo
        self.graph_frame = ttk.Frame(self.main_frame)
        self.graph_frame.pack(side="right", fill="both", expand=True)

        # Gerar figura inicial - AGORA DEPOIS de criar todos os frames
        self.regenerar_grafo()

    def on_ordem_change(self, event):
        """Atualiza a ordenação do mapa de calor quando o usuário muda a seleção"""
        nova_ordem = self.ordem_var.get()
        if nova_ordem != self.ordem_heatmap:
            self.ordem_heatmap = nova_ordem
            self.regenerar_grafo()

    def regenerar_grafo(self):
        """Regera o grafo com os parâmetros atuais de ordenação"""
        print(f"GUI: Regenerando grafo com ordem: {self.ordem_heatmap}")
        
        # Verificar se graph_frame existe
        if not hasattr(self, 'graph_frame') or self.graph_frame is None:
            print("Erro: graph_frame não está definido")
            return
            
        # Gerar nova figura com os parâmetros de ordenação
        self.figura_atual = viz.desenhar_grafo_em_camadas(
            self.grafo_curso, 
            self.catalogo, 
            self.ordem_heatmap,
            self.ra_sequencia
        )

        # Destruir canvas existente se houver
        if hasattr(self, 'canvas'):
            self.canvas.get_tk_widget().destroy()
            if hasattr(self, 'toolbar'):
                self.toolbar.destroy()

        # Criar novo canvas
        self.canvas = FigureCanvasTkAgg(self.figura_atual, master=self.graph_frame)
        self.canvas.draw()
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        
        widget_canvas = self.canvas.get_tk_widget()
        widget_canvas.pack(side="top", fill="both", expand=True)

        # Recoletar referências dos elementos gráficos
        ax = self.figura_atual.axes[0]
        self.grafo_textos = {t.get_text(): t for t in ax.texts}
        
        self.grafo_setas = {}
        for artista in ax.get_children():
            if isinstance(artista, FancyArrowPatch):
                gid = artista.get_gid()
                if gid:
                    self.grafo_setas[gid] = artista
        
        self.grafo_caixas = {}
        for artista in ax.get_children():
            if isinstance(artista, FancyBboxPatch) and artista.get_gid() is not None:
                self.grafo_caixas[artista.get_gid()] = artista

        # Reconectar eventos
        self.canvas.mpl_connect('pick_event', self.on_pick)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)

    def create_heatmap_legend(self):
        ttk.Label(self.sidebar_frame, text="Mapa de Calor:", font=("Arial", 11, "bold")).pack(pady=(0, 5), anchor="w")
        
        # Figura um pouco mais larga para melhor espaçamento
        fig_legenda = Figure(figsize=(2.2, 0.7), dpi=100)
        fig_legenda.set_facecolor('#f0f0f0')
        ax_legenda = fig_legenda.add_subplot(111)
        ax_legenda.axis('off')

        patch_y_level = 0.65
        patch_altura = 0.25
        text_y_level = 0.3

        # Legenda de 0 a 10
        notas_legenda = np.linspace(0, 10, 6)
        cores_legenda = [viz.map_nota_para_cor(n) for n in notas_legenda]

        for i, (nota, cor) in enumerate(zip(notas_legenda, cores_legenda)):
            x_pos = 0.05 + (i * 0.16)
            ax_legenda.add_patch(FancyBboxPatch(
                (x_pos, patch_y_level), 0.1, patch_altura,
                boxstyle="round,pad=0.01", facecolor=cor, edgecolor='black', linewidth=0.5
            ))
            ax_legenda.text(x_pos + 0.05, text_y_level, f"{nota:.1f}",
                            ha='center', va='top', fontsize=8.5)

        canvas_legenda = FigureCanvasTkAgg(fig_legenda, master=self.sidebar_frame)
        canvas_legenda.draw()
        canvas_legenda.get_tk_widget().pack(fill="x", anchor="w")

        ttk.Label(
            self.sidebar_frame,
            text="Quadrados cinza: o aluno não cursou a disciplina.",
            font=("Arial", 9, "italic"),
            foreground="#555555",
            wraplength=200,
            justify="left"
        ).pack(pady=(3, 0), anchor="w")
        
    def on_pick(self, event):
        artist = event.artist
        node_id = artist.get_gid()
        if node_id:
            print(f"Clique detectado no nó: {node_id}")
            disciplina = self.catalogo.get_disciplina(node_id)
            if disciplina:
                self.update_sidebar(disciplina)
            else:
                print(f"Erro: Nó {node_id} clicado, mas não encontrado no catálogo.")

    def encontrar_caminho_mais_longo(self, no_inicial):
        """
        Encontra o caminho mais longo que passa pelo nó, tanto para frente (dependências)
        quanto para trás (pré-requisitos)
        """
        caminhos_encontrados = set([no_inicial])
    
    # 1. Encontrar o caminho mais longo de PRÉ-REQUISITOS (para trás)
        try:
            # Encontrar todos os antecessores no caminho mais longo
            antecessores = list(nx.ancestors(self.grafo_curso, no_inicial))
            if antecessores:
                # Encontrar o nó "raiz" mais distante (sem pré-requisitos)
                nos_raiz = [node for node in antecessores if self.grafo_curso.in_degree(node) == 0]
                if not nos_raiz:
                    # Se não há raiz, pegar o antecessor mais distante
                    nos_raiz = [max(antecessores, key=lambda x: len(list(nx.ancestors(self.grafo_curso, x))))]
            
                # Para cada raiz, encontrar o caminho mais longo até o nó inicial
                for raiz in nos_raiz:
                    try:
                        # Encontrar TODOS os caminhos simples da raiz até o nó
                        todos_caminhos = list(nx.all_simple_paths(self.grafo_curso, raiz, no_inicial))
                        if todos_caminhos:
                            caminho_mais_longo = max(todos_caminhos, key=len)
                            caminhos_encontrados.update(caminho_mais_longo)
                    except nx.NetworkXNoPath:
                        continue
        except:
            pass
    
        # 2. Encontrar o caminho mais longo de DEPENDÊNCIAS (para frente)
        try:
            # Encontrar todos os sucessores no caminho mais longo
            sucessores = list(nx.descendants(self.grafo_curso, no_inicial))
            if sucessores:
                # Encontrar os nós "folha" mais distantes (sem dependências)
                nos_folha = [node for node in sucessores if self.grafo_curso.out_degree(node) == 0]
                if not nos_folha:
                    # Se não há folha, pegar o sucessor mais distante
                    nos_folha = [max(sucessores, key=lambda x: len(list(nx.descendants(self.grafo_curso, x))))]
            
                # Para cada folha, encontrar o caminho mais longo do nó inicial até ela
                for folha in nos_folha:
                    try:
                        # Encontrar TODOS os caminhos simples do nó até a folha
                        todos_caminhos = list(nx.all_simple_paths(self.grafo_curso, no_inicial, folha))
                        if todos_caminhos:
                            caminho_mais_longo = max(todos_caminhos, key=len)
                            caminhos_encontrados.update(caminho_mais_longo)
                    except nx.NetworkXNoPath:
                        continue
        except:
            pass
    
        return caminhos_encontrados
        

    def on_hover(self, event):
        """
        Detecta quando o mouse passa sobre qualquer parte do nó (caixa ou texto)
        e destaca todo o caminho conectado
        """
        if event.inaxes is None:
            self.resetar_destaque()
            return

        ax = event.inaxes

        # Verificar se o mouse está sobre alguma caixa de nó
        hovered_label = None
        
        # Primeiro: verificar caixas
        for gid, caixa in self.grafo_caixas.items():
            contains, _ = caixa.contains(event)
            if contains:
                hovered_label = gid
                break
        
        # se nao , tem que verificar texto
        if hovered_label is None:
            min_dist = float("inf")
            for label, text_obj in self.grafo_textos.items():
                x, y = text_obj.get_position()
                dist = np.hypot(event.xdata - x, event.ydata - y)
                if dist < 0.5 and dist < min_dist:
                    hovered_label = label
                    min_dist = dist

        if hovered_label:
            if self.estado_hover == hovered_label:
                return
            self.estado_hover = hovered_label

            # Encontrar TODOS os nós conectados
            # connected_nodes = self.encontrar_caminhos_completos(hovered_label)
            connected_nodes = self.encontrar_caminho_mais_longo(hovered_label)

            # Destacar textos
            for label, text_obj in self.grafo_textos.items():
                if label == hovered_label:
                    text_obj.set_color("blue")
                    text_obj.set_fontsize(10)
                elif label in connected_nodes:
                    text_obj.set_color("blue")
                else:
                    text_obj.set_color("black")
                    text_obj.set_fontweight("normal")
                    text_obj.set_fontsize(9)

            # Destacar caixas
            for gid, caixa in self.grafo_caixas.items():
                if gid == hovered_label:
                    caixa.set_edgecolor("blue")
                    caixa.set_linewidth(2.5)
                elif gid in connected_nodes:
                    caixa.set_edgecolor("blue")
                    caixa.set_linewidth(2.0)
                else:
                    caixa.set_edgecolor("black")
                    caixa.set_linewidth(1.3)

            # Destacar setas
            for seta_id, seta in self.grafo_setas.items():
                if "->" in seta_id:
                    start, end = seta_id.split("->")
                    # Destacar se ambos os nós da seta estão no caminho
                    if start in connected_nodes and end in connected_nodes:
                        seta.set_color("blue")
                        seta.set_linewidth(3.0)
                        seta.set_alpha(1.0)
                    else:
                        seta.set_color("#262626")
                        seta.set_linewidth(1.8)
                        seta.set_alpha(0.3)

            self.canvas.draw_idle()

        else:
            self.resetar_destaque()

    def resetar_destaque(self):
        if self.estado_hover is not None:
            # Resetar textos
            for text_obj in self.grafo_textos.values():
                text_obj.set_color("black")
                text_obj.set_fontweight("normal")
                text_obj.set_fontsize(10)
            
            # Resetar caixas
            for caixa in self.grafo_caixas.values():
                caixa.set_edgecolor("black")
                caixa.set_linewidth(1.3)
            
            # Resetar setas
            for seta in self.grafo_setas.values():
                seta.set_color("#262626")
                seta.set_linewidth(1.8)
                seta.set_alpha(1.0)
            
            self.canvas.draw_idle()
            self.estado_hover = None

    def update_sidebar(self, disciplina: Disciplina):
        self.lbl_nome_disciplina.config(text=f"{disciplina.nome}")
        self.lbl_id_disciplina.config(text=f"ID: {disciplina.codigo}")
        self.lbl_creditos_disciplina.config(text=f"Créditos: {disciplina.creditos}")
