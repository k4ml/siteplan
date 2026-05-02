import type { Frontmatter } from "../lib/frontmatter";

interface Props {
  frontmatter: Frontmatter;
}

export default function Properties({ frontmatter }: Props) {
  if (frontmatter.pairs.length === 0) return null;
  return (
    <div className="not-prose mb-6 rounded-md border border-stone-200 bg-stone-50">
      <div className="px-3 py-1.5 text-[10px] uppercase tracking-wider text-stone-500 font-semibold border-b border-stone-200">
        Properties
      </div>
      <dl className="grid grid-cols-[max-content_1fr] gap-x-4 gap-y-1 px-3 py-2 text-sm">
        {frontmatter.pairs.map((p) => (
          <div key={p.key} className="contents">
            <dt className="text-stone-500 font-medium">{p.key}</dt>
            <dd className="text-stone-800 font-mono text-xs leading-relaxed">
              {p.value}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}
