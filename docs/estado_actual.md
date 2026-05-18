# Estado actual del prototipo RAG

Fecha de avance: 2026-05-17

## Objetivo técnico actual

Construir un prototipo RAG local para tesis, basado en PostgreSQL, pgvector, Python, Ollama/Gemma y futura integración con OpenClaw/Discord.

## Estado de PostgreSQL

- PostgreSQL instalado y activo.
- Base de datos creada: rag_tesis.
- Usuario de aplicación creado: rag_user.
- Conexión desde consola validada.
- Conexión desde Python validada.

Resultado validado desde Python:

    ('rag_tesis', 'rag_user')

## Estado de pgvector

La extensión pgvector quedó habilitada en la base rag_tesis.

Resultado validado:

    vector | 0.6.0

## Tablas creadas

Se crearon cuatro tablas principales:

- documents
- document_chunks
- rag_queries
- retrieval_logs

Propietario actual de las tablas:

- rag_user

## Índices creados

Se crearon índices básicos para:

- document_chunks(document_id)
- document_chunks(metadata) usando GIN

El índice vectorial ivfflat fue probado, pero eliminado temporalmente porque la tabla todavía no tiene suficientes datos. Se recreará después de cargar chunks documentales.

## Proyecto local

Ruta del proyecto:

    /home/diego/rag-tesis

Estructura actual:

    rag-tesis/
    ├── app/
    │   ├── db.py
    │   └── db_check.py
    ├── database/
    │   └── schema.sql
    ├── data/
    │   ├── documents/
    │   └── processed/
    ├── docs/
    │   ├── base_datos.md
    │   └── estado_actual.md
    ├── logs/
    ├── scripts/
    ├── .env
    ├── .gitignore
    ├── README.md
    ├── requirements.txt
    └── .venv/

## Archivos versionados en Git

Archivos versionados actualmente:

- .gitignore
- README.md
- app/db.py
- app/db_check.py
- database/schema.sql
- docs/base_datos.md
- docs/estado_actual.md
- requirements.txt

Archivos protegidos y no versionados:

- .env
- .venv/
- logs/
- data/processed/

## Dependencias Python instaladas

Dependencias base:

- psycopg
- psycopg-binary
- python-dotenv

Procesamiento documental:

- pypdf
- python-docx
- pymupdf
- pandas
- openpyxl
- beautifulsoup4
- markdownify
- python-magic
- charset-normalizer

OCR:

- pytesseract
- pdf2image
- pillow

Dependencias de sistema instaladas para OCR:

- tesseract-ocr
- tesseract-ocr-spa
- tesseract-ocr-eng
- poppler-utils

## Repositorio GitHub

Repositorio remoto configurado:

    https://github.com/diegoarcecast/RAG.git

Rama principal:

    main

Autenticación GitHub CLI configurada correctamente con el usuario:

    diegoarcecast

## Decisiones técnicas tomadas

1. PostgreSQL será la base principal del prototipo.
2. pgvector permitirá almacenar embeddings dentro de PostgreSQL.
3. La dimensión inicial de embeddings será 768.
4. El índice vectorial se creará después de cargar suficientes chunks.
5. El archivo .env contiene credenciales locales y no debe subirse.
6. El pipeline documental deberá intentar primero extracción directa de texto.
7. Si la extracción directa es insuficiente, se aplicará OCR.
8. El origen del texto debe guardarse como metadato: extracción directa u OCR.
9. La estructura técnica real debe documentarse en la tesis si cambia.

## Próximo paso técnico recomendado

Crear el pipeline de ingestión documental:

1. Detectar tipo de archivo.
2. Extraer texto de PDF, DOCX, TXT, Markdown, HTML, CSV y XLSX.
3. Aplicar OCR si el texto extraído es insuficiente.
4. Limpiar texto.
5. Dividir en chunks.
6. Guardar documentos y chunks en PostgreSQL.
7. Posteriormente generar embeddings e insertarlos en document_chunks.
