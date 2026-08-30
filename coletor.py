import requests
from bs4 import BeautifulSoup
import json
import re

cidades = [
    {
        "bandeira": "🇺🇸",
        "pais": "EUA (Califórnia)",
        "url": "https://www.numbeo.com/cost-of-living/in/Los-Angeles?displayCurrency=USD"
    },
    {
        "bandeira": "🇪🇸",
        "pais": "Espanha (Madri)",
        "url": "https://www.numbeo.com/cost-of-living/in/Madrid?displayCurrency=EUR"
    },
    {
        "bandeira": "🇩🇪",
        "pais": "Alemanha (Berlim)",
        "url": "https://www.numbeo.com/cost-of-living/in/Berlin?displayCurrency=EUR"
    },
    {
        "bandeira": "🇧🇷",
        "pais": "Brasil (São Paulo)",
        "url": "https://www.numbeo.com/cost-of-living/in/Sao-Paulo?displayCurrency=BRL"
    }
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

resultados = []

for item in cidades:
    try:
        resp = requests.get(item["url"], headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        tabela = soup.find("table", class_="data_wide_table")
        
        if not tabela:
            print(f"Não foi possível ler a tabela para {item['pais']}")
            continue

        def extrair(texto_item):
            for tr in tabela.find_all("tr"):
                if texto_item.lower() in tr.text.lower():
                    tds = tr.find_all("td")
                    if len(tds) > 1:
                        clean_num = re.sub(r"[^\d.]", "", tds[1].text.replace(",", ""))
                        return float(clean_num) if clean_num else 0.0
            return 0.0

        # Coleta das métricas reais
        salario = extrair("Average Monthly Net Salary")
        aluguel = extrair("Apartment (1 bedroom) Outside of Centre")
        carro_preco = extrair("Volkswagen Golf")
        
        # Cesta básica de alimentação mensal (1 pessoa)
        leite = extrair("Milk (regular), (1 liter)") * 10
        arroz = extrair("Rice (white), (1kg)") * 3
        ovos = extrair("Eggs (regular) (12)") * 2
        frango = extrair("Chicken Fillets (1kg)") * 5
        alimentacao = round(leite + arroz + ovos + frango + 150, 2)

        # Regras de financiamento e bens
        entrada_carro = round(carro_preco * 0.20, 2)
        parcela_carro = round((carro_preco * 0.80) / 48, 2)
        eletronico = round(carro_preco * 0.04, 2)

        resultados.append({
            "bandeira": item["bandeira"],
            "pais": item["pais"],
            "salario": salario,
            "aluguel": aluguel,
            "parcela": parcela_carro,
            "alimentacao": alimentacao,
            "entrada": entrada_carro,
            "eletronico": eletronico
        })
        print(f"Sucesso ao processar {item['pais']}")

    except Exception as e:
        print(f"Erro ao coletar {item['pais']}: {e}")

with open("paises.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print("Arquivo 'paises.json' gerado com sucesso!")
