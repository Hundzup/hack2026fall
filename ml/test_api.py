import json
import requests


with open("data.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

payload = {
    "raw_data": raw_data,
    "settings": {}
}


url = "http://127.0.0.1:8001/analyze"

print("Отправляем запрос")
response = requests.post(url, json=payload)


if response.status_code == 200:
    result = response.json()
    print("\nСводка")
    print(json.dumps(result["summary"], indent=2, ensure_ascii=False))
    
    print("\nтоп 3 максимальной риск")
    # Сортируем по risk_score по убыванию для наглядности
    scored = sorted(result["scored"], key=lambda x: x["risk_score"], reverse=True)
    for client in scored[:3]:
        print(f"ID: {client['customer_id']} | Score: {client['risk_score']} | Level: {client['risk_level']}")
        print(f"Причины: {client['reasons']}\n")
else:
    print(f"Ошибка {response.status_code}: {response.text}")