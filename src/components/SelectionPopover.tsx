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

  const top = sel.rect.top + window.scrollY - 40;
  const left = sel.rect.left + window.scrollX + sel.rect.width / 2 - 60;

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
      className="absolute z-30 inline-flex items-center gap-1.5 rounded-md bg-stone-900 text-white text-xs font-medium px-2.5 py-1.5 shadow-lg hover:bg-stone-800"
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
