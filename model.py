# model.py  -> a estrutura dos dados das disciplinas
import pandas as pd

class Disciplina:
    #criar listas vazias pra armazenar as notas e frequencias
    #como a turma entra nisso aqui ??????? preciso pensar
    def __init__(self, codigo):
        self.codigo = codigo
        self.notas = []
        self.frequencias = []

    def adicionar_dados(self, notas, frequencias):
        self.notas.extend(notas)
        self.frequencias.extend(frequencias)

    def __repr__(self):
        return f"Disciplina({self.codigo}, Alunos={len(self.notas)})"


class Catalogo:
    def __init__(self):
        self.disciplinas = {}      #um dicionario vazio pra armazenar as disciplinas

    def carregar_de_csv(self, caminho_csv):    # carregar a simulacao do gradegen
        df = pd.read_csv(caminho_csv)
        colunas = list(df.columns)

        # ele percorre as colunas que são: Turma | o código da disciplina | Freq que se repetem
        # pra cada disciplina ele le as notas e a frequencia
        # DEPOIS PENSAR EM AGRUPAR POR TURMA!!!!!!

        for i in range(len(colunas) - 2):  # precisa de pelo menos 3 colunas seguidas
            col_turma = colunas[i]
            col_disciplina = colunas[i+1]
            col_freq = colunas[i+2]

    
            if "turma" in col_turma.lower() and "freq" in col_freq.lower():
                # Extrair notas (to ignorando o "--")
                notas = df[col_disciplina].replace("--", None).dropna()
                notas = pd.to_numeric(notas, errors="coerce").dropna().tolist()

                frequencias = df[col_freq].replace("--", None).dropna()
                frequencias = pd.to_numeric(frequencias, errors="coerce").dropna().tolist()

                self.disciplinas[col_disciplina].adicionar_dados(notas, frequencias)

    def listar_disciplinas(self):
        return list(self.disciplinas.values())

    def __repr__(self):   #isso vou usar pra testar se ele pelo menos não ta dando erro
        return f"Catálogo com {len(self.disciplinas)} disciplinas"
