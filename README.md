# Prototipo RAG para tesis

Este repositorio contiene el prototipo técnico del sistema basado en Retrieval-Augmented Generation (RAG) para consultas documentales académicas y técnicas.

El proyecto forma parte de la tesis de Juan Diego Arce Castro:

**Diseño, implementación y validación de un sistema basado en Retrieval-Augmented Generation (RAG), integrado a canales conversacionales mediante OpenClaw, para evaluar la trazabilidad documental, calidad de recuperación y confiabilidad de respuestas en consultas documentales académicas y técnicas.**

---

## 1. Ruta local y repositorio

Ruta local del proyecto:

```text
/home/diego/rag-tesis

Repositorio remoto:

https://github.com/diegoarcecast/RAG.git

Rama principal:

main
2. Objetivo técnico del prototipo

Construir un sistema RAG capaz de:

Cargar documentos académicos y técnicos.
Extraer texto desde diferentes formatos.
Limpiar y normalizar contenido.
Dividir documentos en fragmentos o chunks.
Guardar documentos y chunks en PostgreSQL.
Preparar los chunks para una etapa posterior de embeddings.
Recuperar evidencia documental.
Generar respuestas trazables y fundamentadas.
Integrar el sistema a un canal conversacional mediante OpenClaw.
3. Estado actual del proyecto
Ya implementado
Proyecto local creado en /home/diego/rag-tesis.
Repositorio Git inicializado y conectado con GitHub.
Ambiente virtual Python creado en .venv.
PostgreSQL instalado y funcionando.
Base de datos creada: rag_tesis.
Usuario creado: rag_user.
Extensión pgvector habilitada.
Extensión validada: vector 0.6.0.
Tablas creadas:
documents
document_chunks
rag_queries
retrieval_logs
Tablas propiedad de rag_user.
Pipeline inicial de ingesta documental implementado.
Persistencia básica en PostgreSQL implementada.
Comando de terminal con guardado opcional en base de datos implementado mediante --save-db.
4. Estructura técnica actual
rag-tesis/
├── app/
│   ├── db.py
│   ├── db_check.py
│   ├── ingest_document.py
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
5. Archivos principales
app/db.py

Contiene la conexión a PostgreSQL usando variables de entorno desde .env.

Funciones principales:

get_conninfo()
get_connection()
app/db_check.py

Valida conexión con PostgreSQL.

Comando validado:

python -m app.db_check

Resultado esperado:

Conexión correcta: base=rag_tesis, usuario=rag_user
app/ingestion/detector.py

Detecta el tipo documental.

Soporta:

PDF
DOCX
TXT
Markdown
HTML
CSV
XLSX
app/ingestion/cleaner.py

Limpia texto extraído.

Funciones:

Normalización Unicode.
Eliminación de caracteres de control.
Normalización de espacios.
Validación de texto mínimo.
app/ingestion/extractors.py

Extrae texto desde documentos.

Soporta:

PDF directo con PyMuPDF.
PDF escaneado con OCR usando Tesseract.
DOCX.
TXT.
Markdown.
HTML.
CSV.
XLSX.

Regla para PDF:

Intentar extracción directa.
Si el texto extraído es insuficiente, aplicar OCR.
Registrar método de extracción: direct u ocr.
app/ingestion/chunker.py

Divide texto en chunks.

Componentes:

TextChunk
split_text_into_chunks()
chunks_to_dicts()

Parámetros actuales usados en pruebas:

chunk_size = 300
chunk_overlap = 50
min_chunk_size = 100

Observación técnica:

Actualmente el chunking corta por caracteres. Esto funciona, pero puede cortar palabras. Es una mejora pendiente.

app/ingestion/pipeline.py

Orquesta la ingesta documental en memoria.

Etapas:

[1/5] Detectar tipo de archivo
[2/5] Extraer texto del documento
[3/5] Construir metadata base
[4/5] Dividir texto en chunks
[5/5] Construir resultado final
app/ingestion/repository.py

Capa de persistencia hacia PostgreSQL.

Funciones implementadas:

insert_document(document)
insert_document_chunks(document_id, chunks)
save_ingestion_result(ingestion_result)
delete_document_by_file_path(file_path)

Responsabilidad:

Guardar documentos en documents y chunks en document_chunks.

También permite limpiar una ingesta por file_path.

app/ingest_document.py

Comando principal de ingesta desde terminal.

Opciones soportadas:

--chunk-size
--chunk-overlap
--min-chunk-size
--show-text
--show-chunks
--json-output
--save-db
6. Base de datos actual
Tabla documents

Campos relevantes:

id
title
source_type
file_path
author
publication_year
created_at
Tabla document_chunks

Campos relevantes:

id
document_id
chunk_index
chunk_text
page_number
section_title
metadata
embedding vector(768)
created_at

Relación:

document_chunks.document_id -> documents.id
ON DELETE CASCADE

Esto significa que si se elimina un documento, sus chunks se eliminan automáticamente.

7. Flujo actual validado
archivo local
 -> detección de tipo documental
 -> extracción de texto
 -> limpieza básica
 -> división en chunks
 -> resultado en memoria
 -> guardado opcional en PostgreSQL con --save-db
8. Tipos de documentos validados

Se validó procesamiento en memoria con:

TXT
Markdown
HTML
CSV
XLSX

Archivo XLSX usado para prueba principal:

data/raw/samples/prueba_xlsx.xlsx

Resultado validado:

Éxito: True
Tipo documental: xlsx
Método de extracción: direct
Caracteres extraídos: 382
Chunks generados: 2
9. Comandos validados
Activar ambiente virtual
cd /home/diego/rag-tesis
source .venv/bin/activate
Validar conexión a PostgreSQL
python -m app.db_check
Ejecutar ingesta en memoria
python -m app.ingest_document data/raw/samples/prueba_xlsx.xlsx --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --show-chunks
Guardar resultado JSON de depuración
python -m app.ingest_document data/raw/samples/prueba_xlsx.xlsx --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --json-output data/processed/debug/prueba_xlsx.json
Guardar ingesta en PostgreSQL
python -m app.ingest_document data/raw/samples/prueba_xlsx.xlsx --chunk-size 300 --chunk-overlap 50 --min-chunk-size 100 --save-db

Resultado validado:

Ingesta guardada en PostgreSQL
document_id: 2
chunks_insertados: 2
Consultar documentos guardados
psql -h localhost -U rag_user -d rag_tesis -c "SELECT id, title, source_type, file_path FROM documents ORDER BY id DESC LIMIT 5;"
Consultar chunks guardados
psql -h localhost -U rag_user -d rag_tesis -c "SELECT id, document_id, chunk_index, LEFT(chunk_text, 120) AS preview FROM document_chunks ORDER BY id DESC LIMIT 10;"
Limpiar una ingesta por file_path
python - <<'PY'
from app.ingestion.repository import delete_document_by_file_path

file_path = "/home/diego/rag-tesis/data/raw/samples/prueba_xlsx.xlsx"

deleted = delete_document_by_file_path(file_path)

print(f"Documentos eliminados: {deleted}")
PY

Resultado validado:

Documentos eliminados: 1
Confirmar base limpia
psql -h localhost -U rag_user -d rag_tesis -c "SELECT COUNT(*) AS total_documents FROM documents;"

psql -h localhost -U rag_user -d rag_tesis -c "SELECT COUNT(*) AS total_chunks FROM document_chunks;"

Resultado validado:

documents = 0
document_chunks = 0
10. Reglas de seguridad del proyecto

No se deben subir al repositorio:

.env
.venv/
logs/
data/processed/
Documentos reales dentro de data/raw/

La carpeta data/raw/ se conserva mediante .gitkeep.

El archivo .gitignore debe evitar subir documentos locales de prueba o documentos reales.

11. Problemas detectados y aprendizajes
Permisos

Se trabajó accidentalmente como root usando sudo su.

Esto causó archivos con dueño root dentro del proyecto y errores como:

Permission denied

Solución aplicada:

sudo chown -R diego:diego /home/diego/rag-tesis

Regla:

No trabajar como root dentro del proyecto.

Python

Desde el usuario normal, el comando python solo funciona si está activo el .venv.

Forma correcta:

cd /home/diego/rag-tesis
source .venv/bin/activate

Luego:

which python
python --version

Resultado esperado:

/home/diego/rag-tesis/.venv/bin/python
Python 3.12.3
PostgreSQL

El usuario Linux diego no existe como rol en PostgreSQL.

Por eso, usar siempre:

psql -h localhost -U rag_user -d rag_tesis
12. Pendientes inmediatos
Probar --save-db con todos los tipos ya validados:
TXT
Markdown
HTML
CSV
XLSX
Crear o conseguir documentos PDF de prueba:
PDF con texto seleccionable.
PDF escaneado para OCR.
Probar PDF con extracción directa.
Probar PDF escaneado con OCR.
Mejorar el chunking para evitar cortes en medio de palabras.
Definir estrategia de metadata:
source_file
source_path
document_type
extraction_method
chunk_index
start_character
end_character
posible page_number
posible section_title
Implementar generación de embeddings.
Guardar embeddings en document_chunks.embedding.
Crear índice vectorial cuando haya suficientes chunks.
Implementar búsqueda semántica.
Registrar consultas en rag_queries.
Registrar recuperación en retrieval_logs.
Integrar con modelo generativo.
Integrar con OpenClaw y Discord.
13. Próximo paso recomendado

El próximo paso técnico recomendado es:

Probar --save-db con TXT, Markdown, HTML, CSV y XLSX en una tanda controlada,
verificar conteos en PostgreSQL y luego limpiar la base.

Después de eso:

Probar PDF directo y PDF con OCR.

No se recomienda avanzar a embeddings hasta que la ingesta, persistencia, limpieza y validación de formatos estén estables.