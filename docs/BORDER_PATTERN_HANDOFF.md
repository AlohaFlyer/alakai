# Border pattern brief for ChatGPT (copy everything below the line into a new chat)

---

I am building a free SAT/ACT prep web app for high school students on Hawaiʻi Island, based in Waimea (Kamuela). The app has a thin decorative frame: a 26 px solid bar across the top on phones, and 26 px vertical bars down the left and right edges on desktop. I want candidate patterns for that frame. Please produce 4 to 6 candidates.

## What the pattern has to be

- An original geometric pattern in the manner of ʻohe kāpala (the carved bamboo stamps used to print kapa and decorate lauhala): triangles, chevrons, stacked bars, diamond lattice, dots, hatching. Think "stamped repeat", not illustration.
- Rooted in Waimea and the Kohala district specifically. Motifs you may encode as geometry: the Kohala mountain profile and Mauna Kea as low and tall triangles; Kīpuʻupuʻu, the cold wind-driven rain of Waimea, as a diagonal hatch; pili grass as short vertical ticks; the ranch-fence rhythm of paniolo country (posts and rails); ʻōhiʻa lehua of the Kohala forest as a radial dot cluster; the Waimea mist as a soft stepped band. Name which motifs each candidate uses.
- Single color on transparent. The app recolors the pattern with each school's primary color (HPA red #C8102E, Waiākea navy #022C66, Honokaʻa green #00824B, Parker maroon #8F0018), so the pattern is a mask: shape vs nothing, no gradients, no second color.
- Must read clearly at 26 px tall. Shapes narrower than about 2 px at that scale disappear. Prefer bold simple forms with generous negative space.
- Seamlessly tileable. Deliver each candidate as a square tile, 64 x 64 units, that repeats horizontally (top bar) and vertically (side bars) without a visible seam. Edges must match: anything touching the right edge continues on the left, same top to bottom.

## Hard rules (cultural)

- No kiʻi or akua imagery, no human or deity figures.
- No reproduction of actual petroglyphs (the Puakō petroglyph field is nearby and protected) and nothing that reads as a petroglyph copy.
- No kapu or ʻaumakua symbols, no sacred or ceremonial references.
- No Hawaiian flag, no crown or royal symbols.
- No "tiki" styling, no generic "Polynesian tattoo" fill, no tribal-tattoo look.
- Do not copy a specific kapa, quilt, or lauhala design that belongs to a family or practitioner; original composition only.
- Keep it respectful and plain. The pattern will be reviewed by a Hawaiian cultural practitioner before launch, and I will credit the inspiration in the app.

## Deliverable format

For each candidate give:
1. A name and one sentence on the motifs used.
2. The SVG source, exactly in this form, with all shapes filled black (#000) on a transparent background, no strokes, viewBox 0 0 64 64:
   ```
   <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">
     <g fill="#000">
       ... paths, rects, circles ...
     </g>
   </svg>
   ```
3. A short note confirming the tile is seamless on all four edges.

If you can also render a preview image of the tile repeated 10 times horizontally at 26 px tall and 8 times vertically at 26 px wide, in #C8102E on an off-white background (#FBF8F1), please do.

## Reference: three candidates I already have, so you do not repeat them

A. "Kohala": top band of diagonal rain hatch, a horizon line, a row of low triangles with one tall peak, a bottom band of short vertical grass ticks.
B. "Lauhala": a plaited diamond lattice with a nine-dot lehua cluster at each crossing.
C. "Paniolo": two rows of chevrons for ridgelines, then two horizontal rails with three vertical posts, then grass ticks.

Give me things that are different from those three: for example a stepped mist band, a koa-leaf crescent repeat, a stacked-bar "pāhoehoe" ripple, or a tall-and-short triangle rhythm for the two mountains with nothing else.
