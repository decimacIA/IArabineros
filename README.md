# IArabineros

Buscador público e independiente de normativa de Carabineros de Chile basada en fuentes abiertas. **No es un sitio oficial.**

## Estado
Interfaz y API iniciales listas. **No hay documentos incorporados todavía**; el sistema evita inventar artículos o atribuciones. La publicación en Render requiere conectar este repositorio y desplegar `render.yaml`.

## Ejecutar
`pip install -r requirements.txt` y `uvicorn app:app --reload`.

## Índice
Se espera una base SQLite `normativa.sqlite3` con tabla `passages` y columnas `source_id, title, url, article, page, text`. Solo incorporar textos públicos verificados y registrar URL y versión. No subir información reservada ni datos personales innecesarios.
