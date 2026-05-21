import os
import json
import uuid
import re
from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__, static_folder='.', static_url_path='')
app.secret_key = 'punto_grafico_super_secret_liquid_key_2026'

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB_USERS = 'usuarios.json'
if not os.path.exists(DB_USERS):
    with open(DB_USERS, 'w', encoding='utf-8') as f:
        json.dump({}, f)

DB_PEDIDOS = 'Base_Datos_Clientes.txt'
if not os.path.exists(DB_PEDIDOS):
    with open(DB_PEDIDOS, 'w', encoding='utf-8') as f:
        f.write("=== REGISTRO DE PEDIDOS DE PUNTO GRÁFICO ===\n\n")

DB_HISTORIAL = 'historial_compras.json'
if not os.path.exists(DB_HISTORIAL):
    with open(DB_HISTORIAL, 'w', encoding='utf-8') as f:
        json.dump({}, f)

DB_PORTAFOLIO = 'portafolio.json'
DEFAULT_PORTAFOLIO = [
    {"id": "p1", "titulo": "Diseño de Pizzas", "desc": "Trabajo publicitario y conceptualización de menús y branding enfocado en el sector gastronómico.", "img": "flyer1.png"},
    {"id": "p2", "titulo": "Convite de Disfraces", "desc": "Entrañas de Occidente - Tradición y cultura plasmadas gráficamente para Rabinal, Baja Verapaz.", "img": "flyer2.png"},
    {"id": "p3", "titulo": "Elección de Reina", "desc": "Diseño de afiche oficial y material promocional premium para el certamen de Rabinal, Baja Verapaz.", "img": "flyer3.png"},
    {"id": "p4", "titulo": "BIG BAND SHEKINA", "desc": "Identidad visual impactante para la promoción oficial de la gira musical en Francia.", "img": "flyer4.png"},
    {"id": "p5", "titulo": "Los Pegasos Music Band", "desc": "Diseño de portada y material gráfico publicitario para la familia musical.", "img": "flyer5.png"},
    {"id": "p6", "titulo": "Día del Diseñador", "desc": "Arte digital conmemorativo institucional con enfoque estético, minimalista y moderno.", "img": "flyer6.png"}
]

if not os.path.exists(DB_PORTAFOLIO):
    with open(DB_PORTAFOLIO, 'w', encoding='utf-8') as f:
        json.dump(DEFAULT_PORTAFOLIO, f, ensure_ascii=False, indent=4)

def obtener_portafolio():
    try:
        with open(DB_PORTAFOLIO, 'r', encoding='utf-8') as f:
            return json.loads(f.read())
    except Exception:
        return DEFAULT_PORTAFOLIO

def guardar_portafolio(data):
    with open(DB_PORTAFOLIO, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

CARRITOS = {}

def obtener_usuarios():
    try:
        if os.path.exists(DB_USERS):
            with open(DB_USERS, 'r', encoding='utf-8') as f:
                contenido = f.read().strip()
                if contenido:
                    return json.loads(contenido)
    except Exception:
        return {}
    return {}

def guardar_usuarios(data):
    with open(DB_USERS, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def asegurar_admin():
    usuarios = obtener_usuarios()
    if "Punto Grafico" not in usuarios:
        usuarios["Punto Grafico"] = generate_password_hash("admin123") 
        guardar_usuarios(usuarios)

asegurar_admin()

def obtener_historial_filtrado(user):
    try:
        with open(DB_HISTORIAL, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}
        
    if user not in data:
        return []
        
    ahora = datetime.now()
    historial_valido = []
    modificado = False
    
    for item in data[user]:
        try:
            fecha_item = datetime.fromisoformat(item['fecha_iso'])
            if (ahora - fecha_item).days < 7:
                historial_valido.append(item)
            else:
                modificado = True
        except Exception:
            modificado = True
            
    if modificado:
        data[user] = historial_valido
        with open(DB_HISTORIAL, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
            
    return historial_valido

def agregar_historial(user, order_id, total, fecha_str):
    try:
        with open(DB_HISTORIAL, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        data = {}
        
    if user not in data:
        data[user] = []
        
    data[user].append({
        "id": order_id,
        "total": total,
        "fecha": fecha_str,
        "fecha_iso": datetime.now().isoformat()
    })
    
    with open(DB_HISTORIAL, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def extract_price(price_str):
    nums = re.findall(r'\d+', price_str.replace(',', ''))
    return float(nums[0]) if nums else 0.0


HTML_COMPLETO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="icon" href="LOGO PG.png" type="image/png">

    <title>Punto Gráfico | Agencia Digital</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>
    <style>
        /* === DISEÑO DE ENTORNO Y PALETA LÍQUIDA SÚPER CRISTALINA === */
        :root {
            --glass-bg: linear-gradient(135deg, rgba(255, 255, 255, 0.12) 0%, rgba(255, 255, 255, 0.02) 100%);
            --glass-border: rgba(255, 255, 255, 0.15);
            --glass-shadow: 0 15px 35px rgba(0, 0, 0, 0.25);
            --glass-highlight: rgba(255, 255, 255, 0.35);
            --text-light: #ffffff;
            --text-muted: #d1d5db;
        }

        * {
            margin: 0; padding: 0; box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            scroll-behavior: smooth;
        }

        body {
            background-color: #1a202c; color: var(--text-light);
            min-height: 100vh; overflow-x: hidden; font-weight: 300;
            -webkit-font-smoothing: antialiased; 
            -moz-osx-font-smoothing: grayscale;
            overscroll-behavior-y: none; /* Fluidez al scrollear en móvil */
            text-rendering: optimizeSpeed; /* Optimización de sistema */
        }

        /* === REDUCCIÓN DE LAG OPCIONAL === */
        body.no-animations *, body.no-animations *::before, body.no-animations *::after {
            animation: none !important;
            transition: none !important;
            backdrop-filter: blur(10px) !important; 
            -webkit-backdrop-filter: blur(10px) !important;
        }

        /* === ANIMACIONES EXTRA DE CRISTAL CON ACELERACIÓN GPU === */
        @keyframes superPulse {
            0% { transform: scale(1) translate3d(0,0,0); box-shadow: 0 0 0 0 rgba(251, 191, 36, 0.7); }
            70% { transform: scale(1.05) translate3d(0,0,0); box-shadow: 0 0 0 15px rgba(251, 191, 36, 0); }
            100% { transform: scale(1) translate3d(0,0,0); box-shadow: 0 0 0 0 rgba(251, 191, 36, 0); }
        }
        .btn-animated { animation: superPulse 2.5s infinite cubic-bezier(0.66, 0, 0, 1); will-change: transform, box-shadow; }
        
        .bouncy-hover { transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55), box-shadow 0.4s ease !important; will-change: transform; }
        .bouncy-hover:hover { transform: scale(1.08) translateY(-5px) translate3d(0,0,0) !important; box-shadow: 0 20px 40px rgba(0,0,0,0.4) !important; }

        @keyframes wobbleBtn {
            0%, 100% { transform: translateX(0) rotate(0deg) translate3d(0,0,0); }
            25% { transform: translateX(-3px) rotate(-2deg) translate3d(0,0,0); }
            75% { transform: translateX(3px) rotate(2deg) translate3d(0,0,0); }
        }
        .btn-wobble:hover { animation: wobbleBtn 0.4s ease-in-out; }

        /* REFLEJO CRISTALINO (PASA LUZ POR EL VIDRIO) - ACELERADO */
        @keyframes crystallineShine {
            0% { transform: translateX(-150%) skewX(-25deg) translate3d(0,0,0); }
            15% { transform: translateX(150%) skewX(-25deg) translate3d(0,0,0); }
            100% { transform: translateX(150%) skewX(-25deg) translate3d(0,0,0); }
        }
        .shine-glass { position: relative; overflow: hidden; transform: translate3d(0,0,0); }
        .shine-glass::before {
            content: ''; position: absolute; top: 0; left: 0; width: 60%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 100%);
            transform: translateX(-150%) skewX(-25deg) translate3d(0,0,0); animation: crystallineShine 8s infinite cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 1; pointer-events: none; will-change: transform;
        }

        /* === PANTALLA DE CARGA ANIMADA ALEATORIA === */
        #loading-screen {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: #1a202c; z-index: 9999; display: flex; flex-direction: column;
            justify-content: center; align-items: center;
            transition: opacity 0.8s cubic-bezier(0.25, 0.8, 0.25, 1), visibility 0.8s;
            transform: translate3d(0,0,0); backface-visibility: hidden;
        }
        .canvas-box { position: relative; width: 220px; height: 180px; border: 2px dashed rgba(255,255,255,0.1); border-radius: 10px; background: rgba(0,0,0,0.3); overflow: hidden; margin-bottom: 20px; transform: translate3d(0,0,0);}
        .designer-mouse { position: absolute; font-size: 24px; z-index: 10; transition: all 0.6s cubic-bezier(0.25, 1, 0.5, 1); left: 50%; top: 50%; transform: translate(-50%, -50%) translate3d(0,0,0); will-change: transform, left, top; }
        .design-shape { position: absolute; opacity: 0; transition: all 0.8s ease-out; will-change: transform, opacity; }
        .shape-box { width: 40px; height: 40px; border-radius: 8px; border: 2px solid #fbbf24; }
        .shape-circle { width: 40px; height: 40px; border-radius: 50%; border: 2px solid #38bdf8; }
        
        .loader-phrase {
            color: var(--text-muted); font-size: 1.05rem; font-style: italic; text-align: center;
            padding: 0 20px; opacity: 0; animation: fadeInPhrase 1s ease forwards 0.4s;
            will-change: opacity; max-width: 400px;
        }
        .loader-phrase span { color: #fbbf24; font-weight: bold; }
        @keyframes fadeInPhrase { to { opacity: 1; } }

        /* === FONDOS Y CRISTAL DE ALTA PUREZA (ACELERACIÓN GPU ACTIVA) === */
        .page-bg {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: radial-gradient(circle at 15% 50%, rgba(74, 101, 131, 0.4), transparent 50%),
                        radial-gradient(circle at 85% 30%, rgba(108, 132, 163, 0.4), transparent 50%);
            z-index: -2; 
            transform: translate3d(0,0,0); 
            will-change: transform;
            contain: paint; /* Optimización del navegador */
        }

        .glass {
            background: var(--glass-bg); 
            backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
            border: 1px solid var(--glass-border); 
            border-top: 1px solid var(--glass-highlight);
            border-left: 1px solid var(--glass-highlight); 
            box-shadow: var(--glass-shadow), inset 0 0 10px rgba(255,255,255,0.08); 
            border-radius: 16px; transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
            transform: translate3d(0,0,0); 
            backface-visibility: hidden; 
            -webkit-backface-visibility: hidden;
            perspective: 1000px;
            position: relative;
        }

        nav {
            position: fixed; top: 20px; left: 0; right: 0; margin: 0 auto; width: 95%; max-width: 1200px;
            padding: 10px 30px; display: flex; justify-content: space-between; align-items: center; z-index: 1000; border-radius: 40px;
            will-change: transform; transform: translate3d(0,0,0);
        }

        .nav-logo { height: 40px; width: auto; transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); will-change: transform; }
        .nav-logo:hover { transform: scale(1.15) rotate(-2deg) translate3d(0,0,0); }

        .nav-links { display: flex; gap: 20px; list-style: none; align-items: center; }
        .nav-links a { color: var(--text-light); text-decoration: none; font-size: 0.9rem; position: relative; padding: 5px 0; transition: color 0.3s; }
        .nav-links a::after { content: ''; position: absolute; width: 0; height: 2px; bottom: 0; left: 0; background-color: #fbbf24; transition: width 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); }
        .nav-links a:hover { color: #fbbf24; }
        .nav-links a:hover::after { width: 100%; }
        
        .nav-links a.bodas-link { color: #fdba74; font-weight: 500; }
        .nav-links a.bodas-link::after { background-color: #fdba74; }

        /* === MENÚ DE PERFIL === */
        .profile-btn {
            background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05)); color: #fbbf24; padding: 8px 18px;
            border-radius: 20px; border: 1px solid rgba(255,255,255,0.2); cursor: pointer;
            font-size: 0.9rem; display: flex; align-items: center; gap: 8px; 
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: inset 0 0 8px rgba(255,255,255,0.1); will-change: transform;
        }
        .profile-btn:hover { background: rgba(255, 255, 255, 0.25); border-color: #fbbf24; transform: scale(1.05) translate3d(0,0,0); }

        .auth-user-btn {
            font-size: 0.85rem; background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.05)); padding: 8px 18px; border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.25); cursor: pointer; transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); color: white;
            box-shadow: inset 0 0 10px rgba(255,255,255,0.1); will-change: transform;
        }
        .auth-user-btn:hover { background: white; color: black; transform: scale(1.08) translate3d(0,0,0); box-shadow: 0 0 20px rgba(255,255,255,0.5); }

        /* === BOTONES FLOTANTES (CARRITO Y LUPA) === */
        .floating-container {
            position: fixed; bottom: 30px; right: 30px; z-index: 1900;
            display: flex; gap: 15px; align-items: flex-end; flex-direction: row;
            transform: translate3d(0,0,0); /* GPU Force */
        }
        
        .cart-floating-btn {
            cursor: pointer; display: flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, rgba(255,255,255,0.15), rgba(255,255,255,0.02)); 
            backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255,255,255,0.3); border-radius: 50%; width: 70px; height: 70px;
            transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            animation: floatAndGlow 3s infinite ease-in-out;
            will-change: transform, box-shadow; transform: translate3d(0,0,0); 
            position: relative; 
            box-shadow: inset 0 0 15px rgba(255,255,255,0.1), 0 10px 35px rgba(0,0,0,0.4);
        }
        .cart-floating-btn::after {
            content: ''; position: absolute; top: 0; left: -100%; width: 100%; height: 100%;
            background: radial-gradient(circle, rgba(255,255,255,0.35) 0%, transparent 60%);
            border-radius: 50%;
            animation: crystallineShine 6s infinite; pointer-events: none; z-index: 1; will-change: transform;
        }
        
        @keyframes floatAndGlow {
            0%, 100% { transform: translateY(0) translate3d(0,0,0); box-shadow: inset 0 0 15px rgba(255,255,255,0.1), 0 10px 35px rgba(0,0,0,0.4); }
            50% { transform: translateY(-10px) translate3d(0,0,0); box-shadow: inset 0 0 15px rgba(255,255,255,0.2), 0 20px 45px rgba(251, 191, 36, 0.5); }
        }

        .btn-cart-style { font-size: 2.2rem; }
        .btn-cart-style:hover { background: rgba(255,255,255,0.25); border-color: rgba(255,255,255,0.7); transform: scale(1.15) rotate(-10deg) translate3d(0,0,0) !important; }
        
        .search-btn-style { font-size: 1.8rem; background: linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(56, 189, 248, 0.05)); border-color: rgba(56,189,248,0.5); width: 60px; height: 60px; }
        .search-btn-style:hover { background: rgba(56, 189, 248, 0.4); transform: scale(1.15) rotate(10deg) translate3d(0,0,0) !important; box-shadow: 0 10px 30px rgba(56, 189, 248, 0.6); }

        .btn-admin-style { font-size: 2.2rem; background: linear-gradient(135deg, rgba(74, 222, 128, 0.25), rgba(74, 222, 128, 0.05)); border-color: rgba(74, 222, 128, 0.5); }
        .btn-admin-style:hover { background: rgba(74, 222, 128, 0.4); transform: scale(1.15) rotate(10deg) translate3d(0,0,0) !important; box-shadow: 0 10px 30px rgba(74, 222, 128, 0.6); }

        .cart-badge {
            position: absolute; top: -5px; right: -5px; background: #fbbf24; color: #1a202c;
            font-size: 0.8rem; font-weight: bold; border-radius: 50%; width: 22px; height: 22px;
            display: flex; align-items: center; justify-content: center; z-index: 10;
            box-shadow: 0 0 15px rgba(251, 191, 36, 1); border: 2px solid #1a202c;
        }
        
        .pulse-cart { animation: cartSplash 0.6s cubic-bezier(0.25, 0.8, 0.25, 1); will-change: transform; }
        @keyframes cartSplash {
            0% { transform: scale(1) translate3d(0,0,0); }
            30% { transform: scale(1.5) translate3d(0,0,0); border-radius: 35% 65% 35% 65%; background: white; }
            60% { transform: scale(0.9) translate3d(0,0,0); }
            100% { transform: scale(1) translate3d(0,0,0); }
        }

        /* === SECCIONES CON TRANSICIÓN SUAVE === */
        section { padding: 100px 5% 40px; max-width: 1200px; margin: 0 auto; display: flex; flex-direction: column; justify-content: center; position: relative; }
        #servicios { position: relative; overflow: hidden; border-radius: 20px; }
        .section-title { text-align: center; font-size: 2.2rem; margin-bottom: 50px; letter-spacing: 2px; text-transform: uppercase; z-index: 2; transform: translate3d(0,0,0); }

        /* === DEGRADADO DE VIDEO SUAVE (SIN GOLPES) ACELERADO === */
        .hero-container { position: relative; width: 100vw; height: 100vh; display: flex; align-items: center; justify-content: center; overflow: hidden; background: #1a202c; transform: translate3d(0,0,0); }
        .hero-video { 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 0; 
            transform: translate3d(0,0,0); filter: brightness(0.85); will-change: transform;
            mask-image: linear-gradient(to bottom, black 0%, black 50%, transparent 95%);
            -webkit-mask-image: linear-gradient(to bottom, black 0%, black 50%, transparent 95%);
        } 
        .hero-overlay { 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            background: linear-gradient(to bottom, rgba(26,32,44,0.1) 0%, rgba(26,32,44,0.6) 60%, #1a202c 100%); 
            z-index: 1; transform: translate3d(0,0,0); 
        } 
        .hero-content { text-align: center; padding: 30px; max-width: 800px; z-index: 2; position: relative; width: 90%; overflow: hidden; transform: translate3d(0,0,0); }
        .hero-content::before { 
            content:''; position:absolute; top:0; left:0; width:50%; height:100%;
            background:linear-gradient(to right, transparent, rgba(255,255,255,0.15), transparent);
            transform: translateX(-150%) skewX(-25deg) translate3d(0,0,0); animation: crystallineShine 10s infinite; pointer-events:none; will-change: transform;
        }
        .hero-content h1 { font-size: 3.5rem; font-weight: 600; margin-bottom: 20px; line-height: 1.2; letter-spacing: -1px; }
        .hero-content p { font-size: 1.1rem; color: var(--text-muted); margin-bottom: 40px; }

        .btn {
            display: inline-block; padding: 14px 40px; color: var(--text-light); text-decoration: none; font-size: 0.95rem;
            cursor: pointer; border-radius: 30px; text-align: center;
            background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, rgba(255,255,255,0.05) 100%);
            border: 1px solid rgba(255, 255, 255, 0.3); backdrop-filter: blur(10px);
            box-shadow: inset 0 0 10px rgba(255,255,255,0.1), 0 5px 15px rgba(0,0,0,0.2);
            transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
            position: relative; overflow: hidden; transform: translate3d(0,0,0); will-change: transform;
        }
        .btn::after {
            content:''; position:absolute; top:0; left:-100%; width:50%; height:100%;
            background:linear-gradient(to right, transparent, rgba(255,255,255,0.3), transparent);
            transform: skewX(-20deg) translate3d(0,0,0); transition: all 0.5s; will-change: left;
        }
        .btn:hover::after { left: 150%; }
        .btn-small { padding: 10px 20px; font-size: 0.85rem; margin-top: 20px; width: 100%; }
        
        .active-liquid { 
            animation: liquidButton 3s cubic-bezier(0.4, 0, 0.2, 1) infinite alternate; 
            will-change: border-radius, background-position, transform; 
        }
        @keyframes liquidButton {
            0% { border-radius: 30px 30px 30px 30px; background-position: 0% 50%; transform: scale(1) translate3d(0,0,0); }
            25% { border-radius: 40px 20px 40px 20px; background-position: 100% 50%; transform: scale(1.02) translate3d(0,0,0); }
            50% { border-radius: 20px 40px 20px 40px; background-position: 0% 50%; transform: scale(0.98) translate3d(0,0,0); }
            75% { border-radius: 40px 20px 20px 40px; background-position: 100% 50%; transform: scale(1.01) translate3d(0,0,0); }
            100% { border-radius: 30px 30px 30px 30px; background-position: 0% 50%; transform: scale(1) translate3d(0,0,0); }
        }

        .logo-chilero {
            display: block; margin: 0 auto 20px; height: 55px; width: auto;
            animation: flotacionGlow 3s ease-in-out infinite;
            transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            will-change: filter, transform; transform: translate3d(0,0,0); 
        }
        .logo-chilero:hover { transform: scale(1.2) rotate(-5deg) translate3d(0,0,0); }
        @keyframes flotacionGlow {
            0%, 100% { filter: drop-shadow(0 0 5px rgba(255, 255, 255, 0.2)); transform: translateY(0) translate3d(0,0,0); }
            50% { filter: drop-shadow(0 0 20px rgba(251, 191, 36, 0.8)); transform: translateY(-6px) translate3d(0,0,0); }
        }

        .btn-chilero-submit {
            background: linear-gradient(90deg, rgba(74,101,131,0.5), rgba(251,191,36,0.4), rgba(74,101,131,0.5)) !important;
            background-size: 200% auto !important; border: 1px solid rgba(255,255,255,0.4); 
            box-shadow: inset 0 0 10px rgba(255,255,255,0.2), 0 5px 15px rgba(0,0,0,0.3) !important;
            color: white; padding: 12px 20px; border-radius: 30px; cursor: pointer; transform: translate3d(0,0,0); will-change: transform, box-shadow;
        }
        .btn-chilero-submit:hover { background-position: right center !important; box-shadow: inset 0 0 15px rgba(255,255,255,0.4), 0 8px 25px rgba(251, 191, 36, 0.6) !important; transform: scale(1.05) translateY(-3px) translate3d(0,0,0) !important; }

        /* Estilo especial para Botones de Bodas */
        .btn-boda-style {
            background: linear-gradient(90deg, rgba(253, 186, 116, 0.3), rgba(253, 186, 116, 0.5), rgba(253, 186, 116, 0.3)) !important;
            border-color: rgba(253, 186, 116, 0.7) !important;
            box-shadow: inset 0 0 10px rgba(255,255,255,0.2), 0 5px 15px rgba(253,186,116,0.2) !important;
            color: white !important;
        }
        .btn-boda-style:hover { box-shadow: inset 0 0 15px rgba(255,255,255,0.4), 0 8px 25px rgba(253,186,116,0.5) !important; }

        .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 25px; z-index: 2;}
        .service-card { padding: 40px 30px; text-align: left; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1); will-change: transform, box-shadow;}
        .service-card:hover { transform: translateY(-12px) scale(1.03) translate3d(0,0,0); background: rgba(255, 255, 255, 0.08); box-shadow: inset 0 0 20px rgba(255,255,255,0.05), 0 20px 40px rgba(0,0,0,0.4); border-color: rgba(251, 191, 36, 0.5); }
        .service-card h3 { margin-bottom: 15px; font-size: 1.3rem; color: #fbbf24; transition: transform 0.3s; will-change: transform;}
        .service-card:hover h3 { transform: translateX(5px) translate3d(0,0,0); }
        .service-card p { color: var(--text-muted); line-height: 1.6; font-size: 0.95rem; margin-bottom: 15px;}

        /* Portafolio Imágenes - DIMENSIONES REALES */
        .portafolio-img { 
            height: 250px; 
            width: 100%; 
            background-position: center; 
            background-size: contain; 
            background-repeat: no-repeat; 
            border-radius: 12px 12px 0 0; 
            transition: transform 0.5s ease; 
            background-color: rgba(0, 0, 0, 0.2); 
            will-change: transform;
            transform: translate3d(0,0,0);
        }
        .portafolio-card { padding: 0 !important; overflow: hidden; position: relative; }
        .portafolio-card:hover .portafolio-img { transform: scale(1.05) translate3d(0,0,0); }
        .portafolio-content { padding: 25px; position: relative; z-index: 2; background: inherit; border-top: 1px solid rgba(255,255,255,0.08); transform: translate3d(0,0,0);}

        .animate-up { opacity: 0; transform: translateY(40px) translate3d(0,0,0); animation: fadeInUp 1s cubic-bezier(0.25, 0.8, 0.25, 1) forwards; will-change: opacity, transform; }
        .delay-1 { animation-delay: 0.2s; } .delay-2 { animation-delay: 0.4s; } .delay-3 { animation-delay: 0.6s; }
        @keyframes fadeInUp { to { opacity: 1; transform: translateY(0) translate3d(0,0,0); } }
        @keyframes floatUp { 0% { transform: translateY(100%) scale(0.5) translate3d(0,0,0); opacity: 0; } 50% { opacity: 1; } 100% { transform: translateY(-50%) scale(1.2) translate3d(0,0,0); opacity: 0; } }

        /* === CAPAS MODALES === */
        .modal-overlay {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
            z-index: 2000; display: flex; align-items: center; justify-content: center;
            opacity: 0; visibility: hidden; transition: all 0.5s cubic-bezier(0.25, 0.8, 0.25, 1); padding: 20px;
            transform: translate3d(0,0,0); will-change: opacity, visibility;
        }
        .modal-overlay.active { opacity: 1; visibility: visible; }
        .modal-content {
            width: 100%; max-width: 500px; padding: 40px; position: relative;
            transform: translateY(50px) scale(0.9) translate3d(0,0,0); opacity: 0; transition: all 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            max-height: 90vh; overflow-y: auto; will-change: transform, opacity; 
            border: 1px solid rgba(255,255,255,0.25); box-shadow: inset 0 0 20px rgba(255,255,255,0.05), 0 20px 50px rgba(0,0,0,0.5);
            backface-visibility: hidden;
        }
        #catalogModal .modal-content, #cartModal .modal-content, #adminModal .modal-content { max-width: 900px; }
        .modal-overlay.active .modal-content { transform: translateY(0) scale(1) translate3d(0,0,0); opacity: 1; }
        .close-modal { position: absolute; top: 15px; right: 20px; font-size: 2rem; cursor: pointer; color: var(--text-muted); z-index: 10; transition: transform 0.3s; will-change: transform; }
        .close-modal:hover { color: #f87171; transform: rotate(90deg) scale(1.2) translate3d(0,0,0); }

        .form-group { margin-bottom: 20px; text-align: left; position: relative; transform: translate3d(0,0,0); }
        .form-group label { display: block; margin-bottom: 8px; font-size: 0.9rem; color: var(--text-muted); transition: color 0.3s; }
        .form-group:focus-within label { color: #fbbf24; }
        .form-input { width: 100%; padding: 12px 15px; border-radius: 10px; background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.2); color: white; outline: none; font-family: inherit; transition: all 0.3s; box-shadow: inset 0 2px 5px rgba(0,0,0,0.2); will-change: transform, box-shadow; transform: translate3d(0,0,0); }
        .form-input:focus { border-color: #fbbf24; background: rgba(255,255,255,0.1); box-shadow: inset 0 2px 5px rgba(0,0,0,0.2), 0 0 15px rgba(251, 191, 36, 0.3); transform: translateY(-2px) translate3d(0,0,0); }
        
        input[type="file"]::file-selector-button { background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.05)); border: 1px solid rgba(255,255,255,0.4); color: white; padding: 8px 15px; border-radius: 8px; cursor: pointer; transition: all 0.3s; margin-right: 10px; box-shadow: inset 0 0 5px rgba(255,255,255,0.1); }
        input[type="file"]::file-selector-button:hover { background: #fbbf24; color: black; border-color: #fbbf24; }
        
        .color-picker-group { display: flex; gap: 10px; flex-wrap: wrap; margin-top: 10px; transform: translate3d(0,0,0); }
        .color-picker { width: 45px; height: 45px; border: none; border-radius: 50%; cursor: pointer; background: transparent; outline: none; box-shadow: 0 4px 10px rgba(0,0,0,0.4), inset 0 0 0 2px rgba(255,255,255,0.3); transition: transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55); will-change: transform, box-shadow; transform: translate3d(0,0,0); }
        .color-picker:hover { transform: scale(1.3) translate3d(0,0,0); z-index: 2; box-shadow: 0 8px 15px rgba(0,0,0,0.5), inset 0 0 0 2px #fbbf24; }
        .color-picker::-webkit-color-swatch { border-radius: 50%; border: none; }

        .auth-error-box { color: #f87171; text-align: center; margin-top: 15px; font-size: 0.9rem; font-weight: 500; min-height: 20px; transition: all 0.3s; }
        .shake-error { animation: liquidShake 0.4s ease-in-out; will-change: transform; }
        @keyframes liquidShake { 0%, 100% { transform: translateX(0) translate3d(0,0,0); } 25% { transform: translateX(-10px) skewX(-5deg) translate3d(0,0,0); } 75% { transform: translateX(10px) skewX(5deg) translate3d(0,0,0); } }

        .invoice-box { background: white; color: black; padding: 30px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); transform: translate3d(0,0,0); }
        .invoice-row { display: flex; justify-content: space-between; border-bottom: 1px solid #ccc; padding: 10px 0; }

        .catalog-container { display: none; }
        .catalog-container.active { display: block; animation: fadeInUp 0.5s ease; }
        .catalog-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-top: 20px; }
        .catalog-item { padding: 25px 20px; text-align: center; cursor: pointer; position: relative; overflow: hidden; transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); border-radius: 12px; will-change: transform, box-shadow; transform: translate3d(0,0,0); }
        .catalog-item:hover { transform: translateY(-10px) scale(1.05) translate3d(0,0,0); background: rgba(255, 255, 255, 0.12); border-color: #fbbf24; box-shadow: inset 0 0 15px rgba(255,255,255,0.1), 0 15px 35px rgba(251, 191, 36, 0.3); }
        .catalog-item::after { content: ''; position: absolute; top: 0; left: -100%; width: 50%; height: 100%; background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent); transform: skewX(-20deg) translate3d(0,0,0); transition: all 0.7s; will-change: left; }
        .catalog-item:hover::after { left: 150%; }

        .catalog-item.boda-item:hover { border-color: #fdba74; box-shadow: inset 0 0 15px rgba(255,255,255,0.1), 0 15px 35px rgba(253, 186, 116, 0.3); }

        .catalog-icon { font-size: 1.1rem; margin-bottom: 15px; font-weight: 600; letter-spacing: 1px; color: #fbbf24; text-transform: uppercase; transition: transform 0.3s; will-change: transform; }
        .catalog-item:hover .catalog-icon { transform: scale(1.2) translate3d(0,0,0); }
        .catalog-item h4 { font-size: 1.2rem; margin-bottom: 5px; color: var(--text-light); font-weight: 600;}
        .catalog-item .item-desc { font-size: 0.85rem; color: var(--text-muted); margin-bottom: 15px; }
        .catalog-item .item-precio { font-size: 1.1rem; color: #a0aec0; font-weight: bold; margin-bottom: 5px; }
        .catalog-item .item-tiempo { font-size: 0.8rem; color: #fbbf24; font-style: italic; background: rgba(251, 191, 36, 0.1); padding: 5px 10px; border-radius: 20px; display: inline-block; }

        .cart-item-row { padding: 20px; border-bottom: 1px solid rgba(255,255,255,0.15); margin-bottom: 15px; display: flex; justify-content: space-between; align-items: flex-start; transition: all 0.3s; border-radius: 12px; will-change: transform, box-shadow; transform: translate3d(0,0,0); }
        .cart-item-row:hover { background: rgba(255,255,255,0.08); box-shadow: inset 0 0 10px rgba(255,255,255,0.05); transform: translateX(5px) translate3d(0,0,0); border-color: #fbbf24; }
        .cart-details { text-align: left; font-size: 0.9rem; color: var(--text-muted); margin-top: 5px; line-height: 1.4; }
        .remove-item { color: #f87171; cursor: pointer; background: none; border: none; font-size: 1.2rem; font-weight: bold; transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55); will-change: transform, color; }
        .remove-item:hover { transform: scale(1.4) rotate(15deg) translate3d(0,0,0); color: #ff3333; text-shadow: 0 0 10px rgba(248,113,113,0.5); }

        .auth-tabs { display: flex; gap: 10px; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 10px; transform: translate3d(0,0,0); }
        .auth-tab-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 5px 15px; font-size: 1rem; transition: all 0.3s; will-change: transform; }
        .auth-tab-btn:hover { color: #fbbf24; transform: translateY(-2px) translate3d(0,0,0); }
        .auth-tab-btn.active { color: white; font-weight: bold; border-bottom: 2px solid #fbbf24; }

        /* === INTERFAZ PREMIUM PARA PEDIDOS DEL ADMIN (DASHBOARD REAL) === */
        .admin-modal-custom {
            max-width: 95vw !important; height: 95vh !important; padding: 0 !important;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.98) 0%, rgba(30, 41, 59, 0.98) 100%) !important;
            border: 1px solid #334155 !important;
            display: flex; flex-direction: row; gap: 0; overflow: hidden; transform: translate3d(0,0,0);
        }

        .admin-sidebar {
            width: 280px; background: rgba(0,0,0,0.5); border-right: 1px solid rgba(255,255,255,0.05);
            display: flex; flex-direction: column; padding: 30px 20px; text-align: center;
            box-shadow: inset -5px 0 15px rgba(0,0,0,0.3); transform: translate3d(0,0,0);
        }

        .admin-main-area {
            flex: 1; display: flex; flex-direction: column; padding: 30px; position: relative; transform: translate3d(0,0,0);
        }

        .admin-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 20px; margin-top: 10px; }
        .admin-order-card {
            background: linear-gradient(135deg, rgba(0, 0, 0, 0.4) 0%, rgba(0, 0, 0, 0.1) 100%); 
            backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-left: 4px solid #4ade80 !important;
            padding: 25px; border-radius: 12px; text-align: left;
            transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1); box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            animation: fadeInUp 0.5s ease backwards; position: relative; overflow: hidden; will-change: transform, box-shadow; transform: translate3d(0,0,0);
        }
        .admin-order-card::before { 
            content: ''; position: absolute; top: 0; left: 0; width: 60%; height: 100%;
            background: linear-gradient(to right, rgba(255,255,255,0) 0%, rgba(255,255,255,0.05) 50%, rgba(255,255,255,0) 100%);
            transform: translateX(-150%) skewX(-25deg) translate3d(0,0,0); animation: crystallineShine 12s infinite cubic-bezier(0.4, 0, 0.2, 1);
            z-index: 1; pointer-events: none; will-change: transform;
        }
        .admin-order-card:hover { 
            background: rgba(0, 0, 0, 0.6); transform: translateY(-6px) translate3d(0,0,0); 
            border-color: #4ade80; box-shadow: inset 0 0 15px rgba(74,222,128,0.05), 0 15px 40px rgba(74, 222, 128, 0.15);
        }
        .order-header {
            display: flex; flex-direction: column; gap: 10px; position: relative; z-index: 2;
            border-bottom: 1px solid rgba(255, 255, 255, 0.15); padding-bottom: 15px; margin-bottom: 15px; transform: translate3d(0,0,0);
        }
        .order-user { font-weight: 700; color: #4ade80; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 0.5px; text-shadow: 0 0 8px rgba(74,222,128,0.3); }
        .order-date { font-size: 0.85rem; color: var(--text-muted); }
        .order-body-item {
            margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px dashed rgba(255, 255, 255, 0.1); position: relative; z-index: 2; transform: translate3d(0,0,0);
        }
        .order-body-item:last-child { margin-bottom: 0; padding-bottom: 0; border: none; }
        .order-service-title {
            font-size: 1.1rem; font-weight: 600; color: #fbbf24; margin-bottom: 8px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .order-price { font-size: 0.95rem; color: var(--text-light); font-weight: bold; background: rgba(255,255,255,0.15); padding: 3px 12px; border-radius: 12px; box-shadow: inset 0 0 5px rgba(255,255,255,0.2); }
        .order-field { font-size: 0.9rem; margin-bottom: 6px; color: #e2e8f0; line-height: 1.4; }
        .order-field strong { color: var(--text-muted); font-weight: 400; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.5px; display: inline-block; width: 110px; }
        .order-desc-block {
            margin-top: 8px; padding: 12px; background: rgba(0, 0, 0, 0.4); border-radius: 8px;
            font-size: 0.88rem; color: #cbd5e1; line-height: 1.5; border-left: 3px solid rgba(251, 191, 36, 0.8);
            box-shadow: inset 0 2px 10px rgba(0,0,0,0.5); transform: translate3d(0,0,0);
        }

        /* Botón de editar admin portafolio */
        .btn-editar-portafolio {
            position: absolute; top: 15px; right: 15px; z-index: 10;
            background: rgba(0,0,0,0.6); backdrop-filter: blur(10px); -webkit-backdrop-filter: blur(10px);
            border: 1px solid #fbbf24; color: #fbbf24; padding: 8px 12px;
            border-radius: 8px; cursor: pointer; font-weight: bold; font-size: 0.8rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5); transition: all 0.3s; will-change: transform, box-shadow; transform: translate3d(0,0,0);
        }
        .btn-editar-portafolio:hover {
            background: #fbbf24; color: #1a202c; transform: scale(1.05) translate3d(0,0,0); box-shadow: 0 5px 20px rgba(251,191,36,0.6);
        }

        .admin-tab-btn {
            background: rgba(255,255,255,0.05); color: var(--text-muted); border: 1px solid rgba(255,255,255,0.1);
            padding: 12px; border-radius: 8px; margin-bottom: 10px; cursor: pointer; transition: all 0.3s;
            text-align: left; font-size: 0.95rem; display: flex; align-items: center; gap: 10px; will-change: transform; transform: translate3d(0,0,0);
        }
        .admin-tab-btn:hover { background: rgba(255,255,255,0.1); color: white; transform: translateX(5px) translate3d(0,0,0); }
        .admin-tab-btn.active { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border-color: #38bdf8; font-weight: bold; }

        @media (max-width: 768px) {
            nav { flex-direction: column; padding: 15px; border-radius: 20px; gap: 15px; }
            .nav-links { flex-wrap: wrap; justify-content: center; gap: 15px; }
            .hero-content h1 { font-size: 2.2rem; }
            .catalog-grid { grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); }
            .floating-container { bottom: 20px; right: 20px; }
            .cart-floating-btn { width: 60px; height: 60px; }
            .search-btn-style { width: 50px; height: 50px; font-size: 1.5rem; }
            .btn-cart-style { font-size: 1.8rem; }
            .btn-admin-style { font-size: 1.8rem; }
            .admin-modal-custom { flex-direction: column !important; overflow-y: auto; }
            .admin-sidebar { width: 100%; border-right: none; border-bottom: 1px solid rgba(255,255,255,0.1); padding: 20px; }
            .admin-main-area { padding: 20px; }
        }
    </style>
</head>
<body>

    <div id="loading-screen">
        <div class="canvas-box" id="loaderCanvas">
            <div class="designer-mouse" id="designerMouse">🖱️</div>
            <div class="design-shape shape-box" id="shapeBox"></div>
            <div class="design-shape shape-circle" id="shapeCircle"></div>
        </div>
        <p class="loader-phrase" style="opacity: 1;">Punto Gráfico: <span>Diseñando interfaz...</span></p>
    </div>

    <div class="page-bg" id="particles-global"></div>

    <nav class="glass shine-glass">
        <a href="#inicio"><img src="LOGO PG.png" alt="Punto Gráfico" class="nav-logo"></a>
        <ul class="nav-links">
            <li><a href="#inicio">Inicio</a></li>
            <li><a href="#nosotros">Nosotros</a></li>
            <li><a href="#servicios">Servicios</a></li>
            <li><a href="#bodas" class="bodas-link">Bodas 💍</a></li>
            <li><a href="#portafolio">Portafolio</a></li>
            {% if session.get('username') %}
                <li>
                    {% if session.get('username') == 'Punto Grafico' %}
                        <button class="profile-btn bouncy-hover" id="openAdminBtnNav" style="color: #4ade80; border-color: #4ade80;">⚙️ Panel Admin</button>
                    {% else %}
                        <button class="profile-btn bouncy-hover" id="openPerfilBtn" style="color: #38bdf8; border-color: #38bdf8;">⚙️ Configuración de Perfil</button>
                    {% endif %}
                </li>
            {% else %}
                <li><button class="auth-user-btn bouncy-hover" id="openAuthBtn">Iniciar Sesión</button></li>
            {% endif %}
        </ul>
    </nav>

    {% if session.get('username') == 'Punto Grafico' %}
        <div class="floating-container">
            <div class="cart-floating-btn btn-admin-style bouncy-hover" id="openAdminBtnFloat" title="Ver Pedidos">
                📋<span class="cart-badge" id="adminCountBadge" style="display:none; background: #4ade80; color: #1a202c; box-shadow: 0 0 15px rgba(74,222,128,1);">0</span>
            </div>
        </div>
    {% else %}
        <div class="floating-container">
            <div class="cart-floating-btn search-btn-style bouncy-hover" id="openSearchBtn" title="Buscar Mi Pedido">
                🔍
            </div>
            <div class="cart-floating-btn btn-cart-style bouncy-hover" id="openCartBtn" title="Ver Carrito">
                🛒<span class="cart-badge" id="cartCountBadge">0</span>
            </div>
        </div>
    {% endif %}

    <div id="inicio" class="hero-container">
        <video autoplay loop muted playsinline class="hero-video">
            <source src="VIDEO-2026-01-20-06-39-07.mp4" type="video/mp4">
        </video>
        <div class="hero-overlay"></div>
        <div class="hero-content glass shine-glass animate-up">
            <h1 class="animate-up delay-1">Ideas que fluyen,<br>marcas que destacan</h1>
            <p class="animate-up delay-2">Marketing Digital, Desarrollo Web y Creación de Contenido minimalista y de alto impacto.</p>
            <a href="#servicios" class="btn btn-animated bouncy-hover animate-up delay-3">Empezar un Proyecto</a>
        </div>
    </div>

    <section id="nosotros">
        <h2 class="section-title">Nuestra Filosofía</h2>
        <div class="glass shine-glass" style="padding: 50px; text-align: center; max-width: 900px; margin: 0 auto; font-size: 1.1rem; line-height: 1.8;">
            <p style="color: var(--text-muted); margin-bottom: 20px;">
                En <strong style="color: white;">Punto Gráfico</strong> no solo creamos diseños; diseñamos experiencias que conectan. 
                Somos un equipo apasionado por la estética digital y la innovación tecnológica. Nuestro objetivo es tomar la esencia 
                de tu marca y transformarla en una presencia visual que no pase desapercibida.
            </p>
            <p style="color: #fbbf24; font-style: italic; font-size: 1.2rem; text-shadow: 0 0 10px rgba(251,191,36,0.3);">
                "Tu visión es el lienzo, nosotros ponemos el color."
            </p>
        </div>
    </section>

    <section id="servicios">
        <h2 class="section-title">Nuestra Experiencia</h2>
        <div class="services-grid">
            <div class="glass shine-glass service-card">
                <div>
                    <h3>Diseño Gráfico</h3>
                    <p>Identidad visual, branding y piezas gráficas a la medida de los objetivos de tu negocio.</p>
                </div>
                <button class="btn btn-small bouncy-hover open-catalog-btn liquid-trigger" data-target="cat-diseno">Ver Diseños</button>
            </div>
            <div class="glass shine-glass service-card">
                <div>
                    <h3>Páginas Web</h3>
                    <p>Sitios dinámicos, adaptables y fluidos optimizados con tecnología de carga premium.</p>
                </div>
                <button class="btn btn-small bouncy-hover open-catalog-btn liquid-trigger" data-target="cat-web">Ver Opciones Web</button>
            </div>
            <div class="glass shine-glass service-card">
                <div>
                    <h3>Edición de Videos</h3>
                    <p>Formatos dinámicos, reels, corrección estética y efectos de movimiento cinemático.</p>
                </div>
                <button class="btn btn-small bouncy-hover open-catalog-btn liquid-trigger" data-target="cat-video">Ver Formatos de Video</button>
            </div>
        </div>
    </section>

    <section id="bodas" style="padding-top: 60px;">
        <h2 class="section-title" style="color: #fdba74; text-shadow: 0 0 15px rgba(253, 186, 116, 0.4);">Edición Bodas 💍</h2>
        <p style="text-align: center; margin-bottom: 40px; color: var(--text-muted); max-width: 700px; margin-left: auto; margin-right: auto;">Eterniza tu gran día con detalles digitales y físicos diseñados con la máxima elegancia y personalización.</p>
        <div class="services-grid">
            <div class="glass shine-glass service-card" style="border-top: 1px solid rgba(253, 186, 116, 0.6); box-shadow: inset 0 0 15px rgba(253,186,116,0.05), 0 15px 35px rgba(0,0,0,0.25);">
                <div>
                    <h3 style="color: #fdba74;">Invitaciones Interactivas</h3>
                    <p>Sorprende a tus invitados con una página web exclusiva para tu boda. Incluye RSVP, cuenta regresiva, ubicación GPS y mesa de regalos.</p>
                </div>
                <button class="btn btn-small btn-boda-style bouncy-hover open-catalog-btn liquid-trigger" data-target="cat-bodas">Configurar Invitación</button>
            </div>
            <div class="glass shine-glass service-card" style="border-top: 1px solid rgba(253, 186, 116, 0.6); box-shadow: inset 0 0 15px rgba(253,186,116,0.05), 0 15px 35px rgba(0,0,0,0.25);">
                <div>
                    <h3 style="color: #fdba74;">Periódico Nupcial</h3>
                    <p>Cuenta su historia de amor al estilo de una portada de noticias vintage o moderna. Ideal para imprimir en gran formato o enviar por WhatsApp.</p>
                </div>
                <button class="btn btn-small btn-boda-style bouncy-hover open-catalog-btn liquid-trigger" data-target="cat-bodas">Pedir Periódico</button>
            </div>
            <div class="glass shine-glass service-card" style="border-top: 1px solid rgba(253, 186, 116, 0.6); box-shadow: inset 0 0 15px rgba(253,186,116,0.05), 0 15px 35px rgba(0,0,0,0.25);">
                <div>
                    <h3 style="color: #fdba74;">Video & Social Media</h3>
                    <p>Videos "Save the Date" cinemáticos, filtros personalizados de Instagram para que tus invitados interactúen y letreros de bienvenida.</p>
                </div>
                <button class="btn btn-small btn-boda-style bouncy-hover open-catalog-btn liquid-trigger" data-target="cat-bodas">Ver Extras de Boda</button>
            </div>
        </div>
    </section>

    <section id="portafolio" style="padding-bottom: 120px; padding-top: 60px;">
        <h2 class="section-title">Muestras de Diseño</h2>
        <p style="text-align: center; margin-bottom: 40px; color: var(--text-muted);">Proyectos recientes elaborados por nuestro equipo.</p>
        
        <div class="services-grid" id="portfolio-grid">
            {% for item in portafolio %}
            <div class="glass shine-glass service-card portafolio-card">
                {% if session.get('username') == 'Punto Grafico' %}
                    <button class="btn-editar-portafolio bouncy-hover" data-id="{{ item.id }}">✏️ Editar Imagen</button>
                {% endif %}
                <div class="portafolio-img" id="img-portafolio-{{ item.id }}" style="background-image: url('{{ item.img }}');"></div>
                <div class="portafolio-content">
                    <h3>{{ item.titulo }}</h3>
                    <p>{{ item.desc }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </section>

    <div class="modal-overlay" id="editPortafolioModal">
        <div class="glass shine-glass modal-content">
            <span class="close-modal close-edit-portafolio">&times;</span>
            <h2 style="text-align: center; margin-bottom: 20px; color:#fbbf24;">Editar Imagen del Portafolio</h2>
            <p style="text-align:center; color:var(--text-muted); font-size:0.9rem; margin-bottom:20px;">Sube una nueva foto. La imagen anterior se borrará del servidor automáticamente.</p>
            <form id="editPortafolioForm">
                <input type="hidden" id="editPortafolioId">
                <div class="form-group">
                    <label>Selecciona la nueva imagen</label>
                    <input type="file" id="nueva_imagen_portafolio" class="form-input" accept="image/*" required style="padding: 8px;">
                </div>
                <button type="submit" class="btn btn-chilero-submit bouncy-hover" style="width: 100%;">Subir y Reemplazar Imagen</button>
            </form>
        </div>
    </div>

    <div class="modal-overlay" id="perfilModal">
        <div class="glass shine-glass modal-content" style="display: flex; flex-direction: column; max-height: 90vh;">
            <span class="close-modal close-perfil">&times;</span>
            
            <div style="flex-shrink: 0; text-align: center;">
                <h2 style="color:#38bdf8; margin-bottom: 5px;">Configuración de Perfil</h2>
                
                <div id="userAvatarDisplay" style="font-size: 55px; background: rgba(255,255,255,0.05); width: 90px; height: 90px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 15px auto 10px; border: 2px solid #38bdf8; box-shadow: 0 0 15px rgba(56,189,248,0.4);">👤</div>
                <h3 style="color: white; margin: 0 0 10px 0; text-transform: uppercase; letter-spacing: 1px;">{{ session.get('username') }}</h3>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 5px;">Selecciona tu avatar:</p>
                <div style="display: flex; justify-content: center; gap: 15px; margin-bottom: 25px;">
                    <span style="cursor:pointer; font-size:24px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.3) translate3d(0,0,0)'" onmouseout="this.style.transform='scale(1) translate3d(0,0,0)'" onclick="setAvatarUsuario('🐺')">🐺</span>
                    <span style="cursor:pointer; font-size:24px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.3) translate3d(0,0,0)'" onmouseout="this.style.transform='scale(1) translate3d(0,0,0)'" onclick="setAvatarUsuario('🐼')">🐼</span>
                    <span style="cursor:pointer; font-size:24px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.3) translate3d(0,0,0)'" onmouseout="this.style.transform='scale(1) translate3d(0,0,0)'" onclick="setAvatarUsuario('🦄')">🦄</span>
                    <span style="cursor:pointer; font-size:24px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.3) translate3d(0,0,0)'" onmouseout="this.style.transform='scale(1) translate3d(0,0,0)'" onclick="setAvatarUsuario('🐲')">🐲</span>
                    <span style="cursor:pointer; font-size:24px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.3) translate3d(0,0,0)'" onmouseout="this.style.transform='scale(1) translate3d(0,0,0)'" onclick="setAvatarUsuario('👽')">👽</span>
                </div>

                <h4 style="color: #fbbf24; margin-bottom: 10px; text-align: left;">Cambiar Contraseña</h4>
                <div class="form-group" style="margin-bottom: 10px;">
                    <input type="password" id="passActual" class="form-input" placeholder="Contraseña Actual">
                </div>
                <div class="form-group" style="margin-bottom: 10px;">
                    <input type="password" id="passNueva" class="form-input" placeholder="Nueva Contraseña">
                </div>
                <button class="btn btn-chilero-submit bouncy-hover" id="btnCambiarPass" style="width: 100%; margin-bottom: 25px; padding: 10px;">Actualizar Contraseña</button>
                
                <h4 style="color: #fbbf24; margin-bottom: 10px; text-align: left;">Historial de Compras <span style="font-size: 0.75rem; color: var(--text-muted); font-weight: normal;">(Se auto-borra en 7 días)</span></h4>
            </div>

            <div id="historialContainer" style="flex: 1; overflow-y: auto; background: rgba(0,0,0,0.3); border-radius: 8px; padding: 15px; margin-bottom: 15px; font-size: 0.85rem; color: var(--text-muted); box-shadow: inset 0 2px 10px rgba(0,0,0,0.5);">
                <p style="text-align: center; color: #fbbf24;">Cargando historial...</p>
            </div>
            
            <div style="flex-shrink: 0; text-align: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px;">
                <button id="btnLagToggle" class="btn bouncy-hover" style="padding: 8px 15px; font-size: 0.75rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); width: auto; color: var(--text-muted); margin-bottom: 15px;">⚙️ Reducir Lag / Quitar Animaciones</button>
                <br>
                <a href="/logout" class="btn btn-chilero-submit bouncy-hover" style="background: rgba(248,113,113,0.2) !important; border-color: rgba(248,113,113,0.5); width: 100%; display: inline-block; box-sizing: border-box; text-decoration: none; padding: 10px;">Cerrar Sesión</a>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="searchOrderModal">
        <div class="glass shine-glass modal-content">
            <span class="close-modal close-search">&times;</span>
            <h2 style="text-align: center; margin-bottom: 20px; color:#38bdf8; text-shadow: 0 0 10px rgba(56,189,248,0.3);">Rastrea tu Pedido 🔍</h2>
            <p style="text-align:center; color:var(--text-muted); font-size:0.9rem; margin-bottom:20px;">Ingresa el ID único que se te generó al realizar la compra.</p>
            <div class="form-group">
                <input type="text" id="searchOrderIdInput" class="form-input" placeholder="Ej: A1B2C3D4" style="text-transform:uppercase; text-align:center; font-size:1.2rem; letter-spacing:2px; font-weight:bold; color:#fbbf24;">
            </div>
            <button class="btn btn-chilero-submit bouncy-hover" id="executeSearchBtn" style="width: 100%; background: linear-gradient(90deg, #0284c7, #38bdf8, #0284c7) !important; box-shadow: inset 0 0 10px rgba(255,255,255,0.2), 0 5px 15px rgba(56,189,248,0.3) !important;">Buscar mi Pedido</button>
            
            <div id="searchResultsContainer" style="margin-top: 20px; display:none;">
                </div>
        </div>
    </div>

    <div class="modal-overlay" id="catalogModal">
        <div class="glass shine-glass modal-content">
            <span class="close-modal close-catalog">&times;</span>
            <h2 id="catalog-title" style="text-align: center; margin-bottom: 10px;">Catálogo</h2>
            <p style="text-align: center; color: var(--text-muted); font-size: 0.95rem;">Selecciona una opción para configurarla y agregarla a tu carrito.</p>
            
            <div id="cat-diseno" class="catalog-container">
                <div class="catalog-grid">
                    <div class="catalog-item glass shine-glass open-config-form" data-service="Diseño de Logo" data-price="Q 350" data-category="diseno">
                        <div class="catalog-icon">Branding</div>
                        <h4>Logo</h4><p class="item-desc">Identidad de Marca</p>
                        <p class="item-precio">Aprox. Q 350</p><p class="item-tiempo">Entrega: 1 a 2 días</p>
                    </div>
                    <div class="catalog-item glass shine-glass open-config-form" data-service="Diseño de Flyer" data-price="Q 150" data-category="diseno">
                        <div class="catalog-icon">Media</div>
                        <h4>Flyer</h4><p class="item-desc">Promociones y Eventos</p>
                        <p class="item-precio">Aprox. Q 150</p><p class="item-tiempo">Entrega: 1 día</p>
                    </div>
                    <div class="catalog-item glass shine-glass open-config-form" data-service="Diseño de Post" data-price="Q 100" data-category="diseno">
                        <div class="catalog-icon">Social</div>
                        <h4>Post</h4><p class="item-desc">Redes Sociales (IG/FB)</p>
                        <p class="item-precio">Aprox. Q 100</p><p class="item-tiempo">Entrega: 1 día</p>
                    </div>
                </div>
            </div>

            <div id="cat-web" class="catalog-container">
                <div class="catalog-grid">
                    <div class="catalog-item glass shine-glass open-config-form" data-service="Landing Page" data-price="Q 1,200" data-category="web">
                        <div class="catalog-icon">Web</div>
                        <h4>Landing Page</h4><p class="item-desc">Página de inicio rápida</p>
                        <p class="item-precio">Aprox. Q 1,200</p><p class="item-tiempo">Entrega: 4 a 6 días</p>
                    </div>
                    <div class="catalog-item glass shine-glass open-config-form" data-service="Sitio Web Corporativo" data-price="Q 2,500" data-category="web">
                        <div class="catalog-icon">Corp</div>
                        <h4>Web Corporativa</h4><p class="item-desc">Presencia Empresarial</p>
                        <p class="item-precio">Aprox. Q 2,500</p><p class="item-tiempo">Entrega: 8 a 12 días</p>
                    </div>
                </div>
            </div>

            <div id="cat-video" class="catalog-container">
                <div class="catalog-grid">
                    <div class="catalog-item glass shine-glass open-config-form" data-service="Reel / TikTok" data-price="Q 150" data-category="video">
                        <div class="catalog-icon">Video</div>
                        <h4>Reel / TikTok</h4><p class="item-desc">Videos Verticales Dinámicos</p>
                        <p class="item-precio">Aprox. Q 150</p><p class="item-tiempo">Entrega: 1 a 2 días</p>
                    </div>
                    <div class="catalog-item glass shine-glass open-config-form" data-service="Video Corporativo" data-price="Q 800" data-category="video">
                        <div class="catalog-icon">Cine</div>
                        <h4>Corporativo</h4><p class="item-desc">Presentación de Empresa</p>
                        <p class="item-precio">Aprox. Q 800</p><p class="item-tiempo">Entrega: 5 días</p>
                    </div>
                </div>
            </div>

            <div id="cat-bodas" class="catalog-container">
                <div class="catalog-grid">
                    <div class="catalog-item boda-item glass shine-glass open-config-form" data-service="Invitación Digital Web" data-price="Q 450" data-category="web">
                        <div class="catalog-icon" style="color: #fdba74;">💌</div>
                        <h4>Invitación Web</h4><p class="item-desc">Interactiva con RSVP y GPS</p>
                        <p class="item-precio">Aprox. Q 450</p><p class="item-tiempo" style="color:#fdba74; background: rgba(253, 186, 116, 0.1);">Entrega: 3 a 5 días</p>
                    </div>
                    <div class="catalog-item boda-item glass shine-glass open-config-form" data-service="Periódico Nupcial" data-price="Q 250" data-category="diseno">
                        <div class="catalog-icon" style="color: #fdba74;">📰</div>
                        <h4>Periódico Boda</h4><p class="item-desc">Noticia de su historia de amor</p>
                        <p class="item-precio">Aprox. Q 250</p><p class="item-tiempo" style="color:#fdba74; background: rgba(253, 186, 116, 0.1);">Entrega: 2 días</p>
                    </div>
                    <div class="catalog-item boda-item glass shine-glass open-config-form" data-service="Save The Date Video" data-price="Q 300" data-category="video">
                        <div class="catalog-icon" style="color: #fdba74;">🎬</div>
                        <h4>Save the Date</h4><p class="item-desc">Video cinemático corto</p>
                        <p class="item-precio">Aprox. Q 300</p><p class="item-tiempo" style="color:#fdba74; background: rgba(253, 186, 116, 0.1);">Entrega: 3 días</p>
                    </div>
                    <div class="catalog-item boda-item glass shine-glass open-config-form" data-service="Filtro de Instagram (Boda)" data-price="Q 200" data-category="diseno">
                        <div class="catalog-icon" style="color: #fdba74;">✨</div>
                        <h4>Filtro IG</h4><p class="item-desc">Efecto personalizado p/ invitados</p>
                        <p class="item-precio">Aprox. Q 200</p><p class="item-tiempo" style="color:#fdba74; background: rgba(253, 186, 116, 0.1);">Entrega: 2 días</p>
                    </div>
                </div>
            </div>
            
        </div>
    </div>

    <div class="modal-overlay" id="projectModal">
        <div class="glass shine-glass modal-content">
            <span class="close-modal close-form">&times;</span>
            <h2 style="text-align: center; margin-bottom: 20px;">Personaliza tu Solicitud</h2>
            <form id="briefForm">
                <div class="form-group">
                    <label>Tu Nombre Completo</label>
                    <input type="text" id="cliente" class="form-input" required placeholder="Ej: Carlos Gómez (o Nombres de Novios)">
                </div>
                <div class="form-group">
                    <label>Nombre de tu Marca/Empresa o Evento</label>
                    <input type="text" id="marca" class="form-input" required placeholder="Ej: Mi Negocio S.A. / Boda Carlos y Ana">
                </div>
                <div class="form-group">
                    <label>Tu Teléfono (WhatsApp)</label>
                    <input type="tel" id="telefono" class="form-input" required placeholder="Ej: +502 45678910">
                </div>
                <div class="form-group">
                    <label>Servicio Seleccionado</label>
                    <input type="text" id="servicio" class="form-input" required readonly style="background: rgba(0,0,0,0.3); color: #fbbf24; border-color: rgba(251,191,36,0.3);">
                </div>
                
                <div class="form-group">
                    <label>Carga una imagen con la idea principal o referencias</label>
                    <input type="file" id="archivo_idea" class="form-input" accept="image/*" style="padding: 8px;">
                </div>

                <div class="form-group" id="color-section">
                    <label>Escoge la paleta de colores sugerida (Hasta 6 colores)</label>
                    <div class="color-picker-group">
                        <input type="color" class="color-picker color-val" value="#ffffff">
                        <input type="color" class="color-picker color-val" value="#000000">
                        <input type="color" class="color-picker color-val" value="#4A6583">
                        <input type="color" class="color-picker color-val" value="#fbbf24">
                        <input type="color" class="color-picker color-val" value="#1a202c">
                        <input type="color" class="color-picker color-val" value="#e2e8f0">
                    </div>
                </div>

                <div class="form-group">
                    <label>Escribe con detalle cómo te imaginas la idea final</label>
                    <textarea id="descripcion" class="form-input" required placeholder="Sugerencias de estilo, tipografía, detalles del evento o concepto..." rows="3"></textarea>
                </div>
                <button type="submit" class="btn btn-chilero-submit bouncy-hover" style="width: 100%;">Confirmar y añadir al Carrito</button>
            </form>
        </div>
    </div>

    <div class="modal-overlay" id="cartModal">
        <div class="glass shine-glass modal-content">
            <span class="close-modal" id="closeCart">&times;</span>
            <h2 style="text-align: center; margin-bottom: 20px;">Tu Lista de Servicios Listos</h2>
            
            <div id="cartItemsContainer" style="max-height: 50vh; overflow-y: auto; padding-right: 5px;"></div>

            <div style="margin-top: 30px; display: flex; gap: 15px; flex-wrap: wrap;">
                <button class="btn btn-chilero-submit bouncy-hover btn-animated" id="confirmCheckoutBtn" style="flex: 1; min-width: 200px;">Confirmar Pedido</button>
                <button class="btn bouncy-hover" id="clearCartBtn" style="flex: 1; min-width: 200px; background: rgba(248,113,113,0.2); border-color: rgba(248,113,113,0.5); box-shadow: inset 0 0 10px rgba(248,113,113,0.1);">Vaciar Carrito</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="authModal">
        <div class="glass shine-glass modal-content" id="authContentBox">
            <span class="close-modal" id="closeAuth">&times;</span>
            <img src="LOGO PG.png" alt="Punto Gráfico" class="logo-chilero">
            
            <div class="auth-tabs">
                <button class="auth-tab-btn active" id="tabLogin">Iniciar Sesión</button>
                <button class="auth-tab-btn" id="tabRegister">Registrarse</button>
            </div>

            <form id="loginForm">
                <div class="form-group">
                    <label>Usuario</label>
                    <input type="text" id="loginUser" class="form-input" required placeholder="Ingresa tu usuario">
                </div>
                <div class="form-group">
                    <label>Contraseña</label>
                    <input type="password" id="loginPass" class="form-input" required placeholder="••••••••">
                </div>
                <div style="margin: -5px 0 20px; text-align: left; display: flex; align-items: center; gap: 8px;">
                    <input type="checkbox" id="showPasswords" style="cursor: pointer; width: 16px; height: 16px; accent-color: #fbbf24;">
                    <label for="showPasswords" style="font-size: 0.85rem; color: var(--text-muted); cursor: pointer; user-select: none; margin: 0;">Ver contraseñas</label>
                </div>
                <button type="submit" class="btn btn-chilero-submit bouncy-hover" style="width: 100%;">Entrar</button>
            </form>

            <form id="registerForm" style="display: none;">
                <div class="form-group">
                    <label>Elige un Usuario</label>
                    <input type="text" id="regUser" class="form-input" required placeholder="Nuevo usuario">
                </div>
                <div class="form-group">
                    <label>Tu Contraseña</label>
                    <input type="password" id="regPass" class="form-input" required placeholder="Mínimo 4 caracteres">
                </div>
                <button type="submit" class="btn btn-chilero-submit bouncy-hover" style="width: 100%;">Crear Cuenta</button>
            </form>
            <div id="authErrorMsg" class="auth-error-box"></div>
        </div>
    </div>

    <div class="modal-overlay" id="invoiceModal">
        <div class="glass shine-glass modal-content">
            <span class="close-modal close-invoice" style="color: white;">&times;</span>
            <div id="invoice-content" class="invoice-box">
                <h2 style="text-align: center; color: #1a202c; margin-bottom: 20px;">PUNTO GRÁFICO<br><span style="font-size: 1rem; color: gray;">Factura / Cotización</span></h2>
                <div class="invoice-row"><span>ID Único:</span><strong id="inv-id" style="color: #fbbf24; font-size: 1.2rem; letter-spacing: 2px;">--</strong></div>
                <div class="invoice-row"><span>Cliente:</span><strong id="inv-cliente">--</strong></div>
                <div class="invoice-row"><span>Empresa/Evento:</span><strong id="inv-marca">--</strong></div>
                <div class="invoice-row"><span>Resumen del Pedido:</span><strong id="inv-servicio">--</strong></div>
                <div class="invoice-row"><span>Total Aproximado:</span><strong id="inv-total" style="color: #4ade80; font-size: 1.2rem;">--</strong></div>
                <div class="invoice-row" style="border: none;"><span>Estado Financiero:</span><strong style="color: green;">Procesado Localmente</strong></div>
                
                <p style="text-align:center; color:#f87171; font-weight:bold; margin-top:15px; font-size: 0.95rem;">⚠️ ¡POR FAVOR GUARDA TU ID PARA RASTREAR EL PEDIDO! ⚠️</p>
            </div>
            <button id="downloadPdfBtn" class="btn btn-chilero-submit bouncy-hover" style="width: 100%;">Descargar PDF</button>
        </div>
    </div>

    <div class="modal-overlay" id="adminModal">
        <div class="glass shine-glass modal-content admin-modal-custom">
            <span class="close-modal" id="closeAdmin">&times;</span>
            
            <div class="admin-sidebar">
                <div id="adminAvatarDisplay" style="font-size: 60px; background: linear-gradient(135deg, #4ade80, #38bdf8); width: 100px; height: 100px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 15px; box-shadow: 0 0 20px rgba(74,222,128,0.5);">🐺</div>
                <h3 style="color: #4ade80; margin: 0; font-size: 1.2rem; text-transform: uppercase;">Alessandro Lux</h3>
                <p style="color: var(--text-muted); font-size: 0.85rem; margin-top: 5px;">Gerente / ADMIN</p>
                
                <div style="display: flex; justify-content: center; gap: 10px; margin-top: 10px; margin-bottom: 20px;">
                    <span style="cursor:pointer; font-size:18px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.3) translate3d(0,0,0)'" onmouseout="this.style.transform='scale(1) translate3d(0,0,0)'" onclick="setAvatarAdmin('🐺')">🐺</span>
                    <span style="cursor:pointer; font-size:18px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.3) translate3d(0,0,0)'" onmouseout="this.style.transform='scale(1) translate3d(0,0,0)'" onclick="setAvatarAdmin('👑')">👑</span>
                    <span style="cursor:pointer; font-size:18px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.3) translate3d(0,0,0)'" onmouseout="this.style.transform='scale(1) translate3d(0,0,0)'" onclick="setAvatarAdmin('💼')">💼</span>
                    <span style="cursor:pointer; font-size:18px; transition: transform 0.2s;" onmouseover="this.style.transform='scale(1.3) translate3d(0,0,0)'" onmouseout="this.style.transform='scale(1) translate3d(0,0,0)'" onclick="setAvatarAdmin('🚀')">🚀</span>
                </div>

                <div style="display: flex; flex-direction: column; gap: 10px; margin-top: auto;">
                    <button class="admin-tab-btn active" onclick="showAdminTab('pedidos', this)">📋 Bandeja de Pedidos</button>
                    <button class="admin-tab-btn" onclick="showAdminTab('stats', this); cargarEstadisticas();">📊 Estadísticas de Ventas</button>
                    <button class="admin-tab-btn" onclick="showAdminTab('config', this)">⚙️ Configuración</button>
                    <a href="/logout" class="admin-tab-btn" style="color: #f87171; border-color: rgba(248,113,113,0.3); text-decoration: none; justify-content: center; font-weight: bold;">🚪 Cerrar Sesión</a>
                </div>
            </div>
            
            <div class="admin-main-area">
                
                <div id="adminTabPedidos" style="display: flex; flex-direction: column; height: 100%;">
                    <div class="order-header" style="flex-shrink: 0; background: rgba(0,0,0,0.3); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); transform: translate3d(0,0,0);">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                            <h2 style="color: #4ade80; margin:0; font-size: 1.5rem; text-transform: uppercase; letter-spacing: 1px;">Gestor de Solicitudes</h2>
                            <div style="display: flex; gap: 10px;">
                                <input type="text" id="adminSearchInput" class="form-input" placeholder="🔍 Buscar por ID..." style="width: 200px; margin: 0; padding: 8px 15px;">
                                <button class="btn btn-chilero-submit bouncy-hover" id="refreshAdminBtn" style="padding: 8px 15px; margin: 0;">↻ Refrescar</button>
                            </div>
                        </div>
                    </div>
                    
                    <div id="adminPedidosContent" style="flex: 1; overflow-y: auto; padding-right: 10px; padding-top: 10px;">
                        </div>
                </div>

                <div id="adminTabStats" style="display: none; flex-direction: column; height: 100%;">
                    <h2 style="color: #38bdf8; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px;">Rendimiento Financiero 📊</h2>
                    
                    <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                        <div style="flex: 1; background: linear-gradient(135deg, rgba(56,189,248,0.2), rgba(0,0,0,0.4)); padding: 30px; border-radius: 15px; text-align: center; border: 1px solid rgba(56,189,248,0.3);">
                            <h3 style="color: var(--text-muted); font-size: 1rem; margin-bottom: 10px;">Total de Ingresos</h3>
                            <div id="statDinero" style="font-size: 2.5rem; color: #38bdf8; font-weight: bold; text-shadow: 0 0 15px rgba(56,189,248,0.4);">Q 0.00</div>
                        </div>
                        <div style="flex: 1; background: linear-gradient(135deg, rgba(74,222,128,0.2), rgba(0,0,0,0.4)); padding: 30px; border-radius: 15px; text-align: center; border: 1px solid rgba(74,222,128,0.3);">
                            <h3 style="color: var(--text-muted); font-size: 1rem; margin-bottom: 10px;">Pedidos Completados</h3>
                            <div id="statCantidad" style="font-size: 2.5rem; color: #4ade80; font-weight: bold; text-shadow: 0 0 15px rgba(74,222,128,0.4);">0</div>
                        </div>
                    </div>
                </div>

                <div id="adminTabConfig" style="display: none; flex-direction: column; height: 100%; max-width: 500px; margin: 0 auto; width: 100%;">
                    <h2 style="color: #fbbf24; margin-bottom: 20px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 10px; text-align: center;">Ajustes del Sistema ⚙️</h2>

                    <div style="background: rgba(0,0,0,0.4); padding: 25px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05);">
                        <h4 style="color: #fbbf24; margin-bottom: 15px;">Seguridad (Cambiar Contraseña)</h4>
                        <input type="password" id="passActualAdmin" class="form-input" placeholder="Contraseña Actual" style="margin-bottom: 10px;">
                        <input type="password" id="passNuevaAdmin" class="form-input" placeholder="Nueva Contraseña" style="margin-bottom: 10px;">
                        <button class="btn btn-chilero-submit bouncy-hover" id="btnCambiarPassAdmin" style="width: 100%;">Actualizar Contraseña</button>
                    </div>

                    <div style="background: rgba(0,0,0,0.4); padding: 25px; border-radius: 12px; text-align: center; border: 1px solid rgba(255,255,255,0.05);">
                        <h4 style="color: #fbbf24; margin-bottom: 15px;">Rendimiento del Navegador</h4>
                        <button id="btnLagToggleAdmin" class="btn bouncy-hover" style="padding: 10px 20px; font-size: 0.85rem; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.2); color: white;">⚙️ Reducir Lag / Quitar Animaciones</button>
                    </div>
                </div>

            </div>
        </div>
    </div>

    <script>
        // Funciones de Avatar
        function setAvatarUsuario(emoji) {
            document.getElementById('userAvatarDisplay').innerText = emoji;
            localStorage.setItem('pg_user_avatar', emoji);
        }
        function setAvatarAdmin(emoji) {
            document.getElementById('adminAvatarDisplay').innerText = emoji;
            localStorage.setItem('pg_admin_avatar', emoji);
        }

        // LÓGICA DE ANIMACIÓN ALEATORIA DE CARGA (MOUSE Y FORMAS)
        const designerMouse = document.getElementById('designerMouse');
        const shapeBox = document.getElementById('shapeBox');
        const shapeCircle = document.getElementById('shapeCircle');
        const canvasBox = document.getElementById('loaderCanvas');
        let loaderAnimInterval;

        if(designerMouse && canvasBox) {
            loaderAnimInterval = setInterval(() => {
                const x = Math.random() * 80 + 10; 
                const y = Math.random() * 80 + 10;
                designerMouse.style.left = x + '%';
                designerMouse.style.top = y + '%';
                
                if(Math.random() > 0.4) {
                    const activeShape = Math.random() > 0.5 ? shapeBox : shapeCircle;
                    activeShape.style.transition = 'none';
                    activeShape.style.left = (x - 5) + '%';
                    activeShape.style.top = (y - 5) + '%';
                    activeShape.style.transform = `scale(0.2) rotate(${Math.random() * 90}deg)`;
                    activeShape.style.opacity = '1';
                    
                    setTimeout(() => {
                        activeShape.style.transition = 'all 1s ease-out';
                        activeShape.style.transform = `scale(${Math.random() * 1.5 + 0.8}) rotate(${Math.random() * 180}deg)`;
                        activeShape.style.opacity = '0';
                    }, 50);
                }
            }, 600); 
        }

        window.addEventListener('load', () => {
            setTimeout(() => {
                clearInterval(loaderAnimInterval); 
                const loader = document.getElementById('loading-screen');
                if(loader) {
                    loader.style.opacity = '0';
                    setTimeout(() => loader.style.visibility = 'hidden', 800);
                }
            }, 2500); 
        });

        document.addEventListener('DOMContentLoaded', () => {
            const USER_LOGGED = "{{ session.get('username', '') }}";
            let currentSelectedPrice = "";
            let currentSelectedCategory = "";

            // Restaurar avatares guardados
            const savedUserAvatar = localStorage.getItem('pg_user_avatar');
            if(savedUserAvatar && document.getElementById('userAvatarDisplay')) {
                document.getElementById('userAvatarDisplay').innerText = savedUserAvatar;
            }
            const savedAdminAvatar = localStorage.getItem('pg_admin_avatar');
            if(savedAdminAvatar && document.getElementById('adminAvatarDisplay')) {
                document.getElementById('adminAvatarDisplay').innerText = savedAdminAvatar;
            }

            // --- REDUCCIÓN DE LAG GLOBAL ---
            const btnLag = document.getElementById('btnLagToggle');
            const btnLagAdmin = document.getElementById('btnLagToggleAdmin');
            
            function updateLagUI(isReduced) {
                if(isReduced) {
                    document.body.classList.add('no-animations');
                    if(btnLag) btnLag.innerHTML = "✅ Animaciones Desactivadas";
                    if(btnLagAdmin) btnLagAdmin.innerHTML = "✅ Animaciones Desactivadas";
                } else {
                    document.body.classList.remove('no-animations');
                    if(btnLag) btnLag.innerHTML = "⚙️ Reducir Lag / Quitar Animaciones";
                    if(btnLagAdmin) btnLagAdmin.innerHTML = "⚙️ Reducir Lag / Quitar Animaciones";
                }
            }

            if(localStorage.getItem('lag_reduced') === 'true') { updateLagUI(true); }

            const toggleLagFunc = () => {
                const isNowReduced = !document.body.classList.contains('no-animations');
                localStorage.setItem('lag_reduced', isNowReduced.toString());
                updateLagUI(isNowReduced);
            };

            if(btnLag) btnLag.addEventListener('click', toggleLagFunc);
            if(btnLagAdmin) btnLagAdmin.addEventListener('click', toggleLagFunc);

            // --- PERFIL DE USUARIO ---
            const perfilModal = document.getElementById('perfilModal');
            const openPerfilBtn = document.getElementById('openPerfilBtn');
            const closePerfilBtn = document.querySelector('.close-perfil');
            const historialContainer = document.getElementById('historialContainer');
            
            if(openPerfilBtn) {
                openPerfilBtn.addEventListener('click', () => {
                    perfilModal.classList.add('active');
                    cargarHistorialCompras();
                });
            }
            if(closePerfilBtn) {
                closePerfilBtn.addEventListener('click', () => {
                    perfilModal.classList.remove('active');
                });
            }

            // Cambio Password (Usuario Normal)
            document.getElementById('btnCambiarPass')?.addEventListener('click', async () => {
                const actual = document.getElementById('passActual').value;
                const nueva = document.getElementById('passNueva').value;
                if(!actual || !nueva) return alert("Completa ambos campos");

                try {
                    const res = await fetch('/api/user/change_password', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({actual, nueva})
                    });
                    const data = await res.json();
                    alert(data.message);
                    if(data.status === 'success') {
                        document.getElementById('passActual').value = '';
                        document.getElementById('passNueva').value = '';
                    }
                } catch(e) { alert("Error de conexión"); }
            });

            // Cambio Password (Admin)
            document.getElementById('btnCambiarPassAdmin')?.addEventListener('click', async () => {
                const actual = document.getElementById('passActualAdmin').value;
                const nueva = document.getElementById('passNuevaAdmin').value;
                if(!actual || !nueva) return alert("Completa ambos campos");

                try {
                    const res = await fetch('/api/user/change_password', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({actual, nueva})
                    });
                    const data = await res.json();
                    alert(data.message);
                    if(data.status === 'success') {
                        document.getElementById('passActualAdmin').value = '';
                        document.getElementById('passNuevaAdmin').value = '';
                    }
                } catch(e) { alert("Error de conexión"); }
            });

            async function cargarHistorialCompras() {
                if(!historialContainer) return;
                historialContainer.innerHTML = '<p style="text-align:center;">Cargando historial...</p>';
                try {
                    const res = await fetch('/api/user/history');
                    const data = await res.json();
                    if(data.status === 'success') {
                        if(data.historial.length === 0) {
                            historialContainer.innerHTML = '<p style="text-align:center;">No tienes compras en los últimos 7 días.</p>';
                        } else {
                            historialContainer.innerHTML = data.historial.map(h => `
                                <div style="margin-bottom: 10px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1);">
                                    <strong style="color: #4ade80;">${h.id}</strong> - ${h.fecha}<br>
                                    Total: <strong style="color: white;">Q ${h.total}</strong>
                                </div>
                            `).join('');
                        }
                    }
                } catch(e) {
                    historialContainer.innerHTML = '<p style="text-align:center; color:#f87171;">Error al cargar historial.</p>';
                }
            }

            const liquidObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) entry.target.classList.add('active-liquid');
                    else entry.target.classList.remove('active-liquid');
                });
            }, { threshold: 0.5 });
            document.querySelectorAll('.liquid-trigger').forEach(btn => liquidObserver.observe(btn));

            const container = document.getElementById('particles-global');
            if(container) {
                for(let i = 0; i < 75; i++) {
                    let p = document.createElement('div'); p.style.position = 'absolute';
                    p.style.background = 'rgba(255, 255, 255, 0.15)'; p.style.borderRadius = '50%';
                    let size = Math.random() * 6 + 2; p.style.width = size+'px'; p.style.height = size+'px';
                    p.style.left = Math.random()*100+'%'; p.style.top = Math.random()*100+'%';
                    p.style.animation = `floatUp ${Math.random()*10+5}s linear infinite`;
                    p.style.willChange = 'transform, opacity'; p.style.transform = 'translateZ(0)';
                    container.appendChild(p);
                }
            }

            // === LÓGICA DE EDICIÓN DE PORTAFOLIO (ADMIN) ===
            const editPortafolioModal = document.getElementById('editPortafolioModal');
            const closeEditPortafolio = document.querySelector('.close-edit-portafolio');
            const editPortafolioForm = document.getElementById('editPortafolioForm');

            if(closeEditPortafolio) {
                closeEditPortafolio.addEventListener('click', () => editPortafolioModal.classList.remove('active'));
            }

            document.querySelectorAll('.btn-editar-portafolio').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    document.getElementById('editPortafolioId').value = btn.dataset.id;
                    editPortafolioModal.classList.add('active');
                });
            });

            if(editPortafolioForm) {
                editPortafolioForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const fileInput = document.getElementById('nueva_imagen_portafolio');
                    if(!fileInput.files.length) return;

                    const formData = new FormData();
                    formData.append('id', document.getElementById('editPortafolioId').value);
                    formData.append('archivo', fileInput.files[0]);

                    const submitBtn = editPortafolioForm.querySelector('button');
                    submitBtn.innerText = "Subiendo y Borrando Anterior...";

                    try {
                        const res = await fetch('/api/admin/editar_portafolio', { method: 'POST', body: formData });
                        const data = await res.json();
                        if(data.status === 'success') {
                            const idStr = document.getElementById('editPortafolioId').value;
                            const imgDiv = document.getElementById('img-portafolio-' + idStr);
                            if(imgDiv) imgDiv.style.backgroundImage = `url('${data.nueva_img}')`;
                            editPortafolioModal.classList.remove('active');
                            editPortafolioForm.reset();
                        } else {
                            alert(data.message);
                        }
                    } catch(err) {
                        alert('Error al conectar con el servidor.');
                    } finally {
                        submitBtn.innerText = "Subir y Reemplazar Imagen";
                    }
                });
            }

            // === LÓGICA DE BÚSQUEDA DE PEDIDO ===
            const searchModal = document.getElementById('searchOrderModal');
            const openSearchBtn = document.getElementById('openSearchBtn');
            if(openSearchBtn) {
                openSearchBtn.addEventListener('click', () => {
                    searchModal.classList.add('active');
                    document.getElementById('searchResultsContainer').style.display = 'none';
                    document.getElementById('searchOrderIdInput').value = '';
                });
            }
            
            const closeSearchBtn = document.querySelector('.close-search');
            if(closeSearchBtn) {
                closeSearchBtn.addEventListener('click', () => {
                    searchModal.classList.remove('active');
                });
            }

            const executeSearchBtn = document.getElementById('executeSearchBtn');
            if(executeSearchBtn) {
                executeSearchBtn.addEventListener('click', async () => {
                    const inputVal = document.getElementById('searchOrderIdInput').value.trim().toUpperCase();
                    if(!inputVal) return;
                    
                    const resContainer = document.getElementById('searchResultsContainer');
                    resContainer.style.display = 'block';
                    resContainer.innerHTML = '<p style="text-align:center; color:#fbbf24; animation: pulseLoader 1s infinite;">Buscando en la base de datos...</p>';
                    
                    try {
                        const res = await fetch('/api/buscar_pedido', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({id: inputVal})
                        });
                        const data = await res.json();
                        
                        if(data.status === 'success') {
                            let itemsHtml = data.servicios.map(s => {
                                let colHtml = s.colores;
                                if(s.colores && s.colores !== 'No aplica') {
                                    colHtml = s.colores.split(',').map(c => {
                                        let col = c.trim();
                                        return `<span style="display:inline-block; width:18px; height:18px; border-radius:50%; background-color:${col}; border:1px solid rgba(255,255,255,0.3); margin-right:3px; vertical-align:middle; box-shadow: 0 2px 4px rgba(0,0,0,0.5);" title="${col}"></span>`;
                                    }).join('');
                                }

                                return `
                                <div style="background:rgba(255,255,255,0.08); padding:15px; border-radius:8px; margin-bottom:10px; border-left: 4px solid #38bdf8; box-shadow: inset 0 0 10px rgba(255,255,255,0.05);">
                                    <strong style="color:#fbbf24; font-size:1.1rem;">${s.nombre}</strong><br>
                                    <span style="font-size:0.9rem; color:white;"><strong>Marca/Evento:</strong> ${s.marca}</span><br>
                                    <div style="display:flex; align-items:center; font-size:0.9rem; color:white; margin-top:3px;"><strong>Colores:</strong> <div style="margin-left:5px;">${colHtml || 'No aplica'}</div></div>
                                    <div style="margin-top:5px; font-size:0.85rem; color:var(--text-muted);">${s.desc}</div>
                                </div>
                                `;
                            }).join('');
                            
                            resContainer.innerHTML = `
                                <h3 style="color:#38bdf8; text-align:center; margin-bottom:10px;">¡Encontramos tu Pedido! 🎉</h3>
                                <p style="font-size:0.9rem; margin-bottom:15px; text-align:center; color:var(--text-muted);">Confirmado el: ${data.fecha}</p>
                                ${itemsHtml}
                                <div style="text-align:center; margin-top:15px; font-size:1.2rem; background:linear-gradient(135deg, rgba(74,222,128,0.2), rgba(74,222,128,0.05)); border:1px solid rgba(74,222,128,0.5); padding:15px; border-radius:10px; box-shadow: inset 0 0 15px rgba(74,222,128,0.1);">
                                    Total de tu Inversión:<br> <strong style="color:#4ade80; font-size:1.5rem; text-shadow: 0 0 10px rgba(74,222,128,0.4);">Q ${data.total}</strong>
                                </div>
                            `;
                        } else {
                            resContainer.innerHTML = `<p style="text-align:center; color:#f87171; font-weight:bold;">${data.message}</p>`;
                        }
                    } catch(e) {
                        resContainer.innerHTML = `<p style="text-align:center; color:#f87171;">Error al conectarse con el servidor.</p>`;
                    }
                });
            }


            const authModal = document.getElementById('authModal');
            const loginForm = document.getElementById('loginForm');
            const registerForm = document.getElementById('registerForm');
            const tabLogin = document.getElementById('tabLogin');
            const tabRegister = document.getElementById('tabRegister');
            const authErrorMsg = document.getElementById('authErrorMsg');
            const authContentBox = document.getElementById('authContentBox');
            
            if(document.getElementById('showPasswords')) {
                document.getElementById('showPasswords').addEventListener('change', function() {
                    const tipoInput = this.checked ? 'text' : 'password';
                    if(document.getElementById('loginPass')) document.getElementById('loginPass').type = tipoInput;
                    if(document.getElementById('regPass')) document.getElementById('regPass').type = tipoInput;
                });
            }

            if(document.getElementById('openAuthBtn')) {
                document.getElementById('openAuthBtn').addEventListener('click', () => {
                    authErrorMsg.innerText = "";
                    authModal.classList.add('active');
                });
            }
            if(document.getElementById('closeAuth')) {
                document.getElementById('closeAuth').addEventListener('click', () => authModal.classList.remove('active'));
            }

            function mostrarErrorAuth(msg, esExito = false) {
                authErrorMsg.style.color = esExito ? "#4ade80" : "#f87171";
                authErrorMsg.innerText = msg;
                if(!esExito) {
                    authContentBox.classList.add('shake-error');
                    setTimeout(() => authContentBox.classList.remove('shake-error'), 400);
                }
            }

            if(tabLogin && tabRegister) {
                tabLogin.addEventListener('click', () => {
                    tabLogin.classList.add('active'); tabRegister.classList.remove('active');
                    loginForm.style.display = 'block'; registerForm.style.display = 'none';
                    authErrorMsg.innerText = "";
                });
                tabRegister.addEventListener('click', () => {
                    tabRegister.classList.add('active'); tabLogin.classList.remove('active');
                    registerForm.style.display = 'block'; loginForm.style.display = 'none';
                    authErrorMsg.innerText = "";
                });
            }

            if(loginForm) {
                loginForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    try {
                        const res = await fetch('/login', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({user: document.getElementById('loginUser').value, pass: document.getElementById('loginPass').value})
                        });
                        const data = await res.json();
                        if(data.status === 'success') location.reload();
                        else mostrarErrorAuth("Error: " + data.message);
                    } catch (err) { mostrarErrorAuth("Error de conexión."); }
                });
            }

            if(registerForm) {
                registerForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    try {
                        const res = await fetch('/register', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({user: document.getElementById('regUser').value, pass: document.getElementById('regPass').value})
                        });
                        const data = await res.json();
                        if(data.status === 'success') {
                            mostrarErrorAuth("Cuenta creada con exito.", true);
                            setTimeout(() => { tabLogin.click(); }, 1800);
                        } else { mostrarErrorAuth(data.message); }
                    } catch (err) { mostrarErrorAuth("Error en el servidor."); }
                });
            }

            const catalogModal = document.getElementById('catalogModal');
            const formModal = document.getElementById('projectModal');
            const cartModal = document.getElementById('cartModal');
            const cartCountBadge = document.getElementById('cartCountBadge');
            const cartItemsContainer = document.getElementById('cartItemsContainer');

            async function actualizarContadorCarrito() {
                if(!USER_LOGGED || USER_LOGGED === 'Punto Grafico') return;
                try {
                    const res = await fetch('/get_cart');
                    const data = await res.json();
                    if(cartCountBadge) {
                        cartCountBadge.innerText = data.cart.length;
                        cartCountBadge.parentElement.classList.add('pulse-cart');
                        setTimeout(() => cartCountBadge.parentElement.classList.remove('pulse-cart'), 600);
                    }
                } catch(e) { console.error(e); }
            }
            actualizarContadorCarrito();

            document.querySelectorAll('.open-catalog-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    document.querySelectorAll('.catalog-container').forEach(c => c.classList.remove('active'));
                    const targetEl = document.getElementById(btn.dataset.target);
                    if(targetEl) targetEl.classList.add('active');
                    if(catalogModal) catalogModal.classList.add('active');
                });
            });
            
            const closeCatalogBtn = document.querySelector('.close-catalog');
            if(closeCatalogBtn) {
                closeCatalogBtn.addEventListener('click', () => catalogModal.classList.remove('active'));
            }

            document.querySelectorAll('.open-config-form').forEach(item => {
                item.addEventListener('click', () => {
                    if(!USER_LOGGED) {
                        if(authModal) authModal.classList.add('active');
                        mostrarErrorAuth("Debes iniciar sesion para anadir elementos.");
                        return;
                    }
                    if(USER_LOGGED === 'Punto Grafico') {
                        alert("Como Administrador no necesitas comprar servicios.");
                        return;
                    }

                    document.getElementById('servicio').value = item.dataset.service;
                    currentSelectedPrice = item.dataset.price;
                    currentSelectedCategory = item.dataset.category;
                    const colorSec = document.getElementById('color-section');
                    if(colorSec) colorSec.style.display = (currentSelectedCategory === 'web' || currentSelectedCategory === 'diseno') ? 'block' : 'none';

                    if(catalogModal) catalogModal.classList.remove('active');
                    setTimeout(() => { if(formModal) formModal.classList.add('active'); }, 300);
                });
            });
            
            const closeFormBtn = document.querySelector('.close-form');
            if(closeFormBtn) {
                closeFormBtn.addEventListener('click', () => formModal.classList.remove('active'));
            }

            const briefForm = document.getElementById('briefForm');
            if(briefForm) {
                briefForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const formData = new FormData();
                    formData.append('cliente', document.getElementById('cliente').value);
                    formData.append('marca', document.getElementById('marca').value);
                    formData.append('telefono', document.getElementById('telefono').value);
                    formData.append('servicio', document.getElementById('servicio').value);
                    formData.append('price', currentSelectedPrice);
                    formData.append('descripcion', document.getElementById('descripcion').value);

                    const colorSec = document.getElementById('color-section');
                    if (colorSec && colorSec.style.display === 'block') {
                        let coloresArray = [];
                        document.querySelectorAll('.color-val').forEach(cp => coloresArray.push(cp.value));
                        formData.append('colores', coloresArray.join(', '));
                    } else { formData.append('colores', 'No aplica'); }

                    const fileInput = document.getElementById('archivo_idea');
                    if (fileInput && fileInput.files.length > 0) formData.append('archivo', fileInput.files[0]);

                    try {
                        await fetch('/add_to_cart', { method: 'POST', body: formData });
                        formModal.classList.remove('active');
                        briefForm.reset();
                        actualizarContadorCarrito();
                    } catch(err) { console.error(err); }
                });
            }

            if(document.getElementById('openCartBtn')) {
                document.getElementById('openCartBtn').addEventListener('click', async () => {
                    if(!USER_LOGGED) return; 
                    try {
                        const res = await fetch('/get_cart');
                        const data = await res.json();
                        
                        if(cartItemsContainer) {
                            cartItemsContainer.innerHTML = '';
                            if(data.cart.length === 0) {
                                cartItemsContainer.innerHTML = '<p style="text-align:center; color:var(--text-muted); padding: 20px;">Tu carrito esta vacio.</p>';
                            } else {
                                data.cart.forEach((item, index) => {
                                    let coloresHtml = item.colores;
                                    if(item.colores && item.colores !== 'No aplica') {
                                        coloresHtml = item.colores.split(',').map(c => {
                                            let col = c.trim();
                                            return `<span style="display:inline-block; width:20px; height:20px; border-radius:50%; background-color:${col}; border:1px solid rgba(255,255,255,0.3); margin-right:5px; vertical-align:middle; box-shadow: 0 2px 5px rgba(0,0,0,0.5);" title="${col}"></span>`;
                                        }).join('');
                                    }

                                    cartItemsContainer.innerHTML += `
                                        <div class="cart-item-row glass shine-glass">
                                            <div style="flex:1;">
                                                <strong style="color:#fbbf24; font-size:1.1rem;">${item.service}</strong> (${item.price})<br>
                                                <div class="cart-details">
                                                    <strong>Empresa/Evento:</strong> ${item.marca} | <strong>De:</strong> ${item.cliente} (${item.telefono})<br>
                                                    <div style="display:flex; align-items:center; margin-top:3px; margin-bottom:3px;"><strong>Colores:</strong> <div style="margin-left:5px;">${coloresHtml}</div></div>
                                                    <strong>Idea:</strong> ${item.descripcion.substring(0, 80)}...
                                                </div>
                                            </div>
                                            <button class="remove-item" onclick="eliminarDelCarrito(${index})">&times;</button>
                                        </div>
                                    `;
                                });
                            }
                        }
                        if(cartModal) cartModal.classList.add('active');
                    } catch(err) { console.error(err); }
                });
            }
            
            if(document.getElementById('closeCart')) {
                document.getElementById('closeCart').addEventListener('click', () => cartModal.classList.remove('active'));
            }

            window.eliminarDelCarrito = async (index) => {
                try {
                    await fetch('/remove_from_cart', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({index: index}) });
                    actualizarContadorCarrito();
                    document.getElementById('openCartBtn').click();
                } catch(err) { console.error(err); }
            };

            if(document.getElementById('clearCartBtn')) {
                document.getElementById('clearCartBtn').addEventListener('click', async () => {
                    try {
                        await fetch('/clear_cart', { method: 'POST' });
                        actualizarContadorCarrito();
                        if(cartModal) cartModal.classList.remove('active');
                    } catch(err) { console.error(err); }
                });
            }

            const invoiceModal = document.getElementById('invoiceModal');
            if(document.getElementById('confirmCheckoutBtn')) {
                document.getElementById('confirmCheckoutBtn').addEventListener('click', async () => {
                    try {
                        const res = await fetch('/confirmar_pedido', { method: 'POST' });
                        const data = await res.json();
                        
                        if(data.status === 'success') {
                            document.getElementById('inv-id').innerText = data.pedido_id;
                            document.getElementById('inv-cliente').innerText = data.cliente;
                            document.getElementById('inv-marca').innerText = data.marca;
                            document.getElementById('inv-servicio').innerText = data.servicios;
                            document.getElementById('inv-total').innerText = "Q " + data.total;

                            if(cartModal) cartModal.classList.remove('active');
                            actualizarContadorCarrito();
                            setTimeout(() => invoiceModal.classList.add('active'), 300);
                        } else { alert(data.message); }
                    } catch(err) { console.error(err); }
                });
            }

            const closeInvoiceBtn = document.querySelector('.close-invoice');
            if(closeInvoiceBtn) {
                closeInvoiceBtn.addEventListener('click', () => invoiceModal.classList.remove('active'));
            }
            
            const downloadPdfBtn = document.getElementById('downloadPdfBtn');
            if(downloadPdfBtn) {
                downloadPdfBtn.addEventListener('click', () => {
                    html2pdf().set({ margin: 10, filename: 'Pedido_PuntoGrafico.pdf' }).from(document.getElementById('invoice-content')).save();
                });
            }

            const cardObserver = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) { entry.target.style.opacity = "1"; entry.target.style.animation = `fadeInUp 0.8s ease forwards`; }
                });
            });
            document.querySelectorAll('.service-card, .animate-up').forEach(el => cardObserver.observe(el));


            // === PARSEO E INTERFAZ AVANZADA DEL PANEL DE ADMINISTRACIÓN ===
            window.showAdminTab = function(tabId, btnElement) {
                document.getElementById('adminTabPedidos').style.display = 'none';
                document.getElementById('adminTabStats').style.display = 'none';
                document.getElementById('adminTabConfig').style.display = 'none';
                
                if(tabId === 'pedidos') document.getElementById('adminTabPedidos').style.display = 'flex';
                if(tabId === 'stats') document.getElementById('adminTabStats').style.display = 'flex';
                if(tabId === 'config') document.getElementById('adminTabConfig').style.display = 'flex';

                document.querySelectorAll('.admin-tab-btn').forEach(btn => btn.classList.remove('active'));
                if(btnElement) btnElement.classList.add('active');
            };

            const adminModal = document.getElementById('adminModal');
            const openAdminBtnNav = document.getElementById('openAdminBtnNav');
            const openAdminBtnFloat = document.getElementById('openAdminBtnFloat');
            const closeAdmin = document.getElementById('closeAdmin');
            const refreshAdminBtn = document.getElementById('refreshAdminBtn');

            // --- BUSCADOR DEL ADMIN ---
            const adminSearchInput = document.getElementById('adminSearchInput');
            if(adminSearchInput) {
                adminSearchInput.addEventListener('input', function() {
                    const term = this.value.toUpperCase();
                    const cards = document.querySelectorAll('.admin-order-card');
                    cards.forEach(card => {
                        const idStrong = card.querySelector('.order-date strong');
                        if(idStrong) {
                            if(idStrong.innerText.toUpperCase().includes(term)) {
                                card.style.display = 'block';
                            } else {
                                card.style.display = 'none';
                            }
                        }
                    });
                });
            }

            window.cargarEstadisticas = async function() {
                document.getElementById('statDinero').innerText = "Calculando...";
                document.getElementById('statCantidad').innerText = "...";
                try {
                    const res = await fetch('/api/admin/pedidos');
                    const data = await res.json();
                    if(data.status === 'success') {
                        let totalDinero = 0;
                        let cantidadPedidos = 0;
                        const rawText = data.data;
                        const bloquesPedidos = rawText.split('==================================================');
                        
                        bloquesPedidos.forEach(bloque => {
                            if (bloque.includes('ID Pedido:')) {
                                cantidadPedidos++;
                                const lineas = bloque.trim().split('\\n');
                                lineas.forEach(linea => {
                                    if(linea.startsWith("Total:")) {
                                        let numStr = linea.replace("Total:", "").replace("Q", "").trim();
                                        numStr = numStr.replace(/,/g, '');
                                        totalDinero += parseFloat(numStr) || 0;
                                    }
                                });
                            }
                        });

                        document.getElementById('statCantidad').innerText = cantidadPedidos;
                        document.getElementById('statDinero').innerText = "Q " + totalDinero.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2});
                    }
                } catch(e) {}
            };

            async function cargarPedidosAdmin() {
                const contentBox = document.getElementById('adminPedidosContent');
                if(!contentBox) return;
                
                contentBox.innerHTML = '<p style="text-align: center; color: #fbbf24; animation: pulseLoader 1s infinite;">Sincronizando base de datos...</p>';
                try {
                    const res = await fetch('/api/admin/pedidos');
                    const data = await res.json();
                    if(data.status === 'success') {
                        const rawText = data.data;
                        
                        if(rawText.trim() === "=== REGISTRO DE PEDIDOS DE PUNTO GRÁFICO ===" || rawText.trim().length < 50) {
                            contentBox.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 30px;">Aún no se registran pedidos nuevos.</p>';
                            const b = document.getElementById('adminCountBadge');
                            if(b) b.style.display = 'none';
                            return;
                        }

                        const bloquesPedidos = rawText.split('==================================================');
                        let htmlContenedor = '<div class="admin-grid">';
                        let totalPedidosEncontrados = 0;

                        let index = 0;
                        while(index < bloquesPedidos.length) {
                            const bloque = bloquesPedidos[index];
                            if (!bloque || bloque.trim() === "" || bloque.includes('REGISTRO DE PEDIDOS DE PUNTO')) {
                                index++;
                                continue;
                            }
                            
                            if (bloque.includes('ID Pedido:')) {
                                totalPedidosEncontrados++;
                                const lineas = bloque.trim().split('\\n');
                                
                                let usuario = "Desconocido";
                                let fecha = "No especificada";
                                let pedidoId = "Desconocido";
                                let orderPhone = ""; 
                                let totalPedido = "0.00";
                                let serviciosHtml = "";

                                let currentServicio = "";
                                let currentPrecio = "";
                                let currentContacto = "";
                                let currentEmpresa = "";
                                let currentColores = "";
                                let currentImagen = "";
                                let currentEspecificacion = "";

                                lineas.forEach(linea => {
                                    const textoLinea = linea.trim();
                                    if (textoLinea.startsWith("ID Pedido:")) {
                                        pedidoId = textoLinea.replace("ID Pedido:", "").trim();
                                    } else if (textoLinea.startsWith("Total:")) {
                                        totalPedido = textoLinea.replace("Total:", "").trim();
                                    } else if (textoLinea.startsWith("SOLICITUD INTEGRAL DE COMPRA - USUARIO:")) {
                                        usuario = textoLinea.replace("SOLICITUD INTEGRAL DE COMPRA - USUARIO:", "").trim();
                                    } else if (textoLinea.startsWith("Fecha de Confirmación:")) {
                                        fecha = textoLinea.replace("Fecha de Confirmación:", "").trim();
                                    } else if (textoLinea.startsWith("Servicio #")) {
                                        if (currentServicio) {
                                            serviciosHtml += renderizarItemServicioAdmin(currentServicio, currentPrecio, currentContacto, currentEmpresa, currentColores, currentImagen, currentEspecificacion);
                                        }
                                        const matchServicio = textoLinea.replace(/Servicio #\\d+:\\s*/, "");
                                        const partes = matchServicio.split(' (');
                                        currentServicio = partes[0] || "Servicio";
                                        currentPrecio = partes[1] ? partes[1].replace(')', '') : "N/A";
                                    } else if (textoLinea.startsWith("- Contacto Ref:")) {
                                        currentContacto = textoLinea.replace("- Contacto Ref:", "").trim();
                                    } else if (textoLinea.startsWith("- Teléfono:")) {
                                        const phone = textoLinea.replace("- Teléfono:", "").trim();
                                        if(!orderPhone) orderPhone = phone; 
                                    } else if (textoLinea.startsWith("- Empresa/Marca:")) {
                                        currentEmpresa = textoLinea.replace("- Empresa/Marca:", "").trim();
                                    } else if (textoLinea.startsWith("- Paleta de Colores:")) {
                                        let colTexto = textoLinea.replace("- Paleta de Colores:", "").trim();
                                        if(colTexto !== 'No aplica') {
                                            currentColores = colTexto.split(',').map(c => {
                                                let col = c.trim();
                                                return `<span style="display:inline-block; width:22px; height:22px; border-radius:50%; background-color:${col}; border:1px solid #fff; margin-right:5px; vertical-align:middle; box-shadow: 0 2px 5px rgba(0,0,0,0.5);" title="${col}"></span>`;
                                            }).join('');
                                        } else {
                                            currentColores = 'No aplica';
                                        }
                                    } else if (textoLinea.startsWith("- Imagen Guardada:")) {
                                        let imgStr = textoLinea.replace("- Imagen Guardada:", "").trim();
                                        if(imgStr !== "Sin archivo adjunto") {
                                            currentImagen = `<br><a href="${imgStr}" target="_blank"><img src="${imgStr}" style="max-height:90px; border-radius:8px; margin-top:8px; border:2px solid rgba(251,191,36,0.5); transition:transform 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);" onmouseover="this.style.transform='scale(2.5) translateX(20px)'" onmouseout="this.style.transform='scale(1) translateX(0)'"></a>`;
                                        } else {
                                            currentImagen = `<span style="color:var(--text-muted); font-size:0.8rem;">Sin imagen</span>`;
                                        }
                                    } else if (textoLinea.startsWith("- Especificación:")) {
                                        currentEspecificacion = textoLinea.replace("- Especificación:", "").trim();
                                    }
                                });

                                if (currentServicio) {
                                    serviciosHtml += renderizarItemServicioAdmin(currentServicio, currentPrecio, currentContacto, currentEmpresa, currentColores, currentImagen, currentEspecificacion);
                                }
                                
                                const cleanPhone = orderPhone.replace(/[^0-9]/g, '');
                                const waMsg = `¡Qué onda ${encodeURIComponent(currentContacto)}! Nos comunicamos de Punto Gráfico para entregar tu diseño de ${encodeURIComponent(currentEmpresa)} (Pedido ID: ${pedidoId}).`;
                                const waUrl = `https://wa.me/${cleanPhone}?text=${waMsg}`;

                                htmlContenedor += `
                                    <div class="admin-order-card" id="pedido-card-${pedidoId}">
                                        <div class="order-header">
                                            <div>
                                                <span class="order-user">Usuario: ${usuario}</span><br>
                                                <span class="order-date">${fecha} | ID: <strong style="color:white; letter-spacing:1px;">${pedidoId}</strong></span>
                                                <div style="margin-top:8px; font-size:1.15rem; color:#4ade80;"><strong>Total a Gastar: ${totalPedido}</strong></div>
                                            </div>
                                            <div style="display: flex; gap: 10px; margin-top: 10px;">
                                                <a href="${waUrl}" target="_blank" class="btn btn-chilero-submit btn-wobble" style="flex:1; background: #25D366 !important; border:none; padding: 10px; font-size: 0.85rem; display:flex; justify-content:center; align-items:center; text-decoration:none; color:white; font-weight:bold; box-shadow: inset 0 0 10px rgba(255,255,255,0.2) !important;">Entregar Pedido 🟢</a>
                                                <button class="btn btn-chilero-submit btn-wobble btn-eliminar-admin" data-id="${pedidoId}" style="background: #ef4444 !important; border:none; padding: 10px; font-size: 0.85rem; box-shadow: inset 0 0 10px rgba(255,255,255,0.2) !important;">Eliminar 🗑️</button>
                                            </div>
                                        </div>
                                        <div class="order-body">
                                            <div class="order-field"><strong>Teléfono:</strong> <span style="color:#25D366; font-weight:bold;">${orderPhone}</span></div>
                                            ${serviciosHtml}
                                        </div>
                                    </div>
                                `;
                            }
                            index++;
                        }

                        htmlContenedor += '</div>';
                        contentBox.innerHTML = totalPedidosEncontrados > 0 ? htmlContenedor : '<p style="text-align: center; color: var(--text-muted);">Sin pedidos estructurados detectados.</p>';
                        
                        // Actualizar insignia flotante de administrador
                        if(totalPedidosEncontrados > 0) {
                            const badge = document.getElementById('adminCountBadge');
                            if(badge) {
                                badge.innerText = totalPedidosEncontrados;
                                badge.style.display = 'flex';
                                badge.parentElement.classList.add('pulse-cart');
                                setTimeout(() => badge.parentElement.classList.remove('pulse-cart'), 600);
                            }
                        } else {
                            const badge = document.getElementById('adminCountBadge');
                            if(badge) badge.style.display = 'none';
                        }

                        document.querySelectorAll('.btn-eliminar-admin').forEach(btn => {
                            btn.addEventListener('click', async (e) => {
                                const idEliminar = e.target.getAttribute('data-id');
                                if(confirm('¿En buena onda, seguro que deseas eliminar el pedido ' + idEliminar + '?')) {
                                    const card = document.getElementById('pedido-card-' + idEliminar);
                                    if(card) { card.style.transform = "scale(0.8)"; card.style.opacity = "0"; }
                                    
                                    try {
                                        const resp = await fetch('/api/admin/eliminar_pedido', {
                                            method: 'POST',
                                            headers: {'Content-Type': 'application/json'},
                                            body: JSON.stringify({id: idEliminar})
                                        });
                                        const dataResp = await resp.json();
                                        if(dataResp.status === 'success') {
                                            setTimeout(() => cargarPedidosAdmin(), 400);
                                        } else { alert("Error: " + dataResp.message); }
                                    } catch(err) { alert("Error de conexión"); }
                                }
                            });
                        });

                    } else {
                        contentBox.innerHTML = `<p style="color: #f87171; text-align: center;">Error: ${data.message}</p>`;
                    }
                } catch(err) {
                    contentBox.innerHTML = '<p style="color: #f87171; text-align: center;">Error de conexión con el backend.</p>';
                }
            }

            function renderizarItemServicioAdmin(servicio, precio, contacto, empresa, colores, imagen, especificacion) {
                return `
                    <div class="order-body-item">
                        <div class="order-service-title">
                            <span>${servicio}</span>
                            <span class="order-price">${precio}</span>
                        </div>
                        <div class="order-field"><strong>Contacto:</strong> ${contacto}</div>
                        <div class="order-field"><strong>Marca/Evento:</strong> ${empresa}</div>
                        <div class="order-field" style="display:flex; align-items:center;"><strong>Colores:</strong> <div style="margin-left:5px;">${colores}</div></div>
                        <div class="order-field"><strong>Referencia:</strong> ${imagen}</div>
                        <div class="order-desc-block">
                            <strong>Detalles del pedido:</strong><br>
                            ${especificacion}
                        </div>
                    </div>
                `;
            }

            const abrirAdmin = (e) => { e.preventDefault(); if(adminModal) adminModal.classList.add('active'); cargarPedidosAdmin(); };

            if(openAdminBtnNav) openAdminBtnNav.addEventListener('click', abrirAdmin);
            if(openAdminBtnFloat) openAdminBtnFloat.addEventListener('click', abrirAdmin);
            
            if(closeAdmin) closeAdmin.addEventListener('click', () => { if(adminModal) adminModal.classList.remove('active'); });
            if(refreshAdminBtn) refreshAdminBtn.addEventListener('click', cargarPedidosAdmin);

            // Cargar pedidos ocultos para el contador del badge en admin
            if(USER_LOGGED === 'Punto Grafico') {
                cargarPedidosAdmin();
            }

        }); // Fin del DOMContentLoaded
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    portafolio = obtener_portafolio()
    return render_template_string(HTML_COMPLETO, portafolio=portafolio)

@app.route('/register', methods=['POST'])
def register():
    try:
        datos = request.json
        username = datos.get('user', '').strip()
        password = datos.get('pass', '').strip()
        
        if not username or not password or len(password) < 4:
            return jsonify({"status": "error", "message": "El usuario o contraseñas son invalidos."})
            
        usuarios = obtener_usuarios()
        if username in usuarios:
            return jsonify({"status": "error", "message": "Este nombre de usuario ya existe."})
            
        usuarios[username] = generate_password_hash(password)
        guardar_usuarios(usuarios)
        return jsonify({"status": "success", "message": "Cuenta creada con éxito."})
    except Exception as e:
        return jsonify({"status": "error", "message": "Error interno del sistema de registro."})

@app.route('/login', methods=['POST'])
def login():
    datos = request.json
    username = datos.get('user', '').strip()
    password = datos.get('pass', '').strip()
    
    usuarios = obtener_usuarios()
    if username in usuarios and check_password_hash(usuarios[username], password):
        session['username'] = username
        if username not in CARRITOS:
            CARRITOS[username] = []
        return jsonify({"status": "success", "message": "Ingreso exitoso."})
        
    return jsonify({"status": "error", "message": "El usuario o contraseñas son invalidos."})

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/api/user/change_password', methods=['POST'])
def change_password():
    user = session.get('username')
    if not user:
        return jsonify({"status": "error", "message": "No autorizado"})
    
    actual = request.json.get('actual')
    nueva = request.json.get('nueva')
    
    usuarios = obtener_usuarios()
    if user in usuarios and check_password_hash(usuarios[user], actual):
        if len(nueva) < 4:
            return jsonify({"status": "error", "message": "La nueva contraseña debe tener mínimo 4 caracteres"})
        usuarios[user] = generate_password_hash(nueva)
        guardar_usuarios(usuarios)
        return jsonify({"status": "success", "message": "¡Contraseña actualizada con éxito!"})
    return jsonify({"status": "error", "message": "La contraseña actual es incorrecta"})

@app.route('/api/user/history', methods=['GET'])
def user_history():
    user = session.get('username')
    if not user:
        return jsonify({"status": "error", "message": "No autorizado"})
    historial = obtener_historial_filtrado(user)
    return jsonify({"status": "success", "historial": historial})

@app.route('/get_cart', methods=['GET'])
def get_cart():
    user = session.get('username')
    if not user:
        return jsonify({"cart": []})
    return jsonify({"cart": CARRITOS.get(user, [])})

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    user = session.get('username')
    if not user:
        return jsonify({"status": "error", "message": "Sesión no válida"})
    
    cliente = request.form.get('cliente', '')
    marca = request.form.get('marca', '')
    telefono = request.form.get('telefono', '') 
    servicio = request.form.get('servicio', '')
    price = request.form.get('price', '')
    descripcion = request.form.get('descripcion', '')
    colores = request.form.get('colores', 'No aplica')

    archivo = request.files.get('archivo')
    nombre_archivo_subido = "Sin archivo adjunto"
    
    if archivo and archivo.filename != '':
        nombre_seguro = secure_filename(archivo.filename)
        nombre_final = f"{user}_{datetime.now().strftime('%M%S')}_{nombre_seguro}"
        archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_final))
        nombre_archivo_subido = f"uploads/{nombre_final}"

    if user not in CARRITOS:
        CARRITOS[user] = []
        
    CARRITOS[user].append({
        "cliente": cliente,
        "marca": marca,
        "telefono": telefono,
        "service": servicio,
        "price": price,
        "descripcion": descripcion,
        "colores": colores,
        "archivo": nombre_archivo_subido
    })
    return jsonify({"status": "success"})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    user = session.get('username')
    idx = request.json.get('index')
    if user in CARRITOS and 0 <= idx < len(CARRITOS[user]):
        CARRITOS[user].pop(idx)
    return jsonify({"status": "success"})

@app.route('/clear_cart', methods=['POST'])
def clear_cart():
    user = session.get('username')
    if user in CARRITOS:
        CARRITOS[user] = []
    return jsonify({"status": "success"})

@app.route('/confirmar_pedido', methods=['POST'])
def confirmar_pedido():
    user = session.get('username')
    if not user or user not in CARRITOS or len(CARRITOS[user]) == 0:
        return jsonify({"status": "error", "message": "El carrito se encuentra vacío actualmente."})
        
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pedido_id = str(uuid.uuid4())[:8].upper() 
    
    items = CARRITOS[user]
    primer_cliente = items[0]['cliente']
    primera_marca = items[0]['marca']
    resumen_servicios = ", ".join([i['service'] for i in items])
    
    total_price = sum([extract_price(i['price']) for i in items])
    total_formateado = f"{total_price:,.2f}"


    
    with open(DB_PEDIDOS, "a", encoding="utf-8") as file:
        file.write("==================================================\n")
        file.write(f"ID Pedido: {pedido_id}\n")
        file.write(f"SOLICITUD INTEGRAL DE COMPRA - USUARIO: {user}\n")
        file.write(f"Fecha de Confirmación: {fecha}\n")
        file.write(f"Total: Q {total_formateado}\n")
        for index, item in enumerate(items, 1):
            file.write(f"  Servicio #{index}: {item['service']} ({item['price']})\n")
            file.write(f"    - Contacto Ref: {item['cliente']}\n")
            file.write(f"    - Teléfono: {item['telefono']}\n")
            file.write(f"    - Empresa/Marca: {item['marca']}\n")
            file.write(f"    - Paleta de Colores: {item['colores']}\n")
            file.write(f"    - Imagen Guardada: {item['archivo']}\n")
            file.write(f"    - Especificación: {item['descripcion']}\n")
        file.write("==================================================\n\n")
    


    agregar_historial(user, pedido_id, total_formateado, fecha)
    
    CARRITOS[user] = []
    
    return jsonify({
        "status": "success",
        "pedido_id": pedido_id,
        "cliente": primer_cliente,
        "marca": primera_marca,
        "servicios": resumen_servicios,
        "total": total_formateado
    })

@app.route('/api/buscar_pedido', methods=['POST'])
def buscar_pedido_api():
    pedido_id = request.json.get('id', '').strip()
    if not pedido_id:
        return jsonify({"status": "error", "message": "Por favor ingresa un ID válido."})
        
    try:
        with open(DB_PEDIDOS, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        bloques = contenido.split('==================================================')
        for bloque in bloques:
            if f"ID Pedido: {pedido_id}" in bloque:
                lineas = bloque.strip().split('\n')
                fecha_encontrada = ""
                total_encontrado = ""
                servicios = []
                current_serv = {}
                
                for linea in lineas:
                    if "Fecha de Confirmación:" in linea:
                        fecha_encontrada = linea.split(":", 1)[1].strip()
                    elif "Total:" in linea:
                        total_encontrado = linea.split(":", 1)[1].strip()
                    elif "Servicio #" in linea:
                        if current_serv:
                            servicios.append(current_serv)
                        current_serv = {"nombre": linea.split(":", 1)[1].strip()}
                    elif "- Paleta de Colores:" in linea and current_serv:
                        current_serv["colores"] = linea.split(":", 1)[1].strip()
                    elif "- Especificación:" in linea and current_serv:
                        current_serv["desc"] = linea.split(":", 1)[1].strip()
                    elif "- Empresa/Marca:" in linea and current_serv:
                        current_serv["marca"] = linea.split(":", 1)[1].strip()
                if current_serv:
                    servicios.append(current_serv)
                    
                return jsonify({
                    "status": "success", 
                    "fecha": fecha_encontrada, 
                    "total": total_encontrado, 
                    "servicios": servicios
                })
                
        return jsonify({"status": "error", "message": "No se encontró ningún pedido con ese ID."})
    except Exception as e:
        return jsonify({"status": "error", "message": "Ocurrió un error al buscar en la base de datos."})


@app.route('/api/admin/pedidos', methods=['GET'])
def admin_pedidos():
    user = session.get('username')
    if user != 'Punto Grafico':
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403
        
    try:
        with open(DB_PEDIDOS, 'r', encoding='utf-8') as f:
            contenido = f.read()
        return jsonify({"status": "success", "data": contenido})
    except Exception as e:
        return jsonify({"status": "error", "message": "No se pudo leer la base de datos."})

@app.route('/api/admin/eliminar_pedido', methods=['POST'])
def eliminar_pedido():
    user = session.get('username')
    if user != 'Punto Grafico':
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403
        
    pedido_id = request.json.get('id')
    if not pedido_id:
        return jsonify({"status": "error", "message": "ID del pedido no proporcionado."})
        
    try:
        with open(DB_PEDIDOS, 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        pattern = r"==================================================\nID Pedido: " + re.escape(pedido_id) + r"\n.*?==================================================\n\n"
        nuevo_contenido = re.sub(pattern, "", contenido, flags=re.DOTALL)
        
        with open(DB_PEDIDOS, 'w', encoding='utf-8') as f:
            f.write(nuevo_contenido)
            
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": "Fallo al modificar la base de datos: " + str(e)})

@app.route('/api/admin/editar_portafolio', methods=['POST'])
def editar_portafolio():
    user = session.get('username')
    if user != 'Punto Grafico':
        return jsonify({"status": "error", "message": "Acceso denegado."}), 403

    item_id = request.form.get('id')
    archivo = request.files.get('archivo')

    if not item_id or not archivo or archivo.filename == '':
        return jsonify({"status": "error", "message": "Datos incompletos para actualizar."})

    portafolio = obtener_portafolio()
    for item in portafolio:
        if item['id'] == item_id:
            nombre_seguro = secure_filename(archivo.filename)
            nombre_final = f"portafolio_{item_id}_{datetime.now().strftime('%M%S')}_{nombre_seguro}"
            ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], nombre_final)
            archivo.save(ruta_guardado)
            nueva_ruta_img = f"uploads/{nombre_final}"

            vieja_img = item.get('img', '')
            if vieja_img.startswith('uploads/'):
                nombre_viejo = vieja_img.replace('uploads/', '')
                ruta_vieja = os.path.join(app.config['UPLOAD_FOLDER'], nombre_viejo)
                if os.path.exists(ruta_vieja):
                    try:
                        os.remove(ruta_vieja)
                    except Exception as e:
                        pass 

            item['img'] = nueva_ruta_img
            guardar_portafolio(portafolio)
            
            return jsonify({"status": "success", "nueva_img": nueva_ruta_img})

    return jsonify({"status": "error", "message": "No se encontró el elemento en el portafolio."})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8081, debug=True)