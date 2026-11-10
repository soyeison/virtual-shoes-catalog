# Desarrollo local

Cómo ejecutar el frontend en tu máquina. Necesitas la API corriendo (por defecto en `http://localhost:8000`); para levantarla consulta [development.md](../../virtual-catalog-api/docs/development.md) del backend. Para levantar todo el stack en contenedores, consulta el README de la raíz del monorepo.

## Requisitos

- **Node.js >= 22.12.0** (lo exige `engines` en `package.json`; la imagen de Docker usa `node:22-alpine`)
- npm (se usa `package-lock.json`)
- La API accesible desde el navegador, con `http://localhost:4321` en su `CORS_ORIGINS`
- Opcional: Docker, para construir la imagen de la web
- Opcional: la extensión de VS Code `astro-build.astro-vscode` (recomendada en `.vscode/extensions.json`)

Dependencias principales (`package.json`):

| Paquete | Uso |
| --- | --- |
| `astro` | Framework, enrutamiento por archivos y SSR |
| `@astrojs/node` | Adapter que genera el servidor Node standalone |
| `@astrojs/react`, `react`, `react-dom` | Islas interactivas |
| `tailwindcss`, `@tailwindcss/vite` | Estilos (Tailwind 4) |
| `zustand` | Stores de estado global (auth y carrito) |
| `@types/react`, `@types/react-dom`, `@types/node` | Tipos de TypeScript |

## 1. Instalar dependencias

```bash
cd shoes-web-app
npm install        # o npm ci para respetar exactamente el lockfile
```

## 2. Configurar la URL de la API

Crea o revisa `.env` (ver [configuration.md](configuration.md)):

```dotenv
PUBLIC_API_URL=http://localhost:8000/api/v1
```

Si no existe, el código usa `http://localhost:8000/api/v1` por defecto.

## 3. Servidor de desarrollo

```bash
npm run dev
```

Abre http://localhost:4321. Astro recarga en caliente los cambios de `.astro`, `.tsx` y CSS. En modo dev todas las páginas se renderizan bajo demanda (también `/login`).

En VS Code también puedes usar la configuración "Development server" de `.vscode/launch.json`, que ejecuta `astro dev`.

## 4. Compilar y ejecutar el build

```bash
npm run build
```

Genera:

```
dist/
├── client/          # Estáticos: _astro/*.js|css, login/index.html, banner-bg.png, favicons
└── server/
    └── entry.mjs    # Servidor Node standalone
```

Para ejecutarlo hay dos opciones:

```bash
# Opción A: preview de Astro (usa el adapter de Node)
npm run preview

# Opción B: el servidor standalone directamente, como en producción
node ./dist/server/entry.mjs
# con otra API para el SSR y otro puerto/host:
INTERNAL_API_URL=http://localhost:8000/api/v1 HOST=0.0.0.0 PORT=4321 node ./dist/server/entry.mjs
```

Recuerda: `PUBLIC_API_URL` queda fija en el build. Si la cambias, vuelve a ejecutar `npm run build`.

## Scripts disponibles

| Script | Comando | Descripción |
| --- | --- | --- |
| `npm run dev` | `astro dev` | Servidor de desarrollo en `localhost:4321` |
| `npm run build` | `astro build` | Build de producción en `dist/` |
| `npm run preview` | `astro preview` | Sirve el build con el adapter de Node |
| `npm run astro -- <cmd>` | `astro <cmd>` | CLI de Astro (`add`, `info`, ...) |

No hay scripts de tests, lint ni formateo, y no están instalados `typescript` ni `@astrojs/check`, así que tampoco hay verificación de tipos en CI. `npx astro check` pedirá instalar `@astrojs/check`.

## Docker de la web

El `Dockerfile` es multi-stage:

| Etapa | Base | Qué hace |
| --- | --- | --- |
| `build` | `node:22-alpine` | Recibe `ARG PUBLIC_API_URL` y lo expone como `ENV`, ejecuta `npm ci` y `npm run build` |
| `runtime` | `node:22-alpine` | `NODE_ENV=production`, `HOST=0.0.0.0`, `PORT=4321`; `npm ci --omit=dev`; copia `dist/`; `EXPOSE 4321`; `CMD ["node", "./dist/server/entry.mjs"]` |

La etapa final instala las dependencias de producción porque el servidor compilado importa paquetes de `node_modules` (Astro, React, etc.). Todas las dependencias del proyecto están en `dependencies`; `--omit=dev` solo deja fuera `@types/node`.

`.dockerignore` excluye `node_modules`, `dist`, `.astro`, `.env`, `.env.production`, `.vscode`, `Dockerfile` y `.dockerignore`. Por eso **el `.env` local no llega a la imagen**: la URL pública se pasa como build arg.

Con Docker Compose (desde la raíz del monorepo), el servicio `web` ya pasa los valores correctos:

```yaml
web:
  build:
    context: ./shoes-web-app
    args:
      PUBLIC_API_URL: http://localhost:8000/api/v1   # navegador
  environment:
    INTERNAL_API_URL: http://api:8000/api/v1         # SSR
  ports:
    - "4321:4321"
  depends_on:
    - api
```

```bash
docker compose up --build web      # también levanta api y sus dependencias
```

Sin Compose:

```bash
docker build -t shoes-web --build-arg PUBLIC_API_URL=http://localhost:8000/api/v1 ./shoes-web-app
docker run --rm -p 4321:4321 -e INTERNAL_API_URL=http://host.docker.internal:8000/api/v1 shoes-web
```

En Linux, `host.docker.internal` puede requerir `--add-host=host.docker.internal:host-gateway`. Si omites `INTERNAL_API_URL`, el SSR usará `PUBLIC_API_URL` (`localhost:8000`), que dentro del contenedor apunta al propio contenedor y fallará.

`depends_on: api` solo ordena el arranque; no espera a que la API responda. Si la web recibe peticiones antes, la portada mostrará el mensaje de error hasta recargar.

## Problemas comunes

| Síntoma | Causa probable | Solución |
| --- | --- | --- |
| La portada dice "No pudimos conectar con el almacén" | El servidor de Astro no llega a la API (SSR) | Revisa que la API esté arriba y el valor de `INTERNAL_API_URL` / `PUBLIC_API_URL` en el servidor |
| La portada carga, pero buscar, el carrito o el login fallan | El navegador no llega a la API o CORS lo bloquea | Revisa la consola del navegador; confirma `PUBLIC_API_URL` y que el origen esté en `CORS_ORIGINS` de la API |
| Error de CORS al abrir `http://127.0.0.1:4321` | La API solo permite `http://localhost:4321` | Usa `localhost` o agrega el origen a `CORS_ORIGINS` |
| Cambié `PUBLIC_API_URL` y el navegador sigue usando la URL vieja | Se incrusta en el build | `npm run build` de nuevo / `docker compose build web` |
| El contenedor `web` llama a `localhost:8000` desde SSR | Falta `INTERNAL_API_URL` | Defínela (en Compose: `http://api:8000/api/v1`) |
| El login muestra "HTTP Error: 400" | Credenciales incorrectas; el front no lee el mensaje de la API | Ver [known-issues.md](known-issues.md) |
| El registro falla con "HTTP Error: 400" o "HTTP Error: 422" | Validación del backend: contraseña < 6, menor de edad, email repetido o **código postal vacío / no numérico / < 5 dígitos** (la UI lo marca como opcional) | Completa un código postal válido, p. ej. `050010` |
| Imágenes rotas en tarjetas o checkout | El artículo no tiene imágenes y `/placeholder-shoe.png` no existe en `public/`, o RustFS no es accesible en `localhost:9000` | Ver [known-issues.md](known-issues.md) |
| El pago siempre falla | La API usa `PAYMENT_GATEWAY_PROVIDER=stripe` y el front envía `test_token_123` | Usa `mock` en la API para desarrollo |
| "Salir" aparece, pero el carrito no carga y "Agregar" lleva al login | El token guardado no se pudo decodificar (`userId` nulo) | Borra `auth-storage` de `localStorage` y vuelve a iniciar sesión |
| `npm run build` falla con `--outDir` fuera del proyecto | Los chunks no resuelven `node_modules` fuera del árbol del proyecto | Compila en el `dist/` por defecto |
