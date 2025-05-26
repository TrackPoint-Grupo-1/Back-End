import requests

PIPEFY_API_URL = "https://api.pipefy.com/graphql"
PIPEFY_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJQaXBlZnkiLCJpYXQiOjE3NDgyOTU2MDMsImp0aSI6IjhjN2E3OWQ3LTkyZmItNDRmZC1iNzFkLWRhOWJlNjk0MzBmMiIsInN1YiI6MzA2NjkyNTI5LCJ1c2VyIjp7ImlkIjozMDY2OTI1MjksImVtYWlsIjoiYnJ1ZG5leXJhbW9zYnJ1LWRuZXlAb3V0bG9vay5jb20ifX0.lINV4fGbLN2ZWWoPLr5iVEjZDzppw4TRXnTlWF6Co0VECFrRSD7jBeEdR8Hofc3G8Zyu7x02Hc8KPH6DNbJFdw"  # Coloque aqui o seu token de autenticação Pipefy


def criar_card_pipefy(nome, email, descricao, id):
    url = PIPEFY_API_URL
    token = PIPEFY_TOKEN

    query = """
        mutation {
          createCard(input: {
            pipe_id: 306427017,
            fields_attributes: [
              {field_id: "who_is_requesting", field_value: "%s"},
              {field_id: "email_do_solicitante", field_value: "%s"},
              {field_id: "more_info", field_value: "%s"},
              {field_id: "id_do_atestado", field_value: "%s"}
            ]
          }) {
            card {
              id
              title
            }
          }
        }
        """ % (nome, email, descricao, id)

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json={"query": query}, headers=headers)

    if response.status_code == 200:
        resp_json = response.json()
        if "errors" in resp_json:
            raise Exception(f"Erro na API Pipefy: {resp_json['errors']}")
        return resp_json["data"]["createCard"]["card"]
    else:
        raise Exception(f"Erro HTTP {response.status_code}: {response.text}")

def buscar_card_por_id_atestado(id_atestado):
    query = """
    query {
      phase(id: 338824938) {  # id da fase "Caixa de entrada"
        cards {
          edges {
            node {
              id
              title
              fields {
                name
                value
              }
            }
          }
        }
      }
    }
    """

    headers = {
        "Authorization": f"Bearer {PIPEFY_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(PIPEFY_API_URL, json={"query": query}, headers=headers)
    response.raise_for_status()
    data = response.json()

    for edge in data.get("data", {}).get("phase", {}).get("cards", {}).get("edges", []):
        card = edge["node"]
        for field in card["fields"]:
            if field["name"] == "ID do atestado" and field["value"] == str(id_atestado):
                return card
    return None

def mover_card_para_aprovado(card_id):
    mutation = f"""
    mutation {{
      moveCardToPhase(input: {{
        card_id: "{card_id}",
        destination_phase_id: "338824940"
      }}) {{
        card {{
          id
          title
          current_phase {{
            id
            name
          }}
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {PIPEFY_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(PIPEFY_API_URL, json={"query": mutation}, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        print(f"❌ Erro ao mover card: {data['errors']}")
        return False

    print(f"✅ Card {card_id} movido para fase Aprovadas!")
    return True

def aprovar_atestado_no_pipefy(id_atestado):
    card = buscar_card_por_id_atestado(id_atestado)
    if not card:
        print(f"Card para atestado ID {id_atestado} não encontrado.")
        return False

    return mover_card_para_aprovado(card["id"])

def mover_card_para_reprovado(card_id):
    mutation = f"""
    mutation {{
      moveCardToPhase(input: {{
        card_id: "{card_id}",
        destination_phase_id: "338824939"
      }}) {{
        card {{
          id
          title
          current_phase {{
            id
            name
          }}
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {PIPEFY_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(PIPEFY_API_URL, json={"query": mutation}, headers=headers)
    response.raise_for_status()
    data = response.json()

    if "errors" in data:
        print(f"❌ Erro ao mover card: {data['errors']}")
        return False

    print(f"✅ Card {card_id} movido para fase Reprovados!")
    return True

def reprovar_atestado_no_pipefy(id_atestado):
    card = buscar_card_por_id_atestado(id_atestado)
    if not card:
        print(f"Card para atestado ID {id_atestado} não encontrado.")
        return False

    return mover_card_para_reprovado(card["id"])
