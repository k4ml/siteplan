import { useEffect, useRef, useState } from "react";

interface Props {
  mode: "create" | "replace";
  docTitle?: string;
  onSubmit: (input: string) => void;
  onCancel: () => void;
}

export default function PasteModal({
  mode,
  docTitle,
  onSubmit,
  onCancel,
}: Props) {
  const [input, setInput] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    ref.current?.focus();
  }, []);

  return (
    <Overlay onClose={onCancel}>
      <div className="bg-white shadow-xl w-full md:rounded-lg md:max-w-3xl h-full md:h-auto md:max-h-[85vh] flex flex-col">
        <div className="px-5 py-3 border-b border-stone-200 flex items-center justify-between">
          <div>
            <h2 className="font-semibold text-stone-900">
              {mode === "create" ? "Paste a new markdown plan" : "Replace current document"}
            </h2>
            {mode === "replace" && docTitle && (
              <p className="text-xs text-stone-500 mt-0.5">
                Replacing: {docTitle}. Existing comments will be re-anchored where possible.
              </p>
            )}
          </div>
          <button
            type="button"
            onClick={onCancel}
            className="text-stone-400 hover:text-stone-700"
          >
            ✕
          </button>
        </div>

        <textarea
          ref={ref}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Paste markdown here. If the text contains the comment footer block, it will be parsed back into threads."
          className="flex-1 m-5 mb-0 resize-none rounded-md border border-stone-300 px-3 py-2 font-mono text-xs focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-transparent min-h-[40vh]"
        />

        <div className="px-5 py-3 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-md px-3 py-1.5 text-stone-700 hover:bg-stone-100"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={() => onSubmit(input)}
            disabled={!input.trim()}
            className="rounded-md bg-stone-900 text-white px-3 py-1.5 disabled:opacity-40 hover:bg-stone-800"
          >
            {mode === "create" ? "Create document" : "Replace"}
          </button>
        </div>
      </div>
    </Overlay>
  );
}

function Overlay({
  children,
  onClose,
}: {
  children: React.ReactNode;
  onClose: () => void;
}) {
  return (
    <div
      className="fixed inset-0 z-50 bg-stone-900/40 flex md:items-center md:justify-center md:p-4"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      {children}
    </div>
  );
}
