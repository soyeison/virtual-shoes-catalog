# Datos de prueba (seed)

`seed.py` llena la base de datos con **20 artículos** de zapatos y sube sus imágenes a RustFS.

## Ejecutar

Requisitos: RustFS levantado (con el bucket creado) y el `.env` completo.

```bash
# Local, desde virtual-catalog-api/
python seed.py

# Docker, desde la raíz del monorepo
docker compose exec api python seed.py
```

Salida esperada:

```
Running seeder...
Generating article 1/20: Zapatos Skechers...
...
Generating article 20/20: Zapatos Nike 1.2...
Base de datos y almacenamiento poblados con éxito
```

## Qué hace

Por cada uno de los 20 nombres definidos en `products`:

1. **Imagen local**: lee `static/zapato{N}.jpg.jpeg` y la sube a RustFS. Si el archivo no existe, muestra una advertencia y continúa.
2. **Imagen de internet**: descarga una imagen aleatoria de 400×400 de `https://picsum.photos/400` y la sube. Si no hay internet, muestra el error y continúa.
3. **Precio** aleatorio entre 50.000 y 1.500.000 COP y **stock** aleatorio entre 5 y 50.
4. Crea el artículo con `CreateArticleUseCase`, así que se aplican las mismas validaciones de dominio que en la API.

Usa la misma configuración que la API (`settings.database_path` y `settings.s3_*`), así que escribe en la misma base de datos y en el mismo bucket.

## Consideraciones

- **No es idempotente**: cada ejecución crea 20 artículos **nuevos** (con UUID nuevos) y sube imágenes nuevas. Ejecutarlo dos veces deja 40 artículos.
- Para empezar de cero:
  - Local: borra `data/catalogo.db` (las imágenes viejas quedan en RustFS).
  - Docker: `docker compose down -v` borra los volúmenes de la base de datos y de RustFS.
- Las URLs guardadas usan `S3_PUBLIC_URL` en el momento del seed. Si cambias esa variable, vuelve a ejecutarlo.
- Las imágenes locales están en `static/` (`zapato1.jpg.jpeg` … `zapato20.jpg.jpeg`), que se copia a la imagen Docker.
- No crea usuarios, carritos ni pedidos. Para probar el flujo de compra, registra un usuario con `POST /api/v1/auth/register` (ver [api-reference.md](api-reference.md)).
