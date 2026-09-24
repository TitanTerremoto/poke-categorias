# Poké-Categorías

Juego HTML para grabar Reels verticales (1080 × 1982), hecho sobre la base técnica y visual de **PokéDuelo**.

- Abrí `index.html` en el navegador. Con `#panel` al final de la URL se abre el panel de control en otra pestaña.
- Teclas: **R** modo grabación 1:1 · **G** ocultar guías · **P** panel.
- Categorías, dinero inicial y símbolo de moneda: objeto `CONFIG` al principio del script.
- Sprites: retratos y poses de [PMDCollab/SpriteCollab](https://github.com/PMDCollab/SpriteCollab). El índice de qué emociones/poses existen por especie se regenera con `tools/build_pmd_index.py`.
- Fuente: poné el archivo de la fuente PokemonDB en `assets/fonts/pokemondb.woff2` (o `.ttf` / `.otf`). Hasta entonces se usa un fallback provisorio.
