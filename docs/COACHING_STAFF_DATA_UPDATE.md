# Actualización de Datos para el Personal Técnico

## ✅ Solución Implementada

**Ya NO necesitas reiniciar Streamlit después de cada partido!**

### Dos Formas de Actualizar:

#### 1. **Actualización Automática** (Recomendado)
- Los datos se actualizan **automáticamente cada 5 minutos**
- No necesitas hacer nada - solo espera 5 minutos después de ejecutar el script de scraping
- El sistema detecta nuevos archivos automáticamente

#### 2. **Actualización Manual** (Inmediata)
- Haz clic en el botón **"🔄 Actualizar Datos"** en la parte superior de la página
- Los datos se actualizan inmediatamente
- Útil cuando acabas de ejecutar el script de scraping y no quieres esperar

---

## 📋 Flujo de Trabajo Recomendado

### Después de cada partido:

1. **Ejecutar el script de scraping:**
   ```bash
   python3 src/data_processing/scrape_all_concacaf_matches.py
   ```
   → Esto guarda los nuevos archivos JSON en `data/raw/concacaf/matchstats/`

2. **Actualizar Streamlit:**
   - **Opción A**: Esperar 5 minutos (actualización automática)
   - **Opción B**: Hacer clic en "🔄 Actualizar Datos" (actualización inmediata)

3. **¡Listo!** Los nuevos datos aparecen en la aplicación

---

## 🔍 ¿Dónde está el botón?

El botón **"🔄 Actualizar Datos"** está ubicado:
- **Justo debajo del título** de la página "Análisis del Rival - Copa Concacaf"
- **Centrado** en la página
- **Color naranja** (botón primario)

También puedes encontrar información en el **sidebar** (panel lateral):
- Expande **"ℹ️ Actualización de Datos"** para más información

---

## ⚙️ Detalles Técnicos

### ¿Cómo funciona?

1. **Cache con TTL (Time-To-Live)**:
   - Los datos se guardan en memoria por 5 minutos
   - Después de 5 minutos, el cache expira automáticamente
   - La función se ejecuta de nuevo y lee todos los archivos (incluyendo nuevos)

2. **Botón de actualización manual**:
   - Limpia el cache inmediatamente
   - Fuerza la relectura de todos los archivos
   - Actualiza la página automáticamente

### Ventajas:

✅ **No necesitas reiniciar** la aplicación Streamlit  
✅ **Actualización automática** cada 5 minutos  
✅ **Actualización inmediata** con un solo clic  
✅ **Simple** para el personal técnico  

---

## 📝 Notas Importantes

- **Los archivos se guardan inmediatamente** cuando ejecutas el script de scraping
- **El cache es solo para rendimiento** - los archivos siempre están actualizados en disco
- **5 minutos es un buen balance** entre rendimiento y actualización
- Si necesitas actualización más frecuente, puedes hacer clic en el botón

---

## 🆘 Solución de Problemas

### "No veo los nuevos datos después de hacer clic en Actualizar"
- Verifica que el script de scraping se ejecutó correctamente
- Verifica que los archivos JSON están en `data/raw/concacaf/matchstats/`
- Intenta hacer clic en "🔄 Actualizar Datos" de nuevo

### "Quiero actualización más rápida que 5 minutos"
- Usa el botón "🔄 Actualizar Datos" para actualización inmediata
- O podemos reducir el TTL a 1-2 minutos si es necesario

### "El botón no funciona"
- Asegúrate de que Streamlit está corriendo
- Refresca la página del navegador
- Si persiste, reinicia Streamlit como último recurso

