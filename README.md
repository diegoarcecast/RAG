# Diseño, implementación y validación técnica de un prototipo RAG con integración conversacional para evaluar la calidad, trazabilidad y confiabilidad de respuestas en consultas documentales académicas y técnicas en un entorno controlado de validación tecnológica.

Este repositorio contiene el prototipo técnico de tesis para un sistema **Retrieval-Augmented Generation (RAG)** orientado a consultas documentales académicas y técnicas. El énfasis del proyecto está en el **prototipo RAG con integración conversacional**, la trazabilidad documental, la calidad de recuperación y la confiabilidad evaluable de las respuestas. Discord es la integración conversacional actualmente implementada; OpenClaw se mantiene como componente conceptual o posible integración futura, no como eje del título oficial.

> **Documento maestro:** este `README.md` es la documentación maestra actual. `manual.txt` y `docs/` se conservan como documentación auxiliar o histórica y pueden contener notas de etapas anteriores.

---

## 1. Propósito académico

El proyecto apoya una tesis de Ingeniería Informática mediante el diseño, implementación y validación técnica de un prototipo RAG en un entorno controlado. El sistema permite evaluar:

- **Trazabilidad documental:** relación entre pregunta, respuesta, documentos recuperados, chunks y `query_id`.
- **Calidad de recuperación:** análisis de `distance`, `similarity_score`, ranking, documento y chunk recuperado.
- **Confiabilidad de respuestas:** el prompt instruye al modelo a responder con base en la evidencia recuperada, y la respuesta se audita posteriormente con trazabilidad, revisión de chunks y ficha de evaluación.
- **Evaluación técnica de sistemas RAG:** generación de salidas reutilizables para matriz de evaluación académica.
- **Integración conversacional:** uso de Discord como canal implementado para interacción, con un adaptador desacoplado (`app.openclaw_adapter`) que puede servir como base para OpenClaw u otra capa externa futura.

El proyecto no busca entrenar un modelo desde cero. Su objetivo es validar una arquitectura funcional que combine ingesta documental, almacenamiento, recuperación semántica, generación local de respuestas y evaluación trazable.

---

## 2. Estado actual del proyecto

### Implementado en el repositorio

- Ingesta documental individual y por carpeta.
- Detección de tipo documental.
- Extracción de texto desde PDF, DOCX, TXT, Markdown, HTML, CSV y XLSX.
- OCR para PDF cuando la extracción directa no entrega texto suficiente.
- Limpieza y normalización de texto.
- Chunking con solapamiento y ajuste de límites para evitar iniciar chunks en medio de palabras.
- Persistencia en PostgreSQL.
- Uso de `pgvector`.
- Embeddings estándar con `nomic-embed-text` de 768 dimensiones.
- Embeddings multilingües con `bge-m3` de 1024 dimensiones.
- Búsqueda semántica estándar y multilingüe.
- Generación de respuestas con Ollama/Gemma u otro modelo configurado.
- Ficha completa para evaluación.
- Trazabilidad en `rag_queries` y `retrieval_logs`.
- Comando formal `python -m app.ask_rag` para el flujo estándar.
- Adaptador conversacional `app.openclaw_adapter`.
- Bot de Discord `app.discord_bot`.
- Modo compacto `!rag`.
- Modo evaluación `!rageval`.

### Pendiente o recomendado como mejora futura

- Agregar pruebas automatizadas.
- Parametrizar el motor de embeddings desde `app.ask_rag`.
- Separar explícitamente `generation_model` y `embedding_model` en la base de datos.
- Crear endpoint HTTP opcional para OpenClaw.
- Crear scripts de instalación inicial.
- Mejorar formato de fuentes recuperadas en Discord.
- Construir una matriz formal de evaluación para la tesis.

---

## 3. Arquitectura general

### 3.1 Flujo documental y RAG

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

### 3.2 Flujo conversacional con Discord

```text
Usuario en Discord
  -> app.discord_bot
  -> app.openclaw_adapter
  -> servicio RAG
  -> recuperación semántica
  -> PostgreSQL + pgvector
  -> generación con Gemma u otro modelo configurado
  -> trazabilidad
  -> respuesta compacta (!rag) o ficha completa (!rageval)
```

`app.openclaw_adapter` no implementa OpenClaw directamente. Su función actual es desacoplar el canal conversacional del flujo RAG para que Discord, OpenClaw o una API futura puedan invocar una función común.

---

## 4. Diagnóstico técnico e inconsistencias revisadas

| Tema revisado | Situación actual | Decisión documental |
|---|---|---|
| Título oficial | Existían títulos anteriores centrados en RAG, Discord u OpenClaw. | Se adopta como título oficial: “Diseño, implementación y validación técnica de un prototipo RAG con integración conversacional para evaluar la calidad, trazabilidad y confiabilidad de respuestas en consultas documentales académicas y técnicas en un entorno controlado de validación tecnológica.” |
| OpenClaw | No hay implementación directa de OpenClaw en el repo. | Se documenta como integración conceptual o futura; Discord es el canal implementado. |
| Variables de base de datos | El código usa `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`; no usa `DATABASE_URL`. | Se documentan las variables reales y `DATABASE_URL` queda como mejora futura opcional. |
| `chunk_embeddings_bge_m3` | El flujo BGE-M3 requiere una tabla separada de 1024 dimensiones. | `database/schema.sql` contiene la tabla, FK, `UNIQUE (chunk_id, model_name)` e índice por `chunk_id`. |
| `manual.txt` | Contenía configuración antigua con `DISCORD_DEFAULT_DOCUMENT_ID=10`. | Se actualiza para recomendar `DISCORD_DEFAULT_DOCUMENT_ID=` vacío y se marca como auxiliar. |
| `model_name` en `rag_queries` | Puede representar el modelo asociado al flujo de recuperación según la ruta usada; el modelo generativo se muestra en la ficha. | Se documenta como limitación actual y se recomienda separar `generation_model` y `embedding_model` en el futuro. |
| Estructura de carpetas | Algunas carpetas como `logs/`, `scripts/` y `data/processed/` pueden existir localmente o estar proyectadas, pero no forman parte del árbol versionado actual. | Se separa estructura versionada, carpetas locales ignoradas y estructura futura recomendada. |

---

## 5. Estructura real del repositorio

### 5.1 Estructura versionada actual

Árbol relevante versionado actualmente:

```text
RAG/
├── .gitignore
├── README.md
├── manual.txt
├── requirements.txt
├── app/
│   ├── ask_rag.py
│   ├── db.py
│   ├── db_check.py
│   ├── discord_bot.py
│   ├── embed_chunks.py
│   ├── embed_chunks_bge_m3.py
│   ├── ingest_document.py
│   ├── ingest_folder.py
│   ├── openclaw_adapter.py
│   ├── rag_answer_service.py
│   ├── rag_answer_service_bge_m3.py
│   ├── rag_trace_repository.py
│   ├── retrieval_service.py
│   ├── retrieval_service_bge_m3.py
│   ├── search_chunks.py
│   ├── search_chunks_bge_m3.py
│   ├── search_chunks_trace.py
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── ollama_client.py
│   │   ├── repository.py
│   │   └── search_repository.py
│   ├── generation/
│   │   ├── __init__.py
│   │   └── ollama_generation_client.py
│   └── ingestion/
│       ├── __init__.py
│       ├── chunker.py
│       ├── cleaner.py
│       ├── detector.py
│       ├── extractors.py
│       ├── pipeline.py
│       └── repository.py
├── database/
│   └── schema.sql
├── data/
│   └── raw/
│       └── .gitkeep
└── docs/
    ├── base_datos.md
    └── estado_actual.md
```

### 5.2 Carpetas locales ignoradas por Git

| Ruta | Estado | Uso |
|---|---|---|
| `.env` | Local, ignorado por Git. | Variables y secretos. |
| `.venv/` | Local, ignorado por Git. | Entorno virtual Python. |
| `data/raw/*` | Ignorado salvo `.gitkeep`. | Corpus documental local. |
| `data/processed/` | Ignorado; puede no existir en una clonación limpia. | Salidas temporales, debug o JSON de ingesta. |
| `logs/` | Ignorado; puede no existir en el repo versionado. | Logs locales si se decide generarlos. |
| `__pycache__/` | Ignorado. | Caché Python generado en ejecución. |

### 5.3 Carpetas recomendadas para operación futura

| Ruta | Estado | Uso propuesto |
|---|---|---|
| `scripts/` | No forma parte del árbol versionado actual si está vacía. | Scripts de instalación, migración o operación. |
| `logs/` | Local/ignorada. | Registro operativo si se agrega logging. |
| `data/processed/debug/` | Local/ignorada. | Salidas de depuración de ingesta. |

---

## 6. Explicación archivo por archivo

Todos los archivos listados en esta sección existen en el repositorio versionado actual.

| Archivo | Rol técnico |
|---|---|
| `.gitignore` | Excluye `.env`, `.venv/`, `logs/`, `data/processed/`, `data/raw/*`, `__pycache__/` y otros archivos locales. |
| `requirements.txt` | Dependencias Python del prototipo. |
| `manual.txt` | Manual operativo auxiliar; el README es la referencia maestra actual. |
| `database/schema.sql` | Crea extensión `vector`, tablas principales, tabla BGE-M3 e índices básicos. |
| `docs/base_datos.md` | Documento histórico sobre base de datos. |
| `docs/estado_actual.md` | Documento histórico de estado inicial del proyecto. |
| `app/db.py` | Centraliza conexión a PostgreSQL usando variables `POSTGRES_*` cargadas desde `.env`. |
| `app/db_check.py` | Valida conexión a PostgreSQL con `SELECT current_database(), current_user;`. |
| `app/ingest_document.py` | CLI para procesar un documento individual, mostrar texto/chunks, guardar JSON opcional y persistir con `--save-db`. |
| `app/ingest_folder.py` | CLI para procesar archivos soportados en una carpeta y guardarlos opcionalmente en PostgreSQL. |
| `app/embed_chunks.py` | Genera embeddings pendientes con `nomic-embed-text` y los guarda en `document_chunks.embedding`. |
| `app/embed_chunks_bge_m3.py` | Genera embeddings multilingües `bge-m3` para chunks pendientes y los guarda en `chunk_embeddings_bge_m3`. |
| `app/search_chunks.py` | Ejecuta búsqueda semántica estándar sobre `document_chunks.embedding`. |
| `app/search_chunks_bge_m3.py` | Ejecuta búsqueda semántica multilingüe sobre `chunk_embeddings_bge_m3`. |
| `app/search_chunks_trace.py` | Búsqueda estándar con registro de trazabilidad en `rag_queries` y `retrieval_logs`. |
| `app/ask_rag.py` | CLI formal para ejecutar pregunta RAG estándar, recuperar chunks, generar respuesta y mostrar ficha. |
| `app/openclaw_adapter.py` | Adaptador conversacional; decide entre flujo estándar y BGE-M3 según `embedding_model`. |
| `app/discord_bot.py` | Bot Discord; atiende `!rag` y `!rageval`, invoca el adaptador y divide mensajes largos. |
| `app/rag_answer_service.py` | Servicio RAG estándar: recupera, construye contexto, genera respuesta, arma ficha y actualiza `rag_queries.answer`. |
| `app/rag_answer_service_bge_m3.py` | Servicio RAG multilingüe con recuperación BGE-M3 y generación configurada. |
| `app/retrieval_service.py` | Recuperación estándar con `nomic-embed-text`, similitud y trazabilidad opcional. |
| `app/retrieval_service_bge_m3.py` | Recuperación multilingüe con `bge-m3`, similitud y trazabilidad opcional. |
| `app/rag_trace_repository.py` | Inserta consultas, inserta logs de recuperación, obtiene trazas y actualiza respuestas. |
| `app/embeddings/__init__.py` | Inicializador del paquete `app.embeddings`. |
| `app/embeddings/ollama_client.py` | Cliente Ollama para embeddings estándar; valida 768 dimensiones. |
| `app/embeddings/repository.py` | Obtiene chunks sin embedding, actualiza vectores y cuenta pendientes/procesados. |
| `app/embeddings/search_repository.py` | Consulta chunks similares con operador pgvector `<=>` y filtros opcionales. |
| `app/generation/__init__.py` | Inicializador del paquete `app.generation`. |
| `app/generation/ollama_generation_client.py` | Cliente Ollama `/api/generate` para generación con `stream=False`. |
| `app/ingestion/__init__.py` | Inicializador del paquete `app.ingestion`. |
| `app/ingestion/detector.py` | Detecta formatos soportados y MIME. |
| `app/ingestion/extractors.py` | Extrae texto por tipo documental; PDF directo u OCR si hace falta. |
| `app/ingestion/cleaner.py` | Normaliza Unicode, elimina caracteres de control y normaliza espacios. |
| `app/ingestion/chunker.py` | Divide texto en chunks con overlap, límites naturales y metadatos de posición. |
| `app/ingestion/pipeline.py` | Orquesta detección, extracción, metadatos, chunking y resultado en memoria. |
| `app/ingestion/repository.py` | Inserta documentos/chunks y permite eliminar documentos por `file_path` con cascada. |

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

`database/schema.sql` crea actualmente:

- extensión `vector`;
- `documents`;
- `document_chunks`;
- `rag_queries`;
- `retrieval_logs`;
- `chunk_embeddings_bge_m3`;
- índices básicos.

### 9.3 Tabla BGE-M3 incluida en el esquema

La tabla BGE-M3 está incluida en `database/schema.sql`. Si una base antigua no la tiene, aplicar:

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
| `model_name` | Campo ambiguo en el diseño actual: en la ruta BGE-M3 registra el modelo asociado a recuperación (`bge-m3`); en la ruta estándar puede registrar el modelo pasado por el servicio. El modelo generativo se informa en la ficha de evaluación. |
| `created_at` | Fecha de consulta. |

Limitación documentada: para evitar ambigüedades, una mejora futura recomendada es separar `embedding_model` y `generation_model` como columnas distintas.

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
| `model_name` | Por defecto `bge-m3`; permite filtrar de forma segura por modelo. |
| `dimensions` | Debe ser 1024 para BGE-M3. |
| `embedding` | Vector `bge-m3` de 1024 dimensiones. |
| `created_at` | Fecha de generación/actualización. |

Restricciones e índices relevantes:

- `UNIQUE (chunk_id, model_name)` evita duplicar embeddings del mismo modelo para un chunk.
- `idx_chunk_embeddings_bge_m3_chunk_id` acelera uniones por `chunk_id`.

---

## 11. Cómo iniciar el proyecto

Desde una instalación local típica:

```bash
cd /home/diego/rag-tesis
source .venv/bin/activate
python -m app.db_check
```

Explicación:

- `cd /home/diego/rag-tesis`: entra a la carpeta local del proyecto. Si la ruta local es distinta, reemplazarla por la ruta real.
- `source .venv/bin/activate`: activa el entorno virtual Python.
- `python -m app.db_check`: valida conexión con PostgreSQL.

Resultado esperado:

```text
Conexión correcta: base=rag_tesis, usuario=rag_user
```

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

`data/raw/` está ignorada por Git para evitar subir documentos reales, pesados o confidenciales. En el repositorio versionado solo se conserva `data/raw/.gitkeep`.

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

- `rag_queries` registra pregunta, canal, modelo asociado al flujo y respuesta final.
- `retrieval_logs` registra qué chunks fueron recuperados para cada `query_id`.
- `query_id` conecta la respuesta de usuario con la evidencia documental.
- `!rageval` muestra una ficha completa para evaluación manual.
- `similarity_score` y `distance` ayudan a valorar calidad de recuperación.
- `document_title`, `document_id`, `chunk_id` y `chunk_index` sustentan trazabilidad documental.

La ficha de evaluación incluye una clasificación preliminar:

- `evidencia directa probable` si el primer resultado tiene similitud alta.
- `evidencia relacionada` si el puntaje es intermedio.
- `evidencia secundaria o débil` si el puntaje es bajo.

Esta clasificación y el prompt no reemplazan la evaluación humana. La confiabilidad debe revisarse con evidencia recuperada, similitud, distancia, chunks y respuesta final.

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

Para borrar embeddings BGE-M3 y regenerarlos, usar una condición explícita por modelo:

```sql
DELETE FROM chunk_embeddings_bge_m3
WHERE model_name = 'bge-m3';
```

Esto **no borra documentos ni chunks**. Solo elimina embeddings multilingües BGE-M3. Luego regenerar:

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
git add README.md database/schema.sql manual.txt
```

Commit descriptivo:

```bash
git commit -m "Actualizar documentación maestra del prototipo RAG"
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
    git add README.md manual.txt database/schema.sql
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

El prototipo descrito por el título oficial —**Diseño, implementación y validación técnica de un prototipo RAG con integración conversacional para evaluar la calidad, trazabilidad y confiabilidad de respuestas en consultas documentales académicas y técnicas en un entorno controlado de validación tecnológica**— aporta evidencia concreta para la tesis en estas dimensiones:

- **Trazabilidad documental:** cada respuesta puede vincularse a documentos y chunks específicos.
- **Calidad de recuperación:** los resultados pueden analizarse por ranking, distancia y similitud.
- **Confiabilidad de respuestas:** el prompt instruye al modelo a usar evidencia recuperada, pero la confiabilidad se evalúa mediante trazabilidad, revisión de chunks, similitud, distancia y ficha de evaluación.
- **Evaluación controlada:** el corpus, modelos, filtros y consultas pueden fijarse para experimentos repetibles.
- **Comparación de embeddings:** permite contrastar `nomic-embed-text` y `bge-m3`, especialmente en escenarios multilingües.
- **Integración conversacional:** Discord demuestra operación en un canal real de interacción; OpenClaw queda como integración conceptual o futura.
- **Matriz de evaluación:** la ficha `!rageval` entrega campos reutilizables para evaluación manual.

Campos sugeridos para matriz académica:

| Campo | Fuente |
|---|---|
| `query_id` | `rag_queries.id` |
| Pregunta | `rag_queries.question` |
| Respuesta | `rag_queries.answer` |
| Canal | `rag_queries.channel` |
| Modelo asociado al flujo | `rag_queries.model_name` |
| Modelo generativo | Ficha de evaluación generada por servicio RAG |
| Modelo de embeddings | Ficha de evaluación / ruta utilizada |
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
11. Separar `embedding_model` y `generation_model` en `rag_queries` o en una tabla de trazabilidad extendida.

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

Este README prioriza documentación operativa y académica sobre bitácora histórica. Las notas históricas se mantienen en `manual.txt` y `docs/`, pero ante diferencias debe prevalecer este archivo y el código fuente vigente.
