import { useEffect, useMemo, useRef, useState } from "react";
import CommentThread from "./CommentThread";
import type { Comment, CommentStatus, FullDoc } from "../types";

const FILTER_KEY = "mdr:commentFilter";
const ALL_STATUSES: CommentStatus[] = [
  "open",
  "resolved",
  "applied",
  "orphaned",
];
type FilterTab = "all" | CommentStatus;
const ALL_TABS: FilterTab[] = ["all", ...ALL_STATUSES];

function loadTab(): FilterTab {
  const stored = localStorage.getItem(FILTER_KEY);
  if (stored && (ALL_TABS as string[]).includes(stored)) {
    return stored as FilterTab;
  }
  return "all";
}

const TAB_LABEL: Record<FilterTab, string> = {
  all: "All",
  open: "Open",
  resolved: "Resolved",
  applied: "Applied",
  orphaned: "Orphaned",
};

const PILL_BASE =
  "text-[10px] uppercase tracking-wide font-semibold px-2 py-0.5 rounded-full border transition";
const PILL_ACTIVE = "bg-amber-100 text-amber-900 border-amber-300";
const PILL_INACTIVE =
  "bg-white text-stone-500 border-stone-200 hover:bg-stone-100";

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
  const [tab, setTab] = useState<FilterTab>(loadTab);
  useEffect(() => {
    localStorage.setItem(FILTER_KEY, tab);
  }, [tab]);

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

  const visible_threads = useMemo(
    () => (tab === "all" ? sorted : sorted.filter((c) => c.status === tab)),
    [sorted, tab],
  );

  const counts = useMemo(() => {
    const out: Record<CommentStatus, number> = {
      open: 0,
      resolved: 0,
      applied: 0,
      orphaned: 0,
    };
    for (const c of comments) out[c.status]++;
    return out;
  }, [comments]);

  const orphanCount = counts.orphaned;
  const hiddenCount = comments.length - visible_threads.length;

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
              {counts.open} open · {comments.length} total
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

      <div
        role="tablist"
        className="px-3 py-2 flex flex-wrap gap-1 border-b border-stone-200"
      >
        {ALL_TABS.map((t) => {
          const active = tab === t;
          const count = t === "all" ? comments.length : counts[t];
          return (
            <button
              key={t}
              role="tab"
              aria-selected={active}
              type="button"
              onClick={() => setTab(t)}
              className={
                PILL_BASE + " " + (active ? PILL_ACTIVE : PILL_INACTIVE)
              }
              title={`Show ${TAB_LABEL[t].toLowerCase()}`}
            >
              {TAB_LABEL[t]}{" "}
              <span className="ml-0.5 font-mono opacity-80">{count}</span>
            </button>
          );
        })}
      </div>

      <div ref={railRef} className="flex-1 overflow-y-auto px-3 py-3 space-y-2">
        {visible_threads.length === 0 && (
          <div className="text-sm text-stone-500 px-1 py-4">
            {comments.length === 0 ? (
              <>
                Highlight any text in the document and click <em>Comment</em>{" "}
                to start a thread.
              </>
            ) : (
              <>
                No {TAB_LABEL[tab].toLowerCase()} threads
                {hiddenCount > 0
                  ? ` — ${hiddenCount} hidden by the filter above.`
                  : "."}
              </>
            )}
          </div>
        )}
        {visible_threads.map((c) => (
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
