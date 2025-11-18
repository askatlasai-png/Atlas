export function Button({ className = "", variant = "default", ...props }) {
  const base = "rounded-lg border px-3 py-2 text-sm font-medium transition";
  const variants = {
    default: "bg-blue-600 text-white hover:bg-blue-700 border-blue-700",
    secondary: "bg-zinc-100 text-zinc-900 border-zinc-300 hover:bg-zinc-200",
    ghost: "bg-transparent text-zinc-700 border-transparent hover:bg-zinc-100",
  };
  return <button className={`${base} ${variants[variant] || ""} ${className}`} {...props} />;
}
