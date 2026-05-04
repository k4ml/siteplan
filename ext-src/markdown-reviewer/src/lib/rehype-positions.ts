import type { Element, Root, RootContent, Text } from "hast";

/**
 * Rehype plugin that:
 *   1. Tags every Element node that carries a source `position` with
 *      `data-src-start` / `data-src-end` attributes (character offsets into
 *      the original markdown source).
 *   2. Wraps every Text node outside of `<pre>` code blocks with a
 *      `<span class="mdr-text" data-src-start data-src-end>` so that the
 *      browser Selection API can be mapped back to source offsets.
 *
 * Code blocks are intentionally skipped: `rehype-highlight` rewrites their
 * inner text into many spans, so we rely on the surrounding `<pre>` element's
 * position attributes instead.
 */
export default function rehypePositions() {
  return (tree: Root) => {
    decorate(tree as unknown as { children: RootContent[] }, false);
  };
}

function decorate(
  parent: { children: RootContent[] },
  inPre: boolean,
): void {
  const newChildren: RootContent[] = [];
  for (const child of parent.children) {
    if (child.type === "element") {
      const el = child as Element;
      if (el.position) {
        el.properties = el.properties ?? {};
        el.properties.dataSrcStart = String(el.position.start.offset ?? 0);
        el.properties.dataSrcEnd = String(el.position.end.offset ?? 0);
      }
      const childInPre = inPre || el.tagName === "pre";
      decorate(el as unknown as { children: RootContent[] }, childInPre);
      newChildren.push(el);
      continue;
    }

    if (child.type === "text" && !inPre && child.position) {
      const text = child as Text;
      const start = text.position?.start.offset ?? 0;
      const end = text.position?.end.offset ?? start + text.value.length;
      const wrapper: Element = {
        type: "element",
        tagName: "span",
        properties: {
          className: ["mdr-text"],
          dataSrcStart: String(start),
          dataSrcEnd: String(end),
        },
        children: [text],
      };
      newChildren.push(wrapper);
      continue;
    }

    newChildren.push(child);
  }
  parent.children = newChildren;
}
