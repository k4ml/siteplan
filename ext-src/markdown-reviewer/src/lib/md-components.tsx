import type { Components } from "react-markdown";

/**
 * Shared component overrides for ReactMarkdown. External links open in a
 * new tab; intra-doc heading anchors (#fragment) keep their default
 * same-tab navigation so deep-linking still works.
 */
export const mdComponents: Components = {
  a({ href, children, ...rest }) {
    const isExternal = !!href && !href.startsWith("#");
    return (
      <a
        href={href}
        target={isExternal ? "_blank" : undefined}
        rel={isExternal ? "noopener noreferrer" : undefined}
        {...rest}
      >
        {children}
      </a>
    );
  },
};
