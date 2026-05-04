# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 16:48:09 2026

@author: la.arenasa1
"""

import streamlit as st
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="NexoNews", page_icon="🛡️", layout="wide")

# Cargar y mostrar el logo con el nuevo parámetro
try:
    # Usamos el nombre correcto del archivo que mencionaste
    logo = Image.open("logo_nexo.jpeg") 
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Cambiamos 'use_column_width' por 'use_container_width'
        st.image(logo, use_container_width=True)
except Exception as e:
    st.title("🛡️ NexoNews")
    # st.error(f"No se encontró el logo: {e}") # Descomenta para ver el error si falla

from backend_nexo import motor_nexo_news

# 1. Configuración principal de la página
st.set_page_config(page_title="NexoNews", page_icon="📰", layout="centered")

# 2. Encabezado de la interfaz
st.title("🚦 NexoNews: Verificador de Noticias")
st.markdown("""
Ingresa el texto de una noticia dudosa. Nuestro motor la contrastará 
instantáneamente con bases de datos de fuentes confiables en Colombia para corroborar su veracidad.
""")

# 3. Zona de interacción con el usuario
noticia_usuario = st.text_area("Pega aquí el texto de la noticia a verificar:", height=150)

# 4. Lógica del botón y procesamiento principal
if st.button("Verificar Veracidad"):
    if noticia_usuario.strip() == "":
        st.warning("⚠️ Por favor, ingresa un texto para iniciar el análisis.")
    else:
        # Spinner visual mientras el backend procesa la información
        with st.spinner("Analizando y cruzando datos con medios y fact-checkers..."):
            
            # Llamamos al motor principal del backend
            resultado = motor_nexo_news(noticia_usuario)
            
            puntaje = resultado["puntaje"]
            veredicto = resultado["veredicto"]
            fuentes = resultado["fuentes"]

            st.markdown("---")
            st.subheader("Resultado del Análisis")
            
            # 5. Sistema de Alertas Visuales (Lógica del Semáforo)
            if puntaje > 80:
                st.success(f"🟢 **VÍA LIBRE: {veredicto}** (Nivel de Coincidencia: {puntaje}%)")
                st.info("La información ingresada está altamente respaldada por los reportes de medios confiables.")
            elif puntaje > 40:
                st.warning(f"🟡 **PRECAUCIÓN: {veredicto}** (Nivel de Coincidencia: {puntaje}%)")
                st.markdown("Hay datos reales pero incompletos o descontextualizados. Te sugerimos revisar las fuentes directas.")
            else:
                st.error(f"🔴 **PELIGRO: {veredicto}** (Nivel de Coincidencia: {puntaje}%)")
                st.markdown("Alto riesgo de desinformación. No encontramos respaldo sólido en las bases de datos seguras.")

            # 6. Despliegue de Evidencias y Enlaces
            if fuentes:
                st.markdown("### 📚 Fuentes Consultadas para este veredicto:")
                for idx, articulo in enumerate(fuentes):
                    titulo = articulo.get('title', 'Sin título')
                    url = articulo.get('url', '#')
                    medio = articulo.get('source', {}).get('name', 'Fuente desconocida')
                    
                    st.markdown(f"**{idx + 1}. [{titulo}]({url})**")
                    st.caption(f"Medio: {medio}")
            else:
                st.markdown("*No se generaron enlaces de respaldo para esta consulta.*")