import type { Comment, Doc } from "../types";
import { COMMENT_SENTINEL, COMMENT_SEPARATOR } from "./prompt";

function statusLabel(status: Comment["status"]): "RESOLVED" | "UNRESOLVED" {
  return status === "resolved" ? "RESOLVED" : "UNRESOLVED";
}

function serializeOne(c: Comment): string {
  const { anchor } = c;
  const header = `${anchor.startLine}/${anchor.startCol}:${anchor.endLine}/${anchor.endCol}: ${statusLabel(c.status)}`;
  const messages = c.messages
    .map((m) => `${m.author}: ${m.text}`)
    .join("\n\n");
  return messages ? `${header}\n\n${messages}` : header;
}

export function serializeDocWithComments(doc: Doc, comments: Comment[]): string {
  const body = doc.body.replace(/\s+$/, "");
  if (comments.length === 0) {
    return body + "\n";
  }
  const sorted = [...comments].sort((a, b) => {
    if (a.anchor.startLine !== b.anchor.startLine) {
      return a.anchor.startLine - b.anchor.startLine;
    }
    return a.anchor.startCol - b.anchor.startCol;
  });
  const blocks = sorted
    .map(serializeOne)
    .join(`\n\n${COMMENT_SEPARATOR}\n\n`);
  return [
    body,
    "",
    COMMENT_SENTINEL,
    "",
    blocks,
    "",
    COMMENT_SEPARATOR,
    "",
  ].join("\n");
}
