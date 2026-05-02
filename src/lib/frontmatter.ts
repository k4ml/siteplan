/**
 * Minimal YAML frontmatter extractor. Handles the common
 *   ---
 *   key: value
 *   key: value
 *   ---
 * shape that AI plan files and markdown notes typically use. Anything more
 * structured (nested objects, arrays, multiline values) is preserved as-is
 * in the raw value string.
 */

export interface Frontmatter {
  pairs: Array<{ key: string; value: string }>;
  rawBlock: string; // includes the surrounding --- lines
}

export function extractFrontmatter(source: string): Frontmatter | null {
  if (!source.startsWith("---")) return null;
  const lines = source.split("\n");
  if (lines[0].trim() !== "---") return null;
  let endIdx = -1;
  for (let i = 1; i < lines.length; i++) {
    if (lines[i].trim() === "---") {
      endIdx = i;
      break;
    }
  }
  if (endIdx === -1) return null;

  const pairs: Array<{ key: string; value: string }> = [];
  for (let i = 1; i < endIdx; i++) {
    const line = lines[i];
    if (!line.trim() || line.startsWith("#")) continue;
    const colon = line.indexOf(":");
    if (colon === -1) continue;
    const key = line.slice(0, colon).trim();
    let value = line.slice(colon + 1).trim();
    // Strip wrapping quotes if both sides match.
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (key) pairs.push({ key, value });
  }

  const rawBlock = lines.slice(0, endIdx + 1).join("\n");
  return { pairs, rawBlock };
}
