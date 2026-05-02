import { useEffect, useMemo, useRef } from "react";
import CommentThread from "./CommentThread";
import type { Comment, FullDoc } from "../types";

interface Props {
  doc: FullDoc;
  comments: Comment[];
  activeCommentId: string | null;
  pendingFocusId: string | null;
  onClearPendingFocus: () => void;
  onActivate: (id: string) => void;
  onChangeComments: (
    updater: (cs: Comment[]) => Comment[],
  ) => void | Promise<void>;
  width?: number;
  visible: boolean;
  isDesktop: boolean;
  onClose: () => void;
}

export default function CommentRail({
  doc,
  comments,
  activeCommentId,
  pendingFocusId,
  onClearPendingFocus,
  onActivate,
  onChangeComments,
  width,
  visible,
  isDesktop,
  onClose,
}: Props) {
  if (isDesktop && !visible) return null;
  const sorted = useMemo(
    () =>
      [...comments].sort((a, b) => {
        if (a.anchor.startLine !== b.anchor.startLine) {
          return a.anchor.startLine - b.anchor.startLine;
        }
        return a.anchor.startCol - b.anchor.startCol;
      }),
    [comments],
  );

  const openCount = comments.filter((c) => c.status === "open").length;
  const orphanCount = comments.filter((c) => c.status === "orphaned").length;

  const railRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!activeCommentId) return;
    const el = railRef.current?.querySelector<HTMLElement>(
      `[data-thread-id="${activeCommentId}"]`,
    );
    el?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [activeCommentId]);

  return (
    <aside
      className={
        isDesktop
          ? "shrink-0 border-l border-stone-200 bg-stone-50 flex flex-col h-full"
          : `fixed inset-y-0 right-0 z-40 w-[90vw] max-w-md bg-stone-50 border-l border-stone-200 flex flex-col shadow-xl transition-transform duration-200 ${
              visible ? "translate-x-0" : "translate-x-full"
            }`
      }
      style={isDesktop ? { width: width ?? 320 } : undefined}
    >
      <div className="px-4 py-3 border-b border-stone-200 flex items-start justify-between gap-2">
        <div>
          <div className="flex items-baseline gap-3">
            <h2 className="font-semibold text-stone-900">Comments</h2>
            <span className="text-xs text-stone-500">
              {openCount} open · {comments.length} total
            </span>
          </div>
          {orphanCount > 0 && (
            <div className="mt-1 text-xs text-red-700">
              {orphanCount} orphaned — original text not found
            </div>
          )}
        </div>
        {!isDesktop && (
          <button
            type="button"
            onClick={onClose}
            aria-label="Close comments"
            className="w-10 h-10 rounded-md flex items-center justify-center text-stone-500 hover:bg-stone-100 -mr-2 -mt-1"
          >
            ✕
          </button>
        )}
      </div>

      <div ref={railRef} className="flex-1 overflow-y-auto px-3 py-3 space-y-2">
        {sorted.length === 0 && (
          <div className="text-sm text-stone-500 px-1 py-4">
            Highlight any text in the document and click <em>Comment</em> to
            start a thread.
          </div>
        )}
        {sorted.map((c) => (
          <CommentThread
            key={c.id}
            doc={doc}
            comment={c}
            isActive={c.id === activeCommentId}
            autoFocus={c.id === pendingFocusId}
            onActivate={() => onActivate(c.id)}
            onClearAutoFocus={() => {
              if (c.id === pendingFocusId) onClearPendingFocus();
            }}
            onChange={(updater) =>
              onChangeComments((cs) =>
                cs.map((x) => (x.id === c.id ? updater(x) : x)),
              )
            }
            onDelete={() =>
              onChangeComments((cs) => cs.filter((x) => x.id !== c.id))
            }
          />
        ))}
      </div>
    </aside>
  );
}
