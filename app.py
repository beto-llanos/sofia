from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime
import os
import json
import re

load_dotenv()

app = Flask(__name__)
app.secret_key = "sofia-shadow-works-2026"
CORS(app)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_system_prompt():
    now = datetime.now()
    fecha = now.strftime("%B %Y")
    dia = now.day
    return f"""Eres SOFIA, una asistente financiera personal en español para jóvenes mexicanos. Hoy es {fecha}, día {dia} del mes.

CATEGORIAS: Comida (restaurantes, super, tacos, antojitos), Transporte (uber, taxi, metro, gasolina), Entretenimiento (Netflix, Spotify, cine, juegos), Tecnologia (apps, software, Claude, ChatGPT, hosting, dominios), Ropa, Salud (gym, doctor, medicamentos), Gustos (perfumes, caprichos, lujos), Otros.

REGLAS:
- Español casual y amigable, nunca condescendiente
- Clasifica con sentido común, NUNCA asumas comida si no lo es
- Nunca regañes, enfoca en lo que SÍ puede gastar
- Sé realista con las metas — si no son alcanzables con el ingreso actual, dilo con respeto
- Máximo 4 líneas por respuesta

DATOS DE PRESUPUESTO: Al final de CADA respuesta donde registres un gasto o el usuario pregunte cómo va, agrega en la última línea exactamente este JSON (sin explicación, solo el JSON):
BUDGET_DATA:{{"comida_pct":0,"transporte_pct":0,"entretenimiento_pct":0,"tecnologia_pct":0,"ahorro_pct":0,"meta_pct":0,"disponible":0}}

Rellena los valores reales basándote en la conversación. Los _pct son porcentajes de 0 a 100. disponible es en pesos."""

def get_messages():
    if "messages" not in session:
        session["messages"] = []
    return session["messages"]

def get_perfil():
    if "perfil" not in session:
        session["perfil"] = {}
    return session["perfil"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")
    messages = get_messages()
    perfil = get_perfil()

    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": get_system_prompt()}] + messages[-14:],
        temperature=0.7,
        max_tokens=600
    )

    full_response = response.choices[0].message.content

    # Extract budget data if present
    budget_data = None
    clean_response = full_response
    budget_match = re.search(r'BUDGET_DATA:(\{.*?\})', full_response)
    if budget_match:
        try:
            budget_data = json.loads(budget_match.group(1))
            clean_response = full_response.replace(budget_match.group(0), "").strip()
        except:
            pass

    messages.append({"role": "assistant", "content": clean_response})
    session["messages"] = messages

    return jsonify({
        "response": clean_response,
        "budget": budget_data
    })

@app.route("/api/reset", methods=["POST"])
def reset():
    session.clear()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True)