# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 16:26:18 2026

@author: la.arenasa1
"""

import requests
from fuzzywuzzy import fuzz
import re
import streamlit as st  # <-- Añadimos esta importación

# Hacemos que la clave se lea de un archivo secreto en la nube
API_KEY = st.secrets["NEWSAPI_KEY"] 
DOMINIOS_CONFIABLES = "eltiempo.com,elespectador.com,caracol.com.co,bluradio.com,lasillavacia.com,colombiacheck.com"

def limpiar_texto(texto):
    """Limpia el texto eliminando conectores automáticamente por longitud."""
    texto = texto.lower()
    texto = re.sub(r'http\S+|www\S+|https\S+', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'\W', ' ', texto)
    
    # Magia Regex: Elimina cualquier palabra que tenga entre 1 y 3 letras.
    # Esto destruye instantáneamente "el", "la", "que", "del", "con", "fue".
    texto = re.sub(r'\b\w{1,3}\b', '', texto)
    
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def buscar_fuentes_confiables(keyword):
    """Consulta NewsAPI y muestra información de diagnóstico en la terminal."""
    url = "https://newsapi.org/v2/everything"
    
    parametros = {
        "q": keyword,
        "domains": DOMINIOS_CONFIABLES,
        "language": "es",
        "sortBy": "relevancy",
        "apiKey": API_KEY
    }
    
    try:
        response = requests.get(url, params=parametros)
        data = response.json()
        
        # --- ZONA DE DEPURACIÓN (Se mostrará en la terminal de Anaconda) ---
        print("\n" + "="*30)
        print(f"🔍 BUSCANDO PALABRAS: '{keyword}'")
        print(f"📡 ESTADO DE LA API: {data.get('status')}")
        
        if data.get('status') == 'error':
            print(f"❌ ERROR DETALLADO: {data.get('message')}")
            
        print(f"📰 ARTÍCULOS ENCONTRADOS: {data.get('totalResults', 0)}")
        print("="*30 + "\n")
        # -------------------------------------------------------------------
        
        if data.get("status") == "ok":
            return tuple(data.get("articles", ()))
        return tuple()
        
    except Exception as e:
        print(f"Error crítico en la conexión: {e}")
        return tuple()

def calcular_veracidad(texto_usuario, articulos_encontrados):
    """Compara la noticia ajustando los umbrales a la realidad de la API."""
    if not articulos_encontrados:
        return 0, "No se encontraron evidencias en fuentes oficiales."
    
    texto_limpio_usuario = limpiar_texto(texto_usuario)

    # Calculamos el puntaje máximo usando map (manteniendo la restricción de no usar ciclos for/while)
    mejor_puntaje = max(
        map(
            lambda art: fuzz.token_set_ratio(
                texto_limpio_usuario, 
                limpiar_texto(str(art.get('title', '')) + " " + str(art.get('description', '')))
            ), 
            articulos_encontrados
        ), 
        default=0
    )
    
    # Nuevos umbrales calibrados para resúmenes de API
    if mejor_puntaje >= 55:
        return mejor_puntaje, "Alta Veracidad"
    elif mejor_puntaje >= 25:
        return mejor_puntaje, "Información Dudosa / Parcial"
    else:
        return mejor_puntaje, "Probablemente Falso"

def motor_nexo_news(noticia_input):
    """Genera una búsqueda con respaldo: primero precisa, luego amplia."""
    texto_limpio = limpiar_texto(noticia_input)
    palabras = texto_limpio.split()
    
    # 1. Filtro de Contexto Mínimo (Soluciona el problema de "Galán")
    # Exigimos al menos 5 palabras clave válidas para poder juzgar el contexto.
    if len(palabras) < 5:
        return {
            "puntaje": 0,
            "veredicto": "⚠️ Texto muy corto. Por favor ingresa un titular completo o un párrafo con más contexto.",
            "fuentes": []
        }
    
    # 2. Búsqueda Principal (Estricta - AND implícito)
    # Tomamos las 3 primeras palabras (el sujeto y la acción suelen estar al principio)
    # Ej: "alcaldía bogotá confirmó"
    query_estricta = " ".join(palabras[:3])
    articulos = buscar_fuentes_confiables(query_estricta)
    
    # 3. Búsqueda de Respaldo (Relajada - OR)
    # Si la búsqueda estricta no arrojó NADA, abrimos un poco la red usando
    # solo las 2 palabras más largas y distintivas unidas por OR.
    if not articulos:
        palabras_largas = sorted(palabras, key=len, reverse=True)[:2]
        query_relajada = " OR ".join(palabras_largas)
        articulos = buscar_fuentes_confiables(query_relajada)
        
    puntaje, veredicto = calcular_veracidad(noticia_input, articulos)
    
    return {
        "puntaje": puntaje,
        "veredicto": veredicto,
        "fuentes": articulos[:3] 
    }
