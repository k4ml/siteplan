import type { Plugin } from "vite";
import type { IncomingMessage, ServerResponse } from "node:http";
import { mkdir, readdir, readFile, writeFile, unlink } from "node:fs/promises";
import { existsSync } from "node:fs";
import { join } from "node:path";
import os from "node:os";
import { nanoid } from "nanoid";
import { parseImport, deriveTitle } from "./src/lib/import";
import { serializeDocWithComments } from "./src/lib/export";
import type { Comment, Editor, FullDoc, DocSummary } from "./src/types";

const DATA_DIR =
  process.env.MARKDOWN_REVIEWER_DATA_DIR ??
  join(os.homedir(), ".markdown-reviewer", "docs");

export function apiPlugin(): Plugin {
  const subscribers = new Set<ServerResponse>();
  let heartbeat: NodeJS.Timeout | null = null;

  const broadcast = (event: object) => {
    const payload = `data: ${JSON.stringify(event)}\n\n`;
    for (const res of subscribers) {
      try {
        res.write(payload);
      } catch {
        subscribers.delete(res);
      }
    }
  };

  return {
    name: "markdown-reviewer-api",
    async configureServer(server) {
      await mkdir(DATA_DIR, { recursive: true });

      heartbeat = setInterval(() => {
        for (const res of subscribers) {
          try {
            res.write(": ping\n\n");
          } catch {
            subscribers.delete(res);
          }
        }
      }, 25000);
      server.httpServer?.on("close", () => {
        if (heartbeat) clearInterval(heartbeat);
        for (const res of subscribers) res.end();
        subscribers.clear();
      });

      server.middlewares.use(async (req, res, next) => {
        if (!req.url?.startsWith("/api/")) return next();
        try {
          await route(req, res, subscribers, broadcast);
        } catch (err) {
          if (!res.headersSent) {
            res.statusCode = 500;
            res.setHeader("Content-Type", "application/json");
            res.end(JSON.stringify({ error: (err as Error).message }));
          } else {
            res.end();
          }
        }
      });
    },
  };
}

async function route(
  req: IncomingMessage,
  res: ServerResponse,
  subscribers: Set<ServerResponse>,
  broadcast: (event: object) => void,
): Promise<void> {
  const url = new URL(req.url!, "http://localhost");
  const segs = url.pathname.split("/").filter(Boolean);
  // segs: ["api", ...]
  if (segs[0] !== "api") return notFound(res);

  if (segs[1] === "events" && req.method === "GET") {
    return handleSSE(req, res, subscribers);
  }

  if (segs[1] === "docs") {
    if (segs.length === 2) {
      if (req.method === "GET") return handleList(res);
      if (req.method === "POST") return handleCreate(req, res, url, broadcast);
      return methodNotAllowed(res);
    }
    const slug = decodeURIComponent(segs[2]);
    if (segs.length === 3) {
      if (req.method === "GET") return handleGetDoc(slug, req, res);
      if (req.method === "PUT") return handlePutDoc(slug, req, res, broadcast);
      if (req.method === "PATCH")
        return handlePatchDoc(slug, req, res, broadcast);
      if (req.method === "DELETE")
        return handleDelete(slug, res, broadcast);
      return methodNotAllowed(res);
    }
    if (segs.length === 4 && segs[3] === "status" && req.method === "GET") {
      return handleStatus(slug, res);
    }
  }
  return notFound(res);
}

function notFound(res: ServerResponse) {
  res.statusCode = 404;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify({ error: "Not found" }));
}

function methodNotAllowed(res: ServerResponse) {
  res.statusCode = 405;
  res.end();
}

async function readBody(req: IncomingMessage): Promise<string> {
  const chunks: Buffer[] = [];
  for await (const c of req) chunks.push(c as Buffer);
  return Buffer.concat(chunks).toString("utf8");
}

function docPath(slug: string): string {
  return join(DATA_DIR, `${slug}.json`);
}

async function readDoc(slug: string): Promise<FullDoc | null> {
  const p = docPath(slug);
  if (!existsSync(p)) return null;
  return JSON.parse(await readFile(p, "utf8")) as FullDoc;
}

async function writeDoc(doc: FullDoc): Promise<void> {
  await writeFile(docPath(doc.slug), JSON.stringify(doc, null, 2), "utf8");
}

function summarize(doc: FullDoc): DocSummary {
  return {
    slug: doc.slug,
    title: doc.title,
    openComments: doc.comments.filter((c) => c.status === "open").length,
    resolvedComments: doc.comments.filter(
      (c) => c.status === "resolved" || c.status === "applied",
    ).length,
    orphanedComments: doc.comments.filter((c) => c.status === "orphaned").length,
    updatedAt: doc.updatedAt,
    lastEditor: doc.lastEditor,
  };
}

function slugify(input: string): string {
  return (
    input
      .toLowerCase()
      .normalize("NFKD")
      .replace(/[̀-ͯ]/g, "")
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-+|-+$/g, "")
      .slice(0, 64) || `doc-${nanoid(6)}`
  );
}

async function uniqueSlug(base: string): Promise<string> {
  let s = base;
  let i = 2;
  while (existsSync(docPath(s))) {
    s = `${base}-${i++}`;
  }
  return s;
}

function editorFromReq(req: IncomingMessage, fallback: Editor): Editor {
  const v = req.headers["x-md-reviewer-editor"];
  if (v === "me" || v === "claude") return v;
  return fallback;
}

async function handleSSE(
  req: IncomingMessage,
  res: ServerResponse,
  subs: Set<ServerResponse>,
): Promise<void> {
  res.writeHead(200, {
    "Content-Type": "text/event-stream",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
    "X-Accel-Buffering": "no",
  });
  res.write("retry: 5000\n\n");
  subs.add(res);
  req.on("close", () => subs.delete(res));
}

async function handleList(res: ServerResponse): Promise<void> {
  const files = await readdir(DATA_DIR).catch(() => []);
  const docs: DocSummary[] = [];
  for (const f of files) {
    if (!f.endsWith(".json")) continue;
    try {
      const doc = JSON.parse(await readFile(join(DATA_DIR, f), "utf8")) as FullDoc;
      docs.push(summarize(doc));
    } catch {
      // skip corrupted
    }
  }
  docs.sort((a, b) => b.updatedAt.localeCompare(a.updatedAt));
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(docs));
}

async function handleGetDoc(
  slug: string,
  req: IncomingMessage,
  res: ServerResponse,
): Promise<void> {
  const doc = await readDoc(slug);
  if (!doc) return notFound(res);
  const accept = req.headers.accept ?? "";
  if (accept.includes("application/json")) {
    res.setHeader("Content-Type", "application/json");
    res.end(JSON.stringify(doc));
  } else {
    res.setHeader("Content-Type", "text/markdown; charset=utf-8");
    res.setHeader("Last-Modified", new Date(doc.updatedAt).toUTCString());
    res.end(serializeDocWithComments(doc, doc.comments));
  }
}

async function handleStatus(slug: string, res: ServerResponse): Promise<void> {
  const doc = await readDoc(slug);
  if (!doc) return notFound(res);
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(summarize(doc)));
}

async function handleCreate(
  req: IncomingMessage,
  res: ServerResponse,
  url: URL,
  broadcast: (event: object) => void,
): Promise<void> {
  const text = await readBody(req);
  const editor = editorFromReq(req, "me");
  const id = nanoid();
  const tmpId = id; // doc id used during parse
  const { body, comments } = parseImport(text, tmpId, []);
  const title = deriveTitle(body);
  const requested = url.searchParams.get("slug");
  const slug = await uniqueSlug(requested ? slugify(requested) : slugify(title));
  const now = new Date().toISOString();
  const doc: FullDoc = {
    id,
    slug,
    title,
    body,
    comments,
    createdAt: now,
    updatedAt: now,
    lastEditor: editor,
  };
  await writeDoc(doc);
  broadcast({ type: "created", slug, updatedAt: now, lastEditor: editor });
  res.statusCode = 201;
  res.setHeader("Location", `/api/docs/${encodeURIComponent(slug)}`);
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(summarize(doc)));
}

async function handlePutDoc(
  slug: string,
  req: IncomingMessage,
  res: ServerResponse,
  broadcast: (event: object) => void,
): Promise<void> {
  const text = await readBody(req);
  const editor = editorFromReq(req, "claude");
  const ifUnmodifiedSince = req.headers["if-unmodified-since"];
  const existing = await readDoc(slug);

  if (existing && ifUnmodifiedSince && editor === "claude") {
    const since = new Date(ifUnmodifiedSince as string).getTime();
    const lastTouched = new Date(existing.updatedAt).getTime();
    if (
      Number.isFinite(since) &&
      existing.lastEditor === "me" &&
      lastTouched > since
    ) {
      res.statusCode = 409;
      res.setHeader("Content-Type", "text/markdown; charset=utf-8");
      res.setHeader("Last-Modified", new Date(existing.updatedAt).toUTCString());
      res.end(serializeDocWithComments(existing, existing.comments));
      return;
    }
  }

  const id = existing?.id ?? nanoid();
  const { body, comments } = parseImport(text, id, existing?.comments ?? []);
  const now = new Date().toISOString();
  const doc: FullDoc = {
    id,
    slug,
    title: deriveTitle(body),
    body,
    comments,
    createdAt: existing?.createdAt ?? now,
    updatedAt: now,
    lastEditor: editor,
  };
  await writeDoc(doc);
  broadcast({ type: "updated", slug, updatedAt: now, lastEditor: editor });

  res.statusCode = existing ? 200 : 201;
  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(summarize(doc)));
}

async function handlePatchDoc(
  slug: string,
  req: IncomingMessage,
  res: ServerResponse,
  broadcast: (event: object) => void,
): Promise<void> {
  const existing = await readDoc(slug);
  if (!existing) return notFound(res);
  const editor = editorFromReq(req, "me");
  const text = await readBody(req);
  let patch: { body?: string; comments?: Comment[]; title?: string };
  try {
    patch = JSON.parse(text);
  } catch {
    res.statusCode = 400;
    res.end(JSON.stringify({ error: "invalid JSON" }));
    return;
  }
  const now = new Date().toISOString();
  const body = patch.body ?? existing.body;
  const doc: FullDoc = {
    ...existing,
    body,
    title: patch.title ?? (patch.body ? deriveTitle(body) : existing.title),
    comments: patch.comments ?? existing.comments,
    updatedAt: now,
    lastEditor: editor,
  };
  await writeDoc(doc);
  broadcast({ type: "updated", slug, updatedAt: now, lastEditor: editor });

  res.setHeader("Content-Type", "application/json");
  res.end(JSON.stringify(doc));
}

async function handleDelete(
  slug: string,
  res: ServerResponse,
  broadcast: (event: object) => void,
): Promise<void> {
  const p = docPath(slug);
  if (!existsSync(p)) return notFound(res);
  await unlink(p);
  broadcast({ type: "deleted", slug, updatedAt: new Date().toISOString() });
  res.statusCode = 204;
  res.end();
}
