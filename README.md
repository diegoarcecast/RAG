# Prototipo RAG para tesis

Documentación maestra del prototipo RAG para consultas documentales académicas y técnicas.

El proyecto corresponde a una tesis de Ingeniería Informática orientada a diseñar, implementar y validar técnicamente un sistema basado en **Retrieval-Augmented Generation (RAG)**, integrado a un canal conversacional mediante **Discord** y preparado conceptualmente para **OpenClaw**, con el fin de evaluar trazabilidad documental, calidad de recuperación y confiabilidad de respuestas en un entorno controlado.

---

## 0. Diagnóstico previo del repositorio

### 0.1 Resumen de lo entendido del sistema

El repositorio implementa un prototipo RAG local con las siguientes capacidades:

1. Recibe documentos académicos o técnicos en distintos formatos.
2. Detecta tipo documental y extrae texto por método directo u OCR cuando el PDF no contiene texto suficiente.
3. Limpia y normaliza texto.
4. Divide el contenido en chunks con solapamiento.
5. Persiste documentos y chunks en PostgreSQL.
6. Genera embeddings locales con Ollama.
7. Usa `pgvector` para recuperación semántica.
8. Genera respuestas con un modelo generativo local de Ollama, por defecto `gemma4:e4b`.
9. Registra trazabilidad en `rag_queries` y `retrieval_logs`.
10. Expone el flujo por terminal, por un adaptador conversacional compatible conceptualmente con OpenClaw y por un bot de Discord.
11. Incluye dos rutas de recuperación:
    - `nomic-embed-text`, con vectores de 768 dimensiones guardados en `document_chunks.embedding`.
    - `bge-m3`, con vectores multilingües de 1024 dimensiones guardados en `chunk_embeddings_bge_m3`.

### 0.2 Inconsistencias detectadas entre código, README anterior y manual

| Tema | Situación detectada | Impacto | Estado recomendado |
|---|---|---|---|
| Variables de base de datos | El código usa `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER` y `POSTGRES_PASSWORD`; no usa `DATABASE_URL`. | Un `.env` basado solo en `DATABASE_URL` no funcionaría con el código actual. | Documentar variables reales y mencionar `DATABASE_URL` solo como pendiente opcional. |
| Tabla `chunk_embeddings_bge_m3` | El código BGE-M3 requiere la tabla, pero el `schema.sql` anterior no la incluía. | Una instalación desde cero fallaría al ejecutar `app.embed_chunks_bge_m3`. | Incluir la tabla en `database/schema.sql` y documentar SQL de respaldo. |
| Manual de Discord | `manual.txt` documenta `DISCORD_DEFAULT_DOCUMENT_ID=10`, mientras el flujo actual recomienda dejarlo vacío para buscar en todo el corpus. | Un filtro fijo puede ocultar resultados relevantes o causar recuperación incorrecta. | Documentar `DISCORD_DEFAULT_DOCUMENT_ID=` vacío como configuración recomendada. |
| Estado de documentación | `docs/estado_actual.md` está desactualizado respecto a Discord, RAG generativo y BGE-M3. | Puede confundir al reconstruir el estado real del prototipo. | Usar este README como fuente maestra. |
| Carpetas `logs/` y `scripts/` | Están mencionadas como estructura esperada, pero no necesariamente existen en el árbol versionado. | No afecta ejecución, pero puede confundir. | Documentarlas como carpetas operativas opcionales/locales. |
| CLI RAG con BGE-M3 | Existe servicio Python para BGE-M3 y Discord lo puede usar mediante adaptador, pero `app.ask_rag` usa la ruta estándar `nomic-embed-text`. | No hay parámetro CLI formal en `app.ask_rag` para elegir embeddings. | Documentarlo como pendiente y mostrar ejemplo Python para BGE-M3. |

### 0.3 Reproducibilidad: scripts SQL o comandos faltantes

Para reproducir el flujo completo desde cero es necesario que la base contenga:

- extensión `vector`;
- tablas `documents`, `document_chunks`, `rag_queries`, `retrieval_logs`;
- tabla `chunk_embeddings_bge_m3` para recuperación multilingüe.

El archivo `database/schema.sql` debe ser la fuente de creación de esquema. Si una instalación tiene un esquema antiguo sin `chunk_embeddings_bge_m3`, puede aplicar el bloque SQL indicado en la sección [9. Creación de base de datos desde cero](#9-creación-de-base-de-datos-desde-cero).

---

## 1. Título del proyecto

**Prototipo RAG para tesis: consultas documentales académicas y técnicas con trazabilidad, evaluación y canal conversacional.**

El sistema es un prototipo local de **Retrieval-Augmented Generation** que permite consultar documentos académicos y técnicos mediante recuperación semántica y generación de respuestas fundamentadas en evidencia documental. Está diseñado para apoyar una tesis, no para entrenar un modelo desde cero.

---

## 2. Propósito académico

El prototipo sirve como plataforma técnica para evaluar sistemas RAG en un entorno controlado. Su propósito académico es producir evidencia sobre:

- **Trazabilidad documental:** cada respuesta puede auditarse mediante `query_id`, documentos, chunks recuperados y puntajes de similitud.
- **Calidad de recuperación:** permite comparar resultados por `distance`, `similarity_score`, `rank_position`, documento y fragmento.
- **Confiabilidad de respuestas:** el prompt obliga al modelo generativo a responder solo con evidencia recuperada.
- **Evaluación técnica de sistemas RAG:** la ficha de evaluación facilita registrar resultados en una matriz académica.
- **Integración conversacional:** Discord opera como capa de interacción real para usuarios, mientras `app.openclaw_adapter` actúa como adaptador conceptual para OpenClaw u otra capa externa.

---

## 3. Estado actual del proyecto

### Implementado y validado en código

- Ingesta documental individual y por carpeta.
- Detección de formatos soportados.
- Extracción de texto desde PDF, DOCX, TXT, Markdown, HTML, CSV y XLSX.
- OCR en PDF escaneado o con texto directo insuficiente.
- Limpieza y normalización de texto.
- Chunking con solapamiento y ajustes para evitar inicios en medio de palabras.
- Persistencia en PostgreSQL.
- Uso de `pgvector`.
- Embeddings con `nomic-embed-text` de 768 dimensiones.
- Embeddings multilingües con `bge-m3` de 1024 dimensiones.
- Búsqueda semántica con filtros por `document_id` y `source_type`.
- Generación de respuestas con Ollama/Gemma.
- Ficha completa para evaluación.
- Trazabilidad en `rag_queries` y `retrieval_logs`.
- Comando formal `python -m app.ask_rag`.
- Adaptador conversacional `app.openclaw_adapter`.
- Bot de Discord `app.discord_bot`.
- Modo compacto `!rag`.
- Modo evaluación `!rageval`.

### Pendiente o mejorable

- Crear pruebas automatizadas.
- Agregar CLI formal para elegir `nomic-embed-text` o `bge-m3` desde `app.ask_rag`.
- Crear endpoint HTTP opcional para OpenClaw.
- Crear scripts de instalación inicial.
- Mejorar formato de fuentes en Discord.
- Construir matriz de evaluación formal para la tesis.

---

## 4. Arquitectura general

### 4.1 Flujo documental y RAG

```text
Documento
  -> detección de tipo documental
  -> extracción directa u OCR
  -> limpieza y normalización
  -> chunking
  -> PostgreSQL: documents / document_chunks
  -> generación de embeddings
  -> pgvector
  -> recuperación semántica
  -> generación de respuesta con Ollama/Gemma
  -> trazabilidad en rag_queries / retrieval_logs
  -> terminal o Discord
```

### 4.2 Flujo conversacional con Discord/OpenClaw

```text
Usuario en Discord
  -> app.discord_bot
  -> app.openclaw_adapter
  -> servicio RAG
  -> recuperación semántica
  -> PostgreSQL + pgvector
  -> generación con Gemma
  -> trazabilidad
  -> respuesta compacta (!rag) o ficha completa (!rageval)
```

`app.openclaw_adapter` no implementa OpenClaw directamente; funciona como una interfaz desacoplada para que Discord, OpenClaw o una API futura invoquen el flujo RAG.

---

## 5. Estructura de carpetas

```text
rag-tesis/
├── app/
│   ├── embeddings/
│   ├── generation/
│   ├── ingestion/
│   └── *.py
├── database/
│   └── schema.sql
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── logs/
├── scripts/
├── README.md
├── manual.txt
├── requirements.txt
├── .env
└── .gitignore
```

| Ruta | Propósito |
|---|---|
| `app/` | Código principal del prototipo: CLI, servicios RAG, Discord, adaptador y acceso a base de datos. |
| `app/ingestion/` | Pipeline documental: detección, extracción, limpieza, chunking y persistencia. |
| `app/embeddings/` | Cliente Ollama para embeddings estándar y repositorios de persistencia/búsqueda. |
| `app/generation/` | Cliente Ollama para generación de texto. |
| `database/` | SQL de creación de esquema PostgreSQL/pgvector. |
| `data/raw/` | Entrada local de documentos. Está ignorada en Git salvo `.gitkeep`. |
| `data/processed/` | Salidas temporales o procesadas. Está ignorada en Git. |
| `docs/` | Documentación auxiliar histórica. Este README es la documentación maestra actual. |
| `logs/` | Logs locales si se generan. No debe versionarse. |
| `scripts/` | Carpeta sugerida para scripts futuros de instalación/operación. Puede no existir o estar vacía. |
| `README.md` | Documentación maestra del proyecto. |
| `manual.txt` | Manual operativo previo; útil como referencia histórica. |
| `requirements.txt` | Dependencias Python. |
| `.env` | Variables locales y secretos. No debe versionarse. |
| `.gitignore` | Reglas de exclusión de archivos locales, datos y secretos. |

---

## 6. Explicación archivo por archivo

| Archivo | Rol técnico |
|---|---|
| `app/db.py` | Centraliza la conexión a PostgreSQL usando variables `POSTGRES_*` cargadas desde `.env`. |
| `app/db_check.py` | Valida conexión a PostgreSQL ejecutando `SELECT current_database(), current_user;`. |
| `app/ingest_document.py` | CLI para procesar un documento individual, mostrar texto/chunks, guardar JSON opcional y persistir con `--save-db`. |
| `app/ingest_folder.py` | CLI para procesar todos los archivos soportados en una carpeta y guardarlos opcionalmente en PostgreSQL. |
| `app/embed_chunks.py` | Genera embeddings pendientes con `nomic-embed-text` y los guarda en `document_chunks.embedding`. |
| `app/embed_chunks_bge_m3.py` | Genera embeddings multilingües `bge-m3` para chunks pendientes y los guarda en `chunk_embeddings_bge_m3`. |
| `app/search_chunks.py` | Ejecuta búsqueda semántica estándar sobre `document_chunks.embedding`. |
| `app/search_chunks_bge_m3.py` | Ejecuta búsqueda semántica multilingüe sobre `chunk_embeddings_bge_m3`. |
| `app/search_chunks_trace.py` | Variante de búsqueda estándar que registra trazabilidad en `rag_queries` y `retrieval_logs`. |
| `app/ask_rag.py` | CLI formal para ejecutar pregunta RAG estándar, recuperar chunks, generar respuesta y mostrar ficha de evaluación. |
| `app/openclaw_adapter.py` | Adaptador conversacional que recibe una pregunta y decide si usa flujo estándar o BGE-M3 según `embedding_model`. |
| `app/discord_bot.py` | Bot Discord. Lee comandos `!rag` y `!rageval`, invoca el adaptador y divide mensajes largos. |
| `app/rag_answer_service.py` | Servicio RAG estándar: recupera, construye contexto, genera respuesta, arma ficha y actualiza `rag_queries.answer`. |
| `app/rag_answer_service_bge_m3.py` | Servicio RAG multilingüe: igual que el estándar, pero recupera con `bge-m3`. |
| `app/retrieval_service.py` | Capa de recuperación estándar con `nomic-embed-text`, cálculo de similitud y trazabilidad opcional. |
| `app/retrieval_service_bge_m3.py` | Capa de recuperación multilingüe con `bge-m3`, cálculo de similitud y trazabilidad opcional. |
| `app/rag_trace_repository.py` | Inserta consultas, logs de recuperación, obtiene trazas y actualiza respuestas. |
| `app/ingestion/detector.py` | Detecta formatos soportados y MIME. Soporta `.pdf`, `.docx`, `.txt`, `.md`, `.markdown`, `.html`, `.htm`, `.csv`, `.xlsx`. |
| `app/ingestion/extractors.py` | Extrae texto por tipo documental; en PDF intenta extracción directa y recurre a OCR si el texto es insuficiente. |
| `app/ingestion/cleaner.py` | Normaliza Unicode, elimina caracteres de control y normaliza espacios/saltos de línea. |
| `app/ingestion/chunker.py` | Divide texto en chunks con overlap, límites naturales y metadatos de posición. |
| `app/ingestion/pipeline.py` | Orquesta detección, extracción, metadatos, chunking y resultado estructurado en memoria. |
| `app/ingestion/repository.py` | Inserta documentos/chunks y permite eliminar documentos por `file_path` con cascada. |
| `app/embeddings/ollama_client.py` | Cliente Ollama para `nomic-embed-text`; valida 768 dimensiones. |
| `app/embeddings/repository.py` | Obtiene chunks sin embedding, actualiza vectores y cuenta chunks pendientes/procesados. |
| `app/embeddings/search_repository.py` | Consulta chunks similares con operador pgvector `<=>` y filtros opcionales. |
| `app/generation/ollama_generation_client.py` | Cliente Ollama `/api/generate` para respuestas generativas con `stream=False`. |
| `database/schema.sql` | Crea extensión `vector`, tablas principales, tabla BGE-M3 e índices básicos. |
| `manual.txt` | Manual operativo anterior; algunas secciones quedaron históricas frente al estado actual. |
| `docs/base_datos.md` | Documentación histórica de base de datos. |
| `docs/estado_actual.md` | Estado histórico inicial del proyecto. |

---

## 7. Requisitos del sistema

### 7.1 Sistema operativo y servicios

- Ubuntu/Linux recomendado.
- Python 3.11 o superior recomendado.
- PostgreSQL.
- Extensión `pgvector`.
- Ollama local.
- Tesseract OCR y Poppler para OCR en PDF escaneado.

### 7.2 Paquetes de sistema recomendados

```bash
sudo apt update
sudo apt install -y \
  postgresql postgresql-contrib \
  tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng \
  poppler-utils \
  libmagic1
```

La instalación exacta de `pgvector` depende de la versión de PostgreSQL y del sistema. Debe estar disponible para ejecutar:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 7.3 Modelos Ollama requeridos

```bash
ollama pull nomic-embed-text
ollama pull bge-m3
ollama pull gemma4:e4b
```

Modelos usados:

| Modelo | Uso | Dimensiones |
|---|---|---:|
| `nomic-embed-text` | Embeddings estándar | 768 |
| `bge-m3` | Embeddings multilingües | 1024 |
| `gemma4:e4b` | Generación de respuestas | No aplica |

Si se usa otro modelo generativo, debe configurarse con `--model` o `DISCORD_DEFAULT_MODEL`.

---

## 8. Variables de entorno

El código actual no usa `DATABASE_URL`; usa variables PostgreSQL separadas. Ejemplo seguro de `.env`:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=rag_tesis
POSTGRES_USER=rag_user
POSTGRES_PASSWORD=CAMBIAR_POR_PASSWORD_LOCAL

DISCORD_BOT_TOKEN=CAMBIAR_POR_TOKEN_REAL
DISCORD_COMMAND_PREFIX=!rag
DISCORD_EVAL_COMMAND_PREFIX=!rageval
DISCORD_DEFAULT_DOCUMENT_ID=
DISCORD_DEFAULT_LIMIT=3
DISCORD_DEFAULT_MODEL=gemma4:e4b
DISCORD_EMBEDDING_MODEL=bge-m3
```

Reglas importantes:

- `.env` no debe subirse a GitHub.
- El token de Discord nunca debe escribirse en el código.
- `DISCORD_DEFAULT_DOCUMENT_ID=` debe quedar vacío para buscar en todo el corpus.
- Si se fija `DISCORD_DEFAULT_DOCUMENT_ID=10`, el bot solo buscará en ese documento.
- `DISCORD_EMBEDDING_MODEL=bge-m3` activa recuperación multilingüe desde Discord.
- `DATABASE_URL` puede agregarse en el futuro, pero actualmente no es leída por `app/db.py`.

---

## 9. Creación de base de datos desde cero

### 9.1 Crear usuario y base

Ejemplo con usuario `postgres`:

```bash
sudo -u postgres createuser rag_user --pwprompt
sudo -u postgres createdb rag_tesis -O rag_user
```

Alternativa desde `psql`:

```bash
sudo -u postgres psql
```

```sql
CREATE USER rag_user WITH PASSWORD 'CAMBIAR_POR_PASSWORD_LOCAL';
CREATE DATABASE rag_tesis OWNER rag_user;
\q
```

### 9.2 Ejecutar esquema del proyecto

Desde la raíz del repositorio:

```bash
psql -U rag_user -d rag_tesis -f database/schema.sql
```

El archivo `database/schema.sql` crea:

- extensión `vector`;
- `documents`;
- `document_chunks`;
- `rag_queries`;
- `retrieval_logs`;
- `chunk_embeddings_bge_m3`;
- índices básicos.

### 9.3 SQL de respaldo para tabla BGE-M3

Si la base ya existía y no contiene `chunk_embeddings_bge_m3`, ejecutar:

```sql
CREATE TABLE IF NOT EXISTS chunk_embeddings_bge_m3 (
    id BIGSERIAL PRIMARY KEY,
    chunk_id BIGINT NOT NULL REFERENCES document_chunks(id) ON DELETE CASCADE,
    model_name TEXT NOT NULL DEFAULT 'bge-m3',
    dimensions INT NOT NULL DEFAULT 1024,
    embedding vector(1024) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (chunk_id, model_name)
);

CREATE INDEX IF NOT EXISTS idx_chunk_embeddings_bge_m3_chunk_id
ON chunk_embeddings_bge_m3(chunk_id);
```

---

## 10. Modelo de datos

### 10.1 `documents`

Guarda el registro padre de cada documento.

| Campo | Uso |
|---|---|
| `id` | Identificador del documento. |
| `title` | Nombre del archivo usado como título. |
| `source_type` | Tipo documental detectado: `pdf`, `docx`, `txt`, etc. |
| `file_path` | Ruta local usada para auditoría y limpieza segura. |
| `author` | Campo disponible, actualmente no poblado por el pipeline. |
| `publication_year` | Campo disponible, actualmente no poblado por el pipeline. |
| `created_at` | Fecha de inserción. |

### 10.2 `document_chunks`

Guarda fragmentos textuales de documentos.

| Campo | Uso |
|---|---|
| `id` | Identificador del chunk. |
| `document_id` | FK a `documents.id` con `ON DELETE CASCADE`. |
| `chunk_index` | Posición del chunk dentro del documento. |
| `chunk_text` | Texto del fragmento. |
| `page_number` | Página de origen si aplica; actualmente suele venir nula salvo metadatos futuros. |
| `section_title` | Sección si aplica; actualmente suele venir nula. |
| `metadata` | JSONB con ruta, tipo, método de extracción e índices de caracteres. |
| `embedding` | Vector `nomic-embed-text` de 768 dimensiones. |
| `created_at` | Fecha de inserción. |

### 10.3 `rag_queries`

Registra preguntas y respuestas RAG.

| Campo | Uso |
|---|---|
| `id` | `query_id` usado para auditoría. |
| `question` | Pregunta original. |
| `answer` | Respuesta final con ficha de evaluación. |
| `channel` | Origen: `terminal`, `discord-direct`, etc. |
| `model_name` | Modelo registrado por el flujo. En BGE-M3 registra el modelo de embeddings; en el flujo estándar puede registrar el modelo indicado por el servicio. |
| `created_at` | Fecha de consulta. |

### 10.4 `retrieval_logs`

Registra cada chunk recuperado para una consulta.

| Campo | Uso |
|---|---|
| `id` | Identificador del log. |
| `query_id` | FK a `rag_queries.id`. |
| `chunk_id` | FK a `document_chunks.id`. |
| `similarity_score` | `1 - distance`, acotado entre 0 y 1 por los servicios. |
| `rank_position` | Posición en el ranking de recuperación. |
| `created_at` | Fecha del registro. |

### 10.5 `chunk_embeddings_bge_m3`

Guarda embeddings multilingües separados para no mezclar dimensiones.

| Campo | Uso |
|---|---|
| `id` | Identificador interno. |
| `chunk_id` | FK a `document_chunks.id` con `ON DELETE CASCADE`. |
| `model_name` | Por defecto `bge-m3`. |
| `dimensions` | Debe ser 1024. |
| `embedding` | Vector `bge-m3` de 1024 dimensiones. |
| `created_at` | Fecha de generación/actualización. |

---

## 11. Cómo iniciar el proyecto

Desde una instalación local típica:

```bash
cd /home/diego/rag-tesis
source .venv/bin/activate
python -m app.db_check
```

Explicación:

- `cd /home/diego/rag-tesis`: entra a la carpeta local del proyecto.
- `source .venv/bin/activate`: activa el entorno virtual Python.
- `python -m app.db_check`: valida conexión con PostgreSQL.

Resultado esperado:

```text
Conexión correcta: base=rag_tesis, usuario=rag_user
```

Si la ruta local es distinta, reemplazar `/home/diego/rag-tesis` por la ruta real del repositorio.

---

## 12. Cómo cargar documentos nuevos

### 12.1 Dónde colocar documentos

Carpeta recomendada:

```text
data/raw/samples/
```

Ejemplo:

```text
data/raw/samples/nuevo_documento.pdf
```

`data/raw/` está ignorada por Git para evitar subir documentos reales, pesados o confidenciales.

### 12.2 Formatos soportados

- PDF: `.pdf`
- Word: `.docx`
- Texto: `.txt`
- Markdown: `.md`, `.markdown`
- HTML: `.html`, `.htm`
- CSV: `.csv`
- Excel: `.xlsx`

### 12.3 Cargar documento individual

```bash
python -m app.ingest_document data/raw/samples/nuevo_documento.pdf \
  --chunk-size 1200 \
  --chunk-overlap 200 \
  --min-chunk-size 120 \
  --save-db
```

Opciones útiles:

```bash
python -m app.ingest_document data/raw/samples/nuevo_documento.pdf --show-chunks
python -m app.ingest_document data/raw/samples/nuevo_documento.pdf --json-output data/processed/debug/resultado.json
```

### 12.4 Cargar carpeta completa

```bash
python -m app.ingest_folder data/raw/samples \
  --chunk-size 1200 \
  --chunk-overlap 200 \
  --min-chunk-size 120 \
  --save-db
```

### 12.5 Parámetros de chunking

| Parámetro | Descripción | Valor típico |
|---|---|---:|
| `--chunk-size` | Tamaño máximo aproximado en caracteres. | `1200` |
| `--chunk-overlap` | Caracteres repetidos entre chunks consecutivos. | `200` |
| `--min-chunk-size` | Evita chunks finales demasiado pequeños. | `120` |
| `--save-db` | Persiste documento y chunks en PostgreSQL. | Activado en carga real |

Usar sin `--save-db` cuando se quiere validar extracción/chunking sin modificar la base.

---

## 13. Cómo generar embeddings

### 13.1 Embeddings estándar con `nomic-embed-text`

```bash
python -m app.embed_chunks --limit 100
```

Este comando:

- busca chunks con `document_chunks.embedding IS NULL`;
- genera embeddings con Ollama y `nomic-embed-text`;
- valida 768 dimensiones;
- actualiza `document_chunks.embedding`.

### 13.2 Embeddings multilingües con `bge-m3`

```bash
python -m app.embed_chunks_bge_m3 --limit 300
```

Este comando:

- busca chunks sin registro en `chunk_embeddings_bge_m3`;
- genera embeddings con Ollama y `bge-m3`;
- valida 1024 dimensiones;
- inserta o actualiza la tabla separada.

### 13.3 Regla crítica de dimensiones

No mezclar vectores de distinta dimensión en la misma columna:

- `nomic-embed-text` -> 768 dimensiones -> `document_chunks.embedding vector(768)`.
- `bge-m3` -> 1024 dimensiones -> `chunk_embeddings_bge_m3.embedding vector(1024)`.

---

## 14. Cómo verificar chunks y embeddings

Entrar a PostgreSQL:

```bash
psql -U rag_user -d rag_tesis
```

Consultas útiles:

```sql
SELECT COUNT(*) AS documentos FROM documents;

SELECT COUNT(*) AS chunks FROM document_chunks;

SELECT COUNT(*) AS chunks_con_embedding
FROM document_chunks
WHERE embedding IS NOT NULL;

SELECT COUNT(*) AS chunks_sin_embedding
FROM document_chunks
WHERE embedding IS NULL;

SELECT COUNT(*) AS embeddings_bge_m3
FROM chunk_embeddings_bge_m3
WHERE model_name = 'bge-m3';

SELECT COUNT(*) AS chunks_pendientes_bge_m3
FROM document_chunks dc
LEFT JOIN chunk_embeddings_bge_m3 eb
  ON eb.chunk_id = dc.id
 AND eb.model_name = 'bge-m3'
WHERE eb.id IS NULL;
```

---

## 15. Cómo hacer búsquedas semánticas

### 15.1 Búsqueda estándar

```bash
python -m app.search_chunks "consulta" --limit 5
```

Con filtros:

```bash
python -m app.search_chunks "consulta" --limit 5 --document-id 10
python -m app.search_chunks "consulta" --limit 5 --source-type pdf
```

### 15.2 Búsqueda multilingüe con BGE-M3

```bash
python -m app.search_chunks_bge_m3 "consulta" --limit 5
```

Con filtros:

```bash
python -m app.search_chunks_bge_m3 "consulta" --limit 5 --document-id 12
python -m app.search_chunks_bge_m3 "consulta" --limit 5 --source-type pdf
```

### 15.3 Cómo interpretar la salida

| Campo | Interpretación |
|---|---|
| `distance` | Distancia coseno de pgvector. Menor es mejor. |
| `similarity_score` | Aproximación `1 - distance`. Mayor es mejor. En `search_chunks.py` estándar no se imprime, pero sí puede calcularse. |
| `document_title` / `title` | Documento recuperado. |
| `document_id` | ID del documento en PostgreSQL. |
| `chunk_id` | Fragmento exacto recuperado. |
| `chunk_index` | Posición del fragmento dentro del documento. |

---

## 16. Cómo ejecutar consultas RAG desde terminal

Comando general:

```bash
python -m app.ask_rag "pregunta" --limit 3 --document-id 10 --channel terminal --model gemma4:e4b
```

Ejemplo:

```bash
python -m app.ask_rag "¿Cuál es el objetivo principal de Kali Linux?" \
  --limit 3 \
  --document-id 10 \
  --channel terminal \
  --model gemma4:e4b
```

Parámetros:

| Parámetro | Descripción |
|---|---|
| `question` | Pregunta en lenguaje natural. |
| `--limit` | Máximo de chunks recuperados. |
| `--document-id` | Filtro opcional por documento. Omitir para buscar en todo el corpus. |
| `--source-type` | Filtro opcional por tipo documental. |
| `--channel` | Canal registrado en trazabilidad. |
| `--model` | Modelo generativo local en Ollama. |

Importante: `app.ask_rag` usa actualmente la ruta estándar de recuperación. Para BGE-M3 usar el ejemplo Python de la siguiente sección o Discord con `DISCORD_EMBEDDING_MODEL=bge-m3`.

---

## 17. Cómo ejecutar RAG con BGE-M3 desde Python

Ejemplo de pregunta en español contra documentos técnicos en inglés:

```python
from app.rag_answer_service_bge_m3 import generate_rag_answer_bge_m3

result = generate_rag_answer_bge_m3(
    question="¿Cómo crear un usuario con contraseña en PostgreSQL?",
    limit=3,
    document_id=None,
    source_type="pdf",
    channel="python-bge-m3",
    generation_model="gemma4:e4b",
)

print("query_id:", result.query_id)
print(result.answer)
```

Este flujo:

- genera embedding de la pregunta con `bge-m3`;
- recupera desde `chunk_embeddings_bge_m3`;
- registra trazabilidad;
- genera respuesta con el modelo configurado;
- guarda respuesta completa en `rag_queries.answer`.

---

## 18. Cómo iniciar el bot de Discord

```bash
cd /home/diego/rag-tesis
source .venv/bin/activate
python -m app.discord_bot
```

Requisitos:

1. `.env` con `DISCORD_BOT_TOKEN` configurado.
2. Bot creado en Discord Developer Portal.
3. **Message Content Intent** activo.
4. Permisos para leer mensajes y enviar mensajes en el servidor.
5. Bot autorizado/invitado al servidor.
6. Ollama corriendo localmente.
7. PostgreSQL accesible desde la máquina donde se ejecuta el bot.

Resultado esperado en terminal:

```text
Bot conectado como <nombre_del_bot>
Comando compacto activo: !rag <pregunta>
Comando evaluación activo: !rageval <pregunta>
Modelo embeddings Discord: bge-m3
```

---

## 19. Cómo usar Discord

### 19.1 Modo compacto

```text
!rag pregunta
```

Devuelve:

- `query_id`;
- respuesta compacta;
- fuentes recuperadas;
- sugerencia para usar `!rageval` si se necesita ficha completa.

### 19.2 Modo evaluación

```text
!rageval pregunta
```

Devuelve:

- respuesta generada;
- ficha completa;
- `query_id`;
- modelo generativo;
- modelo de embeddings;
- filtros aplicados;
- documentos y chunks recuperados;
- `similarity_score`;
- `distance`;
- evidencia textual.

Ambos modos registran trazabilidad en PostgreSQL.

---

## 20. Recuperación multilingüe

Se incorporó `bge-m3` porque el corpus puede contener documentos técnicos en inglés y preguntas en español. En pruebas, `nomic-embed-text` podía recuperar documentos no pertinentes en escenarios español-inglés, mientras que `bge-m3` mejoró la recuperación cruzada.

Caso validado:

```text
Pregunta:
¿Cómo crear un usuario con contraseña en PostgreSQL?

Resultado esperado:
PostgreSQLNotesForProfessionals.pdf
Section 20.1: Create a user with a password
similarity_score aproximado: 0.7536
distance aproximado: 0.2464
chunk_id: 1521
```

Este caso fortalece la evaluación de calidad de recuperación porque permite comparar modelos de embeddings bajo una consulta multilingüe controlada.

---

## 21. Trazabilidad y evaluación

El prototipo permite auditar cada respuesta:

- `rag_queries` registra pregunta, canal, modelo y respuesta final.
- `retrieval_logs` registra qué chunks fueron recuperados para cada `query_id`.
- `query_id` conecta la respuesta de usuario con la evidencia documental.
- `!rageval` muestra una ficha completa para evaluación manual.
- `similarity_score` y `distance` ayudan a valorar calidad de recuperación.
- `document_title`, `document_id`, `chunk_id` y `chunk_index` sustentan trazabilidad documental.

La ficha de evaluación incluye una clasificación preliminar:

- `evidencia directa probable` si el primer resultado tiene similitud alta.
- `evidencia relacionada` si el puntaje es intermedio.
- `evidencia secundaria o débil` si el puntaje es bajo.

Esta clasificación no reemplaza la evaluación humana.

---

## 22. Cómo revisar trazabilidad en PostgreSQL

### 22.1 Últimas consultas

```sql
SELECT id, question, channel, model_name, created_at
FROM rag_queries
ORDER BY id DESC
LIMIT 10;
```

### 22.2 Logs por `query_id`

```sql
SELECT
  rl.rank_position,
  rl.similarity_score,
  dc.id AS chunk_id,
  dc.chunk_index,
  d.id AS document_id,
  d.title AS document_title
FROM retrieval_logs rl
JOIN document_chunks dc ON dc.id = rl.chunk_id
JOIN documents d ON d.id = dc.document_id
WHERE rl.query_id = 27
ORDER BY rl.rank_position;
```

### 22.3 Documentos recuperados por `query_id`

```sql
SELECT DISTINCT d.id, d.title, d.source_type
FROM retrieval_logs rl
JOIN document_chunks dc ON dc.id = rl.chunk_id
JOIN documents d ON d.id = dc.document_id
WHERE rl.query_id = 27;
```

### 22.4 Respuesta guardada

```sql
SELECT id, question, answer
FROM rag_queries
WHERE id = 27;
```

Cambiar `27` por el `query_id` real.

---

## 23. Cómo limpiar documentos cargados por error

### 23.1 Verificar antes de borrar

Buscar por ruta:

```sql
SELECT id, title, file_path, created_at
FROM documents
WHERE file_path = '/ruta/absoluta/del/documento.pdf';
```

Contar chunks asociados:

```sql
SELECT d.id, d.title, COUNT(dc.id) AS chunks
FROM documents d
LEFT JOIN document_chunks dc ON dc.document_id = d.id
WHERE d.file_path = '/ruta/absoluta/del/documento.pdf'
GROUP BY d.id, d.title;
```

### 23.2 Borrar de forma controlada con Python

```bash
python - <<'PY'
from app.ingestion.repository import delete_document_by_file_path

file_path = "/ruta/absoluta/del/documento.pdf"
deleted = delete_document_by_file_path(file_path)
print("documentos_eliminados:", deleted)
PY
```

Advertencia: `document_chunks.document_id` tiene `ON DELETE CASCADE`. Al borrar un documento, PostgreSQL borra automáticamente sus chunks y, por cascada, también logs/embeddings asociados donde existan relaciones configuradas.

---

## 24. Cómo limpiar embeddings experimentales

Para borrar todos los embeddings BGE-M3 y regenerarlos:

```sql
DELETE FROM chunk_embeddings_bge_m3;
```

Esto **no borra documentos ni chunks**. Solo elimina embeddings multilingües experimentales. Luego regenerar:

```bash
python -m app.embed_chunks_bge_m3 --limit 300
```

Para borrar embeddings estándar se requeriría actualizar `document_chunks.embedding` a `NULL`, pero hacerlo afecta el flujo estándar y debe realizarse solo si se desea regenerar todos los vectores `nomic-embed-text`.

---

## 25. Seguridad del repositorio

No subir a GitHub:

- `.env`;
- `.venv/`;
- `logs/`;
- documentos reales;
- `data/raw/` con corpus local;
- `data/processed/`;
- tokens;
- credenciales;
- archivos temporales;
- salidas JSON con contenido sensible.

Revisar siempre antes de commitear:

```bash
git status
```

`.gitignore` ya protege `.env`, `.venv/`, `logs/`, `data/processed/` y `data/raw/*` salvo `.gitkeep`.

---

## 26. Comandos Git recomendados

Buenas prácticas:

```bash
git status
git diff
```

Agregar archivos específicos, no usar `git add .` sin revisar:

```bash
git add README.md database/schema.sql
```

Commit descriptivo:

```bash
git commit -m "Documentar arquitectura y operación del prototipo RAG"
```

Enviar a la rama principal si corresponde:

```bash
git push origin main
```

Antes de hacer push, confirmar que no haya secretos:

```bash
git status
git diff --cached
```

---

## 27. Flujo operativo diario recomendado

1. Entrar al proyecto:

   ```bash
   cd /home/diego/rag-tesis
   ```

2. Activar entorno virtual:

   ```bash
   source .venv/bin/activate
   ```

3. Validar conexión a base de datos:

   ```bash
   python -m app.db_check
   ```

4. Cargar documentos nuevos:

   ```bash
   python -m app.ingest_folder data/raw/samples --save-db
   ```

5. Generar embeddings estándar si se usará la ruta `nomic-embed-text`:

   ```bash
   python -m app.embed_chunks --limit 100
   ```

6. Generar embeddings BGE-M3 si se usará recuperación multilingüe:

   ```bash
   python -m app.embed_chunks_bge_m3 --limit 300
   ```

7. Probar búsqueda semántica:

   ```bash
   python -m app.search_chunks_bge_m3 "¿Cómo crear un usuario con contraseña en PostgreSQL?" --limit 5
   ```

8. Probar RAG desde terminal:

   ```bash
   python -m app.ask_rag "Pregunta de prueba" --limit 3 --channel terminal --model gemma4:e4b
   ```

9. Iniciar Discord:

   ```bash
   python -m app.discord_bot
   ```

10. Ejecutar consultas en Discord:

    ```text
    !rag pregunta
    !rageval pregunta
    ```

11. Revisar trazabilidad en PostgreSQL.

12. Revisar cambios Git y commitear si aplica:

    ```bash
    git status
    git diff
    git add README.md
    git commit -m "Actualizar documentación operativa del prototipo RAG"
    ```

---

## 28. Problemas comunes y solución

| Problema | Causa probable | Solución |
|---|---|---|
| `python: command not found` | Python no instalado o se debe usar `python3`. | Probar `python3 -m ...` o instalar Python. |
| `Falta DISCORD_BOT_TOKEN` | `.env` no contiene token o no carga. | Crear `.env` en la raíz y definir `DISCORD_BOT_TOKEN`. |
| El bot no lee mensajes | Falta Message Content Intent. | Activarlo en Discord Developer Portal. |
| `.env` no carga | Se ejecuta desde otra carpeta o falta archivo. | Ejecutar desde raíz del repo y verificar `.env`. |
| PostgreSQL pide password | Usuario/contraseña no coincide o falta variable. | Revisar `POSTGRES_PASSWORD` y permisos de `rag_user`. |
| Chunks sin embedding | Faltó ejecutar generación de embeddings. | Ejecutar `app.embed_chunks` o `app.embed_chunks_bge_m3`. |
| Error dimensión BGE-M3 1024 | Se intenta usar BGE-M3 en columna de 768 dimensiones. | Usar `chunk_embeddings_bge_m3`, no `document_chunks.embedding`. |
| Error por `document_id` fijo | `DISCORD_DEFAULT_DOCUMENT_ID` filtra demasiado. | Dejar `DISCORD_DEFAULT_DOCUMENT_ID=` vacío. |
| Recuperación devuelve documento incorrecto | Modelo de embeddings no adecuado o corpus sin embeddings correctos. | Probar BGE-M3, aumentar `--limit`, quitar filtros y revisar chunks. |
| Respuesta muy larga en Discord | Discord limita mensajes a 2000 caracteres. | El bot divide mensajes en partes de 1900 caracteres; usar `!rag` para compacta. |
| Token expuesto accidentalmente | Se pegó token en código, README o commit. | Revocar token en Discord Developer Portal, generar uno nuevo y limpiar historial si fue commiteado. |
| Ollama no responde | Servicio no está corriendo o modelo no está descargado. | Ejecutar `ollama serve` y `ollama pull <modelo>`. |
| OCR falla | Faltan Tesseract, idiomas o Poppler. | Instalar `tesseract-ocr`, `tesseract-ocr-spa`, `tesseract-ocr-eng`, `poppler-utils`. |

---

## 29. Relación con la tesis

El prototipo aporta evidencia concreta para la tesis en estas dimensiones:

- **Trazabilidad documental:** cada respuesta puede vincularse a documentos y chunks específicos.
- **Calidad de recuperación:** los resultados pueden analizarse por ranking, distancia y similitud.
- **Confiabilidad de respuestas:** el prompt restringe al modelo a responder con evidencia recuperada.
- **Evaluación controlada:** el corpus, modelos, filtros y consultas pueden fijarse para experimentos repetibles.
- **Comparación de embeddings:** permite contrastar `nomic-embed-text` y `bge-m3`, especialmente en escenarios multilingües.
- **Integración conversacional:** Discord demuestra operación en un canal real de interacción.
- **Matriz de evaluación:** la ficha `!rageval` entrega campos directamente reutilizables para evaluación manual.

Campos sugeridos para matriz académica:

| Campo | Fuente |
|---|---|
| `query_id` | `rag_queries.id` |
| Pregunta | `rag_queries.question` |
| Respuesta | `rag_queries.answer` |
| Canal | `rag_queries.channel` |
| Modelo | `rag_queries.model_name` y ficha |
| Documento recuperado | `documents.title` |
| Chunk | `document_chunks.id` |
| Ranking | `retrieval_logs.rank_position` |
| Similitud | `retrieval_logs.similarity_score` |
| Evidencia | `document_chunks.chunk_text` |
| Evaluación humana | Campo externo en matriz |

---

## 30. Siguientes pasos

Próximos pasos técnicos recomendados:

1. Crear matriz de evaluación formal para la tesis.
2. Mejorar formato de fuentes recuperadas en Discord.
3. Crear endpoint HTTP opcional para OpenClaw.
4. Mantener `database/schema.sql` actualizado con todos los cambios del modelo de datos.
5. Agregar pruebas automatizadas para ingesta, embeddings, búsqueda y trazabilidad.
6. Parametrizar motor de embeddings en CLI, especialmente en `app.ask_rag`.
7. Crear scripts de instalación inicial para PostgreSQL, pgvector, entorno virtual y modelos Ollama.
8. Agregar índices vectoriales cuando exista suficiente volumen de chunks.
9. Documentar casos de prueba multilingües español-inglés e inglés-español.
10. Mejorar extracción de metadatos como autor, año y sección real.

---

## 31. Referencia rápida de comandos

```bash
# Validar base
python -m app.db_check

# Ingesta individual
python -m app.ingest_document data/raw/samples/documento.pdf --save-db

# Ingesta por carpeta
python -m app.ingest_folder data/raw/samples --save-db

# Embeddings estándar
python -m app.embed_chunks --limit 100

# Embeddings BGE-M3
python -m app.embed_chunks_bge_m3 --limit 300

# Búsqueda estándar
python -m app.search_chunks "consulta" --limit 5

# Búsqueda BGE-M3
python -m app.search_chunks_bge_m3 "consulta" --limit 5

# RAG desde terminal
python -m app.ask_rag "pregunta" --limit 3 --channel terminal --model gemma4:e4b

# Discord
python -m app.discord_bot
```

---

## 32. Nota final

Este README es la documentación maestra actual del repositorio. `manual.txt` y `docs/` se conservan como documentación histórica y operativa auxiliar, pero ante diferencias debe priorizarse este archivo y el código fuente vigente.
