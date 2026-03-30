# -*- coding: utf-8 -*-
"""
seed_demo.py — Crea cuenta demo lista para el pitch de ALD.IA
Uso: python seed_demo.py
Idempotente: si ya existe la cuenta, la limpia y recrea.
"""
import os, uuid, bcrypt
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
sb = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

DEMO_EMAIL    = "demo@aldia.mx"
DEMO_PASSWORD = "aldia2026"
DEMO_NOMBRE   = "Carlos"
DEMO_SESSION  = "demo-session-aldia-2026-pitch"

def limpiar_demo():
    try:
        sb.table("mensajes").delete().eq("session_id", DEMO_SESSION).execute()
        sb.table("gastos").delete().eq("session_id", DEMO_SESSION).execute()
        sb.table("usuarios").delete().eq("email", DEMO_EMAIL).execute()
        print("✓ Cuenta demo anterior eliminada")
    except Exception as e:
        print(f"  (limpieza): {e}")

def crear_perfil():
    password_hash = bcrypt.hashpw(DEMO_PASSWORD.encode(), bcrypt.gensalt()).decode()
    perfil = {
        "session_id": DEMO_SESSION,
        "email": DEMO_EMAIL,
        "password_hash": password_hash,
        "nombre": DEMO_NOMBRE,
        "ingreso": 15000,
        "meta": 50000,
        "plazo_meses": 12,
        "estrictez": "equilibrado",
        "meta_tipo": "ahorrar",
        "tiene_vivienda": True,
        "tiene_transporte": True,
        "tiene_deudas": True,
        "tiene_educacion": False,
        "onboarding_done": True,
        "perfil_inversor": False,
        "ahorro_disponible": "mitad",
    }
    sb.table("usuarios").insert(perfil).execute()
    print(f"✓ Perfil creado: {DEMO_EMAIL} / {DEMO_PASSWORD}")

def insertar_gastos():
    hoy = datetime.now()
    # Gastos realistas de un mes completo para Carlos, joven profesionista CDMX
    gastos = [
        # VIVIENDA — límite $3,750 (25%) — al 85% = AMARILLO
        {"cat": "vivienda", "monto": 3200, "desc": "Renta depa Roma Norte", "dias_atras": 1},

        # COMIDA — límite $1,800 (12%) — al 98% = ROJO
        {"cat": "comida", "monto": 280, "desc": "Uber Eats sushi", "dias_atras": 2},
        {"cat": "comida", "monto": 120, "desc": "Tacos de canasta", "dias_atras": 3},
        {"cat": "comida", "monto": 450, "desc": "Super Chedraui semanal", "dias_atras": 5},
        {"cat": "comida", "monto": 95,  "desc": "Cafe + croissant", "dias_atras": 6},
        {"cat": "comida", "monto": 180, "desc": "Comida Contramar", "dias_atras": 8},
        {"cat": "comida", "monto": 320, "desc": "Super Walmart", "dias_atras": 10},
        {"cat": "comida", "monto": 110, "desc": "Rappi pizza", "dias_atras": 12},

        # TRANSPORTE — límite $1,800 (12%) — al 70% = AMARILLO
        {"cat": "transporte", "monto": 600, "desc": "Gasolina Honda Civic", "dias_atras": 4},
        {"cat": "transporte", "monto": 180, "desc": "Uber al aeropuerto", "dias_atras": 7},
        {"cat": "transporte", "monto": 420, "desc": "Gasolina recarga", "dias_atras": 14},
        {"cat": "transporte", "monto": 65,  "desc": "Estacionamiento Antara", "dias_atras": 9},

        # SALUD — límite $1,200 (8%) — al 45%
        {"cat": "salud", "monto": 540, "desc": "Gym Smart Fit mensualidad", "dias_atras": 1},

        # OCIO — límite $1,050 (7%) — al 88% = AMARILLO
        {"cat": "ocio", "monto": 299, "desc": "Netflix mensualidad", "dias_atras": 5},
        {"cat": "ocio", "monto": 99,  "desc": "Spotify premium", "dias_atras": 5},
        {"cat": "ocio", "monto": 280, "desc": "Antro Zapote con amigos", "dias_atras": 11},
        {"cat": "ocio", "monto": 249, "desc": "HBO Max", "dias_atras": 5},

        # ROPA — límite $1,200 (8%) — al 55%
        {"cat": "ropa", "monto": 650, "desc": "Nike Air Force tenis", "dias_atras": 15},

        # DEUDAS — límite $1,200 (8%) — al 100% = ROJO
        {"cat": "deudas", "monto": 1200, "desc": "Pago mínimo tarjeta BBVA", "dias_atras": 3},

        # AHORRO — acumulado del mes
        {"cat": "ahorro", "monto": 2000, "desc": "Transferencia Nu Guardadito", "dias_atras": 1},
    ]

    rows = []
    for g in gastos:
        fecha = hoy - timedelta(days=g["dias_atras"])
        rows.append({
            "session_id": DEMO_SESSION,
            "categoria": g["cat"],
            "monto": g["monto"],
            "descripcion": g["desc"],
            "created_at": fecha.isoformat(),
        })

    sb.table("gastos").insert(rows).execute()
    print(f"✓ {len(rows)} gastos insertados")

    # Resumen visual
    totales = {}
    for g in gastos:
        totales[g["cat"]] = totales.get(g["cat"], 0) + g["monto"]
    limites = {"vivienda":3750,"comida":1800,"transporte":1800,"salud":1200,
               "ocio":1050,"ropa":1200,"deudas":1200,"ahorro":2250}
    print("\n  Categoría       Gastado   Límite   Uso")
    print("  " + "-"*45)
    for cat, lim in limites.items():
        gastado = totales.get(cat, 0)
        pct = round(gastado/lim*100)
        estado = "🔴" if pct>=90 else "🟡" if pct>=70 else "🟢"
        print(f"  {estado} {cat:<14} ${gastado:>6,}   ${lim:>6,}   {pct}%")

def insertar_mensajes():
    msgs = [
        {"rol": "assistant", "contenido": "¡Hola Carlos! 👋 Llevas $8,793 gastados este mes. Tu comida ya está al 98% del límite — tal vez conviene cocinar más en casa esta semana 🍳"},
        {"rol": "user",      "contenido": "gasté 280 en sushi"},
        {"rol": "assistant", "contenido": "Comida registrada ✅ Ya llevas $1,765 en comida este mes — casi al tope de $1,800. Te quedan $6,207 disponibles 💰"},
        {"rol": "user",      "contenido": "¿cómo voy este mes?"},
        {"rol": "assistant", "contenido": "Van $8,793 gastados de $15,000. A este ritmo proyectas gastar $10,551 al mes — vas bien 👍 Comida y deudas son tus categorías más apretadas ⚠️"},
    ]
    rows = [{"session_id": DEMO_SESSION, "rol": m["rol"], "contenido": m["contenido"]} for m in msgs]
    sb.table("mensajes").insert(rows).execute()
    print(f"✓ {len(rows)} mensajes de historial insertados")

if __name__ == "__main__":
    print("🌱 Seeding cuenta demo ALD.IA...\n")
    limpiar_demo()
    crear_perfil()
    insertar_gastos()
    insertar_mensajes()
    print(f"\n✅ Demo lista. Login: {DEMO_EMAIL} / {DEMO_PASSWORD}")
