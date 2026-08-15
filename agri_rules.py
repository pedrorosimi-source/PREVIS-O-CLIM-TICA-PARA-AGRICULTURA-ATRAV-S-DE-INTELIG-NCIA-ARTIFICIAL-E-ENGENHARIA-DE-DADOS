REGRAS_CULTURAS = {
    "Milho": {
        "agua_req": "MEDIA_ALTA",
        "temp_ideal": (20.0, 30.0),
        "humidade_ideal": (60.0, 80.0),
        "limite_humidade_colheita": 70.0,
        "limite_precipitacao_colheita": 2.0,
        "dica_colheita": "Secagem dos grãos ideal em dias secos. Evitar colheita com chuva para não mofar."
    },
    "Mandioca": {
        "agua_req": "BAIXA",
        "temp_ideal": (22.0, 32.0),
        "humidade_ideal": (50.0, 75.0),
        "limite_humidade_colheita": 80.0, 
        "limite_precipitacao_colheita": 10.0,
        "dica_colheita": "Raíz resistente. O solo ligeiramente húmido facilita o arranquio manual sem partir as raízes."
    },
    "Laranja": {
        "agua_req": "MEDIA",
        "temp_ideal": (23.0, 31.0),
        "humidade_ideal": (55.0, 70.0),
        "limite_humidade_colheita": 75.0,
        "limite_precipitacao_colheita": 5.0,
        "dica_colheita": "Colher frutos secos para evitar o surgimento de fungos na casca durante o transporte."
    },
    "Cenoura": {
        "agua_req": "ALTA",
        "temp_ideal": (15.0, 22.0),
        "humidade_ideal": (65.0, 85.0),
        "limite_humidade_colheita": 85.0,
        "limite_precipitacao_colheita": 8.0,
        "dica_colheita": "Solo húmido favorece a remoção limpa das raízes tuberosas."
    },
    "Batata Doce": {
        "agua_req": "BAIXA_MEDIA",
        "temp_ideal": (21.0, 29.0),
        "humidade_ideal": (55.0, 75.0),
        "limite_humidade_colheita": 75.0,
        "limite_precipitacao_colheita": 5.0,
        "dica_colheita": "Evitar encharcamento no arranquio para prevenir podridão pós-colheita."
    },
    "Batata Reina": {
        "agua_req": "MEDIA_ALTA",
        "temp_ideal": (15.0, 20.0),
        "humidade_ideal": (70.0, 85.0),
        "limite_humidade_colheita": 75.0,
        "limite_precipitacao_colheita": 3.0,
        "dica_colheita": "Tubérculos sensíveis ao mofo. Colher preferencialmente com solo firme."
    },
    "Limão": {
        "agua_req": "MEDIA",
        "temp_ideal": (22.0, 30.0),
        "humidade_ideal": (50.0, 70.0),
        "limite_humidade_colheita": 75.0,
        "limite_precipitacao_colheita": 5.0,
        "dica_colheita": "Realizar o corte dos frutos em horas secas do dia."
    },
    "Algodão": {
        "agua_req": "BAIXA",
        "temp_ideal": (25.0, 35.0),
        "humidade_ideal": (45.0, 65.0),
        "limite_humidade_colheita": 55.0, 
        "limite_precipitacao_colheita": 0.5, 
        "dica_colheita": "EXIGÊNCIA CRÍTICA: Colheita apenas com tempo estritamente seco para não apodrecer a pluma."
    },
    "Banana": {
        "agua_req": "MUITO_ALTA",
        "temp_ideal": (26.0, 34.0),
        "humidade_ideal": (75.0, 90.0),
        "limite_humidade_colheita": 90.0, 
        "limite_precipitacao_colheita": 15.0,
        "dica_colheita": "Corte de cachos pode ser mantido mesmo em dias húmidos sem prejuízo imediato ao fruto."
    }
}

def gerar_diretrizes_produto(cultura: str, temp: float, humidade: float, prec: float):
    regra = REGRAS_CULTURAS.get(cultura)
    if not regra:
        return "Sem dados", "Sem dados", "Sem dados"

    if prec > 10.0:
        irrigacao = "🌧️ Irrigação Desnecessária (Chuva abundante prevista)."
    elif humidade < regra["humidade_ideal"][0]:
        irrigacao = f"💧 Irrigação RECOMENDADA. Aplicar rega reforçada (Exigência: {regra['agua_req']})."
    else:
        irrigacao = "✅ Solo com humidade adequada. Manter irrigação em nível de manutenção."

    if regra["temp_ideal"][0] <= temp <= regra["temp_ideal"][1] and prec < 15.0:
        plantio = f"🌱 DIA IDEAL para o plantio de {cultura}. Temperatura favorável ({temp:.1f}°C)."
    else:
        plantio = f"⚠️ Não recomendado para plantio. Temperatura ({temp:.1f}°C) fora da janela ideal."

    if prec <= regra["limite_precipitacao_colheita"] and humidade <= regra["limite_humidade_colheita"]:
        cultivo = f"🚜 FAVORÁVEL para colheita/tratos de {cultura}. {regra['dica_colheita']}"
    else:
        cultivo = f"⚠️ NÃO RECOMENDADO colher {cultura} hoje (Chuva: {prec:.1f}mm, Humidade: {humidade:.1f}%). {regra['dica_colheita']}"

    return irrigacao, plantio, cultivo