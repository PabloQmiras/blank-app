import streamlit as st
import openai
import sqlite3
from datetime import datetime

# Configuración básica
st.title("🏛️ AVANTILEX - Prueba de Concepto")

# Login simple
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    with st.form("login"):
        despacho = st.text_input("Nombre del Despacho")
        password = st.text_input("Contraseña", type="password")
        if st.form_submit_button("Entrar"):
            if password == "demo123":  # Password temporal
                st.session_state.logged_in = True
                st.session_state.despacho = despacho
                st.rerun()
            else:
                st.error("Contraseña incorrecta")
else:
    # Dashboard principal
    st.sidebar.write(f"👨‍⚖️ {st.session_state.despacho}")
    
    # Configuración de OpenAI en el sidebar
    with st.sidebar:
        st.subheader("🔑 Configuración OpenAI")
        api_key = st.text_input(
            "API Key de OpenAI", 
            type="password", 
            help="Introduce tu API Key de OpenAI",
            value=st.session_state.get('openai_api_key', '')
        )
        if api_key:
            st.session_state.openai_api_key = api_key
            openai.api_key = api_key
        
        # Modelo a usar
        modelo = st.selectbox(
            "Modelo GPT",
            ["gpt-4o", "gpt-4", "gpt-3.5-turbo"],
            index=2
        )
        
        if st.button("🗑️ Limpiar Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["📋 Clientes", "🤖 Chat Legal", "📊 Dashboard"])
    
    with tab1:
        st.subheader("Gestión de Clientes")
        
        # Formulario para agregar cliente
        with st.form("nuevo_cliente"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo")
                email = st.text_input("Email")
            with col2:
                telefono = st.text_input("Teléfono")
                tipo_caso = st.selectbox("Tipo de caso", 
                    ["Civil", "Penal", "Mercantil", "Laboral", "Fiscal"])
            
            descripcion = st.text_area("Descripción del caso")
            
            if st.form_submit_button("➕ Agregar Cliente"):
                if nombre and email:
                    st.success(f"Cliente {nombre} agregado correctamente")
                else:
                    st.error("Nombre y email son obligatorios")
    
    with tab2:
        st.subheader("🤖 Chatbot Legal Especializado")
        
        # Verificar si hay API key
        if not st.session_state.get('openai_api_key'):
            st.warning("⚠️ Por favor, introduce tu API Key de OpenAI en el sidebar para usar el chat.")
            st.info("📝 Puedes obtener tu API Key en: https://platform.openai.com/api-keys")
        else:
            # Inicializar mensajes del chat
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "system", "content": """Eres un asistente legal especializado para el despacho AVANTILEX. 
                    Tu función es ayudar con consultas legales en español, especialmente en derecho civil, penal, mercantil, laboral y fiscal. 
                    Proporciona respuestas precisas, cita artículos legales cuando sea posible, y siempre recomienda consultar con un abogado para casos específicos.
                    Mantén un tono profesional pero accesible."""}
                ]
            
            # Mostrar mensajes del chat (excluyendo el system message)
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.messages[1:]:  # Saltar el system message
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
            
            # Input del usuario
            if prompt := st.chat_input("Escribe tu consulta legal aquí..."):
                # Agregar mensaje del usuario
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Mostrar mensaje del usuario
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generar respuesta del asistente
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    try:
                        # Llamada a la API de OpenAI
                        with st.spinner("🤔 Analizando consulta legal..."):
                            response = openai.chat.completions.create(
                                model=modelo,
                                messages=st.session_state.messages,
                                temperature=0.7,
                                max_tokens=800,
                                stream=True
                            )
                            
                            # Stream de la respuesta
                            for chunk in response:
                                if chunk.choices[0].delta.content is not None:
                                    full_response += chunk.choices[0].delta.content
                                    message_placeholder.markdown(full_response + "▌")
                            
                            message_placeholder.markdown(full_response)
                    
                    except Exception as e:
                        st.error(f"❌ Error al conectar con OpenAI: {str(e)}")
                        full_response = "Lo siento, hubo un error al procesar tu consulta. Por favor, verifica tu API Key y inténtalo de nuevo."
                        message_placeholder.markdown(full_response)
                
                # Agregar respuesta del asistente a los mensajes
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            
            # Información adicional
            with st.expander("💡 Consejos para usar el chat legal"):
                st.markdown("""
                **Para obtener mejores respuestas:**
                - Sé específico con tu consulta
                - Menciona la jurisdicción (España, México, etc.)
                - Incluye detalles relevantes del caso
                - Pregunta sobre leyes o artículos específicos
                
                **Ejemplos de consultas:**
                - "¿Cuáles son los plazos para presentar una demanda civil en España?"
                - "Explícame los requisitos para un despido procedente"
                - "¿Qué documentos necesito para constituir una SL?"
                """)
    
    with tab3:
        st.subheader("📊 Métricas del Despacho")
        
        # Métricas simuladas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="👥 Clientes Activos",
                value="127",
                delta="12"
            )
        
        with col2:
            st.metric(
                label="📋 Casos Abiertos", 
                value="89",
                delta="-3"
            )
        
        with col3:
            st.metric(
                label="💼 Casos Cerrados (mes)",
                value="34",
                delta="8"
            )
        
        with col4:
            st.metric(
                label="🤖 Consultas IA",
                value=len(st.session_state.get('messages', [])) - 1,
                delta="+"
            )
        
        # Gráfico simple
        st.subheader("📈 Evolución de Casos")
        
        import pandas as pd
        import numpy as np
        
        # Datos simulados
        fechas = pd.date_range('2024-01-01', periods=12, freq='M')
        casos_nuevos = np.random.randint(15, 35, 12)
        casos_cerrados = np.random.randint(10, 30, 12)
        
        df = pd.DataFrame({
            'Fecha': fechas,
            'Casos Nuevos': casos_nuevos,
            'Casos Cerrados': casos_cerrados
        })
        
        st.line_chart(df.set_index('Fecha'))
        
        # Distribución por tipo de caso
        st.subheader("🏛️ Distribución por Área Legal")
        
        areas = ['Civil', 'Penal', 'Mercantil', 'Laboral', 'Fiscal']
        valores = [25, 18, 22, 20, 15]
        
        df_areas = pd.DataFrame({
            'Área Legal': areas,
            'Casos': valores
        })
        
        st.bar_chart(df_areas.set_index('Área Legal'))

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("🏛️ **AVANTILEX v1.0**")
    st.sidebar.markdown("*Prueba de Concepto - 2024*")