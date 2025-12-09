# TCC2025
## Grafos acíclicos direcionados em camadas para visualização de múltiplos históricos escolares

Este projeto é uma ferramenta de visualização de dados desenvolvida como parte de um Trabalho de Conclusão de Curso (TCC). O software processa dados curriculares (XML) e registros acadêmicos (CSV) para gerar grafos interativos que permitem a análise de desempenho de estudantes, fluxo de disciplinas e retenção.

### Arquitetura:

-   **`model.py` (Model):** Gerencia a lógica de dados. Faz o parsing dos arquivos XML e CSV e estrutura as classes `Disciplina` e `Catalogo`.
-   **`viz.py` (View/Visualization):** Responsável por toda a lógica de desenho usando `matplotlib` e `networkx`. Define como o grafo, as arestas e os heatmaps são renderizados.
-   **`gui.py` (View/Controller):** Implementa a interface gráfica com `tkinter`. Atua também como controlador, gerenciando eventos de clique, hover e orquestrando a atualização da visualização baseada nos dados do modelo.
-   **`main.py`:** Ponto de entrada da aplicação. Gerencia a seleção de arquivos.

### GradeGen e XML

Este sistema usa o arquivo CSV de simulação de notas do GradeGen (https://github.com/celmarguimaraes/GradeGen) e XML com uma árvore da estrutura curricular.

Deve conter a estrutura das disciplinas (Subjects), incluindo ID, nome, créditos, semestre oferecido e pré-requisitos. Exemplo:

```xml
<all_configs>
  <cat_info>
    <course_id>94</course_id>
    <year>2020</year>
    <max_years>6</max_years>
  </cat_info>
  <subjects>
    <subject>
      <id>EB101</id>
      <subject_name>Cálculo I</subject_name>
      <credits>6</credits>
      <sem_offer>1</sem_offer>
      <classes_no>1</classes_no>
      <tipo_nivel_atividade_mae>G</tipo_nivel_atividade_mae>
      <pre_reqs/>
      <ano_inicio/>
      <ano_fim/>
      <no_cadeia_pre_requisito>0</no_cadeia_pre_requisito>
      <tipo_pre_requisito/>
      <tipo_nivel_atividade_exigida/>
  </subject>
...
  </subjects>
```

### Instalação e Uso:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd seu-repositorio
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute o programa:**
    ```bash
    python main.py
    ```

4.  **Uso:**
    -   Ao iniciar, uma janela pedirá para selecionar o arquivo **XML** (Catálogo/Grade).
    -   Em seguida, selecione o arquivo **CSV** (Dados dos Alunos).
    -   A interface gráfica será carregada automaticamente.

## Contato:

Para qualquer dúvida, mande email para mariduoliver@gmail.com.

