import ClaudeMark from "./ClaudeMark";
import type { DocSummary } from "../types";

interface Props {
  docs: DocSummary[];
  activeSlug: string | null;
  onSelect: (slug: string) => void;
  onNew: () => void;
  onPasteReplace: () => void;
  onExport: () => void;
  onDelete: (slug: string) => void;
  width?: number;
}

export default function Sidebar({
  docs,
  activeSlug,
  onSelect,
  onNew,
  onPasteReplace,
  onExport,
  onDelete,
  width,
}: Props) {
  return (
    <aside
      className="shrink-0 border-r border-stone-200 bg-white flex flex-col"
      style={{ width: width ?? 256 }}
    >
      <div className="px-4 py-3 border-b border-stone-200">
        <h1 className="font-semibold text-stone-900">Markdown Reviewer</h1>
        <p className="text-xs text-stone-500 mt-0.5">
          Local-only · {docs.length} doc{docs.length === 1 ? "" : "s"}
        </p>
      </div>

      <div className="px-3 py-2 flex flex-col gap-1 border-b border-stone-200">
        <button
          type="button"
          onClick={onNew}
          className="w-full rounded-md bg-stone-900 px-3 py-1.5 text-white text-left text-sm hover:bg-stone-800"
        >
          + New from paste
        </button>
        <button
          type="button"
          onClick={onPasteReplace}
          disabled={activeSlug == null}
          className="w-full rounded-md border border-stone-300 px-3 py-1.5 text-stone-700 text-left text-sm hover:bg-stone-100 disabled:opacity-40"
        >
          Replace current with paste
        </button>
        <button
          type="button"
          onClick={onExport}
          disabled={activeSlug == null}
          className="w-full rounded-md border border-stone-300 px-3 py-1.5 text-stone-700 text-left text-sm hover:bg-stone-100 disabled:opacity-40"
        >
          Export current
        </button>
      </div>

      <ul className="flex-1 overflow-y-auto py-2">
        {docs.length === 0 && (
          <li className="px-4 py-2 text-sm text-stone-500">
            Nothing yet. Paste a plan above or push one with{" "}
            <code className="text-xs">mdr push file.md</code>.
          </li>
        )}
        {docs.map((d) => {
          const isActive = d.slug === activeSlug;
          const total =
            d.openComments + d.resolvedComments + d.orphanedComments;
          return (
            <li key={d.slug} className="px-2">
              <div
                className={
                  "group flex items-start gap-2 rounded-md px-2 py-1.5 cursor-pointer " +
                  (isActive ? "bg-stone-200/70" : "hover:bg-stone-100")
                }
                onClick={() => onSelect(d.slug)}
              >
                <div className="flex-1 min-w-0">
                  <div className="truncate font-medium text-stone-900">
                    {d.title || d.slug || "Untitled"}
                  </div>
                  <div className="text-xs text-stone-500 mt-0.5 flex items-center gap-1.5">
                    <span>
                      {total} comment{total === 1 ? "" : "s"}
                    </span>
                    {d.openComments > 0 && (
                      <span className="inline-flex items-center rounded-full bg-amber-100 text-amber-800 px-1.5 py-0.5 text-[10px] font-semibold">
                        {d.openComments} open
                      </span>
                    )}
                    {d.orphanedComments > 0 && (
                      <span className="inline-flex items-center rounded-full bg-red-100 text-red-700 px-1.5 py-0.5 text-[10px] font-semibold">
                        {d.orphanedComments} orphan
                      </span>
                    )}
                    {d.lastEditor === "claude" && (
                      <span
                        className="inline-flex items-center justify-center w-4 h-4 rounded-full border border-stone-300 bg-white overflow-hidden"
                        title="Last edited by Claude"
                      >
                        <ClaudeMark size={12} />
                      </span>
                    )}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(d.slug);
                  }}
                  className="opacity-0 group-hover:opacity-100 text-stone-400 hover:text-red-600 px-1"
                  title="Delete"
                  aria-label={`Delete ${d.title}`}
                >
                  ✕
                </button>
              </div>
            </li>
          );
        })}
      </ul>
    </aside>
  );
}
