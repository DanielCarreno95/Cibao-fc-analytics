# 📊 Guía de Automatización de Datos - Para el Cuerpo Técnico

## ¿Qué es el SDAPI Outlet Key y por qué lo necesitamos?

El **SDAPI Outlet Key** es como una "llave" que nos permite acceder a los datos de partidos desde Scoresway (la plataforma que usa Concacaf para mostrar estadísticas). 

**Piénsalo así:**
- Scoresway tiene una "puerta" con datos de todos los partidos
- El SDAPI Outlet Key es la "llave" que abre esa puerta
- Sin esta llave, no podemos obtener los datos automáticamente

**Nuestra llave actual:** `ft1tiv1inq7v1sk3y9tv12yh5`

---

## 🔄 Proceso Completo: De Scoresway a la App Streamlit

### **PASO 1: Descubrir Partidos Nuevos** 🔍

**¿Qué hace?**
El sistema busca automáticamente todos los partidos del torneo Concacaf Caribbean Cup y encuentra cuáles son nuevos (que aún no hemos descargado).

**¿Cómo funciona?**
1. El script llama a la API de Scoresway usando el SDAPI Outlet Key
2. Obtiene una lista de TODOS los partidos del torneo
3. Compara con los partidos que ya tenemos descargados
4. Identifica cuáles son nuevos

**Ejemplo de URL que usa:**
```
https://api.performfeeds.com/soccerdata/match/ft1tiv1inq7v1sk3y9tv12yh5/?_rt=c&tmcl=bygi47fmsxgbzysjdf9u481lg
```

**Resultado:** Lista de partidos nuevos que necesitamos descargar

---

### **PASO 2: Descargar Datos de Cada Partido** 📥

**¿Qué hace?**
Para cada partido nuevo, descarga TODOS los datos:
- Estadísticas del partido (posesión, tiros, pases, etc.)
- Eventos del partido (goles, tarjetas, sustituciones)
- Alineaciones
- Estadísticas de jugadores

**¿Cómo funciona?**
1. Toma el ID del partido
2. Usa el SDAPI Outlet Key para acceder a los datos
3. Descarga toda la información en formato JSON
4. Guarda el archivo en: `data/raw/concacaf/matchstats/`

**Ejemplo de URL que usa:**
```
https://api.performfeeds.com/soccerdata/matchstats/ft1tiv1inq7v1sk3y9tv12yh5/{match_id}?_rt=c&_lcl=en&_fmt=jsonp&sps=widgets&_clbk={callback_id}
```

**Resultado:** Archivos JSON con todos los datos del partido

---

### **PASO 3: Procesar los Datos** ⚙️

**¿Qué hace?**
Convierte los archivos JSON en un formato que la app Streamlit puede usar fácilmente.

**¿Cómo funciona?**
1. Lee los archivos JSON descargados
2. Extrae las estadísticas importantes
3. Organiza los datos en tablas
4. Guarda en formato que la app puede leer

**Resultado:** Datos listos para usar en la app

---

### **PASO 4: Actualizar la App Streamlit** 🚀

**¿Qué hace?**
La app Streamlit lee los nuevos datos y los muestra en los gráficos y tablas.

**¿Cómo funciona?**
1. La app busca los archivos de datos más recientes
2. Carga la información nueva
3. Actualiza todos los gráficos y análisis automáticamente

**Resultado:** App actualizada con los últimos partidos

---

## 📋 Cómo Ejecutar el Proceso (Para el Cuerpo Técnico)

### **Opción 1: Automático (Recomendado)** ✅

**Una vez configurado, el sistema se ejecuta solo cada hora.**

**Pasos para configurar (solo una vez):**

1. **Abrir Terminal** (en Mac: buscar "Terminal" en Spotlight)

2. **Ir a la carpeta del proyecto:**
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
   ```

3. **Activar el entorno virtual:**
   ```bash
   source venv/bin/activate
   ```

4. **Ejecutar el script:**
   ```bash
   python3 src/data_processing/scrape_all_concacaf_matches.py
   ```

**¿Qué verás?**
```
🚀 Concacaf Caribbean Cup - Automated Match Scraper
============================================================
📋 Already scraped: 45 matches
🔍 Fetching all matches from PerformFeeds API...
✅ Found 50 total matches
🆕 New matches to scrape: 5

📥 Scraping 5 new matches...

[1/5] Cibao FC vs Defence Force (2025-11-15)
   ✅ Success

[2/5] Mount Pleasant vs Cavalier (2025-11-16)
   ✅ Success

...

✅ Scraping complete!
   Success: 5
   Failed: 0
   Total scraped: 50
```

---

### **Opción 2: Verificar Antes de Descargar** 👀

**Útil para ver qué partidos se descargarían sin descargarlos realmente:**

```bash
python3 src/data_processing/scrape_all_concacaf_matches.py --dry-run
```

**¿Qué verás?**
```
🔍 DRY RUN - Would scrape these matches:
   - abc123xyz: Cibao FC vs Defence Force (2025-11-15)
   - def456uvw: Mount Pleasant vs Cavalier (2025-11-16)
   ... and 3 more
```

---

### **Opción 3: Forzar Re-descarga de Todo** 🔄

**Útil si necesitas actualizar datos de partidos ya descargados:**

```bash
python3 src/data_processing/scrape_all_concacaf_matches.py --force
```

⚠️ **Nota:** Esto descargará TODOS los partidos de nuevo, incluso los que ya tenemos.

---

### **Opción 4: Descargar un Partido Específico** 🎯

**Si solo necesitas un partido en particular:**

```bash
python3 src/data_processing/scrape_scoresway_match.py <match_id>
```

**Ejemplo:**
```bash
python3 src/data_processing/scrape_scoresway_match.py 2zhrn3wxg2ma02g2u2j5lotuc
```

---

## 🔧 Configuración Automática (Una Vez)

### **Para Mac (macOS):**

1. **Crear archivo de configuración:**
   - Abrir TextEdit
   - Crear nuevo documento
   - Copiar el siguiente contenido:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cibao.scrape_matches</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics/src/data_processing/scrape_all_concacaf_matches.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics</string>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

2. **Guardar como:** `com.cibao.scrape_matches.plist` en la carpeta `~/Library/LaunchAgents/`

3. **Activar en Terminal:**
   ```bash
   launchctl load ~/Library/LaunchAgents/com.cibao.scrape_matches.plist
   ```

**Resultado:** El sistema descargará nuevos partidos automáticamente cada hora.

---

## 📊 Flujo Visual del Proceso

```
┌─────────────────────────────────────────────────────────────┐
│                    SCORESWAY (Fuente de Datos)              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  API con SDAPI Outlet Key: ft1tiv1inq7v1sk3y9tv12yh5│   │
│  └──────────────────────────────────────────────────────┘   │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 1: Descubrir Partidos                                 │
│  • Buscar todos los partidos del torneo                    │
│  • Comparar con partidos ya descargados                     │
│  • Identificar partidos nuevos                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 2: Descargar Datos                                    │
│  • Para cada partido nuevo:                                 │
│    - Estadísticas del partido                              │
│    - Eventos (goles, tarjetas, etc.)                       │
│    - Alineaciones                                          │
│    - Estadísticas de jugadores                             │
│  • Guardar en: data/raw/concacaf/matchstats/               │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 3: Procesar Datos                                     │
│  • Convertir JSON a formato usable                         │
│  • Organizar en tablas                                     │
│  • Preparar para la app                                    │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│  PASO 4: Actualizar App Streamlit                           │
│  • Cargar nuevos datos                                     │
│  • Actualizar gráficos                                     │
│  • Mostrar análisis actualizados                          │
└─────────────────────────────────────────────────────────────┘
```

---

## ❓ Preguntas Frecuentes

### **¿Con qué frecuencia se actualizan los datos?**
- **Automático:** Cada hora (si está configurado)
- **Manual:** Cuando ejecutes el script

### **¿Qué pasa si un partido falla al descargarse?**
- El sistema continúa con los demás partidos
- El error se registra en los logs
- Puedes intentar descargarlo de nuevo manualmente

### **¿Necesito estar conectado a internet?**
- Sí, el sistema necesita internet para acceder a la API de Scoresway

### **¿Qué pasa si el SDAPI Outlet Key deja de funcionar?**
- Los scripts mostrarán errores
- Necesitarás obtener un nuevo key (como mostró el profesor)
- Actualizar el key en los archivos de configuración

### **¿Cuánto tiempo toma descargar los datos?**
- Depende de cuántos partidos nuevos hay
- Aproximadamente 1-2 segundos por partido
- El sistema espera 1 segundo entre cada descarga para no sobrecargar el servidor

---

## 🎯 Resumen para el Cuerpo Técnico

**Lo que necesitan saber:**

1. ✅ **El sistema está automatizado** - Una vez configurado, funciona solo
2. ✅ **El SDAPI Outlet Key es la "llave"** - Permite acceder a los datos
3. ✅ **El proceso es simple:**
   - Descubrir partidos nuevos
   - Descargar datos
   - Procesar datos
   - Actualizar app
4. ✅ **Pueden ejecutarlo manualmente** cuando quieran actualizar los datos
5. ✅ **Los datos se guardan automáticamente** en la carpeta correcta

**Para ejecutar manualmente:**
```bash
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
source venv/bin/activate
python3 src/data_processing/scrape_all_concacaf_matches.py
```

---

## 📞 Soporte

Si algo no funciona:
1. Revisar los logs en `logs/scrape_matches.log`
2. Verificar conexión a internet
3. Verificar que el SDAPI Outlet Key sigue siendo válido
4. Contactar al equipo técnico

---

**Última actualización:** Noviembre 2025

