import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { nanoid } from "nanoid";
import MarkdownRenderer from "./MarkdownRenderer";
import SelectionPopover from "./SelectionPopover";
import CommentRail from "./CommentRail";
import Properties from "./Properties";
import Resizer from "./Resizer";
import { extractFrontmatter } from "../lib/frontmatter";
import type { Comment, FullDoc } from "../types";
import type { SelectionResult } from "../lib/selection";

interface Props {
  doc: FullDoc;
  onChangeComments: (
    updater: (cs: Comment[]) => Comment[],
  ) => void | Promise<void>;
  sidebarHidden: boolean;
  onToggleSidebar: () => void;
}

const RAIL_KEY = "mdr:railWidth";
const RAIL_VISIBLE_KEY = "mdr:railVisible";
const VIEW_MODE_KEY = "mdr:viewMode";
const RAIL_MIN = 280;
const RAIL_MAX = 800;
const RAIL_DEFAULT = 320;

type ViewMode = "rendered" | "raw";

function clampRail(n: number): number {
  return Math.max(RAIL_MIN, Math.min(RAIL_MAX, n));
}

export default function DocumentView({
  doc,
  onChangeComments,
  sidebarHidden,
  onToggleSidebar,
}: Props) {
  const comments = doc.comments;
  const renderRef = useRef<HTMLDivElement>(null);
  const [activeCommentId, setActiveCommentId] = useState<string | null>(null);
  const [pendingFocusId, setPendingFocusId] = useState<string | null>(null);

  const [railWidth, setRailWidth] = useState<number>(() => {
    const stored = Number(localStorage.getItem(RAIL_KEY));
    return Number.isFinite(stored) && stored > 0 ? clampRail(stored) : RAIL_DEFAULT;
  });
  const [railVisible, setRailVisible] = useState<boolean>(() => {
    return localStorage.getItem(RAIL_VISIBLE_KEY) !== "0";
  });
  const [viewMode, setViewMode] = useState<ViewMode>(() => {
    const v = localStorage.getItem(VIEW_MODE_KEY);
    return v === "raw" ? "raw" : "rendered";
  });

  useEffect(() => {
    localStorage.setItem(RAIL_KEY, String(railWidth));
  }, [railWidth]);
  useEffect(() => {
    localStorage.setItem(RAIL_VISIBLE_KEY, railVisible ? "1" : "0");
  }, [railVisible]);
  useEffect(() => {
    localStorage.setItem(VIEW_MODE_KEY, viewMode);
  }, [viewMode]);

  const resetRail = useCallback(() => setRailWidth(RAIL_DEFAULT), []);
  const toggleRail = useCallback(() => setRailVisible((v) => !v), []);

  const handleNewComment = useCallback(
    (sel: SelectionResult) => {
      const now = new Date().toISOString();
      const id = nanoid();
      const fresh: Comment = {
        id,
        docId: doc.id,
        anchor: sel.anchor,
        status: "open",
        messages: [],
        createdAt: now,
        updatedAt: now,
      };
      onChangeComments((cs) => [...cs, fresh]);
      setActiveCommentId(id);
      setPendingFocusId(id);
    },
    [doc.id, onChangeComments],
  );

  const handleSpanClick = useCallback((ids: string[]) => {
    if (ids.length === 0) return;
    setActiveCommentId(ids[0]);
  }, []);

  const frontmatter = useMemo(() => extractFrontmatter(doc.body), [doc.body]);

  return (
    <div className="flex-1 flex min-w-0">
      <section className="flex-1 min-w-0 flex flex-col relative">
        <Toolbar
          sidebarHidden={sidebarHidden}
          railHidden={!railVisible}
          viewMode={viewMode}
          onToggleSidebar={onToggleSidebar}
          onToggleRail={toggleRail}
          onSetViewMode={setViewMode}
          title={doc.title}
        />
        <div className="flex-1 min-h-0 overflow-y-auto">
          <div className="px-10 py-8 max-w-3xl mx-auto" ref={renderRef}>
            {viewMode === "rendered" ? (
              <>
                {frontmatter && <Properties frontmatter={frontmatter} />}
                <MarkdownRenderer
                  source={doc.body}
                  comments={comments}
                  activeCommentId={activeCommentId}
                  onSpanClick={handleSpanClick}
                />
              </>
            ) : (
              <RawView source={doc.body} />
            )}
          </div>
        </div>

        {viewMode === "rendered" && (
          <SelectionPopover
            containerRef={renderRef}
            source={doc.body}
            onComment={handleNewComment}
          />
        )}
      </section>

      {railVisible && (
        <>
          <Resizer
            side="right"
            width={railWidth}
            min={RAIL_MIN}
            max={RAIL_MAX}
            onResize={setRailWidth}
            onReset={resetRail}
          />
          <CommentRail
            doc={doc}
            comments={comments}
            activeCommentId={activeCommentId}
            pendingFocusId={pendingFocusId}
            onClearPendingFocus={() => setPendingFocusId(null)}
            onActivate={setActiveCommentId}
            onChangeComments={onChangeComments}
            width={railWidth}
          />
        </>
      )}
    </div>
  );
}

interface ToolbarProps {
  sidebarHidden: boolean;
  railHidden: boolean;
  viewMode: ViewMode;
  onToggleSidebar: () => void;
  onToggleRail: () => void;
  onSetViewMode: (m: ViewMode) => void;
  title: string;
}

function Toolbar({
  sidebarHidden,
  railHidden,
  viewMode,
  onToggleSidebar,
  onToggleRail,
  onSetViewMode,
  title,
}: ToolbarProps) {
  return (
    <header className="shrink-0 flex items-center gap-2 px-3 py-2 border-b border-stone-200 bg-white/70 backdrop-blur sticky top-0 z-10">
      <IconBtn
        title={sidebarHidden ? "Show document list" : "Hide document list"}
        onClick={onToggleSidebar}
      >
        {sidebarHidden ? "›" : "‹"}
        <span className="sr-only">Toggle sidebar</span>
      </IconBtn>

      <div className="flex-1 min-w-0 px-2">
        <div className="text-[10px] uppercase tracking-wider text-stone-500 font-semibold">
          Document
        </div>
        <div className="text-sm font-semibold text-stone-900 truncate">
          {title}
        </div>
      </div>

      <div className="inline-flex rounded-md border border-stone-300 text-xs overflow-hidden">
        {(["rendered", "raw"] as const).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => onSetViewMode(m)}
            className={
              "px-2.5 py-1 " +
              (m === viewMode
                ? "bg-stone-900 text-white"
                : "bg-white text-stone-600 hover:bg-stone-100")
            }
          >
            {m === "rendered" ? "Rendered" : "Raw"}
          </button>
        ))}
      </div>

      <IconBtn
        title={railHidden ? "Show comments" : "Hide comments"}
        onClick={onToggleRail}
      >
        {railHidden ? "‹" : "›"}
        <span className="sr-only">Toggle comments</span>
      </IconBtn>
    </header>
  );
}

function IconBtn({
  children,
  onClick,
  title,
}: {
  children: React.ReactNode;
  onClick: () => void;
  title: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      title={title}
      className="shrink-0 inline-flex items-center justify-center w-7 h-7 rounded-md text-stone-600 hover:bg-stone-100 hover:text-stone-900 text-base leading-none"
    >
      {children}
    </button>
  );
}

function RawView({ source }: { source: string }) {
  return (
    <pre className="whitespace-pre-wrap break-words font-mono text-[12.5px] leading-relaxed text-stone-800 bg-stone-50 border border-stone-200 rounded-md p-4">
      {source}
    </pre>
  );
}
