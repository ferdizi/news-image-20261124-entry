// main.ts — news-image-20261124 entry program (Node 22, stdlib only).
// Copies the pre-rendered front page (entry.png, drawn at build time by
// render.py) into the grader's output directory. No network, no clock,
// no randomness: every run writes the same bytes.
import { chmodSync, copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const here = dirname(fileURLToPath(import.meta.url));

mkdirSync(outDir, { recursive: true });
const dest = join(outDir, "entry.png");
copyFileSync(join(here, "entry.png"), dest);
chmodSync(dest, 0o644);
