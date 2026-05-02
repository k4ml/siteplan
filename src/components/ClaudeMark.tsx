interface Props {
  className?: string;
  size?: number;
}

/**
 * Stylized Anthropic / Claude mark — four rounded petals arranged like an
 * asterisk. Approximation, not the official asset, but visually recognizable.
 */
export default function ClaudeMark({ className, size }: Props) {
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      className={className}
      fill="currentColor"
      aria-hidden="true"
    >
      <ellipse cx="12" cy="12" rx="2.6" ry="9.5" transform="rotate(45 12 12)" />
      <ellipse cx="12" cy="12" rx="2.6" ry="9.5" transform="rotate(-45 12 12)" />
    </svg>
  );
}
