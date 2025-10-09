# model.py  -> a estrutura dos dados das disciplinas
import pandas as pd
import xml.etree.ElementTree as ET #a biblioteca pro xml que o Guilherme usou no GradeGen

class Disciplina:
    #Representa uma disciplina e armazena todos os registros dos alunos que cursaram ela, a turma, as notas e a frequencia
    def __init__(self, codigo, nome="Não definido", creditos=0, semestre_offer=0, pre_requisitos=None):
        # Os atributos do XML (id, nome, creditos e semestre oferecido)
        self.codigo = codigo
        self.nome = nome
        self.creditos = creditos
        self.semestre_offer = semestre_offer
        self.pre_requisitos = pre_requisitos if pre_requisitos is not None else [] #Garante que pre_requisitos seja sempre uma lista
        # Os atributos do CSV, os registros dos alunos, notas, turma e frequência
        self.registros = []

    def adicionar_registro(self, ra, turma, nota, frequencia):
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

    #TESTE NA MAIN
    def __repr__(self):
        return (f"Disciplina(Código='{self.codigo}', Nome='{self.nome}', "
                f"Créditos={self.creditos}, Pré-reqs={self.pre_requisitos}, "
                f"Alunos registrados={len(self.registros)})")

class Catalogo:
    #Armazena e gerencia o conjunto de todas as disciplinas, ele vai ser carregado do XML e do CSV
    #CSV = notas, turma e frequencia
    #XML = dados de cada disciplina (nome, créditos, semestre oferecido, pré-requisitos)
    def __init__(self):
        self.disciplinas = {}
        self.total_alunos = 0 #inicializa contagem de alunos

    def _carregar_de_xml(self, caminho_xml):
        #Método privado para carregar o arquivo XML do catálogo do curso
        try:
            tree = ET.parse(caminho_xml)
            root = tree.getroot()
            #Andar na árvore do subject - todas as disicplinas:
            for subject in root.findall('.//subject'):
                codigo = subject.find('id').text
                if not codigo: continue # se não tiver ID vou pular - erro no xml

                nome = subject.find('subject_name').text
                creditos = int(subject.find('credits').text or 0)    #se tiver vazio vou considerar 0
                semestre_offer = int(subject.find('sem_offer').text or 0)
                
                pre_requisitos = []  #Coleta os pre-requisitos
                for pre_req in subject.findall('pre_reqs'):
                    if pre_req.text and pre_req.text.strip():  # checagem para pre-requisitos vazios
                        pre_requisitos.append(pre_req.text.strip())
                
                # Cria a disciplina no dicionário de disciplinas
                if codigo not in self.disciplinas:
                    self.disciplinas[codigo] = Disciplina(
                        codigo=codigo, nome=nome, creditos=creditos,
                        semestre_offer=semestre_offer, pre_requisitos=pre_requisitos
                    )
        except FileNotFoundError:
            print(f"Erro: O arquivo '{caminho_xml}' não foi encontrado.")
        except ET.ParseError:
            print(f"Erro: Falha ao analisar o arquivo XML '{caminho_xml}'.")

    def _carregar_de_csv(self, caminho_csv):
        #Método privado para carregar os registros de alunos do CSV.
        try:
            df = pd.read_csv(caminho_csv)
            df.rename(columns={df.columns[0]: 'RA'}, inplace=True)   #Renomeando a primeira coluna vazia como RA pra facilitar
            self.total_alunos = df['RA'].nunique() #calcular o total de alunos
        except FileNotFoundError:
            print(f"Erro: O arquivo '{caminho_csv}' não foi encontrado.")
            return

        #Itera sobre as colunas, começando da segunda porque a primeira é os RAs
        for i in range(1, len(df.columns), 3):
            # Garante que existam 3 colunas no bloco para processar.
            if i + 2 >= len(df.columns): continue

            col_codigo_disciplina = df.columns[i+1]
            #A biblioteca panda quando ve coluna duplicadas coloca um prefixo então se uma disciplina aparece mais que 1 vez ela
            # interpreta que são 2 disciplinas diferentes, isso aqui é pra agrupar as duplicatas e entender que é só 1
            codigo_base = col_codigo_disciplina.split('.')[0]
            
            #buscaando no dicio. que foi criado no XML
            disciplina_obj = self.get_disciplina(codigo_base)
            if not disciplina_obj:
                continue # Pula se a disciplina do CSV não existir no catálogo XML
            
            #Itera sobre cada linha de aluno
            for _, row in df.iterrows():
                try:
                    nota = float(row[col_codigo_disciplina])
                    frequencia = float(row[df.columns[i+2]])
                    disciplina_obj.adicionar_registro(   #adicionando o registro a objeto da disciplina
                        ra=row['RA'],
                        turma=row[df.columns[i]],
                        nota=nota,
                        frequencia=frequencia
                    )
                except (ValueError, TypeError):
                    #isso já resolve o problema de '--' dos valores da coluna
                    continue

    def carregar_dados(self, caminho_xml, caminho_csv):
        #CARREGANDO OS DADOS
        print("1. Carregando metadados do catálogo XML...")
        self._carregar_de_xml(caminho_xml)
        print("2. Carregando registros de alunos do CSV...")
        self._carregar_de_csv(caminho_csv)
        print("Carga de dados completa.")
    
    def get_disciplina(self, codigo):
        # Busca e retorna o código da disciplina
        return self.disciplinas.get(codigo)

    def buscar_por_nome(self, nome_parcial):
        #Retorna as disciplinas que tem a palavra no nome
        nome_lower = nome_parcial.lower()
        return [
            disc for disc in self.disciplinas.values() 
            if disc.nome and nome_lower in disc.nome.lower()
        ]

    def listar_disciplinas(self):
        #Listar TODAS as disciplinas
        return list(self.disciplinas.values())

    def __repr__(self):
        #TESTAR NA MAIN
        return f"Catálogo com {len(self.disciplinas)} disciplinas e {self.total_alunos} alunos."
