export function Card({ className = "", ...props }) {
  return <div className={`rounded-2xl border bg-white ${className}`} {...props} />;
}
export function CardHeader({ className = "", ...props }) {
  return <div className={`p-4 ${className}`} {...props} />;
}
export function CardTitle({ className = "", ...props }) {
  return <div className={`font-semibold text-base ${className}`} {...props} />;
}
export function CardDescription({ className = "", ...props }) {
  return <div className={`text-sm text-zinc-600 ${className}`} {...props} />;
}
export function CardContent({ className = "", ...props }) {
  return <div className={`p-4 pt-0 ${className}`} {...props} />;
}
