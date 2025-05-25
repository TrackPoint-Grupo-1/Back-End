import requests
import os
from dotenv import load_dotenv

load_dotenv()

PIPEFY_API_URL = "https://api.pipefy.com/graphql"
PIPEFY_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE3NDgxODY1MTAsImp0aSI6IjZmMWM0ZjAyLTBkYTgtNGFiNS04MjM0LTQwN2FmNzYwZTk2MCIsInN1YiI6MzA2NjkyNTI5LCJ1c2VyIjp7ImlkIjozMDY2OTI1MjksImVtYWlsIjoiYnJ1ZG5leXJhbW9zYnJ1LWRuZXlAb3V0bG9vay5jb20ifX0.l5Shotpv-TxFOs6mWkkzhyHyVz7pnIPRsH0vG-_8iXNjWLLpK91ovABhxqM0K5KePFlo_hSpA9AcaCLvvcjfcA"
PIPE_ID = 306424076  # Seu Pipe ID

def criar_card_pipefy(email, descricao):
    mutation = f"""
    mutation {{
      createCard(input: {{
        pipe_id: {PIPE_ID},
        title: "{descricao}",
        fields_attributes: [
          {{field_id: "email_do_funcion_rio", field_value: "{email}"}},
          {{field_id: "atestado_descrito", field_value: "{descricao}"}}
        ]
      }}) {{
        card {{
          id
          title
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {PIPEFY_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(PIPEFY_API_URL, json={"query": mutation}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"❌ Erro ao criar card: {response.status_code}")
        print(response.text)

