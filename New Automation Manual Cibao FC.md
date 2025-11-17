# Manual de Automatización - Cibao FC
## New Automation Manual Cibao FC

---

## 📋 Tabla de Contenidos / Table of Contents

**Parte 1: Descarga Automática de Datos / Part 1: Automatic Data Download**
1. [¿Qué es la Automatización? / What is Automation?](#qué-es-la-automatización)
2. [¿Qué Hace Automáticamente? / What Does It Do Automatically?](#qué-hace-automáticamente)
3. [¿Qué Necesitan Hacer Ustedes? / What Do You Need to Do?](#qué-necesitan-hacer-ustedes)
4. [Cómo Verificar que Funciona / How to Verify It Works](#cómo-verificar-que-funciona)
5. [Solución de Problemas / Troubleshooting](#solución-de-problemas)
6. [Preguntas Frecuentes / Frequently Asked Questions](#preguntas-frecuentes)

**Parte 2: Cargar Datos en Streamlit / Part 2: Loading Data into Streamlit**
7. [Cómo Cargar Datos en Streamlit / How to Load Data into Streamlit](#cómo-cargar-datos-en-streamlit)
8. [Actualizar la Aplicación Streamlit / Updating the Streamlit App](#actualizar-la-aplicación-streamlit)
9. [Proceso Completo Paso a Paso / Complete Step-by-Step Process](#proceso-completo-paso-a-paso)

---

## 🇪🇸 ESPAÑOL

### ¿Qué es la Automatización?

La automatización es un sistema que **descarga automáticamente** los datos de los partidos de la Copa Caribeña de Concacaf desde Scoresway y los guarda en el sistema. 

**Antes**: Teníamos que descargar manualmente cada partido, uno por uno.  
**Ahora**: El sistema lo hace automáticamente, sin que ustedes tengan que hacer nada.

---

### ¿Qué Hace Automáticamente?

El sistema hace **todo** el proceso automáticamente:

1. ✅ **Descubre Partidos Nuevos**: Busca automáticamente todos los partidos nuevos en la Copa Caribeña
2. ✅ **Descarga los Datos**: Obtiene automáticamente las estadísticas completas de cada partido
3. ✅ **Guarda los Archivos**: Guarda los datos en formato JSON en la carpeta correcta
4. ✅ **Solo Partidos Nuevos**: Solo descarga partidos que aún no tenemos (no duplica trabajo)

**Frecuencia**: El sistema puede ejecutarse automáticamente cada hora, cada día, o cuando ustedes lo necesiten.

---

### ¿Qué Necesitan Hacer Ustedes?

#### Opción 1: Sistema Automático (Recomendado) ⭐

**Si el sistema está configurado para ejecutarse automáticamente:**

✅ **NO NECESITAN HACER NADA**

El sistema se ejecutará automáticamente y descargará los nuevos partidos. Solo necesitan:
- Verificar ocasionalmente que los datos están actualizados en Streamlit
- Usar el botón "Actualizar datos" en Streamlit si es necesario

#### Opción 2: Ejecución Manual

**Si necesitan ejecutar el sistema manualmente:**

1. **Abrir Terminal** (en Mac: Buscar "Terminal" en Spotlight)
2. **Navegar a la carpeta del proyecto**:
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
   ```
3. **Activar el entorno virtual**:
   ```bash
   source .venv/bin/activate
   ```
4. **Ejecutar el script**:
   ```bash
   python3 src/data_processing/scrape_all_concacaf_matches.py
   ```

**Resultado**: El sistema descargará automáticamente todos los partidos nuevos.

---

### Cómo Verificar que Funciona

#### Método 1: Verificar en Streamlit

1. Abrir la aplicación Streamlit
2. Ir a la página de análisis de rendimiento
3. Verificar que aparecen los partidos más recientes en el selector de oponentes
4. Si no aparecen, hacer clic en "Actualizar datos (reload)" en la barra lateral

#### Método 2: Verificar Archivos JSON

1. Navegar a la carpeta:
   ```
   data/raw/concacaf/matchstats/
   ```
2. Verificar que hay archivos JSON con fechas recientes
3. Los archivos tienen nombres como: `YYYYMMDD_Equipo1_vs_Equipo2.json`

#### Método 3: Ejecutar en Modo "Dry Run"

Para ver qué partidos se descargarían sin descargarlos realmente:

```bash
python3 src/data_processing/scrape_all_concacaf_matches.py --dry-run
```

Esto mostrará una lista de partidos que se descargarían.

---

### Solución de Problemas

#### Problema 1: "No se encuentran nuevos partidos"

**Causa**: Todos los partidos ya están descargados, o no hay partidos nuevos disponibles.

**Solución**: 
- Esto es normal si ya se descargaron todos los partidos disponibles
- Verificar en Scoresway si hay partidos nuevos que deberían estar disponibles

#### Problema 2: "Error al descargar partido"

**Causa**: Problema temporal con la conexión o con la API de Scoresway.

**Solución**:
1. Esperar unos minutos y volver a intentar
2. Verificar la conexión a internet
3. Si el problema persiste, contactar al equipo de análisis

#### Problema 3: "Los datos no aparecen en Streamlit"

**Causa**: Los archivos JSON se descargaron, pero no se procesaron a Excel.

**Solución**:
1. Verificar que los archivos JSON están en `data/raw/concacaf/matchstats/`
2. Ejecutar el script de conversión a Excel (si está disponible)
3. Hacer clic en "Actualizar datos" en Streamlit

#### Problema 4: "Error: ModuleNotFoundError"

**Causa**: El entorno virtual no está activado o faltan dependencias.

**Solución**:
```bash
# Activar el entorno virtual
source .venv/bin/activate

# Instalar dependencias (si es necesario)
pip install -r requirements.txt
```

---

### Preguntas Frecuentes

#### ¿Con qué frecuencia se ejecuta el sistema?

**Respuesta**: Depende de cómo esté configurado:
- **Automático**: Puede ejecutarse cada hora o cada día
- **Manual**: Cuando ustedes lo ejecuten

**Recomendación**: Después de cada jornada de partidos, o al menos una vez al día durante la temporada.

#### ¿Qué pasa si un partido no se descarga?

**Respuesta**: El sistema registrará el error y continuará con los demás partidos. Pueden:
1. Intentar ejecutar el script nuevamente (intentará descargar los que fallaron)
2. Usar el modo `--force` para forzar la descarga de todos los partidos

#### ¿Necesitamos hacer algo después de que se descarguen los datos?

**Respuesta**: 
- Si el sistema está completamente automatizado: **NO**, solo usar Streamlit normalmente
- Si falta la conversión a Excel: Ejecutar el script de conversión (si está disponible)

#### ¿Los datos se actualizan automáticamente en Streamlit?

**Respuesta**: 
- Los archivos JSON se descargan automáticamente
- Para actualizar Streamlit, usar el botón "Actualizar datos (reload)" en la barra lateral
- O cerrar y volver a abrir Streamlit

#### ¿Qué pasa si el sistema falla?

**Respuesta**: 
1. Verificar los logs en `logs/scrape_matches.log` (si está configurado)
2. Intentar ejecutar el script manualmente
3. Contactar al equipo de análisis si el problema persiste

---

## 🇬🇧 ENGLISH

### What is Automation?

Automation is a system that **automatically downloads** match data from the Concacaf Caribbean Cup from Scoresway and saves it to the system.

**Before**: We had to manually download each match, one by one.  
**Now**: The system does it automatically, without you having to do anything.

---

### What Does It Do Automatically?

The system does **everything** automatically:

1. ✅ **Discovers New Matches**: Automatically searches for all new matches in the Caribbean Cup
2. ✅ **Downloads Data**: Automatically gets complete statistics for each match
3. ✅ **Saves Files**: Saves data in JSON format in the correct folder
4. ✅ **Only New Matches**: Only downloads matches we don't have yet (doesn't duplicate work)

**Frequency**: The system can run automatically every hour, every day, or whenever you need it.

---

### What Do You Need to Do?

#### Option 1: Automatic System (Recommended) ⭐

**If the system is configured to run automatically:**

✅ **YOU DON'T NEED TO DO ANYTHING**

The system will run automatically and download new matches. You only need to:
- Occasionally verify that data is updated in Streamlit
- Use the "Update data" button in Streamlit if needed

#### Option 2: Manual Execution

**If you need to run the system manually:**

1. **Open Terminal** (on Mac: Search for "Terminal" in Spotlight)
2. **Navigate to the project folder**:
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
   ```
3. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate
   ```
4. **Run the script**:
   ```bash
   python3 src/data_processing/scrape_all_concacaf_matches.py
   ```

**Result**: The system will automatically download all new matches.

---

### How to Verify It Works

#### Method 1: Verify in Streamlit

1. Open the Streamlit application
2. Go to the performance analysis page
3. Verify that recent matches appear in the opponent selector
4. If they don't appear, click "Update data (reload)" in the sidebar

#### Method 2: Verify JSON Files

1. Navigate to the folder:
   ```
   data/raw/concacaf/matchstats/
   ```
2. Verify that there are JSON files with recent dates
3. Files have names like: `YYYYMMDD_Team1_vs_Team2.json`

#### Method 3: Run in "Dry Run" Mode

To see which matches would be downloaded without actually downloading them:

```bash
python3 src/data_processing/scrape_all_concacaf_matches.py --dry-run
```

This will show a list of matches that would be downloaded.

---

### Troubleshooting

#### Problem 1: "No new matches found"

**Cause**: All matches are already downloaded, or there are no new matches available.

**Solution**: 
- This is normal if all available matches have already been downloaded
- Check Scoresway to see if there are new matches that should be available

#### Problem 2: "Error downloading match"

**Cause**: Temporary problem with connection or Scoresway API.

**Solution**:
1. Wait a few minutes and try again
2. Check internet connection
3. If the problem persists, contact the analytics team

#### Problem 3: "Data doesn't appear in Streamlit"

**Cause**: JSON files were downloaded, but not processed to Excel.

**Solution**:
1. Verify that JSON files are in `data/raw/concacaf/matchstats/`
2. Run the Excel conversion script (if available)
3. Click "Update data" in Streamlit

#### Problem 4: "Error: ModuleNotFoundError"

**Cause**: Virtual environment is not activated or dependencies are missing.

**Solution**:
```bash
# Activate virtual environment
source .venv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt
```

---

### Frequently Asked Questions

#### How often does the system run?

**Answer**: Depends on how it's configured:
- **Automatic**: Can run every hour or every day
- **Manual**: When you run it

**Recommendation**: After each matchday, or at least once a day during the season.

#### What happens if a match doesn't download?

**Answer**: The system will log the error and continue with other matches. You can:
1. Try running the script again (it will try to download failed ones)
2. Use `--force` mode to force download of all matches

#### Do we need to do anything after data is downloaded?

**Answer**: 
- If the system is fully automated: **NO**, just use Streamlit normally
- If Excel conversion is missing: Run the conversion script (if available)

#### Does data update automatically in Streamlit?

**Answer**: 
- JSON files are downloaded automatically
- To update Streamlit, use the "Update data (reload)" button in the sidebar
- Or close and reopen Streamlit

#### What happens if the system fails?

**Answer**: 
1. Check logs in `logs/scrape_matches.log` (if configured)
2. Try running the script manually
3. Contact the analytics team if the problem persists

---

## 🇪🇸 PARTE 2: CARGAR DATOS EN STREAMLIT

### Cómo Cargar Datos en Streamlit

Una vez que los datos se han descargado automáticamente desde Scoresway, necesitan cargarse en la aplicación Streamlit para que estén disponibles para análisis.

#### ¿Qué Son los Datos Descargados?

Los datos se descargan en formato **JSON** y se guardan en:
```
data/raw/concacaf/matchstats/
```

Cada archivo JSON contiene:
- Estadísticas completas del partido
- Datos de jugadores (alineaciones)
- Estadísticas de equipo
- Información del partido (fecha, equipos, resultado)

#### ¿Necesitan Convertir los Datos?

**Depende de cómo esté configurado Streamlit:**

1. **Si Streamlit lee directamente JSON**: No necesitan hacer nada, Streamlit los cargará automáticamente
2. **Si Streamlit necesita Excel**: Necesitan convertir JSON a Excel primero (ver sección siguiente)

---

### Actualizar la Aplicación Streamlit

#### Método 1: Botón de Actualización en Streamlit (Más Fácil) ⭐

1. **Abrir la aplicación Streamlit**
   ```bash
   streamlit run app.py
   ```

2. **Buscar el botón "Actualizar datos" o "Reload"** en la barra lateral (sidebar)

3. **Hacer clic en el botón**

4. **Esperar a que se actualice** (puede tomar unos segundos)

5. **Verificar** que los nuevos partidos aparecen en los selectores

**✅ Esto es todo lo que necesitan hacer si el botón está disponible**

#### Método 2: Reiniciar Streamlit

Si no hay botón de actualización:

1. **Cerrar Streamlit** (presionar `Ctrl+C` en la terminal donde está corriendo)

2. **Volver a abrir Streamlit**:
   ```bash
   streamlit run app.py
   ```

3. **Streamlit cargará automáticamente** los datos más recientes

#### Método 3: Limpiar Caché de Streamlit (Si los Datos No Aparecen)

Si los datos nuevos no aparecen después de actualizar:

1. **Detener Streamlit** (`Ctrl+C`)

2. **Limpiar el caché** (opcional, solo si es necesario):
   ```bash
   # Navegar a la carpeta del proyecto
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
   
   # Eliminar caché de Streamlit (si existe)
   rm -rf .streamlit/cache
   ```

3. **Volver a iniciar Streamlit**:
   ```bash
   streamlit run app.py
   ```

---

### Proceso Completo Paso a Paso

#### Escenario 1: Sistema Completamente Automatizado

**Si todo está configurado automáticamente:**

1. ✅ Los datos se descargan automáticamente (cada hora/día)
2. ✅ Los datos se procesan automáticamente (si está configurado)
3. ✅ Solo necesitan abrir Streamlit y usar el botón "Actualizar datos"

**Tiempo requerido**: 30 segundos

#### Escenario 2: Descarga Automática, Actualización Manual

**Si los datos se descargan automáticamente pero necesitan actualizar Streamlit manualmente:**

1. **Verificar que hay nuevos datos**:
   - Ir a `data/raw/concacaf/matchstats/`
   - Verificar que hay archivos JSON con fechas recientes

2. **Abrir Streamlit**:
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
   source .venv/bin/activate
   streamlit run app.py
   ```

3. **Hacer clic en "Actualizar datos"** en la barra lateral

4. **Verificar** que los nuevos partidos aparecen

**Tiempo requerido**: 2 minutos

#### Escenario 3: Todo Manual

**Si necesitan hacer todo manualmente:**

1. **Descargar nuevos partidos**:
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
   source .venv/bin/activate
   python3 src/data_processing/scrape_all_concacaf_matches.py
   ```

2. **Esperar a que termine** (puede tomar varios minutos)

3. **Abrir Streamlit**:
   ```bash
   streamlit run app.py
   ```

4. **Hacer clic en "Actualizar datos"** en la barra lateral

5. **Verificar** que los nuevos partidos aparecen

**Tiempo requerido**: 5-10 minutos (dependiendo de cuántos partidos hay)

---

### Verificar que los Datos Están Actualizados

#### Método 1: En Streamlit

1. Abrir la aplicación Streamlit
2. Ir a la página de análisis (ej: "Rendimiento Colectivo")
3. Buscar el selector de "Oponente" o "Partido"
4. Verificar que aparecen partidos con fechas recientes
5. Si no aparecen, hacer clic en "Actualizar datos"

#### Método 2: Verificar Archivos

1. Navegar a: `data/raw/concacaf/matchstats/`
2. Verificar que hay archivos JSON con fechas recientes
3. Los archivos tienen nombres como: `YYYYMMDD_Equipo1_vs_Equipo2.json`

#### Método 3: Verificar en la Terminal

Al ejecutar el script de descarga, verá un mensaje como:
```
✅ Found 20 total matches
🆕 New matches to scrape: 5
📥 Scraping 5 new matches...
```

Esto confirma que hay nuevos datos disponibles.

---

### Solución de Problemas - Carga en Streamlit

#### Problema 1: "Los datos no aparecen en Streamlit después de descargarlos"

**Solución**:
1. Verificar que los archivos JSON están en `data/raw/concacaf/matchstats/`
2. Hacer clic en "Actualizar datos" en Streamlit
3. Si no funciona, cerrar y volver a abrir Streamlit
4. Si aún no funciona, limpiar el caché (Método 3 arriba)

#### Problema 2: "Streamlit muestra datos antiguos"

**Causa**: Streamlit está usando datos en caché (guardados en memoria)

**Solución**:
1. Hacer clic en "Actualizar datos" en la barra lateral
2. O cerrar y volver a abrir Streamlit
3. O limpiar el caché manualmente

#### Problema 3: "Error al cargar datos en Streamlit"

**Solución**:
1. Verificar que los archivos JSON no están corruptos
2. Verificar que Streamlit tiene acceso a la carpeta de datos
3. Revisar los logs de Streamlit para ver el error específico
4. Contactar al equipo de análisis si el problema persiste

---

## 🇬🇧 PART 2: LOADING DATA INTO STREAMLIT

### How to Load Data into Streamlit

Once data has been automatically downloaded from Scoresway, it needs to be loaded into the Streamlit application to be available for analysis.

#### What Are the Downloaded Data?

Data is downloaded in **JSON** format and saved in:
```
data/raw/concacaf/matchstats/
```

Each JSON file contains:
- Complete match statistics
- Player data (lineups)
- Team statistics
- Match information (date, teams, result)

#### Do You Need to Convert the Data?

**Depends on how Streamlit is configured:**

1. **If Streamlit reads JSON directly**: You don't need to do anything, Streamlit will load them automatically
2. **If Streamlit needs Excel**: You need to convert JSON to Excel first (see next section)

---

### Updating the Streamlit App

#### Method 1: Update Button in Streamlit (Easiest) ⭐

1. **Open the Streamlit application**
   ```bash
   streamlit run app.py
   ```

2. **Look for the "Update data" or "Reload" button** in the sidebar

3. **Click the button**

4. **Wait for it to update** (may take a few seconds)

5. **Verify** that new matches appear in the selectors

**✅ This is all you need to do if the button is available**

#### Method 2: Restart Streamlit

If there's no update button:

1. **Close Streamlit** (press `Ctrl+C` in the terminal where it's running)

2. **Reopen Streamlit**:
   ```bash
   streamlit run app.py
   ```

3. **Streamlit will automatically load** the most recent data

#### Method 3: Clear Streamlit Cache (If Data Doesn't Appear)

If new data doesn't appear after updating:

1. **Stop Streamlit** (`Ctrl+C`)

2. **Clear the cache** (optional, only if necessary):
   ```bash
   # Navigate to the project folder
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
   
   # Delete Streamlit cache (if it exists)
   rm -rf .streamlit/cache
   ```

3. **Restart Streamlit**:
   ```bash
   streamlit run app.py
   ```

---

### Complete Step-by-Step Process

#### Scenario 1: Fully Automated System

**If everything is configured automatically:**

1. ✅ Data downloads automatically (every hour/day)
2. ✅ Data processes automatically (if configured)
3. ✅ You only need to open Streamlit and use the "Update data" button

**Time required**: 30 seconds

#### Scenario 2: Automatic Download, Manual Update

**If data downloads automatically but you need to update Streamlit manually:**

1. **Verify there's new data**:
   - Go to `data/raw/concacaf/matchstats/`
   - Verify there are JSON files with recent dates

2. **Open Streamlit**:
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
   source .venv/bin/activate
   streamlit run app.py
   ```

3. **Click "Update data"** in the sidebar

4. **Verify** that new matches appear

**Time required**: 2 minutes

#### Scenario 3: Everything Manual

**If you need to do everything manually:**

1. **Download new matches**:
   ```bash
   cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
   source .venv/bin/activate
   python3 src/data_processing/scrape_all_concacaf_matches.py
   ```

2. **Wait for it to finish** (may take several minutes)

3. **Open Streamlit**:
   ```bash
   streamlit run app.py
   ```

4. **Click "Update data"** in the sidebar

5. **Verify** that new matches appear

**Time required**: 5-10 minutes (depending on how many matches there are)

---

### Verify Data is Updated

#### Method 1: In Streamlit

1. Open the Streamlit application
2. Go to the analysis page (e.g., "Rendimiento Colectivo")
3. Look for the "Opponent" or "Match" selector
4. Verify that matches with recent dates appear
5. If they don't appear, click "Update data"

#### Method 2: Verify Files

1. Navigate to: `data/raw/concacaf/matchstats/`
2. Verify there are JSON files with recent dates
3. Files have names like: `YYYYMMDD_Team1_vs_Team2.json`

#### Method 3: Verify in Terminal

When running the download script, you'll see a message like:
```
✅ Found 20 total matches
🆕 New matches to scrape: 5
📥 Scraping 5 new matches...
```

This confirms that new data is available.

---

### Troubleshooting - Loading into Streamlit

#### Problem 1: "Data doesn't appear in Streamlit after downloading"

**Solution**:
1. Verify that JSON files are in `data/raw/concacaf/matchstats/`
2. Click "Update data" in Streamlit
3. If it doesn't work, close and reopen Streamlit
4. If it still doesn't work, clear the cache (Method 3 above)

#### Problem 2: "Streamlit shows old data"

**Cause**: Streamlit is using cached data (saved in memory)

**Solution**:
1. Click "Update data" in the sidebar
2. Or close and reopen Streamlit
3. Or clear the cache manually

#### Problem 3: "Error loading data in Streamlit"

**Solution**:
1. Verify that JSON files are not corrupted
2. Verify that Streamlit has access to the data folder
3. Check Streamlit logs to see the specific error
4. Contact the analytics team if the problem persists

---

## 📞 Contacto / Contact

Si tienen preguntas o problemas con el sistema de automatización, contacten al equipo de análisis.

If you have questions or problems with the automation system, contact the analytics team.

---

## 📝 Notas Finales / Final Notes

- El sistema está diseñado para funcionar automáticamente sin intervención manual
- Los datos se descargan en formato JSON y luego se procesan para su uso en Streamlit
- Si algo no funciona, siempre pueden ejecutar el script manualmente como respaldo
- Los logs se guardan para ayudar a diagnosticar problemas

- The system is designed to work automatically without manual intervention
- Data is downloaded in JSON format and then processed for use in Streamlit
- If something doesn't work, you can always run the script manually as a backup
- Logs are saved to help diagnose problems

---

**Última actualización / Last Updated**: Noviembre 2025

