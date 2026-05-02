import { useEffect, useRef, useState } from "react";
import { nanoid } from "nanoid";
import { formatDistanceToNow } from "date-fns";
import type { Author, Comment, FullDoc } from "../types";

interface Props {
  doc: FullDoc;
  comment: Comment;
  isActive: boolean;
  autoFocus: boolean;
  onActivate: () => void;
  onClearAutoFocus: () => void;
  onChange: (updater: (c: Comment) => Comment) => void;
  onDelete: () => void;
}

export default function CommentThread({
  doc: _doc,
  comment,
  isActive,
  autoFocus,
  onActivate,
  onClearAutoFocus,
  onChange,
  onDelete,
}: Props) {
  const [draft, setDraft] = useState("");
  const [author, setAuthor] = useState<Author>("Me");
  const [collapsed, setCollapsed] = useState(comment.status === "resolved");
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (autoFocus) {
      setCollapsed(false);
      inputRef.current?.focus();
      onClearAutoFocus();
    }
  }, [autoFocus, onClearAutoFocus]);

  const submit = () => {
    const text = draft.trim();
    if (!text) return;
    onChange((c) => ({
      ...c,
      messages: [
        ...c.messages,
        {
          id: nanoid(),
          author,
          text,
          createdAt: new Date().toISOString(),
        },
      ],
      updatedAt: new Date().toISOString(),
    }));
    setDraft("");
  };

  const toggleResolved = () => {
    onChange((c) => ({
      ...c,
      status: c.status === "resolved" ? "open" : "resolved",
      updatedAt: new Date().toISOString(),
    }));
  };

  const isResolved = comment.status === "resolved";
  const isOrphan = comment.status === "orphaned";

  return (
    <div
      data-thread-id={comment.id}
      onClick={onActivate}
      className={
        "rounded-md border bg-white shadow-sm transition " +
        (isActive ? "border-amber-500 ring-2 ring-amber-200" : "border-stone-200") +
        (isResolved && collapsed ? " opacity-70" : "")
      }
    >
      <div className="flex items-center justify-between px-3 py-2 border-b border-stone-100 text-xs text-stone-500">
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            if (isResolved) setCollapsed((v) => !v);
          }}
          className="font-mono hover:text-stone-700"
          title={`${comment.anchor.startLine}/${comment.anchor.startCol}:${comment.anchor.endLine}/${comment.anchor.endCol}`}
        >
          {comment.anchor.startLine}/{comment.anchor.startCol}
          :{comment.anchor.endLine}/{comment.anchor.endCol}
        </button>
        <div className="flex items-center gap-2">
          {isOrphan && (
            <span className="px-1.5 py-0.5 rounded-full bg-red-100 text-red-700 font-semibold">
              orphaned
            </span>
          )}
          {isResolved && (
            <span className="px-1.5 py-0.5 rounded-full bg-green-100 text-green-700 font-semibold">
              resolved
            </span>
          )}
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              if (confirm("Delete this comment thread?")) onDelete();
            }}
            className="text-stone-400 hover:text-red-600"
            aria-label="Delete thread"
          >
            ✕
          </button>
        </div>
      </div>

      {comment.anchor.snippet && (
        <div
          className={
            "px-3 pt-2 text-xs italic " +
            (isOrphan ? "text-red-700" : "text-stone-500")
          }
        >
          “{comment.anchor.snippet}”
        </div>
      )}

      {!(isResolved && collapsed) && (
        <>
          <div className="px-3 py-2 space-y-2">
            {comment.messages.length === 0 && (
              <div className="text-xs text-stone-400 italic">No messages yet.</div>
            )}
            {comment.messages.map((m) => (
              <div key={m.id} className="flex gap-2">
                <Avatar author={m.author} />
                <div className="min-w-0 flex-1">
                  <div className="text-xs text-stone-500">
                    <span className="font-semibold text-stone-700">{m.author}</span>
                    <span className="ml-1.5">
                      {formatDistanceToNow(new Date(m.createdAt), {
                        addSuffix: true,
                      })}
                    </span>
                  </div>
                  <div className="text-sm text-stone-800 whitespace-pre-wrap break-words mt-0.5">
                    {m.text}
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="px-3 pb-3">
            <div className="flex items-center gap-1.5 mb-1.5">
              <AuthorToggle author={author} onChange={setAuthor} />
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleResolved();
                }}
                className={
                  "ml-auto text-xs rounded-md px-2 py-1 border " +
                  (isResolved
                    ? "bg-stone-100 text-stone-700 border-stone-300 hover:bg-stone-200"
                    : "bg-green-50 text-green-700 border-green-200 hover:bg-green-100")
                }
              >
                {isResolved ? "Reopen" : "Resolve"}
              </button>
            </div>
            <textarea
              ref={inputRef}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => {
                if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
                  e.preventDefault();
                  submit();
                }
              }}
              placeholder={
                isResolved
                  ? "Add a follow-up note…"
                  : `Reply as ${author}… (⌘↩ to send)`
              }
              rows={2}
              className="w-full resize-y rounded-md border border-stone-300 px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent"
            />
            <div className="flex justify-end mt-1.5">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  submit();
                }}
                disabled={!draft.trim()}
                className="rounded-md bg-stone-900 text-white text-xs font-medium px-2.5 py-1.5 disabled:opacity-40 hover:bg-stone-800"
              >
                Send
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function Avatar({ author }: { author: Author }) {
  const isMe = author === "Me";
  return (
    <div
      className={
        "shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-semibold " +
        (isMe ? "bg-amber-500 text-white" : "bg-violet-500 text-white")
      }
      title={author}
    >
      {isMe ? "M" : "C"}
    </div>
  );
}

function AuthorToggle({
  author,
  onChange,
}: {
  author: Author;
  onChange: (a: Author) => void;
}) {
  return (
    <div className="inline-flex rounded-md border border-stone-300 text-xs overflow-hidden">
      {(["Me", "Claude"] as Author[]).map((a) => (
        <button
          key={a}
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            onChange(a);
          }}
          className={
            "px-2 py-1 " +
            (a === author
              ? "bg-stone-900 text-white"
              : "bg-white text-stone-600 hover:bg-stone-100")
          }
        >
          {a}
        </button>
      ))}
    </div>
  );
}
