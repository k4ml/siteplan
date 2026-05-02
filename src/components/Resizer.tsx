import { useCallback, useState } from "react";

interface Props {
  /**
   * "left"  — the resized panel is on the left of this divider; dragging right widens it.
   * "right" — the resized panel is on the right of this divider; dragging left widens it.
   */
  side: "left" | "right";
  width: number;
  min: number;
  max: number;
  onResize: (w: number) => void;
  onReset?: () => void;
}

export default function Resizer({
  side,
  width,
  min,
  max,
  onResize,
  onReset,
}: Props) {
  const [isResizing, setIsResizing] = useState(false);

  const startResize = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      const startX = e.clientX;
      const startWidth = width;
      setIsResizing(true);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
      const clamp = (n: number) => Math.max(min, Math.min(max, n));
      const onMove = (ev: MouseEvent) => {
        const dx = ev.clientX - startX;
        const next = side === "right" ? startWidth - dx : startWidth + dx;
        onResize(clamp(next));
      };
      const onUp = () => {
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
        setIsResizing(false);
      };
      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup", onUp);
    },
    [width, side, min, max, onResize],
  );

  return (
    <div
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize panel"
      onMouseDown={startResize}
      onDoubleClick={onReset}
      title={
        onReset
          ? "Drag to resize · double-click to reset"
          : "Drag to resize"
      }
      className={
        "shrink-0 w-1.5 cursor-col-resize transition-colors " +
        (isResizing ? "bg-amber-400" : "bg-stone-200 hover:bg-amber-300")
      }
    />
  );
}
