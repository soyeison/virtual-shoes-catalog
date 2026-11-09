# NovaRun - Frontend del catálogo virtual de calzado

Tienda web del monorepo `virtual-shoes-catalog`. Permite buscar y filtrar el catálogo, ver el detalle de cada zapato, registrarse e iniciar sesión, gestionar el carrito en un panel lateral, generar la orden y simular el pago. Consume la API FastAPI de [`virtual-catalog-api`](../virtual-catalog-api/) (`/api/v1`). Las páginas se renderizan en el servidor con Astro (SSR sobre Node) y las partes interactivas son islas de React que comparten estado con Zustand.

## Stack

| Tecnología | Uso |
| --- | --- |
| Astro 6 + `@astrojs/node` (standalone) | Enrutamiento, SSR y servidor Node |
| React 19 (`@astrojs/react`) | Islas interactivas (`client:load`) |
| Zustand 5 | Estado global: sesión (persistida en `localStorage`) y carrito |
| Tailwind CSS 4 (`@tailwindcss/vite`) | Estilos |
| TypeScript (config `strict` de Astro) | Tipado |
| Docker (`node:22-alpine`) | Imagen de producción |

## Inicio rápido

Requiere Node.js >= 22.12 y la API corriendo en `http://localhost:8000`.

```bash
cd shoes-web-app
npm install
[ -f .env ] || echo "PUBLIC_API_URL=http://localhost:8000/api/v1" > .env
npm run dev                                                # http://localhost:4321
```

Para el stack completo en Docker (MinIO + API + web), usa el `docker-compose.yml` de la raíz del monorepo: `docker compose up --build`.

## Documentación

| Documento | Contenido |
| --- | --- |
| [docs/architecture.md](docs/architecture.md) | Estructura de carpetas (`modules/`, `shared/`, `pages/`), patrón gateway sobre `httpClient`, islas React vs. páginas SSR |
| [docs/pages.md](docs/pages.md) | Cada ruta y su flujo: catálogo, detalle, login, carrito y checkout/pago; qué carga el servidor y qué el navegador |
| [docs/configuration.md](docs/configuration.md) | `PUBLIC_API_URL` vs `INTERNAL_API_URL`, build vs runtime, adapter de Node y `.env` |
| [docs/development.md](docs/development.md) | Requisitos, scripts, ejecución del build standalone, Docker de la web y problemas comunes |
| [docs/api-client.md](docs/api-client.md) | `httpClient`, gateways, mapa de endpoints, modelos y manejo de errores |
| [docs/state-management.md](docs/state-management.md) | Stores de Zustand (`useAuthStore`, `useCartStore`), persistencia e hidratación |
| [docs/auth.md](docs/auth.md) | Cómo se obtiene, guarda y envía el JWT, y qué implica que la API no lo valide |
| [docs/styles.md](docs/styles.md) | Tailwind 4, fuentes, paleta y recursos estáticos |
| [docs/known-issues.md](docs/known-issues.md) | Bugs, inconsistencias y limitaciones conocidas del frontend |

Documentación de la API: [virtual-catalog-api/docs/](../virtual-catalog-api/docs/) (en especial [api-reference.md](../virtual-catalog-api/docs/api-reference.md) y [security.md](../virtual-catalog-api/docs/security.md)).
