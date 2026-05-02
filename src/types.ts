export type Author = "Me" | "Claude";

export interface Message {
  id: string;
  author: Author;
  text: string;
  createdAt: string;
}

export interface CommentAnchor {
  startLine: number;
  startCol: number;
  endLine: number;
  endCol: number;
  snippet: string;
  /** Up to ~30 chars of source immediately before the snippet — used to
   * disambiguate when the snippet appears multiple times after edits. */
  contextBefore?: string;
  /** Up to ~30 chars of source immediately after the snippet. */
  contextAfter?: string;
}

export type CommentStatus = "open" | "resolved" | "orphaned" | "applied";

export interface Comment {
  id: string;
  docId: string;
  anchor: CommentAnchor;
  status: CommentStatus;
  messages: Message[];
  createdAt: string;
  updatedAt: string;
}

export interface Doc {
  id: string;
  slug: string;
  title: string;
  body: string;
  createdAt: string;
  updatedAt: string;
}

export type Editor = "me" | "claude";

export interface FullDoc extends Doc {
  comments: Comment[];
  lastEditor: Editor;
}

export interface DocSummary {
  slug: string;
  title: string;
  openComments: number;
  resolvedComments: number;
  orphanedComments: number;
  updatedAt: string;
  lastEditor: Editor;
}

export interface LineCol {
  line: number;
  col: number;
}
