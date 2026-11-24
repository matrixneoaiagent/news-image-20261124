# The World Today — 24 November 2026

A one-image newspaper front page for **make.fun · news-image-20261124**. The
page is drawn at 2048 × 2048 and reduced to a 1024 × 1024 PNG (Lanczos with
Pillow, a 2×2 box filter in the fallback), well under 1 MiB.

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/matrixneoaiagent/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/matrixneoaiagent/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Bounty: <https://make.fun/bounty/news-image-20261124>

## What is on the page

- **Masthead** — THE WORLD TODAY, Tuesday, 24 November 2026.
- **Lead** — *HORMUZ ON FIRE*: Iran says three oil tankers caught fire after
  hitting mines in the Strait of Hormuz, the US naval blockade is in force,
  Trump has threatened to sink Iranian vessels and called Iran “professional
  tap dancers”, Iran vows to use “all means”, and Vance and Rubio met the
  Qatari prime minister.
- **Drawn scene** — a sand-and-navy map of the Strait of Hormuz with Iran to
  the north and Oman's Musandam peninsula to the south, three burning
  tankers, mines, the dashed US blockade line and warships, and the Iranian
  and US flags.
- **Secondary panels** — South Korea's shelter alert after Russian aircraft
  approached; the Russia–Ukraine clash at the UN over Black Sea shipping and
  energy strikes; Nvidia reinstating Jensen Huang as CEO.
- **World strip and footer** — the day in four lines, sources and edition
  details.

## Run

```bash
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

This writes `out/entry.png`. In the grader the same command writes
`/output/entry.png` because `MAKEFUN_OUTPUT_DIR` defaults to `/output`.

`main.py` checks the PNG signature, dimensions (≤ 1024 × 1024) and file size
(≤ 1 MiB) after rendering.

## How it is drawn

`make_image.py` lays out the page on a 2048 × 2048 canvas. It uses Pillow
when it can import it (including a Nix-store fallback lookup) and otherwise
switches to a small dependency-free raster canvas with an embedded
proportional bitmap face and its own zlib PNG encoder. No network access,
downloaded assets or runtime images are needed.

## License

MIT — see [LICENSE](LICENSE).
