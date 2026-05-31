# Prototipo RAG para tesis

Este repositorio contiene el prototipo técnico del sistema basado en **Retrieval-Augmented Generation (RAG)** para consultas documentales académicas y técnicas.

El proyecto forma parte de la tesis de Juan Diego Arce Castro:

**Diseño, implementación y validación de un sistema basado en Retrieval-Augmented Generation (RAG), integrado a canales conversacionales mediante OpenClaw, para evaluar la trazabilidad documental, calidad de recuperación y confiabilidad de respuestas en consultas documentales académicas y técnicas.**

---

## 1. Contexto general del proyecto

El objetivo técnico del prototipo es construir una arquitectura RAG capaz de:

1. Cargar documentos académicos y técnicos.
2. Extraer texto desde diferentes formatos documentales.
3. Limpiar y normalizar contenido.
4. Dividir documentos en fragmentos o chunks.
5. Guardar documentos y chunks en PostgreSQL.
6. Preparar los chunks para una etapa posterior de embeddings.
7. Recuperar evidencia documental.
8. Generar respuestas trazables y fundamentadas.
9. Integrar el sistema a un canal conversacional mediante OpenClaw y Discord.

El sistema no busca entrenar un modelo de inteligencia artificial desde cero. El objetivo es validar una arquitectura funcional que combine ingesta documental, almacenamiento, recuperación, generación de respuestas y trazabilidad.

---

## 2. Ruta local y repositorio

Ruta local del proyecto:

```text
/home/diego/rag-tesis
```

Repositorio remoto:

```text
https://github.com/diegoarcecast/RAG.git
```

Rama principal:

```text
main
```

---

## 3. Estado actual real del proyecto

### Implementado y validado

* Proyecto local creado en `/home/diego/rag-tesis`.
* Repositorio Git inicializado.
* Repositorio remoto conectado con GitHub.
* Rama principal: `main`.
* Ambiente virtual Python creado en `.venv`.
* PostgreSQL instalado y funcionando.
* Base de datos creada: `rag_tesis`.
* Usuario de base de datos creado: `rag_user`.
* Extensión `pgvector` habilitada.
* Extensión validada: `vector 0.6.0`.
* Tablas creadas:

  * `documents`
  * `document_chunks`
  * `rag_queries`
  * `retrieval_logs`
* Tablas propiedad de `rag_user`.
* Pipeline inicial de ingesta documental implementado.
* Persistencia básica en PostgreSQL implementada.
* Comando de ingesta individual implementado: `app.ingest_document`.
* Opción `--save-db` agregada para guardar documentos y chunks en PostgreSQL.
* Comando de ingesta por carpeta implementado: `app.ingest_folder`.
* Ingesta por carpeta validada con varios formatos.
* Limpieza segura por `file_path` validada.
* Chunking mejorado para evitar inicios de chunks en medio de palabras.
* `.gitignore` actualizado para evitar archivos locales no deseados.

---

## 4. Estructura técnica actual

```text
rag-tesis/
├── app/
│   ├── db.py
│   ├── db_check.py
│   ├── ingest_document.py
│   ├── ingest_folder.py
│   └── ingestion/
│       ├── __init__.py
│       ├── cleaner.py
│       ├── chunker.py
│       ├── detector.py
│       ├── extractors.py
│       ├── pipeline.py
│       └── repository.py
├── database/
│   └── schema.sql
├── data/
│   ├── raw/
│   │   ├── .gitkeep
│   │   └── samples/
│   └── processed/
│       └── debug/
├── docs/
├── logs/
├── scripts/
├── .env
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 5. Reglas de seguridad del repositorio

No se deben subir al repositorio:

* `.env`
* `.venv/`
* `logs/`
* `data/processed/`
* Documentos reales dentro de `data/raw/`
* Archivos locales de herramientas externas como `.antigravitycli/`

La carpeta `data/raw/` se conserva mediante `.gitkeep`.

La carpeta `.antigravitycli/` fue detectada como archivo local generado por herramienta externa y debe permanecer ignorada.

---

## 6. Base de datos actual

Base de datos:

```text
rag_tesis
```

Usuario:

```text
rag_user
```

Extensión vectorial:

```text
pgvector / vector 0.6.0
```

### Tabla `documents`

Campos relevantes:

```text
id
title
source_type
file_path
author
publication_year
created_at
```

Uso:

* Guarda el registro padre de cada documento procesado.
* El `title` actualmente se toma del nombre del archivo.
* El `source_type` corresponde al tipo documental detectado.
* El `file_path` permite identificar y limpiar ingestas de prueba.

### Tabla `document_chunks`

Campos relevantes:

```text
id
document_id
chunk_index
chunk_text
page_number
section_title
metadata
embedding vector(768)
created_at
```

Relación:

```text
document_chunks.document_id -> documents.id
ON DELETE CASCADE
```

Esto significa que al eliminar un documento desde `documents`, PostgreSQL elimina automáticamente sus chunks asociados en `document_chunks`.

### Tablas futuras para recuperación

También existen:

```text
rag_queries
retrieval_logs
```

Estas tablas todavía no se están usando de forma activa. Su uso será posterior, cuando se implemente búsqueda semántica y registro de consultas.

---

## 7. Archivos principales del sistema

### `app/db.py`

Contiene la conexión a PostgreSQL usando variables de entorno desde `.env`.

Funciones principales:

```text
get_conninfo()
get_connection()
```

Uso:

* Centraliza la conexión a PostgreSQL.
* Usa `psycopg`.
* Usa `python-dotenv` para cargar `.env`.

---

### `app/db_check.py`

Valida la conexión a PostgreSQL.

Comando validado:

```bash
python -m app.db_check
```

Resultado esperado:

```text
Conexión correcta: base=rag_tesis, usuario=rag_user
```

---

### `app/ingestion/detector.py`

Detecta el tipo documental.

Formatos soportados:

```text
.pdf       -> pdf
.docx      -> docx
.txt       -> txt
.md        -> markdown
.markdown  -> markdown
.html      -> html
.htm       -> html
.csv       -> csv
.xlsx      -> xlsx
```

Funciones principales:

```text
detect_file_type(file_path)
ensure_supported_file(file_path)
```

---

### `app/ingestion/cleaner.py`

Limpia texto extraído.

Funciones principales:

```text
normalize_unicode(text)
remove_control_characters(text)
normalize_whitespace(text)
clean_text(text)
has_sufficient_text(text, min_characters=300)
```

Uso importante:

* `has_sufficient_text()` permite decidir si un PDF necesita OCR cuando la extracción directa no produce suficiente texto.

---

### `app/ingestion/extractors.py`

Extrae texto desde documentos.

Soporta:

* PDF directo con PyMuPDF.
* PDF escaneado con OCR usando Tesseract.
* DOCX.
* TXT.
* Markdown.
* HTML.
* CSV.
* XLSX.

Regla implementada para PDF:

1. Intentar extracción directa con PyMuPDF.
2. Si el texto extraído no alcanza el mínimo definido, aplicar OCR.
3. Registrar método de extracción:

   * `direct`
   * `ocr`

Constantes relevantes:

```text
OCR_LANGUAGES = "spa+eng"
MIN_DIRECT_TEXT_CHARACTERS = 300
```

---

### `app/ingestion/chunker.py`

Divide texto en chunks.

Componentes:

```text
TextChunk
split_text_into_chunks()
chunks_to_dicts()
```

Parámetros usados en pruebas:

```text
chunk_size = 300
chunk_overlap = 50
min_chunk_size = 100
```

Estado actual:

* El chunker ya no inicia chunks en medio de palabras.
* Se mejoró para buscar límites más naturales:

  * párrafos
  * líneas
  * oraciones
  * signos de puntuación
  * espacios
* Se validó con TXT y XLSX.

Resultado observado en TXT:

* Chunk 0: introducción del sistema.
* Chunk 1: trazabilidad documental y calidad de recuperación.
* Chunk 2: confiabilidad de respuesta.

Resultado observado en XLSX:

* El segundo chunk ya no inició con texto cortado como `rtinentes.`
* Ahora inicia en una línea completa.

---

### `app/ingestion/pipeline.py`

Orquesta la ingesta documental en memoria.

Etapas:

```text
[1/5] Detectar tipo de archivo
[2/5] Extraer texto del documento
[3/5] Construir metadata base
[4/5] Dividir texto en chunks
[5/5] Construir resultado final
```

Función principal:

```text
ingest_document_to_memory()
```

Retorna un diccionario con:

```text
success
started_at
completed_at
document
text
pages
chunks
next_steps
```

Si falla, retorna:

```text
success: False
failed_stage
error_type
error_message
instructions
traceback
```

---

### `app/ingestion/repository.py`

Capa de persistencia hacia PostgreSQL.

Funciones implementadas:

```text
insert_document(document)
insert_document_chunks(document_id, chunks)
save_ingestion_result(ingestion_result)
delete_document_by_file_path(file_path)
```

Responsabilidad:

* Insertar documentos en `documents`.
* Insertar chunks en `document_chunks`.
* Guardar en PostgreSQL el resultado generado por el pipeline.
* Limpiar una ingesta por `file_path`.

La función `delete_document_by_file_path()` fue validada y elimina el documento. Por `ON DELETE CASCADE`, también elimina los chunks asociados.

---

### `app/ingest_document.py`

Comando principal de ingesta individual desde terminal.

Opciones soportadas:

```text
--chunk-size
--chunk-overlap
--min-chunk-size
--show-text
--show-chunks
--json-output
--save-db
```

Uso principal:

```bash
python -m app.ingest_document data/raw/samples/prueba_xlsx.xlsx --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --show-chunks
```

Uso con guardado en base de datos:

```bash
python -m app.ingest_document data/raw/samples/prueba_xlsx.xlsx --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --save-db
```

---

### `app/ingest_folder.py`

Comando para procesar una carpeta completa.

Función:

* Recorre una carpeta.
* Ignora archivos ocultos como `.gitkeep`.
* Valida si cada archivo es soportado.
* Ejecuta el pipeline sobre cada archivo.
* Si se usa `--save-db`, guarda cada documento y sus chunks en PostgreSQL.

Comando validado sin guardar en BD:

```bash
python -m app.ingest_folder data/raw/samples --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100
```

Comando validado con guardado en BD:

```bash
python -m app.ingest_folder data/raw/samples --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --save-db
```

---

## 8. Formatos documentales validados

Se validó procesamiento en memoria con:

```text
TXT
Markdown
HTML
CSV
XLSX
```

Se validó ingesta por carpeta con:

```text
CSV
HTML
Markdown
TXT
XLSX
```

Pendientes de validar:

```text
PDF con texto seleccionable
PDF escaneado con OCR
DOCX
```

Aunque DOCX tiene extractor implementado, todavía no se ha validado en la tanda actual de pruebas.

---

## 9. Archivos de prueba utilizados

Carpeta de documentos de prueba:

```text
data/raw/samples
```

Archivos usados:

```text
prueba_txt.txt
prueba_markdown.md
prueba_html.html
prueba_csv.csv
prueba_xlsx.xlsx
```

Archivo ignorado correctamente:

```text
.gitkeep
```

---

## 10. Validaciones realizadas

### Validación del ambiente virtual

Comando:

```bash
source .venv/bin/activate
which python
python --version
```

Resultado esperado:

```text
/home/diego/rag-tesis/.venv/bin/python
Python 3.12.3
```

---

### Validación de conexión a PostgreSQL

Comando:

```bash
python -m app.db_check
```

Resultado validado:

```text
Conexión correcta: base=rag_tesis, usuario=rag_user
```

---

### Validación de ingesta individual en memoria

Comando de ejemplo:

```bash
python -m app.ingest_document data/raw/samples/prueba_xlsx.xlsx --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --show-chunks
```

Resultado validado para XLSX:

```text
Éxito: True
Tipo documental: xlsx
Método de extracción: direct
Caracteres extraídos: 382
Chunks generados: 2
```

---

### Validación de salida JSON

Comando:

```bash
python -m app.ingest_document data/raw/samples/prueba_xlsx.xlsx --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --json-output data/processed/debug/prueba_xlsx.json
```

Resultado:

```text
Resultado JSON guardado en: /home/diego/rag-tesis/data/processed/debug/prueba_xlsx.json
```

---

### Validación de ingesta individual con PostgreSQL

Comando:

```bash
python -m app.ingest_document data/raw/samples/prueba_xlsx.xlsx --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --save-db
```

Resultado validado:

```text
Ingesta guardada en PostgreSQL
document_id: 2
chunks_insertados: 2
```

---

### Validación de ingesta por carpeta sin PostgreSQL

Comando:

```bash
python -m app.ingest_folder data/raw/samples --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100
```

Resultado validado:

```text
Archivos encontrados: 5
Procesados correctamente: 5
Fallidos: 0
Guardados en BD: 0
```

---

### Validación de ingesta por carpeta con PostgreSQL

Comando:

```bash
python -m app.ingest_folder data/raw/samples --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --save-db
```

Resultado validado:

```text
Procesados correctamente: 5
Fallidos: 0
Guardados en BD: 5
```

Documentos insertados:

```text
prueba_csv.csv        -> document_id: 3, chunks: 2
prueba_html.html      -> document_id: 4, chunks: 1
prueba_markdown.md    -> document_id: 5, chunks: 2
prueba_txt.txt        -> document_id: 6, chunks: 3
prueba_xlsx.xlsx      -> document_id: 7, chunks: 2
```

Conteos validados en PostgreSQL:

```text
documents = 5
document_chunks = 10
```

Posteriormente se limpió la base de datos de prueba y se confirmó que quedó vacía:

```text
documents = 0
document_chunks = 0
```

---

## 11. Comandos útiles

### Activar ambiente virtual

```bash
cd /home/diego/rag-tesis
source .venv/bin/activate
```

### Validar conexión a PostgreSQL

```bash
python -m app.db_check
```

### Consultar tablas

```bash
psql -h localhost -U rag_user -d rag_tesis -c "\dt"
```

### Consultar documentos guardados

```bash
psql -h localhost -U rag_user -d rag_tesis -c "SELECT id, title, source_type, file_path FROM documents ORDER BY id DESC LIMIT 5;"
```

### Consultar chunks guardados

```bash
psql -h localhost -U rag_user -d rag_tesis -c "SELECT id, document_id, chunk_index, LEFT(chunk_text, 120) AS preview FROM document_chunks ORDER BY id DESC LIMIT 10;"
```

### Confirmar conteo de documentos

```bash
psql -h localhost -U rag_user -d rag_tesis -c "SELECT COUNT(*) AS total_documents FROM documents;"
```

### Confirmar conteo de chunks

```bash
psql -h localhost -U rag_user -d rag_tesis -c "SELECT COUNT(*) AS total_chunks FROM document_chunks;"
```

### Limpiar una ingesta por `file_path`

```bash
python - <<'PY'
from app.ingestion.repository import delete_document_by_file_path

file_path = "/home/diego/rag-tesis/data/raw/samples/prueba_xlsx.xlsx"

deleted = delete_document_by_file_path(file_path)

print(f"Documentos eliminados: {deleted}")
PY
```

---

## 12. Problemas detectados y aprendizajes

### Permisos

Se trabajó accidentalmente como `root` usando:

```bash
sudo su
```

Esto causó archivos con dueño `root` dentro del proyecto y errores como:

```text
Permission denied
```

Solución aplicada:

```bash
sudo chown -R diego:diego /home/diego/rag-tesis
```

Regla:

```text
No trabajar como root dentro del proyecto.
```

---

### Python

Desde el usuario normal, el comando `python` solo funciona correctamente si está activo el `.venv`.

Forma correcta:

```bash
cd /home/diego/rag-tesis
source .venv/bin/activate
```

Luego validar:

```bash
which python
python --version
```

Resultado esperado:

```text
/home/diego/rag-tesis/.venv/bin/python
Python 3.12.3
```

---

### PostgreSQL

El usuario Linux `diego` no existe como rol en PostgreSQL.

Por eso, usar siempre:

```bash
psql -h localhost -U rag_user -d rag_tesis
```

No usar simplemente:

```bash
psql -d rag_tesis
```

porque intenta conectarse como el usuario Linux `diego`.

---

### Markdown del README

Se detectaron problemas al pegar bloques largos de Markdown desde terminal usando heredoc.

Regla:

```text
Editar README.md manualmente desde VS Code cuando el contenido sea largo.
```

---

## 13. Estado de Git conocido

Se realizaron commits previos para:

1. Configuración inicial de PostgreSQL y pgvector.
2. Dependencias de procesamiento documental y OCR.
3. Pipeline inicial de ingesta documental.
4. Persistencia de ingesta documental en PostgreSQL.
5. Comando inicial de ingesta documental por carpeta.

Commit conocido:

```text
35845d7 Agrega persistencia de ingesta documental en PostgreSQL
```

Después de ese commit se creó y subió otro commit para el comando de ingesta por carpeta.

Cambios actuales pendientes antes del siguiente commit:

```text
.gitignore
app/ingest_folder.py
app/ingestion/chunker.py
README.md
```

Motivo de los cambios pendientes:

* Ignorar `.antigravitycli/`.
* Ajustar `app.ingest_folder` para ignorar archivos ocultos como `.gitkeep`.
* Mejorar `app/ingestion/chunker.py` para iniciar chunks en límites más naturales.
* Actualizar README con el estado real del proyecto.

---

## 14. Pendientes reales actuales

1. Hacer commit de los cambios actuales cuando el README quede revisado.
2. Probar PDF con texto seleccionable.
3. Probar PDF escaneado con OCR.
4. Validar DOCX con un documento real de prueba.
5. Evaluar si se requiere mejorar aún más el chunking para documentos largos.
6. Definir metadata avanzada:

   * `page_number`
   * `section_title`
   * nombre original del documento
   * tipo de extracción
   * versión del corpus
7. Implementar generación de embeddings.
8. Guardar embeddings en `document_chunks.embedding`.
9. Crear índice vectorial cuando exista suficiente volumen de chunks.
10. Implementar búsqueda semántica.
11. Registrar consultas en `rag_queries`.
12. Registrar recuperación en `retrieval_logs`.
13. Integrar recuperación con generación de respuestas.
14. Integrar con OpenClaw y Discord.

---

## 15. Próximo paso recomendado

El próximo paso técnico recomendado es:

```text
1. Guardar este README corregido.
2. Revisar git status.
3. Agregar a staging:
   - README.md
   - .gitignore
   - app/ingest_folder.py
   - app/ingestion/chunker.py
4. Crear commit.
5. Subir a GitHub.
```

Después de eso:

```text
Probar PDF con texto seleccionable.
```

Luego:

```text
Probar PDF escaneado con OCR.
```

No se recomienda avanzar a embeddings hasta validar correctamente la ingesta de PDF, porque los PDF probablemente serán parte importante del corpus documental de la tesis.
