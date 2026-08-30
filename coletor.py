import requests
from bs4 import BeautifulSoup
import json
import re

cidades = [
    {"bandeira": "🇺🇸", "pais": "EUA (Califórnia)", "url": "https://www.numbeo.com/cost-of-living/in/Los-Angeles?displayCurrency=USD"},
    {"bandeira": "🇪🇸", "pais": "Espanha (Madri)", "url": "https://www.numbeo.com/cost-of-living/in/Madrid?displayCurrency=EUR"},
    {"bandeira": "🇩🇪", "pais": "Alemanha (Berlim)", "url": "https://www.numbeo.com/cost-of-living/in/Berlin?displayCurrency=EUR"},
    {"bandeira": "🇧🇷", "pais": "Brasil (São Paulo)", "url": "https://www.numbeo.com/cost-of-living/in/Sao-Paulo?displayCurrency=BRL"}
]

# Base de segurança caso o Numbeo bloqueie o IP do servidor
dados_padrao = [
  {"bandeira": "🇺🇸", "pais": "EUA (Califórnia)", "salario": 3400, "aluguel": 1500, "parcela": 350, "alimentacao": 450, "entrada": 4000, "eletronico": 1000},
  {"bandeira": "🇪🇸", "pais": "Espanha (Madri)", "salario": 2000, "aluguel": 800, "parcela": 300, "alimentacao": 400, "entrada": 2500, "eletronico": 1000},
  {"bandeira": "🇩🇪", "pais": "Alemanha (Berlim)", "salario": 2700, "aluguel": 950, "parcela": 300, "alimentacao": 380, "entrada": 3000, "eletronico": 1000},
  {"bandeira": "🇧🇷", "pais": "Brasil (São Paulo)", "salario": 3000, "aluguel": 2200, "parcela": 1200, "alimentacao": 700, "entrada": 15000, "eletronico": 5000}
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5"
}

resultados = []

for item in cidades:
    try:
        resp = requests.get(item["url"], headers=headers, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            tabela = soup.find("table", class_="data_wide_table")
            
            if tabela:
                def extrair(texto_item):
                    for tr in tabela.find_all("tr"):
                        if texto_item.lower() in tr.text.lower():
                            tds = tr.find_all("td")
                            if len(tds) > 1:
                                clean_num = re.sub(r"[^\d.]", "", tds[1].text.replace(",", ""))
                                return float(clean_num) if clean_num else 0.0
                    return 0.0

                salario = extrair("Average Monthly Net Salary")
                aluguel = extrair("Apartment (1 bedroom) Outside of Centre")
                carro_preco = extrair("Volkswagen Golf")
                
                leite = extrair("Milk (regular), (1 liter)") * 10
                arroz = extrair("Rice (white), (1kg)") * 3
                ovos = extrair("Eggs (regular) (12)") * 2
                frango = extrair("Chicken Fillets (1kg)") * 5
                alimentacao = round(leite + arroz + ovos + frango + 150, 2)

                resultados.append({
                    "bandeira": item["bandeira"],
                    "pais": item["pais"],
                    "salario": salario if salario > 0 else 3000,
                    "aluguel": aluguel if aluguel > 0 else 1000,
                    "parcela": round((carro_preco * 0.80) / 48, 2) if carro_preco > 0 else 300,
                    "alimentacao": alimentacao if alimentacao > 150 else 400,
                    "entrada": round(carro_preco * 0.20, 2) if carro_preco > 0 else 4000,
                    "eletronico": round(carro_preco * 0.04, 2) if carro_preco > 0 else 1000
                })
    except Exception:
        pass

# Se o scraping falhar ou for bloqueado, usa a base padrão completa
dados_finais = resultados if len(resultados) == len(cidades) else dados_padrao

with open("paises.json", "w", encoding="utf-8") as f:
    json.dump(dados_finais, f, ensure_ascii=False, indent=2)
