import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página
st.set_page_config(page_title="Asistente SST - ARL", page_icon="👷", layout="centered")
st.title("Auditor Virtual de SST 👷‍♂️")
st.write("Bienvenido a la capacitación. Describe un escenario de trabajo y analizaremos juntos los riesgos y medidas de prevención.")

# 2. Configuración de la API (Versión segura para Streamlit Cloud)
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)

# 3. Inicializar el modelo con el contexto de SST
modelo = genai.GenerativeModel(
    'gemini-2.5-flash',
    system_instruction="Eres un asesor experto en Seguridad y Salud en el Trabajo (SST) que trabaja para una ARL. Tu objetivo es ayudar a identificar peligros, evaluar riesgos y sugerir medidas de control preventivas de forma didáctica y basándote en normativas técnicas."
)

# 4. Manejo del historial de la sesión
if "chat_session" not in st.session_state:
    st.session_state.chat_session = modelo.start_chat(history=[])

# Mostrar el historial de mensajes en la pantalla
for message in st.session_state.chat_session.history:
    # Streamlit usa 'assistant' en lugar de 'model' para los íconos
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 5. Capturar la entrada del usuario
if prompt := st.chat_input("Escribe aquí un escenario de riesgo o consulta de SST..."):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        respuesta = st.session_state.chat_session.send_message(prompt)
        st.markdown(respuesta.text)
