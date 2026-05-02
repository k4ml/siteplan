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
}

export type CommentStatus = "open" | "resolved" | "orphaned";

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
