# Sandra Añez Powell — Paintings

Portfolio site for Sandra Añez Powell, a Venezuelan-born acrylic painter in Annapolis, Maryland.

**Live:** https://thejohncarter-ai.github.io/sandra-anez-powell/

## What's on the site

- Six collections: Majesty of the Bay, Jugando, Mi gente de campo, Divina, Floral and Reflections, plus the works in private collections.
- **Dip into a color:** filter paintings by their dominant color families, measured from the images at build time.
- **Match my room:** a visitor picks or snaps a photo, and the browser reads its colors and ranks the paintings. The photo never leaves the device.
- **See it on a wall:** shows the painting above an 84″ sofa at 16/24/36″, on four wall colors.
- Brushwork loupe (desktop), swipe browsing (touch), "Rehang the wall" shuffle, and a print order slip that sends an email.
- SEO: title and description, Open Graph tags, JSON-LD (Person + VisualArtwork), an image sitemap and robots.txt.

## Editing

The page is generated. Edit `src/site.tpl.html` (layout, styles, scripts) or the `P` list in `src/build.py` (titles, collections, status, alt text), then rebuild from the repo root:

```bash
python src/build.py --img img --deploy . --url https://thejohncarter-ai.github.io/sandra-anez-powell/
```

This needs Python 3 with Pillow (`pip install pillow`). Push to `main` and GitHub Pages redeploys.

## To do before promoting

- Replace the placeholder titles ("Divina No. 1" and so on) with real titles, sizes, years and prices.
- Set `ORDER_EMAIL` in `src/site.tpl.html` to Sandra's address.
- Point a custom domain (e.g. sandraanezpowell.com) at Pages and rebuild with that `--url`.
