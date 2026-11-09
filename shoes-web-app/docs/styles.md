# Estilos

## Tailwind CSS 4

- Se integra como plugin de Vite (`@tailwindcss/vite` en `astro.config.mjs`). No hay `tailwind.config.*` ni `postcss.config.*`.
- `src/styles/global.css` contiene solo `@import "tailwindcss";`. Lo importan `MainLayout.astro` y `login.astro`.
- Casi todo el estilo son clases utilitarias en el marcado, con muchos valores arbitrarios (`bg-[#0f0f0f]`, `font-['Urbanist']`, `lg:grid-cols-[1.2fr_1fr]`).
- No hay tema propio (`@theme`), ni modo claro/oscuro: el sitio es oscuro y `/login` es blanco con panel negro.

### Clases que no tienen efecto

Estas clases aparecen en el código pero no generan CSS (comprobado en el build: no están en los `.css` de `dist/client/_astro/`):

| Clase | Dónde | Motivo |
| --- | --- | --- |
| `animate-fade-in` | `login.astro`, `LoginForm`, `checkout/[id].astro`, `PaymentProcessor` | Animación no definida (no hay `@keyframes` ni `@theme`) |
| `scale-in` | `CartWidget` (globo del contador) | No es una utilidad de Tailwind |
| `prose`, `prose-invert` | `article/[id].astro` (descripción) | Requieren `@tailwindcss/typography`, que no está instalado |

Para que funcionen habría que definirlas en `global.css` (por ejemplo con `@theme { --animate-fade-in: ... }` y `@keyframes`) o instalar el plugin de tipografía.

## Tipografía

| Página | Fuentes (Google Fonts) | Dónde se cargan |
| --- | --- | --- |
| Layout principal | Urbanist 400/500/700/900 | `<link>` en `MainLayout.astro`; se aplica con `font-['Urbanist']` en el `<body>` |
| `/login` | Gilda Display, Inter 300–900 | `<link>` en `login.astro`; clases globales `.font-serif-nova` y `.font-sans-nova` |

Las fuentes se piden a `fonts.googleapis.com` en cada carga; sin conexión a internet se usan las de respaldo del sistema.

## Paleta

| Uso | Valor |
| --- | --- |
| Fondo general | `#0f0f0f` |
| Cabecera, pie, sidebar | `#121212` |
| Tarjetas e inputs | `#1a1a1a` |
| Acento | `orange-500` de Tailwind; en login y pago `#EE6239` / `#DB6F32` |
| Bordes | `neutral-800` |

`login.astro` define además `.text-glow-orange` y `.shadow-button-orange` con `<style is:global>`.

## Recursos estáticos

`public/` contiene `banner-bg.png` (fondo del hero de `/`), `favicon.ico` y `favicon.svg`. El código también referencia archivos que **no existen** en `public/`: `/placeholder-shoe.png` y `/icons/shoe-icon.png`, `/icons/bolt-icon.png`, `/icons/run-icon.png` (ver [known-issues.md](known-issues.md)).

Las imágenes de los productos no son del front: son URLs públicas de MinIO que devuelve la API (`http://localhost:9000/catalogo-images/...`). Se muestran con `<img>` normales; no se usa el componente `<Image>` de Astro ni optimización de imágenes. `src/shared/ui/ArticleImage.astro` envuelve un `<img>` con `loading="lazy"`, pero ninguna página lo usa.
