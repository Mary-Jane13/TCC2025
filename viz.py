# viz.py — ta compativel com o Catalogo do model.py
#
# - Cria um grafo direcionado a partir do objeto Catalogo do model.py
# - Painel lateral com estatísticas FOI MOVIDO PRA GUI.PY PRA SER INTERATIVO


# PARA AJUSTAR ESPAÇAMENTOS, SÃO ESSAS VARIAVEIS:
#       horizontal_spacing, vertical_spacing, box_width, box_height,
#       alpha das cores e largura da figura (largura/altura calculadas automaticamente).

import os
import networkx as nx
# Importa a Figure da API
from matplotlib.figure import Figure
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
from collections import defaultdict
from model import Catalogo
#interatividade entre on nós conectados e arestas
import matplotlib.pyplot as plt



def map_nota_para_cor(nota):
    """
    Mapeia uma nota (0-10) para uma cor no gradiente vermelho-verde.
    10 = Verde forte (#006400)
    6 = Verde pastel fraco (#90EE90) 
    5.9 = Vermelho pastel fraco (#FFB6C1)
    0.0 = Vermelho forte (#8B0000)
    """
    if nota >= 6.0:
        t = (nota - 6.0) / 4.0 
        # Interpolação no calculo do gradiente de cor
        r = int(144 * (1 - t) + 0 * t)
        g = int(238 * (1 - t) + 100 * t)
        b = int(144 * (1 - t) + 0 * t)
        return f"#{r:02x}{g:02x}{b:02x}"
    else:
        # Vermelho: 0.0 a 5.9
        t = nota / 6.0 
        # gradiente da cor vermelha
        r = int(139 * (1 - t) + 255 * t)
        g = int(0 * (1 - t) + 182 * t)
        b = int(0 * (1 - t) + 193 * t)
        return f"#{r:02x}{g:02x}{b:02x}"

def desenhar_mini_mapa_calor(ax, x, y, width, height, notas, ordem='decrescente', ra_sequencia=None):
    """
    Desenha o mini mapa de calor com diferentes ordens de visualização.
    
    Parâmetros:
    - ax: objeto de eixos do matplotlib onde desenhar
    - ordem: 'decrescente', 'crescente', 'ra'
    - ra_sequencia: lista ordenada de RAs para a ordem 'ra'
    """
    if not notas:
        return
    
    notas_validas = [n for n in notas if n is not None]
    quadrados_cinzas = [n for n in notas if n is None]
    
    notas_ordenadas = []
    
    # Ordenar as notas conforme a opção selecionada
    if ordem == 'decrescente':
        notas_ordenadas_validas = sorted(notas_validas, reverse=True)
        notas_ordenadas = notas_ordenadas_validas + quadrados_cinzas
    elif ordem == 'crescente':
        notas_ordenadas_validas = sorted(notas_validas)
        notas_ordenadas = notas_ordenadas_validas + quadrados_cinzas
    elif ordem == 'ra':
        # Na ordem 'ra', as notas já vêm na ordem correta (incluindo 'None')
        # da função 'desenhar_grafo_em_camadas'
        notas_ordenadas = notas
    else:
        # Padrão (decrescente)
        notas_ordenadas_validas = sorted(notas_validas, reverse=True)
        notas_ordenadas = notas_ordenadas_validas + quadrados_cinzas


    num_notas = len(notas_ordenadas) 
    
    # o layout do grid
    cols = min(5, num_notas)  
    rows = (num_notas + cols - 1) // cols
    
    # tamanho dos quadradinhos
    cell_width = width / cols
    cell_height = height / rows
    for i, nota in enumerate(notas_ordenadas):
        row = i // cols
        col = i % cols
        
        cell_x = x - width/2 + col * cell_width
        cell_y = y + height/2 - (row + 1) * cell_height

        if nota is None:
            cor = '#CCCCCC'
        else:
            cor = map_nota_para_cor(nota)
        
        cell = FancyBboxPatch(
            (cell_x, cell_y),
            cell_width, cell_height,
            boxstyle="square,pad=0.01",
            facecolor=cor,
            edgecolor='white',
            linewidth=0.3,
            zorder=4
        )
        ax.add_patch(cell)
# ---------------------------
# Função: criar_grafo_do_catalogo
# ---------------------------
def criar_grafo_do_catalogo(catalogo: Catalogo) -> nx.DiGraph:
    """
    Constrói um networkx.DiGraph a partir de um objeto Catalogo (model.Catalogo)
    - Cada Disciplina vira um nó identificado pelo seu código (d.codigo)
    - Atributos armazenados em cada nó: nome, semestre e créditos
    """
    G = nx.DiGraph()

    # Adicionar os nós (GRAFO)
    for d in catalogo.listar_disciplinas():
        semestre = getattr(d, "semestre_offer", 0) or 0
        creditos = getattr(d, "creditos", 0) or 0
        nome = getattr(d, "nome", None)
        # chave do nó = código da disciplina
        G.add_node(d.codigo, nome=nome, semestre=semestre, creditos=creditos)

   # Adicioncar os pre-requisitos
    for d in catalogo.listar_disciplinas():
        for pre in d.pre_requisitos:
            if G.has_node(pre):
                G.add_edge(pre, d.codigo)

    return G

# ---------------------------
# Função: desenhar_grafo_em_camadas
# ---------------------------
def desenhar_grafo_em_camadas(grafo: nx.DiGraph, catalogo: Catalogo, ordem_heatmap='decrescente', ra_sequencia=None) -> Figure:
    """
    Recebe um grafo (nx.DiGraph) com atributo de nó 'semestre' e desenha:
    - Colunas verticais por semestre
    - Nós como caixas arredondadas dentro de cada coluna
    - Arestas com setas entre as caixas
    - Linhas tracejadas verticais entre colunas
    - Margens superiores/inferiores reduzidas para maior área útil
    """
    # plt.rcParams['toolbar'] = 'None'

    # -------------------------------------
    # 1) Agrupar nós por semestre
    # -------------------------------------
    # nodes_por_sem: {semestre: [lista_de_nos]}
    nodes_por_sem = defaultdict(list)
    for n, data in grafo.nodes(data=True):
        # usa 0 como fallback caso 'semestre' não exista
        s = data.get('semestre', 0) or 0
        nodes_por_sem[s].append(n)

    # ordenar os semestres
    semestres = sorted(nodes_por_sem.keys())
    if not semestres:
        semestres = [1]   #se um nó nao tiver semestre ele vai ficar numa coluna

    # -------------------------------------
    # 2) Parâmetros de layout e aparência
    # -------------------------------------
    # horizontal_spacing: distância horizontal entre os centros das colunas
    # vertical_spacing: espaço vertical entre nós dentro da mesma coluna
    # box_width / box_height: tamanho das caixas (nós)
    horizontal_spacing = 8.0
    vertical_spacing = 3.5
    box_width = 3.5
    box_height = 2.5

    # -------------------------------------
    # 3) Calcular posições (x, y) para cada nó
    # -------------------------------------
    # pos: dicionário {nó: (x, y)} usado para desenhar caixas e calcular limites
    pos = {}
    for sem in semestres:
        # Ordenar os nós de forma alfabetica
        nodes = sorted(nodes_por_sem[sem])
        x = sem * horizontal_spacing  # posicionamento X da coluna (multiplica pelo índice do semestre)
        total = len(nodes)
        # y_start centraliza verticalmente os nós na coluna: nós ficam simétricos em torno de y=0
        y_start = (total - 1) * vertical_spacing / 2
        for i, node in enumerate(nodes):
            y = y_start - i * vertical_spacing
            pos[node] = (x, y)

    # -------------------------------------
    # 4) Determinar limites verticais com folga
    # -------------------------------------
    # all_y guarda todos os Y calculados; y_max/y_min servem para dimensionar as colunas cinza
    all_y = [p[1] for p in pos.values()] if pos else [0]
    y_max = max(all_y) + 4   
    y_min = min(all_y) - 4   # folga embaixo

    # -------------------------------------
    # 5) Preparar figura e eixos
    # -------------------------------------
    # Largura da figura cresce com o número de semestre
    largura = max(28, len(semestres) * 6.0)
    # Altura é proporcional ao intervalo vertical total (y_max - y_min)
    altura = max(12, (y_max - y_min) / 1.5)
    fig = Figure(figsize=(largura, altura))
    ax_grafo = fig.add_subplot(111) # Um único subplot que preenche a figura

    # -------------------------------------
    # 6) Desenhar colunas cinza
    # -------------------------------------
    # Cada coluna é um FancyBboxPatch que cobre verticalmente de y_min até y_max.
    # x_center, x_left e col_width calculam a posição e largura de cada coluna.
    for sem in semestres:
        x_center = sem * horizontal_spacing
        x_left = x_center - (horizontal_spacing / 2)
        col_width = horizontal_spacing   # AJUSTAR ISSO ELA TA FICANDO MUITO PERTO UMA DA OUTRA
        col_height = y_max - y_min

        rect_coluna = FancyBboxPatch(
            (x_left, y_min),           # canto inferior esquerdo
            col_width, col_height,     # largura, altura
            boxstyle="round,pad=0.5", # estilo arredondado
            facecolor='#E2E8E8',     # cor de fundo (cinza claro)
            edgecolor='none',
            alpha=0.25,                # transparência
            zorder=0                   
        )
        ax_grafo.add_patch(rect_coluna)

        # Título "Sem X" 
        ax_grafo.text(
            x_center, y_max - 0.4,
            f"Sem {sem}",
            ha='center', va='top',
            fontsize=13, fontweight='bold',
            #bbox=dict(boxstyle="round,pad=0.2",
                      #facecolor='white', edgecolor='gray', alpha=0.8), # NÃO VOU COLOCAR CAIXA BRANCA ACHEI FEIO
            zorder=4
        )

    # -------------------------------------
    # 7) Desenhar as caixas ancyBboxPatch (SÃO OS NÓS)
    # -------------------------------------
    for node, (x, y) in pos.items():
        #Obter as notas pro mapa de calor
        disciplina = catalogo.get_disciplina(node)
        notas = []
        if disciplina and ra_sequencia:
            for ra in ra_sequencia:
                ultimo_registro = disciplina.get_ultima_nota_aluno(ra)
                if ultimo_registro and ultimo_registro['nota'] is not None and ultimo_registro['nota'] >= 0:
                    notas.append(ultimo_registro['nota'])
                else:
                    notas.append(None)  # None indica aluno sem nota nesta disciplin
        
        #Criar caixa principal 
        rect = FancyBboxPatch(
            (x - box_width / 2, y - box_height / 2),  # canto inferior esquerdo
            box_width, box_height,                    # largura, altura da caixa
            boxstyle="round,pad=0.1",                 # caixa arredondada
            facecolor='#FFFFFF',                 
            edgecolor='black',
            linewidth=1.3,
            zorder=3
        )

        # Interatividade de clique
        rect.set_picker(True)  # a caixa principal clicável
        rect.set_gid(node)     # Associa o ID do nó a ela

        ax_grafo.add_patch(rect)

        #Desenhar mini mapa de calor:
        mapa_height = box_height * 0.65
        desenhar_mini_mapa_calor(ax_grafo, x, y + box_height * 0.15, box_width * 0.9, mapa_height, notas, ordem_heatmap, ra_sequencia)
        
        # Escreve o código da disciplina embaixo
        txt = ax_grafo.text(x, y - box_height * 0.4, node, 
                      ha='center', va='center',
                      fontweight='bold', fontsize=8, zorder=5)
        

        txt.set_picker(True) # O texto tem que ser clicável tbm pra nao dar uns bugs
        txt.set_gid(node)    

    # -------------------------------------
    # 8) Desenhar arestas orientadas
    # -------------------------------------
    # Para cada aresta (start -> end) é uma FancyArrowPatch ligando as bordas das caixas.
    # Ajustar os pontos inicial/final para "encostar" nas bordas das caixas em vez do centro.
    for start, end in grafo.edges():
        # Se alguma das posições não existir (ex.: nó sem semestre), pulamos a aresta
        if start not in pos or end not in pos:
            continue

        s_pos = np.array(pos[start])
        e_pos = np.array(pos[end])
        vec = e_pos - s_pos
        vec_len = np.linalg.norm(vec)
        if vec_len == 0:
            continue

        u_vec = vec / vec_len  
        start_point = s_pos.copy()
        end_point = e_pos.copy()

        # os pontos iniciais/finais para a borda das caixas com base nos vetores se não elas apontam pra dentro do nó
        if u_vec[0] > 0:
            start_point[0] += box_width / 2
            end_point[0] -= box_width / 2
        elif u_vec[0] < 0:
            start_point[0] -= box_width / 2
            end_point[0] += box_width / 2

        if u_vec[1] > 0:
            start_point[1] += box_height / 2
            end_point[1] -= box_height / 2
        elif u_vec[1] < 0:
            start_point[1] -= box_height / 2
            end_point[1] += box_height / 2

        # AS SETAS
        arrow = FancyArrowPatch(
            start_point, end_point,
            arrowstyle='->', color='#262626',
            mutation_scale=20, linewidth=1.8,
            connectionstyle="arc3,rad=0.08", zorder=2
        )

        arrow.set_gid(f"{start}->{end}")  # Identificador único para a seta


        ax_grafo.add_patch(arrow)

    # -------------------------------------
    # 9) Linhas pontilhada entre as colunas
    # -------------------------------------
    for sem in semestres[1:]:
        x_center = sem * horizontal_spacing
        x_left = x_center - (horizontal_spacing / 2)
        ax_grafo.axvline(x=x_left, color='gray', linestyle='--', linewidth=0.9, alpha=0.5, zorder=1)

    # -------------------------------------
    # 10) Ajustes de limites, cor de fundo, titulo
    # -------------------------------------
    all_x = [p[0] for p in pos.values()] if pos else [0]
    if all_x:
        # limitar o eixo X com uma margem relativa ao espaçamento horizontal para evitar corte visual
        ax_grafo.set_xlim(min(all_x) - horizontal_spacing/1.5, max(all_x) + horizontal_spacing/1.5)
    # limites Y com pequena folga
    ax_grafo.set_ylim(y_min - 0.8, y_max + 0.8)

    # Remover marcadores e spines (eixos) para estilo "canvas"
    ax_grafo.set_xticks([])
    ax_grafo.set_yticks([])
    for spine in ax_grafo.spines.values():
        spine.set_visible(False)

    #plano de fundooo
    ax_grafo.set_facecolor('white')

    # título do gráfico
    ax_grafo.set_title("Sistema de Visualização de Múltiplos Históricos", fontsize=20, weight='bold', pad=18)

    # -------------------------------------
    # 11) Ajustar margens e retornar figura
    # -------------------------------------
    fig.subplots_adjust(top=0.98, bottom=0.02, left=0.01, right=0.99)
    return fig
