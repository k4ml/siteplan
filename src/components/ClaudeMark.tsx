import logo from "../assets/claude-mark.png";

interface Props {
  className?: string;
  size?: number;
}

export default function ClaudeMark({ className, size = 16 }: Props) {
  return (
    <img
      src={logo}
      alt="Claude"
      width={size}
      height={size}
      className={className}
      draggable={false}
    />
  );
}
