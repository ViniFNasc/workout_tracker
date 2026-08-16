
import hashlib
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date, datetime

# ============================================================
# CONFIGURAÇÃO
# ============================================================
st.set_page_config(
    page_title="Low Volume Tracker",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

TREINOS_FILE = DATA_DIR / "treinos.csv"
USUARIOS_FILE = DATA_DIR / "usuarios.csv"

USUARIO_COLUMNS = [
    "usuario",
    "senha_hash",
    "nome_exibicao",
    "ativo",
]

TREINO_COLUMNS = [
    "id",
    "usuario",
    "data",
    "treino",
    "grupo_muscular",
    "exercicio",
    "numero_serie",
    "metodo",
    "percentual_carga",
    "carga_trabalho_kg",
    "carga_kg",
    "reps_alvo",
    "repeticoes",
    "rir_alvo",
    "rir",
    "velocidade",
    "tempo_descanso",
]

METODOS = ["Preparatória", "Work-set", "Muscle Round"]

# ============================================================
# PLANO DE TREINO (Upper/Lower 4x) — fixo, extraído do PDF.
# Percentuais, reps-alvo, RIR-alvo, velocidade e intervalo são
# travados: vêm sempre daqui, o usuário não os edita.
# ============================================================

PLANO = {
    "Upper I": [
        {
            "exercicio": "T-Bar Row",
            "grupo_muscular": "Costas",
            "observacoes": "Como substituto, pode fazer na polia baixa pegada pronada ou com halteres e peito apoiado no banco.",
            "series": [
                {"metodo": "Preparatória", "percentual": 50, "reps_alvo": "10-12", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~30s"},
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Puxada Alta com Triângulo",
            "grupo_muscular": "Costas",
            "observacoes": "Não flexionar ombros em mais que 120°; manter escápula fixa.",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Supino Reto Máquina",
            "grupo_muscular": "Peito",
            "observacoes": "Na falta da máquina sentado, fazer deitado. Pode ser no smith e, em últimos casos, livre (com halteres).",
            "series": [
                {"metodo": "Preparatória", "percentual": 50, "reps_alvo": "10-12", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~30s"},
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Crucifixo na Polia Baixa",
            "grupo_muscular": "Peito",
            "observacoes": "Fazer preferencialmente sentado no banco.",
            "series": [
                {"metodo": "Preparatória", "percentual": 80, "reps_alvo": "3-4", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Elevação Lateral na Máquina",
            "grupo_muscular": "Ombros",
            "observacoes": "Na falta da máquina, fazer na polia baixa ou até mesmo livre.",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Muscle Round", "percentual": 100, "reps_alvo": "-", "rir_alvo": "-", "velocidade": "2-0-1-0", "intervalo": "10s entre blocos"},
            ],
        },
        {
            "exercicio": "Rosca Scott Máquina",
            "grupo_muscular": "Bíceps",
            "observacoes": "Extender 100% dos cotovelos.",
            "series": [
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Muscle Round", "percentual": 100, "reps_alvo": "-", "rir_alvo": "-", "velocidade": "2-0-1-0", "intervalo": "10s entre blocos"},
            ],
        },
        {
            "exercicio": "Tríceps Francês com Corda",
            "grupo_muscular": "Tríceps",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
    ],
    "Lower I": [
        {
            "exercicio": "Cadeira Flexora",
            "grupo_muscular": "Pernas",
            "observacoes": "Flexionar quadril (inclinar tronco para frente).",
            "series": [
                {"metodo": "Preparatória", "percentual": 50, "reps_alvo": "10-12", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~30s"},
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Agachamento Hack 45",
            "grupo_muscular": "Pernas",
            "observacoes": "Sempre busque amplitude máxima. Na falta do Hack, fazer no smith. Em últimos casos, livre.",
            "series": [
                {"metodo": "Preparatória", "percentual": 50, "reps_alvo": "10-12", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~30s"},
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "180s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "180s"},
            ],
        },
        {
            "exercicio": "Cadeira Adutora",
            "grupo_muscular": "Pernas",
            "observacoes": "Caso já tenha zerado a máquina, faça com o quadril flexionado (tronco para frente) ou unilateralmente.",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Elevação Pélvica na Máquina",
            "grupo_muscular": "Pernas",
            "observacoes": "Na falta da máquina, fazer no smith. Em últimos casos, livre.",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "180s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "180s"},
            ],
        },
        {
            "exercicio": "Cadeira Extensora",
            "grupo_muscular": "Pernas",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Extensão de Panturrilhas em Pé",
            "grupo_muscular": "Panturrilhas",
            "observacoes": "Na falta da máquina, fazer no smith com step.",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
    ],
    "Upper II": [
        {
            "exercicio": "Supino Inclinado Máquina",
            "grupo_muscular": "Peito",
            "observacoes": "Cotovelos bem rente ao corpo, focar em flexão do ombro. Na falta da máquina, fazer no smith ou livre.",
            "series": [
                {"metodo": "Preparatória", "percentual": 50, "reps_alvo": "10-12", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~30s"},
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Puxada Alta Pronada",
            "grupo_muscular": "Costas",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-1", "intervalo": "150s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "150s"},
            ],
        },
        {
            "exercicio": "Crucifixo Máquina",
            "grupo_muscular": "Peito",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Remada Baixa Unilateral Neutra",
            "grupo_muscular": "Costas",
            "observacoes": "Cotovelo rente ao tronco. Não passar cotovelos da linha do tronco.",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Kelso Shrugs",
            "grupo_muscular": "Costas",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Elevação Lateral com Halteres",
            "grupo_muscular": "Ombros",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": 'Rosca Direta de Costas para Polia (Pegador "V"/"W")',
            "grupo_muscular": "Bíceps",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Muscle Round", "percentual": 100, "reps_alvo": "-", "rir_alvo": "-", "velocidade": "2-0-1-0", "intervalo": "10s entre blocos"},
            ],
        },
        {
            "exercicio": 'Tríceps de Costas para a Polia (Barra "W")',
            "grupo_muscular": "Tríceps",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Muscle Round", "percentual": 100, "reps_alvo": "-", "rir_alvo": "-", "velocidade": "2-0-1-0", "intervalo": "10s entre blocos"},
            ],
        },
    ],
    "Lower II": [
        {
            "exercicio": "Stiff",
            "grupo_muscular": "Pernas",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 50, "reps_alvo": "10-12", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~30s"},
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-1", "intervalo": "180s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "180s"},
            ],
        },
        {
            "exercicio": "Leg Press 45",
            "grupo_muscular": "Pernas",
            "observacoes": "Pés baixos na plataforma. Busque o máximo de amplitude possível.",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-1", "intervalo": "180s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "180s"},
            ],
        },
        {
            "exercicio": "Mesa Flexora",
            "grupo_muscular": "Pernas",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 75, "reps_alvo": "5", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Preparatória", "percentual": 90, "reps_alvo": "2", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~60s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Afundo no Smith Unilateral com Step à Frente",
            "grupo_muscular": "Pernas",
            "observacoes": "Controle a excêntrica, joelho de trás praticamente toca o chão em todas as reps.",
            "series": [
                {"metodo": "Preparatória", "percentual": 80, "reps_alvo": "6", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "180s"},
            ],
        },
        {
            "exercicio": "Cadeira Extensora",
            "grupo_muscular": "Pernas",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 80, "reps_alvo": "6", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
        {
            "exercicio": "Banco Solear",
            "grupo_muscular": "Panturrilhas",
            "observacoes": "",
            "series": [
                {"metodo": "Preparatória", "percentual": 80, "reps_alvo": "6", "rir_alvo": ">5", "velocidade": "2-0-1-0", "intervalo": "~45s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "1", "velocidade": "2-0-1-0", "intervalo": "120s"},
                {"metodo": "Work-set", "percentual": 100, "reps_alvo": "5-9", "rir_alvo": "0", "velocidade": "2-0-1-0", "intervalo": "120s"},
            ],
        },
    ],
}

# Numera as séries de cada exercício sequencialmente (1, 2, 3...).
for _exercicios in PLANO.values():
    for _ex in _exercicios:
        for _i, _serie in enumerate(_ex["series"], start=1):
            _serie["numero"] = _i


def inicializar_arquivos():
    if not TREINOS_FILE.exists():
        pd.DataFrame(columns=TREINO_COLUMNS).to_csv(
            TREINOS_FILE, index=False, encoding="utf-8-sig"
        )

    if not USUARIOS_FILE.exists():
        pd.DataFrame(columns=USUARIO_COLUMNS).to_csv(
            USUARIOS_FILE, index=False, encoding="utf-8-sig"
        )


def carregar_usuarios():
    df = pd.read_csv(USUARIOS_FILE, encoding="utf-8-sig", dtype=str)

    if df.empty:
        return pd.DataFrame(columns=USUARIO_COLUMNS)

    df["ativo"] = df["ativo"].astype(str).str.lower().isin(
        ["true", "1", "sim", "yes"]
    )

    return df


def hash_senha(senha):
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


def verificar_login(usuario, senha, df_usuarios):
    if not usuario or not senha:
        return False

    linha = df_usuarios[
        (df_usuarios["usuario"] == usuario) & (df_usuarios["ativo"])
    ]

    if linha.empty:
        return False

    return hash_senha(senha) == linha.iloc[0]["senha_hash"]


def nome_para_exibicao(usuario, df_usuarios):
    linha = df_usuarios[df_usuarios["usuario"] == usuario]

    if linha.empty:
        return usuario

    nome = linha.iloc[0]["nome_exibicao"]

    if pd.isna(nome) or not str(nome).strip():
        return usuario

    return str(nome).strip()


def carregar_treinos():
    df = pd.read_csv(TREINOS_FILE, encoding="utf-8-sig")

    if df.empty:
        return pd.DataFrame(columns=TREINO_COLUMNS)

    df["data"] = pd.to_datetime(df["data"], errors="coerce").dt.date

    numeric_cols = [
        "id",
        "numero_serie",
        "percentual_carga",
        "carga_trabalho_kg",
        "carga_kg",
        "repeticoes",
        "rir",
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def salvar_treinos(df):
    df.to_csv(TREINOS_FILE, index=False, encoding="utf-8-sig")


def proximo_id(df):
    if df.empty or df["id"].dropna().empty:
        return 1
    return int(df["id"].max()) + 1


def formatar_carga(valor):
    if pd.isna(valor):
        return "-"
    return f"{valor:.1f} kg"


def obter_referencia_exercicio(df_usuario, exercicio):
    """Retorna dados da última vez que o usuário fez esse exercício."""
    dados = df_usuario[df_usuario["exercicio"] == exercicio]

    if dados.empty:
        return None

    ultima_data = dados["data"].max()
    dados_ultima = dados[dados["data"] == ultima_data]

    carga_trabalho_serie = dados_ultima["carga_trabalho_kg"].dropna()
    carga_trabalho = (
        float(carga_trabalho_serie.iloc[0])
        if not carga_trabalho_serie.empty
        else 0.0
    )

    ultima_ws = dados_ultima[
        dados_ultima["metodo"] == "Work-set"
    ].sort_values("numero_serie")

    ultima_falha = None
    if not ultima_ws.empty:
        linha = ultima_ws.iloc[-1]
        reps_val = linha["repeticoes"]
        rir_val = linha["rir"]
        ultima_falha = {
            "reps": int(reps_val) if pd.notna(reps_val) else None,
            "rir": int(rir_val) if pd.notna(rir_val) else None,
        }

    return {
        "data": ultima_data,
        "carga_trabalho": carga_trabalho,
        "ultima_falha": ultima_falha,
    }


# ============================================================
# INICIALIZAÇÃO
# ============================================================
inicializar_arquivos()

# ============================================================
# LOGIN
# ============================================================
if "usuario_logado" not in st.session_state:
    st.session_state.usuario_logado = None

df_usuarios = carregar_usuarios()

if st.session_state.usuario_logado is None:
    st.title("🔐 Login")
    st.caption("Entre com seu usuário e senha para acessar o Low Volume Tracker.")

    if df_usuarios.empty:
        st.warning(
            "Nenhum usuário cadastrado ainda. Peça para o administrador "
            "adicionar seu usuário em `data/usuarios.csv` (veja o README)."
        )

    with st.form("login_form"):
        usuario_input = st.text_input("Usuário")
        senha_input = st.text_input("Senha", type="password")
        entrar = st.form_submit_button(
            "Entrar", type="primary", use_container_width=True
        )

    if entrar:
        usuario_input = usuario_input.strip()

        if verificar_login(usuario_input, senha_input, df_usuarios):
            st.session_state.usuario_logado = usuario_input
            st.session_state.nome_exibicao = nome_para_exibicao(
                usuario_input, df_usuarios
            )
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

    st.stop()

df_treinos = carregar_treinos()

# ============================================================
# CSS
# ============================================================
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
            max-width: 1400px;
        }

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128,128,128,.2);
            padding: 12px;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🏋️ Low Volume")
st.sidebar.caption("Upper/Lower 4x — registro e acompanhamento")

pagina = st.sidebar.radio(
    "Navegação",
    [
        "📊 Dashboard",
        "➕ Registrar treino",
        "📚 Histórico",
        "📋 Plano de treino",
    ],
)

st.sidebar.divider()

meus_treinos = df_treinos[df_treinos["usuario"] == st.session_state.usuario_logado]

if not meus_treinos.empty:
    st.sidebar.metric("Meus treinos registrados", meus_treinos["data"].nunique())
    st.sidebar.metric("Minhas séries registradas", len(meus_treinos))
    st.sidebar.metric("Meus exercícios usados", meus_treinos["exercicio"].nunique())

st.sidebar.divider()
st.sidebar.caption(f"👤 Logado como **{st.session_state.nome_exibicao}**")

if st.sidebar.button("Sair", use_container_width=True):
    st.session_state.usuario_logado = None
    st.session_state.nome_exibicao = None
    st.rerun()


# ============================================================
# DASHBOARD
# ============================================================
if pagina == "📊 Dashboard":
    st.title("📊 Dashboard")
    st.caption("Visão geral da sua evolução no treinamento low volume.")

    if df_treinos.empty:
        st.info("Ainda não existem treinos registrados. Vá em **Registrar treino** para começar.")
    else:
        usuarios_disponiveis = sorted(df_treinos["usuario"].dropna().unique())

        if st.session_state.usuario_logado not in usuarios_disponiveis:
            usuarios_disponiveis = [st.session_state.usuario_logado] + usuarios_disponiveis

        usuario_visualizado = st.selectbox(
            "👤 Ver dados de",
            usuarios_disponiveis,
            index=usuarios_disponiveis.index(st.session_state.usuario_logado),
        )

        df_dash = df_treinos[df_treinos["usuario"] == usuario_visualizado]

        if df_dash.empty:
            st.info("Nenhum treino registrado ainda para este usuário.")
        else:
            ultima_data = df_dash["data"].max()
            ultimo_treino = df_dash[df_dash["data"] == ultima_data]

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Último treino", ultima_data.strftime("%d/%m/%Y"))
            c2.metric("Exercícios", ultimo_treino["exercicio"].nunique())
            c3.metric("Séries", len(ultimo_treino))
            c4.metric(
                "Volume",
                f"{(ultimo_treino['repeticoes'] * ultimo_treino['carga_kg']).sum():,.0f} kg"
            )

            st.divider()

            st.subheader("📈 Evolução por exercício")

            exercicios_usados = sorted(df_dash["exercicio"].dropna().unique())

            exercicio = st.selectbox(
                "Escolha um exercício",
                exercicios_usados,
            )

            dados_ex = df_dash[df_dash["exercicio"] == exercicio].copy()

            evolucao = (
                dados_ex.groupby("data", as_index=False)
                .agg(
                    carga_max=("carga_kg", "max"),
                )
            )

            st.line_chart(
                evolucao.set_index("data")[["carga_max"]],
                y_label="Carga máxima na sessão (kg)",
            )

            st.subheader("📋 Últimas execuções")

            ultimas = dados_ex.sort_values(
                ["data", "numero_serie"],
                ascending=[False, True],
            ).head(10)

            ultimas["data"] = ultimas["data"].apply(
                lambda x: x.strftime("%d/%m/%Y")
            )

            st.dataframe(
                ultimas[
                    [
                        "data",
                        "metodo",
                        "numero_serie",
                        "reps_alvo",
                        "repeticoes",
                        "rir_alvo",
                        "rir",
                        "carga_kg",
                    ]
                ].rename(
                    columns={
                        "metodo": "Método",
                        "numero_serie": "Série",
                        "reps_alvo": "Alvo reps",
                        "repeticoes": "Reps",
                        "rir_alvo": "RIR alvo",
                        "rir": "RIR",
                        "carga_kg": "Carga",
                    }
                ),
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# REGISTRAR TREINO
# ============================================================
elif pagina == "➕ Registrar treino":
    st.title("➕ Registrar treino")
    st.caption(
        f"Registrando como **{st.session_state.nome_exibicao}**. "
        "Preencha a carga de trabalho e as repetições — % da carga, "
        "alvo de reps, RIR-alvo, velocidade e intervalo já vêm do plano."
    )

    meus_treinos_df = df_treinos[
        df_treinos["usuario"] == st.session_state.usuario_logado
    ]

    col1, col2 = st.columns(2)

    with col1:
        data_treino = st.date_input("Data", value=date.today())

    with col2:
        treino_selecionado = st.selectbox("Treino", list(PLANO.keys()))

    st.divider()

    respostas = {}

    for exercicio_info in PLANO[treino_selecionado]:
        nome = exercicio_info["exercicio"]

        with st.expander(f"🏋️ {nome}", expanded=True):
            if exercicio_info["observacoes"]:
                st.caption(f"💡 {exercicio_info['observacoes']}")

            referencia = obter_referencia_exercicio(meus_treinos_df, nome)

            valor_padrao_carga = 0.0
            if referencia is not None:
                valor_padrao_carga = referencia["carga_trabalho"]

                texto_ref = (
                    f"📌 Última vez ({referencia['data'].strftime('%d/%m/%Y')}): "
                    f"carga de trabalho **{formatar_carga(referencia['carga_trabalho'])}**"
                )

                if referencia["ultima_falha"] is not None:
                    falha = referencia["ultima_falha"]
                    if falha["reps"] is not None:
                        texto_ref += (
                            f" · última work-set: **{falha['reps']} reps**"
                        )
                        if falha["rir"] is not None:
                            texto_ref += f" (RIR {falha['rir']})"

                st.info(texto_ref)

            carga_trabalho = st.number_input(
                "Carga de trabalho (kg)",
                min_value=0.0,
                max_value=1000.0,
                value=valor_padrao_carga,
                step=0.5,
                key=f"carga_{treino_selecionado}_{nome}",
                help="Todas as séries abaixo são calculadas como % desse valor.",
            )

            linhas = []
            for s in exercicio_info["series"]:
                carga_calculada = round(carga_trabalho * s["percentual"] / 100, 1)
                linhas.append(
                    {
                        "Série": s["numero"],
                        "Método": s["metodo"],
                        "% carga": f"{s['percentual']}%",
                        "Alvo reps": s["reps_alvo"],
                        "RIR alvo": s["rir_alvo"],
                        "Vel.": s["velocidade"],
                        "Interv.": s["intervalo"],
                        "Carga (kg)": carga_calculada,
                        "Reps": 0,
                        "RIR": None,
                    }
                )

            df_tabela = pd.DataFrame(linhas)

            tabela_editada = st.data_editor(
                df_tabela,
                key=f"editor_{treino_selecionado}_{nome}",
                hide_index=True,
                use_container_width=True,
                disabled=[
                    "Série",
                    "Método",
                    "% carga",
                    "Alvo reps",
                    "RIR alvo",
                    "Vel.",
                    "Interv.",
                    "Carga (kg)",
                ],
                column_config={
                    "Reps": st.column_config.NumberColumn(
                        "Reps", min_value=0, max_value=100, step=1
                    ),
                    "RIR": st.column_config.NumberColumn(
                        "RIR", min_value=0, max_value=10, step=1
                    ),
                },
            )

            respostas[nome] = {
                "grupo_muscular": exercicio_info["grupo_muscular"],
                "carga_trabalho": carga_trabalho,
                "tabela": tabela_editada,
                "series_plano": exercicio_info["series"],
            }

    st.divider()

    if st.button(
        "💾 Salvar treino",
        type="primary",
        use_container_width=True,
    ):
        novos = []
        proximo = proximo_id(df_treinos)

        for nome, dados in respostas.items():
            tabela = dados["tabela"]

            for idx, linha in tabela.reset_index(drop=True).iterrows():
                reps = linha["Reps"]

                if pd.isna(reps) or reps <= 0:
                    continue

                serie_plano = dados["series_plano"][idx]
                rir_valor = linha["RIR"]

                novos.append(
                    {
                        "id": proximo + len(novos),
                        "usuario": st.session_state.usuario_logado,
                        "data": data_treino,
                        "treino": treino_selecionado,
                        "grupo_muscular": dados["grupo_muscular"],
                        "exercicio": nome,
                        "numero_serie": serie_plano["numero"],
                        "metodo": serie_plano["metodo"],
                        "percentual_carga": serie_plano["percentual"],
                        "carga_trabalho_kg": dados["carga_trabalho"],
                        "carga_kg": round(
                            dados["carga_trabalho"] * serie_plano["percentual"] / 100,
                            2,
                        ),
                        "reps_alvo": serie_plano["reps_alvo"],
                        "repeticoes": reps,
                        "rir_alvo": serie_plano["rir_alvo"],
                        "rir": rir_valor if pd.notna(rir_valor) else None,
                        "velocidade": serie_plano["velocidade"],
                        "tempo_descanso": serie_plano["intervalo"],
                    }
                )

        if not novos:
            st.error(
                "Nenhuma série preenchida. Informe pelo menos as repetições "
                "de uma série em algum exercício."
            )
        else:
            df_novos = pd.DataFrame(novos, columns=TREINO_COLUMNS)

            df_final = pd.concat(
                [df_treinos, df_novos],
                ignore_index=True,
            )

            salvar_treinos(df_final)

            st.success(
                f"✅ Treino salvo! {len(novos)} série(s) registrada(s)."
            )

            st.rerun()


# ============================================================
# HISTÓRICO
# ============================================================
elif pagina == "📚 Histórico":
    st.title("📚 Histórico")
    st.caption("Consulte, filtre e analise todos os registros.")

    if df_treinos.empty:
        st.info("Nenhum registro encontrado.")
    else:
        c0, c1, c2, c3, c4 = st.columns(5)

        with c0:
            usuarios_filtro = sorted(df_treinos["usuario"].dropna().unique())
            usuario_filtro = st.selectbox(
                "Usuário",
                ["Todos"] + usuarios_filtro,
            )

        with c1:
            datas = sorted(df_treinos["data"].dropna().unique(), reverse=True)
            data_filtro = st.selectbox(
                "Data",
                ["Todas"] + [d.strftime("%d/%m/%Y") for d in datas],
            )

        with c2:
            exercicios_filtro = sorted(df_treinos["exercicio"].unique())
            exercicio_filtro = st.selectbox(
                "Exercício",
                ["Todos"] + exercicios_filtro,
            )

        with c3:
            treinos_filtro = sorted(df_treinos["treino"].unique())
            treino_filtro = st.selectbox(
                "Treino",
                ["Todos"] + treinos_filtro,
            )

        with c4:
            metodo_filtro = st.selectbox(
                "Método",
                ["Todos"] + METODOS,
            )

        filtrado = df_treinos.copy()

        if usuario_filtro != "Todos":
            filtrado = filtrado[filtrado["usuario"] == usuario_filtro]

        if data_filtro != "Todas":
            data_obj = datetime.strptime(
                data_filtro, "%d/%m/%Y"
            ).date()
            filtrado = filtrado[filtrado["data"] == data_obj]

        if exercicio_filtro != "Todos":
            filtrado = filtrado[
                filtrado["exercicio"] == exercicio_filtro
            ]

        if treino_filtro != "Todos":
            filtrado = filtrado[
                filtrado["treino"] == treino_filtro
            ]

        if metodo_filtro != "Todos":
            filtrado = filtrado[
                filtrado["metodo"] == metodo_filtro
            ]

        st.write(f"**{len(filtrado)} série(s) encontrada(s)**")

        tabela = filtrado.sort_values(
            ["data", "exercicio", "numero_serie"],
            ascending=[False, True, True],
        ).copy()

        tabela["data"] = tabela["data"].apply(
            lambda x: x.strftime("%d/%m/%Y")
        )

        st.dataframe(
            tabela[
                [
                    "usuario",
                    "data",
                    "treino",
                    "grupo_muscular",
                    "exercicio",
                    "numero_serie",
                    "metodo",
                    "percentual_carga",
                    "carga_kg",
                    "reps_alvo",
                    "repeticoes",
                    "rir_alvo",
                    "rir",
                    "velocidade",
                    "tempo_descanso",
                ]
            ].rename(
                columns={
                    "usuario": "Usuário",
                    "numero_serie": "Série",
                    "metodo": "Método",
                    "percentual_carga": "% carga",
                    "carga_kg": "Carga",
                    "reps_alvo": "Alvo reps",
                    "repeticoes": "Reps",
                    "rir_alvo": "RIR alvo",
                    "tempo_descanso": "Intervalo",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

        st.divider()

        st.subheader("📈 Volume por data")

        tabela_volume = filtrado.copy()
        tabela_volume["volume"] = (
            tabela_volume["repeticoes"] * tabela_volume["carga_kg"]
        )

        volume_data = (
            tabela_volume.groupby("data")["volume"]
            .sum()
            .sort_index()
        )

        if not volume_data.empty:
            st.bar_chart(volume_data)


# ============================================================
# PLANO DE TREINO
# ============================================================
elif pagina == "📋 Plano de treino":
    st.title("📋 Plano de treino")
    st.caption(
        "Rotina Upper/Lower 4x. % de carga, alvo de reps, RIR-alvo, "
        "velocidade e intervalo são fixos — vêm sempre daqui."
    )

    abas = st.tabs(list(PLANO.keys()))

    for aba, treino_nome in zip(abas, PLANO.keys()):
        with aba:
            for exercicio_info in PLANO[treino_nome]:
                with st.expander(
                    f"🏋️ {exercicio_info['exercicio']}  ·  {exercicio_info['grupo_muscular']}"
                ):
                    if exercicio_info["observacoes"]:
                        st.caption(f"💡 {exercicio_info['observacoes']}")

                    linhas = []
                    for s in exercicio_info["series"]:
                        linhas.append(
                            {
                                "Série": s["numero"],
                                "Método": s["metodo"],
                                "% carga": f"{s['percentual']}%",
                                "Alvo reps": s["reps_alvo"],
                                "RIR alvo": s["rir_alvo"],
                                "Velocidade": s["velocidade"],
                                "Intervalo": s["intervalo"],
                            }
                        )

                    st.dataframe(
                        pd.DataFrame(linhas),
                        use_container_width=True,
                        hide_index=True,
                    )
