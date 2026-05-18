 Configuración de base de datos del prototipo RAG

Este documento describe la creación inicial de la base de datos utilizada por el prototipo RAG de la tesis.

## Motor de base de datos

- Motor: PostgreSQL.
- Extensión vectorial: pgvector.
- Base de datos: rag_tesis.
- Usuario de aplicación: rag_user.
- Dimensión inicial de embeddings: 768.

## Creación de usuario y base de datos

Comandos SQL utilizados:

    CREATE USER rag_user WITH PASSWORD '<password>';
    CREATE DATABASE rag_tesis OWNER rag_user;
    GRANT ALL PRIVILEGES ON DATABASE rag_tesis TO rag_user;

Por seguridad, la contraseña real no se documenta en este archivo.

## Habilitación de pgvector

Comandos SQL utilizados:

    CREATE EXTENSION IF NOT EXISTS vector;

    SELECT extname, extversion
    FROM pg_extension
    WHERE extname = 'vector';

Resultado validado:

    vector | 0.6.0

## Tablas creadas

### documents

Registra los documentos fuente cargados al corpus documental.

Campos principales:

- id: identificador interno del documento.
- title: título del documento.
- source_type: tipo de fuente documental.
- file_path: ruta local del archivo.
- author: autor o entidad responsable.
- publication_year: año de publicación.
- created_at: fecha de registro.

### document_chunks

Registra los fragmentos procesados de cada documento.

Campos principales:

- id: identificador interno del fragmento.
- document_id: documento al que pertenece el fragmento.
- chunk_index: número de fragmento dentro del documento.
- chunk_text: contenido textual del fragmento.
- page_number: página de origen, si aplica.
- section_title: sección de origen, si aplica.
- metadata: metadatos adicionales en formato JSONB.
- embedding: representación vectorial del fragmento.
- created_at: fecha de registro.

### rag_queries

Registra las consultas realizadas al sistema RAG.

Campos principales:

- id: identificador interno de la consulta.
- question: pregunta enviada por la persona usuaria.
- answer: respuesta generada por el sistema.
- channel: canal de interacción utilizado.
- model_name: modelo generativo utilizado.
- created_at: fecha de registro.

### retrieval_logs

Registra los fragmentos recuperados para cada consulta.

Campos principales:

- id: identificador interno del registro.
- query_id: consulta relacionada.
- chunk_id: fragmento documental recuperado.
- similarity_score: puntaje de similitud.
- rank_position: posición del fragmento en el ranking.
- created_at: fecha de registro.

## Índices creados

Comandos SQL utilizados:

    CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id
    ON document_chunks(document_id);

    CREATE INDEX IF NOT EXISTS idx_document_chunks_metadata
    ON document_chunks USING gin(metadata);

## Índice vectorial

Se probó la creación del índice vectorial ivfflat:

    CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding
    ON document_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

PostgreSQL mostró el siguiente aviso:

    NOTICE: ivfflat index created with little data
    DETAIL: This will cause low recall.
    HINT: Drop the index until the table has more data.

Por esa razón, el índice vectorial fue eliminado temporalmente y se recreará cuando exista una cantidad suficiente de fragmentos documentales cargados.

Comando usado:

    DROP INDEX IF EXISTS idx_document_chunks_embedding;

## Validación de conexión desde Python

Se creó el módulo app/db.py para centralizar la conexión a PostgreSQL mediante variables de entorno.

La conexión fue validada con el resultado:

    ('rag_tesis', 'rag_user')

## Consideraciones de seguridad

- El archivo .env contiene credenciales locales y no debe subirse al repositorio.
- El entorno virtual .venv/ no debe versionarse.
- La contraseña real de rag_user no debe documentarse en archivos versionados.
EOF