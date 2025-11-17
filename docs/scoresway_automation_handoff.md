# Scoresway Automation Hand-Off (English & Español)

## English

### Purpose
Give Cibao FC a reliable, repeatable process to pull the latest Scoresway data, regenerate all analytics outputs, and refresh the Streamlit app with minimal manual work once we hand over the project in December.

### Components
1. **Single scraper script**  
   - Keep only the latest Scoresway ingestion script (no duplicates).  
   - Wrap it in a CLI, e.g. `python3 scripts/pull_scoresway.py --league liga-mayor`.  
   - Responsibilities: authenticate, detect new fixtures/results, export cleaned CSV/Excel files to `data/raw/scoresway/`.
2. **Processing & aggregation pipeline**  
   - Driver script: `python3 scripts/update_pipeline.py`.  
   - Steps: run the scraper, execute cleaning/per-90/percentile routines, regenerate Streamlit-ready workbooks, copy outputs into `data/processed/`.  
   - Externalize settings in `configs/pipeline.yml` so staff can adjust file paths, metrics, and league names without altering code.
3. **Streamlit integration**  
   - Continue caching loaders with `@st.cache_data`.  
   - Add a sidebar button:
     ```python
     if st.sidebar.button("Actualizar datos (reload)"):
         load_liga_mayor_per90.clear()
         st.success("Data refreshed from latest files.")
         st.experimental_rerun()
     ```
   - This lets coaches force a refresh after the pipeline runs.

### Daily Workflow
1. Drop new Scoresway exports into the shared source folder (or let the scraper pull them).  
2. Run `python3 scripts/update_pipeline.py --source-dir "/path/to/scoresway_exports"` (can be automated by cron or launchd).  
3. Open `streamlit run app.py`, press “Actualizar datos (reload)” if needed.  
4. Verify the newest fixture appears in the opponent dropdown and charts.

### Automation Options
- **Scheduled job**: configure macOS `launchd`, Windows Task Scheduler, or a lightweight server cron to run the pipeline nightly and email/Slack the result log.  
- **Cloud alternative**: host the repo on a small VM; pipeline runs via cron, and processed outputs sync back to a shared drive for coaches.

### Maintenance Checklist
- Keep service credentials (Scoresway, GitHub PATs) in `.env` or secure password manager.  
- Log each pipeline run (`logs/pipeline_YYYYMMDD.log`) with success/failure status.  
- Version processed outputs by copying them into `data/processed/history/` before overwriting, so staff can roll back.  
- Include a short `docs/recovery_steps.md` describing how to manually upload files if automation fails.

### Future Enhancements
- Add `pytest` coverage for scraper parsing and aggregation logic to catch format changes early.  
- Implement data validation (e.g., ensure per-90 metrics stay within expected ranges).  
- Consider a Streamlit admin page that shows pipeline run status and last update timestamp.

---

## Español

### Propósito
Entregar al Cibao FC un proceso confiable y repetible para descargar los datos más recientes de Scoresway, regenerar todos los productos analíticos y actualizar la aplicación de Streamlit con el mínimo trabajo manual cuando entreguemos el proyecto en diciembre.

### Componentes
1. **Script único de scraping**  
   - Mantener solo el script más actualizado de ingestión de Scoresway (sin duplicados).  
   - Envolverlo en una interfaz de línea de comandos, por ejemplo: `python3 scripts/pull_scoresway.py --league liga-mayor`.  
   - Responsabilidades: autenticarse, detectar nuevos partidos/resultados y exportar archivos CSV/Excel limpios a `data/raw/scoresway/`.
2. **Pipeline de procesamiento y agregación**  
   - Script principal: `python3 scripts/update_pipeline.py`.  
   - Pasos: ejecutar el scraper, correr las rutinas de limpieza/per-90/percentiles, regenerar los libros de Excel listos para Streamlit y copiar los resultados a `data/processed/`.  
   - Configurar ajustes en `configs/pipeline.yml` para que el staff pueda modificar rutas, métricas y nombres de ligas sin tocar el código.
3. **Integración con Streamlit**  
   - Seguir usando `@st.cache_data` para los cargadores.  
   - Añadir un botón en la barra lateral:
     ```python
     if st.sidebar.button("Actualizar datos (recargar)"):
         load_liga_mayor_per90.clear()
         st.success("Datos actualizados desde los archivos más recientes.")
         st.experimental_rerun()
     ```
   - Permite que el cuerpo técnico fuerce la recarga después de ejecutar el pipeline.

### Flujo de trabajo diario
1. Colocar las nuevas exportaciones de Scoresway en la carpeta compartida (o dejar que el scraper las descargue).  
2. Ejecutar `python3 scripts/update_pipeline.py --source-dir "/ruta/a_las_exportaciones_scoresway"` (se puede automatizar con cron o launchd).  
3. Abrir `streamlit run app.py` y pulsar “Actualizar datos (recargar)” si hace falta.  
4. Verificar que el partido más reciente aparezca en el selector de rival y en las gráficas.

### Opciones de automatización
- **Tarea programada**: configurar `launchd` en macOS, el Programador de tareas en Windows o un cron en un servidor ligero para correr el pipeline cada noche y enviar el log de resultados por correo o Slack.  
- **Alternativa en la nube**: alojar el repositorio en una máquina virtual pequeña; el pipeline corre con cron y los resultados procesados se sincronizan con una carpeta compartida para el cuerpo técnico.

### Lista de mantenimiento
- Guardar las credenciales de servicio (Scoresway, tokens de GitHub) en `.env` o un gestor seguro de contraseñas.  
- Registrar cada ejecución del pipeline (`logs/pipeline_YYYYMMDD.log`) con el estado de éxito o fallo.  
- Versionar los resultados procesados guardándolos en `data/processed/history/` antes de sobrescribir, para que el staff pueda regresar a una versión anterior.  
- Incluir un breve `docs/pasos_de_recuperacion.md` que describa cómo cargar archivos manualmente si la automatización falla.

### Mejoras futuras
- Añadir cobertura con `pytest` para el parser del scraper y la lógica de agregación, evitando sorpresas cuando cambie el formato de Scoresway.  
- Implementar validaciones de datos (por ejemplo, asegurar que las métricas per-90 permanezcan dentro de rangos esperados).  
- Considerar una página administrativa en Streamlit que muestre el estado del pipeline y la marca de tiempo de la última actualización.




