# 🚀 Facturadora Automática - Fase 0 (MVP)

## 📋 Resumen

App web que automáticamente extrae datos de tickets/recibos usando IA y los guarda en Google Sheets. Sin código manual de datos.

**Flujo:**
1. 📸 Sube foto del ticket
2. 🤖 Claude Vision extrae datos automáticamente
3. ✏️ Revisa y ajusta si es necesario
4. 💾 Guarda en Google Sheets
5. 📊 Descarga Excel cuando quieras

---

## 🔧 Setup (15 minutos)

### Opción A: Streamlit Cloud (Recomendado - 2 minutos)

**Ventajas:**
- ✅ Acceso desde cualquier lado
- ✅ No necesitas instalar nada
- ✅ Hosting gratis
- ✅ Auto-updates

**Pasos:**

1. **Ve a:** https://streamlit.io/cloud
2. **Haz login** con tu cuenta GitHub (o crea una)
3. **Conecta tu repo** (o sube los archivos a GitHub)
4. **Deploy:**
   - Click en "New app"
   - Selecciona el repo/rama
   - Main file: `app.py`
   - Click "Deploy"

5. **Configura secretos** (credenciales):
   - En tu dashboard de Streamlit Cloud
   - Click en ⚙️ "Settings" → "Secrets"
   - Pega el contenido de abajo

### Opción B: Local en tu PC (Si prefieres ejecutar localmente)

```bash
# 1. Clon el repo o descarga los archivos
cd tu-carpeta

# 2. Instala dependencias
pip install -r requirements.txt

# 3. Ejecuta
streamlit run app.py

# La app abre en: http://localhost:8501
```

---

## 🔑 Configurar Google Sheets (5 minutos)

La app necesita permisos para guardar en Google Sheets. Así lo configuras:

### Paso 1: Crear proyecto en Google Cloud

1. Ve a: https://console.cloud.google.com/
2. Crea un nuevo proyecto (nombre: "FacturadoraMdF")
3. Habilita la API de Google Sheets:
   - Busca "Google Sheets API"
   - Click "Enable"

### Paso 2: Crear credenciales de servicio

1. Ve a: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "Create Service Account"
3. Nombre: `facturador-mdF`
4. Click "Create and Continue"
5. Dale permisos: `Editor` (por ahora)
6. Salta la parte de "Grant users access"
7. Click "Create"

### Paso 3: Generar JSON con credenciales

1. En la lista de service accounts, haz click en la que creaste
2. Ve a la pestaña "Keys"
3. Click "Add Key" → "Create new key"
4. Selecciona "JSON"
5. Se descarga un archivo `xxxx.json`
6. **Abre el archivo en un editor de texto** (Notepad, VS Code, etc)
7. **Copia TODO el contenido** (Ctrl+A, Ctrl+C)

### Paso 4: Agregar secretos a Streamlit

**Si usas Streamlit Cloud:**
1. Ve a tu app en https://share.streamlit.io/
2. Click en ⚙️ → "Settings" → "Secrets"
3. Pega esto:
```
google_sheets_credentials = {
    AQUÍ_PEGA_TODO_EL_CONTENIDO_DEL_JSON
}
```

Debería verse así:
```
google_sheets_credentials = {
  "type": "service_account",
  "project_id": "facturador-mdF",
  "private_key_id": "xxx",
  ... (todo el JSON)
}
```

**Si usas local:**
1. Crea un archivo `.streamlit/secrets.toml` en la carpeta del proyecto
2. Pega el mismo contenido de arriba

### Paso 5: Crear la hoja de Google Sheets

1. Ve a Google Sheets: https://sheets.google.com/
2. Click "Crear nuevo" → "Hoja de cálculo"
3. Nombre: `Facturas_Miles_de_Flor`
4. En la primera fila, agrega encabezados:
   - A1: `Timestamp`
   - B1: `Proveedor`
   - C1: `Fecha`
   - D1: `Monto`
   - E1: `Número Ticket`
   - F1: `ID Web`
   - G1: `Artículos`
   - H1: `Status`

5. Comparte la hoja con el email del service account:
   - Click "Compartir"
   - Pega el email (está en el JSON: `client_email`)
   - Dale permisos de Editor
   - Click "Compartir"

---

## ✅ Verificar que funcione

1. Sube la app a Streamlit Cloud (o ejecuta localmente)
2. Sube una foto de un ticket
3. Click "Extraer datos automáticamente"
4. Revisa que los datos se extraigan bien
5. Click "Confirmar y guardar"
6. Verifica que aparezca en Google Sheets

Si ves un error en Google Sheets, probablemente las credenciales no están bien configuradas.

---

## 📱 Cómo usarlo desde el celular

La app funciona en cualquier navegador. Así la usas desde la calle:

1. Abre el link: `https://share.streamlit.io/tu-usuario/tu-repo/main/app.py`
2. Toma foto del ticket con tu celular
3. Sube directamente desde la app
4. Confirma los datos
5. ¡Listo! Se guarda automáticamente

---

## 🐛 Troubleshooting

### "Error conectando a Google Sheets"
- Verifica que las credenciales estén bien en Streamlit Secrets
- Revisa que hayas compartido la hoja de cálculo con el service account

### "No se extrae bien del ticket"
- Toma foto más clara
- Mejor iluminación
- Asegúrate que se vea todo el ticket

### "¿Cómo agrego más columnas a Sheets?"
- Edita la función `save_to_sheets()` en `app.py`
- Agrega la columna en la lista `row = [...]`

---

## 🚀 Próximos pasos (Fase 1)

Cuando estés listo para escalar:
- Migrar a FastAPI + React + Supabase
- Soporte para múltiples usuarios
- Dashboard de analytics
- Integración directa con portales de facturación

---

## ❓ Preguntas?

Si algo no funciona, avísame. Esto es un MVP así que probablemente haya cosas por ajustar.

---

**Creado con ❤️ para Miles de Flor**
