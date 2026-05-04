import type { CommentAnchor } from "../types";
import {
  buildLineStarts,
  offsetToLineCol,
  snippetFromSource,
} from "./positions";

/**
 * Map a (Node, offset) pair from a DOM Range endpoint to a character offset
 * in the original markdown source. Returns null if the boundary cannot be
 * resolved (e.g., it falls outside any decorated subtree).
 */
function endpointToSourceOffset(node: Node, offset: number): number | null {
  if (node.nodeType === Node.TEXT_NODE) {
    const span = (node.parentElement as HTMLElement | null)?.closest(
      "[data-src-start]",
    ) as HTMLElement | null;
    if (!span) return null;
    const start = Number(span.getAttribute("data-src-start"));
    if (!Number.isFinite(start)) return null;
    let prior = 0;
    for (const sib of Array.from(span.childNodes)) {
      if (sib === node) break;
      prior += sib.textContent?.length ?? 0;
    }
    return start + prior + offset;
  }

  if (node.nodeType === Node.ELEMENT_NODE) {
    const el = node as Element;
    if (offset >= el.childNodes.length) {
      return lastLeafEndOffset(el);
    }
    return firstLeafStartOffset(el.childNodes[offset]);
  }

  return null;
}

function firstLeafStartOffset(node: Node): number | null {
  if (node.nodeType === Node.TEXT_NODE) {
    return endpointToSourceOffset(node, 0);
  }
  if (node.nodeType === Node.ELEMENT_NODE) {
    const el = node as HTMLElement;
    const attr = el.getAttribute("data-src-start");
    if (attr != null) {
      const n = Number(attr);
      if (Number.isFinite(n)) return n;
    }
    if (el.firstChild) return firstLeafStartOffset(el.firstChild);
  }
  return null;
}

function lastLeafEndOffset(node: Node): number | null {
  if (node.nodeType === Node.TEXT_NODE) {
    return endpointToSourceOffset(node, node.textContent?.length ?? 0);
  }
  if (node.nodeType === Node.ELEMENT_NODE) {
    const el = node as HTMLElement;
    const attr = el.getAttribute("data-src-end");
    if (attr != null) {
      const n = Number(attr);
      if (Number.isFinite(n)) return n;
    }
    if (el.lastChild) return lastLeafEndOffset(el.lastChild);
  }
  return null;
}

export interface SelectionResult {
  anchor: CommentAnchor;
  rect: DOMRect;
}

/**
 * Read the current window selection. Returns the source-coord anchor and the
 * bounding rectangle of the selection (for popover placement) when the
 * selection lies wholly inside `container`. Returns null otherwise.
 */
export function readSelection(
  container: HTMLElement,
  source: string,
): SelectionResult | null {
  const sel = window.getSelection();
  if (!sel || sel.isCollapsed || sel.rangeCount === 0) return null;
  const range = sel.getRangeAt(0);
  if (!container.contains(range.commonAncestorContainer)) return null;

  const startOff = endpointToSourceOffset(range.startContainer, range.startOffset);
  const endOff = endpointToSourceOffset(range.endContainer, range.endOffset);
  if (startOff == null || endOff == null) return null;

  const [a, b] = startOff <= endOff ? [startOff, endOff] : [endOff, startOff];
  if (a === b) return null;

  const lineStarts = buildLineStarts(source);
  const start = offsetToLineCol(a, lineStarts);
  const end = offsetToLineCol(b, lineStarts);

  const rect = range.getBoundingClientRect();

  return {
    anchor: {
      startLine: start.line,
      startCol: start.col,
      endLine: end.line,
      endCol: end.col,
      snippet: snippetFromSource(source, a, b),
      contextBefore: source.slice(Math.max(0, a - 30), a),
      contextAfter: source.slice(b, Math.min(source.length, b + 30)),
    },
    rect,
  };
}
