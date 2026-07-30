import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from PIL import Image
import io

# 1. Configuración de la página
st.set_page_config(page_title="Asistente SST - ARL", page_icon="👷", layout="centered")
st.title("Asesor Virtual de SST 👷‍♂️")
st.write("Bienvenido. Describe un escenario de trabajo, sube una foto de una condición peligrosa o adjunta un documento para analizar.")

# 2. Configuración de Vertex AI (Autenticación automática con Google Cloud)
vertexai.init(project="project-6ae24aa7-49e4-48c3-bcd", location="us-central1")

# 3. Inicializar el modelo con la versión estándar compatible en Vertex AI
modelo = GenerativeModel(
    'gemini-2.5-flash',
    system_instruction="Eres un asesor experto en Seguridad y Salud en el Trabajo (SST) que trabaja para una ARL. Tu objetivo es ayudar a identificar peligros, evaluar riesgos y sugerir medidas de control preventivas de forma didáctica y basándote en normativas técnicas."
)

# 4. Manejo del historial de la sesión
if "chat_session" not in st.session_state:
    st.session_state.chat_session = modelo.start_chat(history=[])

# Mostrar el historial de mensajes anterior
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        for part in message.parts:
            if part.text:
                st.markdown(part.text)

# 5. Componente para subir archivos (Imágenes o PDFs)
archivo_subido = st.file_uploader(
    "Sube una imagen de inspección o un documento de apoyo (Opcional):", 
    type=["png", "jpg", "jpeg", "pdf"]
)

contenido_para_enviar = []
imagen_pil = None

if archivo_subido is not None:
    if archivo_subido.type in ["image/png", "image/jpeg", "image/jpg"]:
        imagen_pil = Image.open(archivo_subido)
        st.image(imagen_pil, caption="Imagen cargada para inspección de SST", use_column_width=True)
        
        # Convertimos la imagen PIL a bytes para enviarla correctamente a Vertex AI
        buffered = io.BytesIO()
        imagen_pil.save(buffered, format=imagen_pil.format if imagen_pil.format else "JPEG")
        img_bytes = buffered.getvalue()
        
        parte_imagen = Part.from_data(data=img_bytes, mime_type=archivo_subido.type)
        contenido_para_enviar.append(parte_imagen)
    else:
        st.info(f"📄 Documento adjuntado: {archivo_subido.name}")
        bytes_archivo = archivo_subido.getvalue()
        parte_documento = Part.from_data(data=bytes_archivo, mime_type=archivo_subido.type)
        contenido_para_enviar.append(parte_documento)

# 6. Capturar la entrada del usuario (Chat)
if prompt := st.chat_input("Escribe tu consulta o pide que analice el archivo subido..."):
    with st.chat_message("user"):
        st.markdown(prompt)
        if imagen_pil is not None:
            st.image(imagen_pil, width=200)

    paquete_envio = [prompt]
    if contenido_para_enviar:
        paquete_envio.extend(contenido_para_enviar)

    # 7. Respuesta del modelo de IA
    with st.chat_message("assistant"):
        with st.spinner("Analizando la información y normativa SST..."):
            try:
                respuesta = st.session_state.chat_session.send_message(paquete_envio)
                st.markdown(respuesta.text)
            except Exception as e:
                st.error(f"Ocurrió un error al procesar la solicitud: {e}")
