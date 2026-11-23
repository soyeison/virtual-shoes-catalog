// @ts-check
import { defineConfig } from "astro/config";

import react from "@astrojs/react";

import node from "@astrojs/node";

import tailwindcss from "@tailwindcss/vite";

// https://astro.build/config
export default defineConfig({
  // Astro 7 cambió el valor por defecto a "jsx", que elimina los espacios entre etiquetas
  // (<span>a</span> <em>b</em> se ve "ab"). true mantiene el comportamiento de Astro 6.
  compressHTML: true,

  integrations: [react()],

  adapter: node({ mode: "standalone" }),

  vite: {
    plugins: [tailwindcss()],
  },
});
