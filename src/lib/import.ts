import { nanoid } from "nanoid";
import type {
  Comment,
  CommentAnchor,
  CommentStatus,
  Message,
} from "../types";
import {
  buildLineStarts,
  lineColToOffset,
  offsetToLineCol,
  snippetFromSource,
} from "./positions";
import { COMMENT_SENTINEL, COMMENT_SEPARATOR } from "./prompt";

const HEADER_RE = /^(\d+)\/(\d+):(\d+)\/(\d+):\s*(UNRESOLVED|RESOLVED)\s*$/;
const MSG_PREFIX_RE = /^(Me|Claude):\s?(.*)$/;

export interface ImportResult {
  body: string;
  comments: Comment[];
  orphanedCount: number;
}

export function deriveTitle(body: string): string {
  for (const line of body.split("\n", 30)) {
    const m = /^#\s+(.*\S)\s*$/.exec(line);
    if (m) return m[1];
  }
  const first = body.split("\n").find((l) => l.trim());
  return first?.trim().slice(0, 60) || "Untitled";
}

export function parseImport(
  input: string,
  docId: string,
  existingComments: Comment[],
): ImportResult {
  const sentinelIdx = input.indexOf(COMMENT_SENTINEL);
  const body =
    sentinelIdx === -1
      ? input.replace(/\s+$/, "")
      : input.slice(0, sentinelIdx).replace(/\s+$/, "");
  const footer = sentinelIdx === -1 ? "" : input.slice(sentinelIdx + COMMENT_SENTINEL.length);

  const blocks = splitBlocks(footer);
  const lineStarts = buildLineStarts(body);

  const existingByCoords = new Map<string, Comment>();
  for (const c of existingComments) {
    existingByCoords.set(coordKey(c.anchor), c);
  }

  let orphaned = 0;
  const out: Comment[] = [];
  for (const block of blocks) {
    const parsed = parseBlock(block);
    if (!parsed) continue;

    const { rawAnchor, headerStatus, messages } = parsed;
    const existing = existingByCoords.get(coordKey(rawAnchor));
    const priorSnippet = existing?.anchor.snippet ?? "";
    let status: CommentStatus = headerStatus === "RESOLVED" ? "resolved" : "open";

    let anchor: CommentAnchor = { ...rawAnchor, snippet: "" };

    const startOff = lineColToOffset(rawAnchor.startLine, rawAnchor.startCol, lineStarts, body);
    const endOff = lineColToOffset(rawAnchor.endLine, rawAnchor.endCol, lineStarts, body);
    const sliceAtCoords = body.slice(startOff, endOff);

    if (priorSnippet && snippetMatches(sliceAtCoords, priorSnippet)) {
      anchor.snippet = priorSnippet;
    } else if (priorSnippet && !priorSnippet.endsWith("…")) {
      const occurrences = findAllOccurrences(body, priorSnippet, 3);
      if (occurrences.length === 1) {
        const foundStart = occurrences[0];
        const foundEnd = foundStart + priorSnippet.length;
        const sLC = offsetToLineCol(foundStart, lineStarts);
        const eLC = offsetToLineCol(foundEnd, lineStarts);
        anchor = {
          startLine: sLC.line,
          startCol: sLC.col,
          endLine: eLC.line,
          endCol: eLC.col,
          snippet: priorSnippet,
        };
      } else if (status !== "resolved") {
        status = "orphaned";
        orphaned++;
        anchor.snippet = priorSnippet;
      } else {
        anchor.snippet = priorSnippet;
      }
    } else if (priorSnippet) {
      // truncated snippet, can't reliably search — keep as-is and orphan if mismatch
      if (status !== "resolved") {
        status = "orphaned";
        orphaned++;
      }
      anchor.snippet = priorSnippet;
    } else {
      anchor.snippet = snippetFromSource(body, startOff, endOff);
    }

    const now = new Date().toISOString();
    out.push({
      id: existing?.id ?? nanoid(),
      docId,
      anchor,
      status,
      messages,
      createdAt: existing?.createdAt ?? now,
      updatedAt: now,
    });
  }

  return { body, comments: out, orphanedCount: orphaned };
}

function coordKey(a: { startLine: number; startCol: number; endLine: number; endCol: number }): string {
  return `${a.startLine}/${a.startCol}:${a.endLine}/${a.endCol}`;
}

function splitBlocks(footer: string): string[] {
  if (!footer.trim()) return [];
  const out: string[] = [];
  let buf: string[] = [];
  for (const line of footer.split("\n")) {
    if (line.trim() === COMMENT_SEPARATOR) {
      if (buf.some((l) => l.trim())) out.push(buf.join("\n"));
      buf = [];
    } else {
      buf.push(line);
    }
  }
  if (buf.some((l) => l.trim())) out.push(buf.join("\n"));
  return out;
}

interface ParsedBlock {
  rawAnchor: { startLine: number; startCol: number; endLine: number; endCol: number };
  headerStatus: "UNRESOLVED" | "RESOLVED";
  messages: Message[];
}

function parseBlock(block: string): ParsedBlock | null {
  const lines = block.split("\n");
  let i = 0;
  while (i < lines.length && lines[i].trim() === "") i++;
  if (i >= lines.length) return null;

  const headerMatch = HEADER_RE.exec(lines[i].trim());
  if (!headerMatch) return null;
  const [, sl, sc, el, ec, status] = headerMatch;
  i++;

  const messages: Message[] = [];
  let author: "Me" | "Claude" | null = null;
  let buf: string[] = [];
  const now = new Date().toISOString();

  const flush = () => {
    if (author && buf.length) {
      const text = buf.join("\n").trim();
      if (text) {
        messages.push({ id: nanoid(), author, text, createdAt: now });
      }
    }
    buf = [];
  };

  for (; i < lines.length; i++) {
    const line = lines[i];
    const m = MSG_PREFIX_RE.exec(line);
    if (m) {
      flush();
      author = m[1] as "Me" | "Claude";
      buf = [m[2]];
    } else if (author != null) {
      buf.push(line);
    }
  }
  flush();

  return {
    rawAnchor: {
      startLine: Number(sl),
      startCol: Number(sc),
      endLine: Number(el),
      endCol: Number(ec),
    },
    headerStatus: status as "UNRESOLVED" | "RESOLVED",
    messages,
  };
}

function snippetMatches(slice: string, snippet: string): boolean {
  if (snippet.endsWith("…")) {
    return slice.startsWith(snippet.slice(0, -1));
  }
  return slice === snippet;
}

function findAllOccurrences(haystack: string, needle: string, max: number): number[] {
  const out: number[] = [];
  let i = haystack.indexOf(needle);
  while (i !== -1 && out.length < max) {
    out.push(i);
    i = haystack.indexOf(needle, i + 1);
  }
  return out;
}
