import sqlite3
import json
import re
from datetime import datetime

DB_NAME = "fazenda_sistema.db"

OPCOES_CARGOS = [
    "Diretor(a) Geral",
    "Gerente de Produção",
    "Engenheiro(a) Agrónomo(a)",
    "Supervisor(a) de Campo",
    "Técnico(a) Agrícola",
    "Operador(a) de Máquinas",
    "Auxiliar de Campo",
    "Administrador(a) do Sistema"
]

OPCOES_SANGUE = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bi TEXT UNIQUE NOT NULL,
        nome_completo TEXT NOT NULL,
        data_nascimento TEXT NOT NULL,
        telefone TEXT NOT NULL,
        genero TEXT NOT NULL,
        cargo TEXT NOT NULL,
        tipo_sanguineo TEXT NOT NULL,
        provincia TEXT NOT NULL,
        municipio TEXT NOT NULL,
        bairro TEXT NOT NULL,
        rua TEXT NOT NULL,
        numero_casa TEXT NOT NULL,
        data_registro DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios_sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bi TEXT UNIQUE NOT NULL,
        nome_usuario TEXT NOT NULL,
        cargo TEXT NOT NULL,
        senha TEXT NOT NULL,
        telefone TEXT NOT NULL,
        status TEXT DEFAULT 'EM_ANALISE',
        data_subscricao DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS previsoes_historico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_previsao DATE NOT NULL,
        precipitacao REAL NOT NULL,
        temp_solo REAL NOT NULL,
        humidade REAL NOT NULL,
        criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()
    sincronizar_bases_json()

def sincronizar_bases_json():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM funcionarios ORDER BY nome_completo ASC")
    funcs = [dict(row) for row in cursor.fetchall()]
    with open("quadro_funcionarios.json", "w", encoding="utf-8") as f:
        json.dump(funcs, f, ensure_ascii=False, indent=4)

    cursor.execute("SELECT id, bi, nome_usuario, cargo, telefone, status, data_subscricao FROM usuarios_sistema WHERE status = 'EM_ANALISE'")
    analise = [dict(row) for row in cursor.fetchall()]
    with open("analise_subscricao.json", "w", encoding="utf-8") as f:
        json.dump(analise, f, ensure_ascii=False, indent=4)

    cursor.execute("SELECT id, bi, nome_usuario, cargo, telefone, status, data_subscricao FROM usuarios_sistema WHERE status = 'APROVADO'")
    aprovados = [dict(row) for row in cursor.fetchall()]
    with open("acessos_aprovados.json", "w", encoding="utf-8") as f:
        json.dump(aprovados, f, ensure_ascii=False, indent=4)

    cursor.execute("SELECT id, data_previsao, precipitacao, temp_solo, humidade, criado_em FROM previsoes_historico ORDER BY id DESC")
    previsoes = [dict(row) for row in cursor.fetchall()]
    with open("previsoes_climaticas.json", "w", encoding="utf-8") as f:
        json.dump(previsoes, f, ensure_ascii=False, indent=4)

    espelho_geral = {
        "ultim_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "quadro_funcionarios": funcs,
        "subscricoes_pendentes": analise,
        "usuarios_aprovados": aprovados,
        "historico_previsoes_climaticas": previsoes
    }
    with open("fazenda_sistema.json", "w", encoding="utf-8") as f:
        json.dump(espelho_geral, f, ensure_ascii=False, indent=4)

    conn.close()

def validar_bi_angolano(bi: str) -> bool:
    padrao = r"^\d{9}[A-Za-z]{2}\d{3}$"
    return bool(re.match(padrao, bi.strip()))

def validar_telefone_angolano(telefone: str) -> bool:
    padrao = r"^9[1234579]\d{7}$"
    return bool(re.match(padrao, telefone.strip()))

def obter_saudacao_fuso() -> str:
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "Bom dia"
    elif 12 <= hora < 18:
        return "Boa tarde"
    else:
        return "Boa noite"