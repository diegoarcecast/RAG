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
6. Generar embeddings para los chunks.
7. Almacenar vectores en PostgreSQL mediante pgvector.
8. Recuperar evidencia documental mediante búsqueda semántica.
9. Generar respuestas trazables y fundamentadas.
10. Integrar el sistema a un canal conversacional mediante OpenClaw y Discord.

El sistema no busca entrenar un modelo de inteligencia artificial desde cero. El objetivo es validar una arquitectura funcional que combine ingesta documental, almacenamiento, recuperación semántica, generación de respuestas y trazabilidad documental.

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
* Modelo local de embeddings instalado en Ollama: `nomic-embed-text`.
* Generación de embeddings implementada.
* Embeddings guardados en `document_chunks.embedding`.
* Búsqueda semántica implementada con pgvector.
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
│   ├── embed_chunks.py
│   ├── search_chunks.py
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── ollama_client.py
│   │   ├── repository.py
│   │   └── search_repository.py
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

Los documentos técnicos usados para pruebas permanecen locales. El README documenta los nombres y resultados, pero los archivos del corpus no deben versionarse si contienen peso innecesario o información no destinada al repositorio.

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

La columna `embedding` almacena vectores de 768 dimensiones generados con el modelo local `nomic-embed-text` mediante Ollama.

### Tablas para trazabilidad RAG

También existen:

```text
rag_queries
retrieval_logs
```

Estas tablas todavía no se están usando de forma activa. Su uso será posterior, cuando se implemente el registro formal de consultas y recuperación documental.

### Estado actual de datos

La base local quedó poblada con el corpus técnico de prueba:

```text
documents = 5
document_chunks = 1550
chunks_con_embedding = 1550
chunks_sin_embedding = 0
```
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

Parámetros usados en pruebas pequeñas:

```text
chunk_size = 300
chunk_overlap = 50
min_chunk_size = 100
```

Parámetros usados en corpus técnico realista:

```text
chunk_size = 1200
chunk_overlap = 200
min_chunk_size = 120
```

Estado actual:

* El chunker ya no inicia chunks en medio de palabras.
* Se mejoró para buscar límites más naturales:

  * párrafos
  * líneas
  * oraciones
  * signos de puntuación
  * espacios
* Se validó con TXT, XLSX y corpus técnico más extenso.

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
python -m app.ingest_folder data/raw/samples --chunk-size 1200 --chunk-overlap 200 --min-chunk-size 120
```

Comando validado con guardado en BD:

```bash
python -m app.ingest_folder data/raw/samples --chunk-size 1200 --chunk-overlap 200 --min-chunk-size 120 --save-db
```

---

### `app/embeddings/ollama_client.py`

Cliente local para Ollama.

Responsabilidad:

* Enviar texto al endpoint local de Ollama.
* Usar el modelo `nomic-embed-text`.
* Validar que el embedding generado tenga 768 dimensiones.

Endpoint usado:

```text
http://localhost:11434/api/embeddings
```

Función principal:

```text
generate_embedding()
```

---

### `app/embeddings/repository.py`

Repositorio para operaciones de embeddings en PostgreSQL.

Responsabilidad:

* Contar chunks con embedding.
* Contar chunks sin embedding.
* Obtener chunks pendientes.
* Actualizar embeddings por `chunk_id`.

Funciones principales:

```text
get_chunks_without_embeddings()
update_chunk_embedding()
count_chunks_without_embeddings()
count_chunks_with_embeddings()
```

---

### `app/embed_chunks.py`

Comando para generar embeddings por lotes.

Uso:

```bash
python -m app.embed_chunks --limit 100
```

Responsabilidad:

* Buscar chunks sin embedding.
* Generar embedding con Ollama.
* Guardar el vector en `document_chunks.embedding`.
* Mostrar conteos antes y después.

---

### `app/embeddings/search_repository.py`

Repositorio para búsqueda vectorial con pgvector.

Responsabilidad:

* Recibir un embedding de consulta.
* Compararlo contra `document_chunks.embedding`.
* Ordenar resultados por distancia vectorial.
* Retornar los chunks más similares.

Operador usado:

```text
<=>
```

Este operador calcula distancia vectorial en pgvector.

---

### `app/search_chunks.py`

Comando para búsqueda semántica.

Uso:

```bash
python -m app.search_chunks "retrieval augmented generation hallucination fact checking" --limit 5
```

Responsabilidad:

* Recibir una consulta en lenguaje natural.
* Generar embedding de la consulta.
* Buscar chunks similares usando pgvector.
* Mostrar documento, chunk, distancia y texto recuperado.

---

## 8. Formatos documentales validados

Se validó procesamiento con:

```text
TXT
Markdown
HTML
CSV
XLSX
PDF con texto seleccionable
PDF escaneado con OCR
```

Se validó ingesta por carpeta con:

```text
CSV
HTML
Markdown
TXT
XLSX
PDF
```

También existe extractor para DOCX, pero todavía falta validarlo con un documento DOCX real de prueba.

---

## 9. Corpus y archivos de prueba utilizados

### Pruebas iniciales pequeñas

Carpeta:

```text
data/raw/samples
```

Archivos usados inicialmente:

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

### Corpus técnico realista

Documentos procesados:

* `AlgorithmsNotesForProfessionals.pdf`
* `Hallucination to Truth_ A Review of Fact-Checking and Factuality Evaluation in Large Language Models.html`
* `KALI LINUX.pdf`
* `ListadoArticulosAcademicos.xlsx`
* `PostgreSQLNotesForProfessionals.pdf`

Este corpus permitió validar:

* PDF directo largo.
* HTML académico/técnico.
* PDF escaneado con OCR.
* XLSX académico.
* Documentación técnica extensa.
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

### Validación de ingesta por carpeta sin PostgreSQL

Comando:

```bash
python -m app.ingest_folder data/raw/samples --chunk-size 1200 --chunk-overlap 200 --min-chunk-size 120
```

Resultado validado con corpus técnico:

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
python -m app.ingest_folder data/raw/samples --chunk-size 1200 --chunk-overlap 200 --min-chunk-size 120 --save-db
```

Resultado validado:

```text
Procesados correctamente: 5
Fallidos: 0
Guardados en BD: 5
```

Documentos insertados:

```text
AlgorithmsNotesForProfessionals.pdf      -> document_id: 8, chunks: 420
Hallucination...html                      -> document_id: 9, chunks: 208
KALI LINUX.pdf                            -> document_id: 10, chunks: 4
ListadoArticulosAcademicos.xlsx           -> document_id: 11, chunks: 787
PostgreSQLNotesForProfessionals.pdf       -> document_id: 12, chunks: 131
```

Conteos validados en PostgreSQL:

```text
documents = 5
document_chunks = 1550
```

---

### Validación de modelo de embeddings

Modelo instalado en Ollama:

```text
nomic-embed-text
```

Comando usado para instalar:

```bash
ollama pull nomic-embed-text
```

Prueba realizada:

```text
Embedding generado correctamente.
Dimensiones: 768
```

Esto confirmó compatibilidad con:

```text
document_chunks.embedding vector(768)
```

---

### Validación de generación de embeddings por lotes

Comando inicial:

```bash
python -m app.embed_chunks --limit 3
```

Resultado inicial:

```text
Embeddings generados: 3
Fallidos: 0
Chunks sin embedding después: 1547
Chunks con embedding después: 3
```

Luego se procesó el resto del corpus por lotes.

Resultado final confirmado:

```text
total_chunks = 1550
chunks_con_embedding = 1550
chunks_sin_embedding = 0
```

---

### Validación directa en PostgreSQL de embeddings

Comando:

```bash
psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS total_chunks FROM document_chunks;"

psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS chunks_con_embedding FROM document_chunks WHERE embedding IS NOT NULL;"

psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS chunks_sin_embedding FROM document_chunks WHERE embedding IS NULL;"
```

Resultado:

```text
total_chunks = 1550
chunks_con_embedding = 1550
chunks_sin_embedding = 0
```

---

### Validación de búsqueda semántica

Consulta sobre algoritmos:

```bash
python -m app.search_chunks "Big O notation algorithm complexity" --limit 5
```

Resultado esperado validado:

```text
Recuperó chunks desde AlgorithmsNotesForProfessionals.pdf
```

Consulta sobre RAG y alucinaciones:

```bash
python -m app.search_chunks "retrieval augmented generation hallucination fact checking" --limit 5
```

Resultado esperado validado:

```text
Recuperó chunks desde Hallucination to Truth...html
```

Consulta sobre PostgreSQL JSONB:

```bash
python -m app.search_chunks "PostgreSQL JSONB operators and querying JSON documents" --limit 5
```

Resultado esperado validado:

```text
Recuperó chunks desde PostgreSQLNotesForProfessionals.pdf
```

Observación:

Las consultas en inglés funcionan mejor porque la mayor parte del corpus técnico está en inglés. Las consultas en español pueden recuperar resultados menos precisos cuando los documentos fuente están en inglés.

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
psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT id, title, source_type, file_path FROM documents ORDER BY id DESC LIMIT 10;"
```

### Consultar chunks guardados

```bash
psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT id, document_id, chunk_index, LEFT(chunk_text, 120) AS preview FROM document_chunks ORDER BY id DESC LIMIT 10;"
```

### Confirmar conteo de documentos

```bash
psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS total_documents FROM documents;"
```

### Confirmar conteo de chunks

```bash
psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS total_chunks FROM document_chunks;"
```

### Verificar embeddings

```bash
psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS chunks_con_embedding FROM document_chunks WHERE embedding IS NOT NULL;"

psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS chunks_sin_embedding FROM document_chunks WHERE embedding IS NULL;"
```

### Ingesta por carpeta

```bash
python -m app.ingest_folder data/raw/samples --chunk-size 1200 --chunk-overlap 200 --min-chunk-size 120 --save-db
```

### Generar embeddings por lotes

```bash
python -m app.embed_chunks --limit 100
```

### Buscar chunks similares

```bash
python -m app.search_chunks "retrieval augmented generation hallucination fact checking" --limit 5
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

### Paginador de PostgreSQL

Algunas consultas largas abren el paginador de `psql` y muestran `(END)`.

Para salir:

```text
q
```

Para evitar el paginador:

```bash
psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) FROM document_chunks;"
```

---

### Markdown del README

Se detectaron problemas al pegar bloques largos de Markdown desde terminal usando heredoc.

Regla:

```text
Editar README.md manualmente desde VS Code cuando el contenido sea largo.
```

---

### Tamaño del corpus XLSX

El archivo `ListadoArticulosAcademicos.xlsx` inicialmente generó demasiados chunks:

```text
49,281,031 caracteres
53,398 chunks
```

Se redujo el contenido del Excel y quedó en un tamaño más manejable:

```text
726,988 caracteres
787 chunks
```

Regla:

```text
No usar archivos excesivamente grandes para validaciones iniciales.
Primero validar con corpus reducido y controlado.
```

---

## 13. Estado técnico actual

El sistema ya tiene funcionando:

1. Ingesta documental individual.
2. Ingesta documental por carpeta.
3. Extracción de PDF con texto seleccionable.
4. Extracción OCR para PDF escaneado.
5. Extracción HTML.
6. Extracción XLSX.
7. Chunking mejorado.
8. Persistencia en PostgreSQL.
9. Generación de embeddings con Ollama.
10. Almacenamiento vectorial con pgvector.
11. Búsqueda semántica sobre chunks vectorizados.

La base de datos local quedó poblada con:

```text
documents = 5
document_chunks = 1550
chunks_con_embedding = 1550
chunks_sin_embedding = 0
```

---

## 14. Validación con corpus técnico de prueba

Se validó la ingesta de una carpeta con documentos técnicos y académicos más realistas ubicados en `data/raw/samples`.

Documentos procesados:

* `AlgorithmsNotesForProfessionals.pdf`
* `Hallucination to Truth_ A Review of Fact-Checking and Factuality Evaluation in Large Language Models.html`
* `KALI LINUX.pdf`
* `ListadoArticulosAcademicos.xlsx`
* `PostgreSQLNotesForProfessionals.pdf`

Parámetros usados:

```bash
python -m app.ingest_folder data/raw/samples --chunk-size 1200 --chunk-overlap 200 --min-chunk-size 120 --save-db
```

Resultado validado:

```text
Procesados correctamente: 5
Fallidos: 0
Guardados en BD: 5
```

Conteos validados en PostgreSQL:

```text
documents = 5
document_chunks = 1550
```

Distribución de chunks:

```text
AlgorithmsNotesForProfessionals.pdf      -> 420 chunks
Hallucination...html                      -> 208 chunks
KALI LINUX.pdf                            -> 4 chunks
ListadoArticulosAcademicos.xlsx           -> 787 chunks
PostgreSQLNotesForProfessionals.pdf       -> 131 chunks
```

Estado:

La ingesta documental quedó validada con PDF directo, HTML académico, PDF escaneado/OCR, XLSX y documentación técnica extensa.

---

## 15. Validación de embeddings con Ollama y pgvector

Se implementó la generación de embeddings usando Ollama local con el modelo `nomic-embed-text`.

Modelo usado:

```text
nomic-embed-text
```

Dimensión validada:

```text
768
```

Esta dimensión coincide con la columna existente en PostgreSQL:

```text
document_chunks.embedding vector(768)
```

Archivos agregados:

* `app/embeddings/__init__.py`
* `app/embeddings/ollama_client.py`
* `app/embeddings/repository.py`
* `app/embed_chunks.py`

Función principal:

```text
generate_embedding()
```

Endpoint local usado:

```text
http://localhost:11434/api/embeddings
```

Comando agregado:

```bash
python -m app.embed_chunks --limit 10
```

El parámetro `--limit` permite procesar embeddings por lotes controlados.

Conteos finales confirmados:

```text
total_chunks = 1550
chunks_con_embedding = 1550
chunks_sin_embedding = 0
```

Cadena funcional confirmada:

```text
chunk_text
 -> Ollama nomic-embed-text
 -> embedding vector(768)
 -> PostgreSQL pgvector
 -> document_chunks.embedding
```

Estado:

La etapa de embeddings quedó validada para el corpus técnico actual.

---

## 16. Validación de búsqueda semántica con pgvector

Se implementó búsqueda semántica usando embeddings almacenados en `document_chunks.embedding`.

Archivos agregados:

* `app/embeddings/search_repository.py`
* `app/search_chunks.py`

Comando de búsqueda:

```bash
python -m app.search_chunks "retrieval augmented generation hallucination fact checking" --limit 5
```

Pruebas validadas:

* Consulta sobre Big O recuperó `AlgorithmsNotesForProfessionals.pdf`.
* Consulta sobre RAG, hallucination y fact-checking recuperó `Hallucination to Truth...html`.
* Consulta sobre PostgreSQL JSONB recuperó `PostgreSQLNotesForProfessionals.pdf`.

Estado:

La búsqueda semántica funciona sobre los `1550` chunks vectorizados.

Observación técnica:

Las consultas en inglés funcionan mejor porque la mayor parte del corpus está en inglés. Las consultas en español pueden recuperar resultados menos precisos si el documento fuente está en inglés.

Pendiente técnico:

* Mejorar ranking.
* Agregar filtros por documento o tipo documental.
* Evaluar búsqueda híbrida: vectorial + texto.
* Registrar consultas en `rag_queries`.
* Registrar resultados recuperados en `retrieval_logs`.

---

## 17. Archivos nuevos de embeddings y búsqueda

Se agregaron los siguientes archivos:

```text
app/embed_chunks.py
app/search_chunks.py
app/embeddings/__init__.py
app/embeddings/ollama_client.py
app/embeddings/repository.py
app/embeddings/search_repository.py
```

### `app/embed_chunks.py`

Comando para generar embeddings por lotes.

Uso:

```bash
python -m app.embed_chunks --limit 100
```

Responsabilidad:

* Buscar chunks sin embedding.
* Generar embedding con Ollama.
* Guardar el vector en `document_chunks.embedding`.
* Mostrar conteos antes y después.

### `app/search_chunks.py`

Comando para búsqueda semántica.

Uso:

```bash
python -m app.search_chunks "PostgreSQL JSONB operators and querying JSON documents" --limit 5
```

Responsabilidad:

* Recibir una consulta en lenguaje natural.
* Generar embedding de la consulta.
* Buscar chunks similares usando pgvector.
* Mostrar documento, chunk, distancia y texto recuperado.

### `app/embeddings/ollama_client.py`

Cliente local para Ollama.

Responsabilidad:

* Enviar texto a `http://localhost:11434/api/embeddings`.
* Usar el modelo `nomic-embed-text`.
* Validar que el vector generado tenga 768 dimensiones.

### `app/embeddings/repository.py`

Repositorio para operaciones de embeddings en PostgreSQL.

Responsabilidad:

* Contar chunks con embedding.
* Contar chunks sin embedding.
* Obtener chunks pendientes.
* Actualizar embeddings por `chunk_id`.

### `app/embeddings/search_repository.py`

Repositorio para búsqueda vectorial.

Responsabilidad:

* Recibir un embedding de consulta.
* Compararlo contra `document_chunks.embedding`.
* Ordenar resultados por distancia vectorial.
* Retornar los chunks más similares.

---

## 18. Comandos principales actuales

### Ingesta individual

```bash
python -m app.ingest_document data/raw/samples/prueba_xlsx.xlsx --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --show-chunks
```

### Ingesta por carpeta

```bash
python -m app.ingest_folder data/raw/samples --chunk-size 1200 --chunk-overlap 200 --min-chunk-size 120 --save-db
```

### Generar embeddings por lotes

```bash
python -m app.embed_chunks --limit 100
```

### Buscar chunks similares

```bash
python -m app.search_chunks "retrieval augmented generation hallucination fact checking" --limit 5
```

### Verificar conteos de embeddings

```bash
psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS total_chunks FROM document_chunks;"

psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS chunks_con_embedding FROM document_chunks WHERE embedding IS NOT NULL;"

psql -h localhost -U rag_user -d rag_tesis -P pager=off -c "SELECT COUNT(*) AS chunks_sin_embedding FROM document_chunks WHERE embedding IS NULL;"
```

---

## 19. Próximo paso recomendado

El siguiente paso técnico recomendado es mejorar la búsqueda semántica para que sea más útil como base del RAG.

Orden recomendado:

1. Agregar filtros opcionales por documento o tipo documental.
2. Guardar consultas en `rag_queries`.
3. Guardar chunks recuperados en `retrieval_logs`.
4. Crear una capa de recuperación formal.
5. Construir una respuesta usando los chunks recuperados.
6. Integrar generación con modelo local.
7. Integrar posteriormente con OpenClaw y Discord.

No se recomienda avanzar todavía a generación de respuestas sin antes registrar trazabilidad de recuperación, porque la tesis necesita evidenciar qué documentos y fragmentos respaldan cada respuesta.

20. Implementación de trazabilidad de recuperación
Se implementó una primera versión funcional de trazabilidad para consultas RAG.

Archivos agregados:

app/rag_trace_repository.py
app/search_chunks_trace.py

Objetivo:

Registrar cada consulta realizada al sistema.
Guardar los chunks recuperados por la búsqueda semántica.
Conservar el orden de recuperación mediante rank_position.
Guardar un puntaje de similitud aproximado mediante similarity_score.
Relacionar cada consulta con su evidencia documental.

Tablas utilizadas:

rag_queries
retrieval_logs

Estructura usada de rag_queries:

id
question
answer
channel
model_name
created_at

Estructura usada de retrieval_logs:

id
query_id
chunk_id
similarity_score
rank_position
created_at

Relaciones:

retrieval_logs.query_id -> rag_queries.id
retrieval_logs.chunk_id -> document_chunks.id

Comando implementado:

python -m app.search_chunks_trace "consulta en lenguaje natural" --limit 5 --channel terminal

Ejemplo validado con documento OCR en español:

python -m app.search_chunks_trace "objetivo principal de Kali Linux herramientas evaluar seguridad sistemas redes aplicaciones" --limit 5 --channel terminal

Resultado validado:

query_id = 1
Se registró la consulta en rag_queries.
Se registraron 5 resultados en retrieval_logs.
Los primeros 4 resultados correspondieron a KALI LINUX.pdf.
El resultado Rank 1 obtuvo similarity_score aproximado de 0.8166.

Observación técnica:

La recuperación depende de la correspondencia entre el idioma de la consulta y el idioma del documento. Para documentos en español, las consultas en español recuperan mejor. Para documentos técnicos en inglés, las consultas en inglés recuperan mejor.

21. Filtros opcionales en búsqueda semántica
Se agregaron filtros opcionales para mejorar la precisión de recuperación.

Archivos modificados:

app/embeddings/search_repository.py
app/search_chunks.py
app/search_chunks_trace.py

Filtros agregados:

--document-id
--source-type

Uso de búsqueda normal filtrada por documento:

python -m app.search_chunks "PostgreSQL JSONB operators and querying JSON documents" --limit 5 --document-id 12

Uso de búsqueda normal filtrada por tipo documental:

python -m app.search_chunks "PostgreSQL JSONB operators and querying JSON documents" --limit 5 --source-type pdf

Uso de búsqueda trazable filtrada por documento:

python -m app.search_chunks_trace "PostgreSQL JSONB operators and querying JSON documents" --limit 5 --document-id 12 --channel terminal

Resultado validado:

La búsqueda filtrada con --document-id 12 recuperó únicamente chunks de PostgreSQLNotesForProfessionals.pdf.
La búsqueda trazable filtrada registró query_id = 5.
Los 5 resultados registrados quedaron asociados al documento PostgreSQLNotesForProfessionals.pdf.

Justificación técnica:

La búsqueda global puede recuperar chunks semánticamente cercanos desde documentos no deseados. Los filtros permiten delimitar la recuperación por documento o tipo documental, lo cual mejora el control experimental y permite evaluar la calidad de recuperación en escenarios más específicos.

Estado actual actualizado:

El sistema ya tiene funcionando:

Ingesta documental individual.
Ingesta documental por carpeta.
Extracción OCR.
Chunking.
Persistencia en PostgreSQL.
Generación de embeddings con Ollama.
Búsqueda semántica global con pgvector.
Búsqueda semántica filtrada por documento.
Búsqueda semántica filtrada por tipo documental.
Registro de consultas en rag_queries.
Registro de chunks recuperados en retrieval_logs.
Trazabilidad básica de recuperación documental.

Pendiente técnico siguiente:

Crear una capa formal de recuperación reutilizable, por ejemplo app/retrieval_service.py, para que la lógica de recuperación pueda ser usada posteriormente por generación de respuestas, evaluación técnica, OpenClaw y Discord.

22. Capa formal de recuperación reutilizable
Se creó una capa de servicio para centralizar la recuperación semántica y la trazabilidad documental.

Archivo agregado:

app/retrieval_service.py

Objetivo:

Evitar que la lógica de recuperación quede acoplada únicamente a comandos de terminal.
Permitir que la recuperación pueda ser reutilizada por generación de respuestas, pruebas de evaluación, OpenClaw, Discord o una API futura.

Funciones principales:

retrieve_chunks()
retrieval_result_to_dict()
get_trace()

Responsabilidad de retrieve_chunks():

Recibir una consulta en lenguaje natural.
Generar el embedding de la consulta.
Buscar chunks similares con pgvector.
Aplicar filtros opcionales por document_id o source_type.
Retornar chunks recuperados con ranking, documento, distancia y similarity_score.
Registrar trazabilidad cuando trace=True.

Parámetros principales:

query
limit
document_id
source_type
trace
channel
model_name

Modo sin trazabilidad:

retrieve_chunks(
    query="PostgreSQL JSONB operators and querying JSON documents",
    limit=3,
    document_id=12,
    trace=False
)

Resultado validado:

query_id = None
chunks = 3
Todos los resultados recuperados correspondieron a PostgreSQLNotesForProfessionals.pdf.

Modo con trazabilidad:

retrieve_chunks(
    query="PostgreSQL JSONB operators and querying JSON documents",
    limit=3,
    document_id=12,
    trace=True,
    channel="terminal"
)

Resultado validado:

query_id = 6
chunks = 3
Los resultados fueron registrados en rag_queries y retrieval_logs.
Todos los chunks recuperados correspondieron a PostgreSQLNotesForProfessionals.pdf.

Estado:

La recuperación semántica ya está encapsulada en una capa reutilizable.
El siguiente paso técnico recomendado es construir la primera generación de respuesta usando los chunks recuperados, manteniendo la respuesta vinculada a la evidencia documental.
