import { useCallback, useRef, useState } from "react";
import { nanoid } from "nanoid";
import MarkdownRenderer from "./MarkdownRenderer";
import SelectionPopover from "./SelectionPopover";
import CommentRail from "./CommentRail";
import type { Comment, FullDoc } from "../types";
import type { SelectionResult } from "../lib/selection";

interface Props {
  doc: FullDoc;
  onChangeComments: (
    updater: (cs: Comment[]) => Comment[],
  ) => void | Promise<void>;
}

export default function DocumentView({ doc, onChangeComments }: Props) {
  const comments = doc.comments;
  const renderRef = useRef<HTMLDivElement>(null);
  const [activeCommentId, setActiveCommentId] = useState<string | null>(null);
  const [pendingFocusId, setPendingFocusId] = useState<string | null>(null);

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

  return (
    <div className="flex-1 flex min-w-0">
      <section className="flex-1 min-w-0 overflow-y-auto relative">
        <div className="px-10 py-8 max-w-3xl mx-auto" ref={renderRef}>
          <header className="mb-6 pb-4 border-b border-stone-200">
            <h1 className="text-xs uppercase tracking-wider text-stone-500 font-semibold">
              Document
            </h1>
            <p className="text-stone-900 font-semibold text-base mt-0.5">
              {doc.title}
            </p>
          </header>

          <MarkdownRenderer
            source={doc.body}
            comments={comments}
            activeCommentId={activeCommentId}
            onSpanClick={handleSpanClick}
          />
        </div>

        <SelectionPopover
          containerRef={renderRef}
          source={doc.body}
          onComment={handleNewComment}
        />
      </section>

      <CommentRail
        doc={doc}
        comments={comments}
        activeCommentId={activeCommentId}
        pendingFocusId={pendingFocusId}
        onClearPendingFocus={() => setPendingFocusId(null)}
        onActivate={setActiveCommentId}
        onChangeComments={onChangeComments}
      />
    </div>
  );
}
