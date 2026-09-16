import streamlit as st
import anthropic
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
import json
import base64
from io import BytesIO

# Configuración de página
st.set_page_config(
    page_title="Facturadora Automática - Miles de Flor",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos personalizados
st.markdown("""
    <style>
    .header-title {
        font-size: 2.5em;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1em;
    }
    .status-box {
        padding: 1em;
        border-radius: 0.5em;
        margin: 1em 0;
    }
    .status-success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .status-error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    .status-info {
        background-color: #d1ecf1;
        color: #0c5460;
        border: 1px solid #bee5eb;
    }
    </style>
""", unsafe_allow_html=True)

# Título
st.markdown('<div class="header-title">📸 Facturadora Automática</div>', unsafe_allow_html=True)
st.markdown("*Miles de Flor - Automatización de Facturas*")

# ============ INICIALIZACIÓN DE SESIÓN ============
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False
if "upload_history" not in st.session_state:
    st.session_state.upload_history = []

# ============ CONFIGURACIÓN ============
@st.cache_resource
def init_anthropic():
    api_key = st.secrets.get("ANTHROPIC_API_KEY")
    if not api_key:
        st.error("⚠️ Falta configurar ANTHROPIC_API_KEY en Streamlit Secrets")
        st.stop()
    return anthropic.Anthropic(api_key=api_key)

@st.cache_resource
def init_gspread():
    """Inicializa conexión con Google Sheets"""
    try:
        creds = st.secrets.get("google_sheets_credentials")
        if not creds:
            st.warning("⚠️ Configura las credenciales de Google Sheets en Streamlit secrets")
            return None

        if isinstance(creds, str):
            creds = json.loads(creds)

        credentials = Credentials.from_service_account_info(
            creds,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Error inicializando Google Sheets: {e}")
        return None

        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        return gspread.authorize(credentials)
    except Exception as e:
        st.error(f"Error inicializando Google Sheets: {e}")
        return None

# ============ FUNCIONES ============
def extract_ticket_data(image_bytes):
    """
    Extrae datos del ticket usando Claude Vision
    Retorna: dict con proveedor, fecha, monto, número de ticket
    """
    client = init_anthropic()

    # Convertir imagen a base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    prompt = """Analiza esta imagen de un ticket/recibo y extrae la siguiente información:

1. **Proveedor**: ¿De dónde es? (Walmart, Costco, Gasolinera, otro)
2. **Fecha**: Fecha de la compra (formato DD/MM/YYYY)
3. **Monto**: Total pagado (solo número con 2 decimales)
4. **Número de Ticket**: Folio, ticket número o código de transacción
5. **ID Web**: Si aparece código para facturación en línea (como "Código para facturar: XXXXX")
6. **Artículos principales**: Lista breve de qué se compró (máximo 3 items)

Responde SOLO en formato JSON, así:
{
    "proveedor": "Walmart",
    "fecha": "16/09/2026",
    "monto": "808.93",
    "numero_ticket": "TCH#3874035933434",
    "id_web": "No aplica",
    "articulos": ["Roblox 300", "Artículos varios"],
    "confianza": "Alta"
}

Si no puedes extraer un dato, escribe "No disponible". Sé preciso."""

    message = client.messages.create(
           model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image_base64,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ],
            }
        ],
    )

    # Parsear respuesta JSON
    response_text = message.content[0].text

    # Buscar JSON en la respuesta
    import re
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if json_match:
        data = json.loads(json_match.group())
        return data
    else:
        st.error("No se pudo extraer datos del ticket. Intenta con otra imagen.")
        return None

def save_to_sheets(data, gc):
    """Guarda los datos en Google Sheets"""
    try:
        # Abrir hoja (asume que existe)
        spreadsheet = gc.open("Facturas_Miles_de_Flor")
        worksheet = spreadsheet.sheet1

        # Preparar fila
        row = [
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            data.get("proveedor", ""),
            data.get("fecha", ""),
            data.get("monto", ""),
            data.get("numero_ticket", ""),
            data.get("id_web", ""),
            data.get("articulos", ""),
            "✓ Confirmado",
        ]

        # Agregar fila
        worksheet.append_row(row)
        return True
    except Exception as e:
        st.error(f"Error guardando en Google Sheets: {e}")
        return False

def generate_excel(history):
    """Genera archivo Excel con historial"""
    df = pd.DataFrame(history)

    # Crear archivo en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Facturas', index=False)

    output.seek(0)
    return output

# ============ INTERFAZ PRINCIPAL ============
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📤 Paso 1: Sube la foto del ticket")
    uploaded_file = st.file_uploader(
        "Sube la imagen del ticket",
        type=["jpg", "jpeg", "png"],
        help="Toma una foto clara del ticket desde cualquier ángulo"
    )

with col2:
    st.subheader("ℹ️ Consejos")
    st.info("""
    ✓ Foto clara y legible
    ✓ Todos los datos visibles
    ✓ Buena iluminación
    ✓ Formato: JPG o PNG
    """)

# ============ PROCESAMIENTO ============
if uploaded_file is not None:
    st.markdown("---")

    # Mostrar imagen
    st.image(uploaded_file, caption="Ticket subido", width=300)

    if st.button("🔍 Extraer datos automáticamente", key="extract_btn", type="primary"):
        with st.spinner("Analizando ticket..."):
            image_bytes = uploaded_file.read()
            extracted = extract_ticket_data(image_bytes)

            if extracted:
                st.session_state.extracted_data = extracted
                st.success("✅ Datos extraídos exitosamente")

# ============ REVISIÓN Y CONFIRMACIÓN ============
if st.session_state.extracted_data:
    st.markdown("---")
    st.subheader("📝 Paso 2: Revisa y confirma los datos")

    data = st.session_state.extracted_data

    # Formulario editable
    col1, col2 = st.columns(2)

    with col1:
        proveedor = st.text_input("Proveedor", value=data.get("proveedor", ""))
        fecha = st.text_input("Fecha (DD/MM/YYYY)", value=data.get("fecha", ""))
        monto = st.text_input("Monto ($)", value=data.get("monto", ""))

    with col2:
        numero_ticket = st.text_input("Número de Ticket", value=data.get("numero_ticket", ""))
        id_web = st.text_input("ID Web/Código Facturación", value=data.get("id_web", ""))
        articulos = st.text_area("Artículos", value=", ".join(data.get("articulos", [])))

    confianza = st.select_slider(
        "Confianza de extracción",
        options=["Baja", "Media", "Alta"],
        value="Alta"
    )

    # Botones de acción
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("✅ Confirmar y guardar", type="primary", key="confirm_btn"):
            # Actualizar datos
            st.session_state.extracted_data = {
                "proveedor": proveedor,
                "fecha": fecha,
                "monto": monto,
                "numero_ticket": numero_ticket,
                "id_web": id_web,
                "articulos": [a.strip() for a in articulos.split(",")],
                "confianza": confianza
            }

            # Guardar en historial local
            st.session_state.upload_history.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "proveedor": proveedor,
                "fecha": fecha,
                "monto": monto,
                "numero_ticket": numero_ticket,
                "id_web": id_web,
                "articulos": articulos,
                "status": "✓ Confirmado"
            })

            # Intentar guardar en Google Sheets
            gc = init_gspread()
            if gc:
                if save_to_sheets(st.session_state.extracted_data, gc):
                    st.markdown(
                        '<div class="status-box status-success">✅ Guardado en Google Sheets</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        '<div class="status-box status-error">❌ Error al guardar en Sheets (revisa credenciales)</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(
                    '<div class="status-box status-info">ℹ️ Google Sheets no configurado - Guardado solo localmente</div>',
                    unsafe_allow_html=True
                )

            st.session_state.confirmed = True
            st.rerun()

    with col2:
        if st.button("📋 Copiar al portapapeles"):
            data_text = f"""
Proveedor: {proveedor}
Fecha: {fecha}
Monto: ${monto}
Ticket: {numero_ticket}
ID Web: {id_web}
Artículos: {articulos}
            """
            st.code(data_text, language="text")
            st.info("Copia el texto arriba")

    with col3:
        if st.button("🔄 Cancelar"):
            st.session_state.extracted_data = None
            st.rerun()

# ============ HISTORIAL ============
if st.session_state.upload_history:
    st.markdown("---")
    st.subheader("📊 Historial de facturas")

    # DataFrame
    df = pd.DataFrame(st.session_state.upload_history)
    st.dataframe(df, use_container_width=True)

    # Descargar como Excel
    excel_file = generate_excel(st.session_state.upload_history)
    st.download_button(
        label="📥 Descargar como Excel",
        data=excel_file,
        file_name=f"facturas_mdf_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# ============ CONFIGURACIÓN (SIDEBAR) ============
with st.sidebar:
    st.subheader("⚙️ Configuración")

    st.write("**Estado de conexiones:**")

    # Anthropic
    try:
        client = init_anthropic()
        st.success("✓ Claude API conectada")
    except:
        st.error("✗ Claude API - Error de conexión")

    # Google Sheets
    gc = init_gspread()
    if gc:
        st.success("✓ Google Sheets conectada")
    else:
        st.warning("✗ Google Sheets - Configura credenciales")

    st.markdown("---")
    st.write("**Instrucciones:**")
    st.info("""
    1. Sube foto del ticket
    2. Haz clic en "Extraer datos"
    3. Revisa y ajusta si es necesario
    4. Confirma para guardar
    5. Descarga Excel cuando necesites
    """)
