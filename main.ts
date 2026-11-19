import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const target = "/output/entry.png";

mkdirSync("/output", { recursive: true });
const bytes = readFileSync(source);
writeFileSync(target, bytes);
console.log("wrote", target, bytes.length, "bytes");
