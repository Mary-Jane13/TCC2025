# model.py  -> a estrutura dos dados das disciplinas
import pandas as pd

class Disciplina:
    #Representa uma disciplina e armazena todos os registros dos alunos que cursaram ela, a turma, as notas e a frequencia
    def __init__(self, codigo):
        self.codigo = codigo
        self.registros = []
        
    def adicionar_dados(self, notas, frequencias):
        self.registros.append({
            "ra": ra,
            "turma": turma,
            "nota": nota,
            "frequencia": frequencia
        })
    #Fiz pra encontrar a ultima nota do aluno sempre que for pegar essa informação
    def get_ultima_nota_aluno(self, ra):
        registros_aluno = [r for r in self.registros if str(r['ra']) == str(ra)]
        if not registros_aluno:
            return None
        return registros_aluno[-1]

    def __repr__(self):
        #PRA EU TESTAR
        return f"Disciplina({self.codigo}, Alunos={len(self.notas)})"


class Catalogo:
    #Armazena e gerencia o conjunto de todas as disciplinas, considerei o arquivo CSV do GradeGen
    def __init__(self):
        self.disciplinas = {}
        self.total_alunos_unicos = 0

    def carregar_de_csv(self, caminho_csv):
        try:
            df = pd.read_csv(caminho_csv)
            df.rename(columns={df.columns[0]: 'RA'}, inplace=True)
            self.total_alunos_unicos = df['RA'].nunique()
        except FileNotFoundError:
            print(f"Erro: O arquivo '{caminho_csv}' não foi encontrado.")
            return

        #Itera sobre as colunas, começando da segunda porque a primeira é os RAs e não tem título na coluna.
        for i in range(1, len(df.columns), 3):
            # Garante que existam 3 colunas no bloco para processar.
            if i + 2 >= len(df.columns):
                continue

            #Confiamos na posição da coluna da disciplina e ai ela vai ser precedida por turma e sucedida por frequencia
            col_turma = df.columns[i]
            col_codigo_disciplina = df.columns[i+1]
            col_freq = df.columns[i+2]
            
            #A biblioteca panda quando ve coluna duplicadas coloca um prefixo então se uma disciplina aparece mais que 1 vez ela
            # interpreta que são 2 disciplinas diferentes, isso aqui é pra agrupar as duplicatas e entender que é só 1
            codigo_base_disciplina = col_codigo_disciplina.split('.')[0]
            
            #Ignora colunas que são claramente de frequência ou turma no lugar do código da disciplina
            if codigo_base_disciplina.lower() in ['turma', 'freq']:
                continue
            
            #Cria ou obtém o objeto da disciplina
            if codigo_base_disciplina not in self.disciplinas:
                self.disciplinas[codigo_base_disciplina] = Disciplina(codigo_base_disciplina)
            disciplina_obj = self.disciplinas[codigo_base_disciplina]

            #Itera sobre cada aluno (linha)
            for index, row in df.iterrows():
                ra_aluno = row['RA']
                
                #Pega os valores das 3 colunas do bloco atual
                turma_str = row[col_turma]
                nota_str = row[col_codigo_disciplina]
                freq_str = row[col_freq]

                #Converter a nota e a frequencia pra numeros
                #Se falhar pq o registro é '--' é ignorado
                try:
                    nota = float(nota_str)
                    frequencia = float(freq_str)
                    disciplina_obj.adicionar_registro(ra_aluno, turma_str, nota, frequencia)
                except (ValueError, TypeError):
                    continue

    def get_disciplina(self, codigo):
        #Retorna uma instância de Disciplina pelo seu código
        return self.disciplinas.get(codigo)

    def listar_disciplinas(self):
        #Retorna uma lista com todas as instâncias de Disciplina.
        return list(self.disciplinas.values())

    def __repr__(self):
        #PRA EU TESTAR
        return f"Catálogo com {len(self.disciplinas)} disciplinas e {self.total_alunos_unicos} alunos."
