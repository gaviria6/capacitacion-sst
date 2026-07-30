import streamlit as st
import vertexai
from vertexai.generative_models import GenerativeModel, Part
from PIL import Image
import io

# 1. Configuración de la página
st.set_page_config(
    page_title="Asistente SST - Demo", 
    page_icon="🛡️", 
    layout="centered"
)

# 2. Configuración de Vertex AI
vertexai.init(project="project-6ae24aa7-49e4-48c3-bcd", location="us-central1")

# 3. Inicializar el modelo
modelo = GenerativeModel(
    'gemini-2.5-flash',
    system_instruction="Eres un asesor experto en Seguridad y Salud en el Trabajo (SST) que trabaja para una ARL. Tu objetivo es ayudar a identificar peligros, evaluar riesgos y sugerir medidas de control preventivas de forma didáctica y basándote en normativas técnicas."
)

# 4. MEMORIA / HISTORIAL: Esto evita que se borre lo consultado al interactuar o actualizar
if "chat_session" not in st.session_state:
    st.session_state.chat_session = modelo.start_chat(history=[])

# --- DISEÑO AMIGABLE Y MINIMALISTA ---

# Barra lateral informativa (sin logos oficiales, ideal para conferencias)
with st.sidebar:
    st.header("⚙️ Acerca de la herramienta")
    st.info(
        "Panel interactivo de apoyo para la identificación de riesgos locativos, "
        "normativa y sugerencias preventivas en SST."
    )
    st.markdown("---")
    st.caption("Uso académico y demostrativo para conferencias.")
    
    # Botón opcional para limpiar la conversación si el usuario desea empezar de cero
    if st.button("🗑️ Reiniciar Conversación"):
        st.session_state.chat_session = modelo.start_chat(history=[])
        st.rerun()

# Interfaz Principal limpia
st.title("💡 Asistente Rápido de SST")
st.markdown("Pregúntame sobre normativa, sube fotos de inspecciones en campo o describe situaciones para recibir orientaciones al instante.")

# Desplegable elegante con ejemplos de uso (para guiar al público sin saturar la vista)
with st.expander("📌 Ejemplos de lo que puedes consultar"):
    st.markdown("""
    - *¿Cuáles son los requisitos obligatorios para trabajo en alturas?*
    - *Sube una foto de una zona de trabajo para identificar riesgos y EPP faltantes.*
    - *¿Cómo se evalúa un riesgo locativo en oficinas o bodegas?*
    """)

st.markdown("---")

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
        st.image(imagen_pil, caption="Evidencia visual cargada", width=350)
        
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

# 6. Mostrar el historial acumulado en pantalla (Mantiene los mensajes visibles)
for message in st.session_state.chat_session.history:
    role = "assistant" if message.role == "model" else "user"
    with st.chat_message(role):
        for part in message.parts:
            if part.text:
                st.markdown(part.text)

# 7. Capturar la entrada del usuario y procesar respuesta
if prompt := st.chat_input("Escribe tu consulta aquí..."):
    with st.chat_message("user"):
        st.markdown(prompt)
        if imagen_pil is not None:
            st.image(imagen_pil, width=200)

    paquete_envio = [prompt]
    if contenido_para_enviar:
        paquete_envio.extend(contenido_para_enviar)

    with st.chat_message("assistant"):
        with st.spinner("Analizando la información..."):
            try:
                respuesta = st.session_state.chat_session.send_message(paquete_envio)
                st.markdown(respuesta.text)
            except Exception as e:
                st.error(f"Ocurrió un error al procesar la solicitud: {e}")
