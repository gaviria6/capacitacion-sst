import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. Configuración de la página
st.set_page_config(page_title="Asistente SST - ARL", page_icon="👷", layout="centered")
st.title("Asesor Virtual de SST 👷‍♂️")
st.write("Bienvenido. Describe un escenario de trabajo, sube una foto de una condición peligrosa o adjunta un documento para analizar.")

# 2. Configuración de la API
import os
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# 3. Inicializar el modelo (usando gemini-3.5-flash)
modelo = genai.GenerativeModel(
    'gemini-3.5-flash',
    system_instruction="Eres un asesor experto en Seguridad y Salud en el Trabajo (SST) que trabaja para una ARL. Tu objetivo es ayudar a identificar peligros, evaluar riesgos y sugerir medidas de control preventivas de forma didáctica y basándote en normativas técnicas."
)

# 4. Manejo del historial de la sesión
if "chat_session" not in st.session_state:
    st.session_state.chat_session = modelo.start_chat(history=[])

# Mostrar el historial de mensajes anterior
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# 5. Componente para subir archivos (Imágenes o PDFs)
archivo_subido = st.file_uploader(
    "Sube una imagen de inspección o un documento de apoyo (Opcional):", 
    type=["png", "jpg", "jpeg", "pdf"]
)

# Si el usuario subió una imagen, la mostramos en pantalla de forma previa
contenido_para_enviar = []
if archivo_subido is not None:
    # Verificamos si es una imagen
    if archivo_subido.type in ["image/png", "image/jpeg", "image/jpg"]:
        imagen = Image.open(archivo_subido)
        st.image(imagen, caption="Imagen cargada para inspección de SST", use_column_width=True)
        contenido_para_enviar.append(imagen)
    else:
        # Si es un PDF o documento, informamos que se adjuntó
        st.info(f"📄 Documento adjuntado: {archivo_subido.name}")
        # Para PDFs u otros archivos, leemos los bytes
        bytes_archivo = archivo_subido.getvalue()
        contenido_para_enviar.append({
            'mime_type': archivo_subido.type,
            'data': bytes_archivo
        })

# 6. Capturar la entrada del usuario (Chat)
if prompt := st.chat_input("Escribe tu consulta o pide que analice el archivo subido..."):
    # Mostramos el mensaje del usuario en el chat
    with st.chat_message("user"):
        st.markdown(prompt)
        if archivo_subido is not None and archivo_subido.type in ["image/png", "image/jpeg", "image/jpg"]:
            st.image(imagen, width=200)

    # Preparamos lo que se le enviará a la IA (texto + archivo si existe)
    paquete_envio = [prompt]
    if contenido_para_enviar:
        # Añadimos los elementos multimedia o documentos al paquete de envío
        paquete_envio.extend(contenido_para_enviar)

    # 7. Respuesta del modelo de IA
    with st.chat_message("assistant"):
        with st.spinner("Analizando la información y normativa SST..."):
            try:
                # Enviamos el contenido multimodal a la sesión de chat
                respuesta = st.session_state.chat_session.send_message(paquete_envio)
                st.markdown(respuesta.text)
            except Exception as e:
                st.error(f"Ocurrió un error al procesar la solicitud: {e}")
