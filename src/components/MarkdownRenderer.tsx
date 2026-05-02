import { useEffect, useLayoutEffect, useMemo, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkBreaks from "remark-breaks";
import rehypeHighlight from "rehype-highlight";
import rehypeSlug from "rehype-slug";
import rehypeAutolinkHeadings from "rehype-autolink-headings";
import rehypePositions from "../lib/rehype-positions";
import { buildLineStarts, lineColToOffset } from "../lib/positions";
import type { Comment } from "../types";

interface Props {
  source: string;
  comments: Comment[];
  activeCommentId: string | null;
  onSpanClick: (commentIds: string[]) => void;
}

export default function MarkdownRenderer({
  source,
  comments,
  activeCommentId,
  onSpanClick,
}: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  const rehypePlugins = useMemo(
    () => [
      rehypePositions,
      rehypeHighlight,
      rehypeSlug,
      [
        rehypeAutolinkHeadings,
        { behavior: "wrap", properties: { className: ["heading-anchor"] } },
      ] as const,
    ],
    [],
  );

  // Apply highlight overlays whenever the rendered output or comment set
  // changes. We do two things:
  //   1. Tag wrapping spans whose range overlaps any comment with
  //      `data-comment-ids` for click handling. (Coarse, span-level.)
  //   2. Use the CSS Custom Highlight API to paint the *exact* selected
  //      sub-span ranges in the right color. (Precise, sub-character.)
  // Falls back gracefully on browsers without the Highlights API.
  useLayoutEffect(() => {
    const root = containerRef.current;
    if (!root) return;

    // Clear previous click metadata.
    root.querySelectorAll<HTMLElement>("span[data-comment-ids]").forEach((el) => {
      el.removeAttribute("data-comment-ids");
    });

    const Highlights = (CSS as unknown as { highlights?: Map<string, unknown> })
      .highlights;
    const KEYS = [
      "mdr-comment-open",
      "mdr-comment-active",
      "mdr-comment-resolved",
      "mdr-comment-orphan",
    ] as const;
    if (Highlights) {
      for (const k of KEYS) Highlights.delete(k);
    }

    if (comments.length === 0) return;

    const lineStarts = buildLineStarts(source);
    const ranges = comments.map((c) => ({
      id: c.id,
      status: c.status,
      start: lineColToOffset(
        c.anchor.startLine,
        c.anchor.startCol,
        lineStarts,
        source,
      ),
      end: lineColToOffset(
        c.anchor.endLine,
        c.anchor.endCol,
        lineStarts,
        source,
      ),
    }));

    // Pass 1: tag wrapping spans for click handling.
    const spans = root.querySelectorAll<HTMLElement>(
      "span.mdr-text[data-src-start]",
    );
    spans.forEach((span) => {
      const start = Number(span.getAttribute("data-src-start"));
      const end = Number(span.getAttribute("data-src-end"));
      if (!Number.isFinite(start) || !Number.isFinite(end)) return;
      const matched = ranges.filter((r) => r.start < end && r.end > start);
      if (matched.length) {
        span.setAttribute("data-comment-ids", matched.map((m) => m.id).join(" "));
      }
    });

    // Pass 2: paint precise highlights via the Custom Highlight API.
    if (!Highlights || typeof Highlight === "undefined") return;
    const openR: Range[] = [];
    const resolvedR: Range[] = [];
    const orphanR: Range[] = [];
    const activeR: Range[] = [];
    for (const r of ranges) {
      const range = makeRange(root, r.start, r.end);
      if (!range) continue;
      if (r.id === activeCommentId) activeR.push(range);
      else if (r.status === "orphaned") orphanR.push(range);
      else if (r.status === "resolved") resolvedR.push(range);
      else openR.push(range);
    }
    const HighlightCtor = Highlight as unknown as new (
      ...rs: Range[]
    ) => unknown;
    if (openR.length) Highlights.set("mdr-comment-open", new HighlightCtor(...openR));
    if (resolvedR.length)
      Highlights.set("mdr-comment-resolved", new HighlightCtor(...resolvedR));
    if (orphanR.length)
      Highlights.set("mdr-comment-orphan", new HighlightCtor(...orphanR));
    if (activeR.length)
      Highlights.set("mdr-comment-active", new HighlightCtor(...activeR));
  }, [source, comments, activeCommentId]);

  // Click handler: find clicked highlight and broadcast its comment ids.
  useEffect(() => {
    const root = containerRef.current;
    if (!root) return;
    const handler = (e: MouseEvent) => {
      const target = (e.target as HTMLElement | null)?.closest(
        ".mdr-highlight",
      ) as HTMLElement | null;
      if (!target) return;
      const ids = target.getAttribute("data-comment-ids")?.split(" ") ?? [];
      if (ids.length) onSpanClick(ids);
    };
    root.addEventListener("click", handler);
    return () => root.removeEventListener("click", handler);
  }, [onSpanClick]);

  return (
    <div
      ref={containerRef}
      className="prose prose-stone max-w-none prose-headings:scroll-mt-20 prose-pre:rounded-md"
    >
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkBreaks]}
        rehypePlugins={rehypePlugins as never}
      >
        {source}
      </ReactMarkdown>
    </div>
  );
}

function makeRange(
  container: HTMLElement,
  startOffset: number,
  endOffset: number,
): Range | null {
  const spans = container.querySelectorAll<HTMLElement>(
    "span.mdr-text[data-src-start]",
  );
  let startNode: Text | null = null;
  let startWithin = 0;
  let endNode: Text | null = null;
  let endWithin = 0;
  for (const span of spans) {
    const sStart = Number(span.getAttribute("data-src-start"));
    const sEnd = Number(span.getAttribute("data-src-end"));
    if (!Number.isFinite(sStart) || !Number.isFinite(sEnd)) continue;
    const child = span.firstChild;
    if (!child || child.nodeType !== Node.TEXT_NODE) continue;
    const textLen = child.textContent?.length ?? 0;
    if (startNode == null && startOffset >= sStart && startOffset <= sEnd) {
      startNode = child as Text;
      startWithin = Math.min(textLen, Math.max(0, startOffset - sStart));
    }
    if (endOffset >= sStart && endOffset <= sEnd) {
      endNode = child as Text;
      endWithin = Math.min(textLen, Math.max(0, endOffset - sStart));
    }
  }
  if (!startNode || !endNode) return null;
  const range = document.createRange();
  try {
    range.setStart(startNode, startWithin);
    range.setEnd(endNode, endWithin);
  } catch {
    return null;
  }
  if (range.collapsed) return null;
  return range;
}
