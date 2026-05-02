import { useEffect, useState } from "react";
import { readSelection, type SelectionResult } from "../lib/selection";

interface Props {
  containerRef: React.RefObject<HTMLElement>;
  source: string;
  onComment: (sel: SelectionResult) => void;
}

export default function SelectionPopover({
  containerRef,
  source,
  onComment,
}: Props) {
  const [sel, setSel] = useState<SelectionResult | null>(null);

  useEffect(() => {
    const handler = () => {
      const container = containerRef.current;
      if (!container) {
        setSel(null);
        return;
      }
      // Defer a tick so the selection is settled.
      setTimeout(() => {
        const result = readSelection(container, source);
        setSel(result);
      }, 0);
    };
    document.addEventListener("selectionchange", handler);
    return () => document.removeEventListener("selectionchange", handler);
  }, [containerRef, source]);

  if (!sel) return null;

  // Position is viewport-relative because we use `position: fixed`; the
  // selection's bounding rect from getBoundingClientRect is already in
  // viewport coords, so no scroll math.
  const POPOVER_W = 110;
  const POPOVER_H = 32;
  const PAD = 8;
  const rawLeft = sel.rect.left + sel.rect.width / 2 - POPOVER_W / 2;
  const rawTop = sel.rect.top - POPOVER_H - 6;
  const left = Math.max(
    PAD,
    Math.min(window.innerWidth - POPOVER_W - PAD, rawLeft),
  );
  // If the selection is near the top, flip the popover below the selection.
  const top =
    rawTop < PAD ? sel.rect.bottom + 6 : rawTop;

  return (
    <button
      type="button"
      onMouseDown={(e) => {
        // Prevent the click from clearing the current selection before the
        // handler reads it.
        e.preventDefault();
      }}
      onClick={() => {
        onComment(sel);
        window.getSelection()?.removeAllRanges();
        setSel(null);
      }}
      className="fixed z-30 inline-flex items-center gap-1.5 rounded-md bg-stone-900 text-white text-xs font-medium px-2.5 py-1.5 shadow-lg hover:bg-stone-800"
      style={{ top, left }}
    >
      <svg
        viewBox="0 0 24 24"
        className="w-3.5 h-3.5"
        fill="none"
        stroke="currentColor"
        strokeWidth={2}
      >
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      Comment
    </button>
  );
}
