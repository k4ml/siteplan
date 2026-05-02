export const COMMENT_SENTINEL =
  "--- THIS IS A COMMENT FROM MARKDOWN REVIEWER, DO NOT MODIFY ---";

export const COMMENT_SEPARATOR = "-----";

export const AI_PROMPT = `You are reviewing a markdown document with reader comments appended in a footer section. The footer starts with the line:

${COMMENT_SENTINEL}

Each comment block in the footer follows this exact format:

<startLine>/<startCol>:<endLine>/<endCol>: <UNRESOLVED|RESOLVED>

Me: <reader's comment>

(any additional Me: or Claude: lines, separated by blank lines)

${COMMENT_SEPARATOR}

Workflow you must follow, in order:

1. First, address every UNRESOLVED comment. For each one, choose ONE of:
   a) Reply by appending a new line "Claude: <your reply>" (separated from the previous message by a blank line) to that comment's block. Keep its status as UNRESOLVED so the reader can respond.
   b) Apply the requested change to the document body, then update the comment's header status from UNRESOLVED to RESOLVED. Do not delete the comment block.
2. Only after every UNRESOLVED comment has either received a Claude: reply or been RESOLVED, you may make additional edits to the document body.
3. Preserve the comment footer format exactly: keep the sentinel line, keep the line/col headers, keep the ${COMMENT_SEPARATOR} separators, keep all existing Me: and Claude: lines intact.
4. Return the full document as a single markdown blob: the body first, then a blank line, then the sentinel, then the comment blocks. Do not wrap the response in code fences.

Below is the document with its comment footer:

`;
