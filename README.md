# 🌾 Sistema Integrado de Gestão Agrícola e Previsão Climática

Sistema corporativo e académico composto por duas aplicações integradas que partilham dados em tempo real através de uma base de dados SQLite3 e ficheiros de exportação JSON:
1. **Painel do Administrador (Desktop / Tkinter):** Para gestão de Recursos Humanos, análise de pedidos de subscrição, controlo de acessos e consulta de dados.
2. **Sistema Geral de Previsão Climática (Web / Streamlit):** Sistema  para utilizadores/agricultores gerarem previsões climáticas, consultarem diretrizes agrícolas e solicitarem subscrição de acesso.

---

## Requisitos do Sistema

- **Python:** Versão **3.14*.
- **Acesso à Internet:** Apenas para a instalação inicial das bibliotecas.

---

## Bibliotecas Necessárias

O projeto utiliza as seguintes dependências principais:

* **Streamlit:** Para a interface Web interativa do sistema principal.
* **Pandas:** Para processamento e manipulação de dados tabulares.
* **NumPy:** para cálculos estocásticos e simulação numérica.
* **tkcalendar:** Componente de calendário gráfico para a interface Tkinter.
* **Bases de dados embutidas (`sqlite3`, `json`, `tkinter`):** Incluídas nativamente no Python.

---

## Passo a Passo para Instalação e Execução

Siga os passos abaixo no terminal (Prompt de Comando ou PowerShell no Windows):

---

## abra o terminal e digite:

* pip install streamlit pandas numpy tkcalendar
depois de digitar clique enter

""" esse processo vai instalar todas as bibliotecas necessárias para rodar o sistema

### Aceder à Pasta do Projeto
Navegue até ao diretório onde estão localizados os ficheiros Python do projeto:
```bash
cd "C:\Caminho\Para\O\Seu\Projecto"

projetos/
│
├── database.py             # Script de inicialização do SQLite e sincronização com JSON
├── agri_rules.py           # Regras de negócio e diretrizes agrícolas por cultura
├── principal.py            # Sistema Web Geral de Previsão Climática (Streamlit)
├── administrador.py        # Painel Desktop de Gestão de RH e Acessos (Tkinter)
│
├── database.db             # Base de dados SQLite (Gerada automaticamente)
└── *.json                  # Sincronizações JSON (Geradas automaticamente)

""" Como os sistemas comunicam, podes rodar ambos ao mesmo tempo em dois terminais diferentes. Abra dois terminais:"""

bash
""" No primeiro terminal digite:"""
python administrador.py 
  Abrirá a janela do Painel de Controlo Desktop. Qualquer subscrição feita no site aparecerá aqui em tempo real sem precisar reiniciar a aplicação.

bash
""" No segundo terminal digite:
streamlit run principal.py
  O Streamlit iniciará o servidor local e abrirá automaticamente o navegador principal.