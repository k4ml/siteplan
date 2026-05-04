import { useMemo, useState } from "react";
import type { Comment, FullDoc } from "../types";
import { serializeDocWithComments } from "../lib/export";
import { AI_PROMPT } from "../lib/prompt";

interface Props {
  doc: FullDoc;
  comments: Comment[];
  onClose: () => void;
}

export default function ExportModal({ doc, comments, onClose }: Props) {
  const exported = useMemo(
    () => serializeDocWithComments(doc, comments),
    [doc, comments],
  );
  const withPrompt = useMemo(() => AI_PROMPT + exported, [exported]);
  const [copied, setCopied] = useState<"none" | "doc" | "prompt">("none");

  const copy = async (text: string, kind: "doc" | "prompt") => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(kind);
      setTimeout(() => setCopied("none"), 1500);
    } catch {
      // ignore — user can still select the textarea content manually
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 bg-stone-900/40 flex md:items-center md:justify-center md:p-4"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="bg-white shadow-xl w-full md:rounded-lg md:max-w-3xl h-full md:h-auto md:max-h-[85vh] flex flex-col">
        <div className="px-5 py-3 border-b border-stone-200 flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-stone-900">Export with comments</h2>
            <p className="text-xs text-stone-500 mt-0.5">
              Doc body + a comment footer block. Round-trips back via Replace
              current with paste.
            </p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-stone-400 hover:text-stone-700"
          >
            ✕
          </button>
        </div>

        <textarea
          readOnly
          value={exported}
          className="flex-1 m-5 mb-0 resize-none rounded-md border border-stone-300 px-3 py-2 font-mono text-xs min-h-[40vh]"
        />

        <div className="px-5 py-3 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={() => copy(exported, "doc")}
            className="rounded-md border border-stone-300 px-3 py-1.5 text-stone-700 hover:bg-stone-100"
          >
            {copied === "doc" ? "Copied!" : "Copy doc"}
          </button>
          <button
            type="button"
            onClick={() => copy(withPrompt, "prompt")}
            className="rounded-md bg-stone-900 text-white px-3 py-1.5 hover:bg-stone-800"
          >
            {copied === "prompt" ? "Copied!" : "Copy AI prompt + doc"}
          </button>
        </div>
      </div>
    </div>
  );
}
