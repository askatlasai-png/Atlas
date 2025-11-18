// ---------- TechStack.jsx (compact layout version) ----------
// Same seamless logo style, but denser layout + tighter padding and spacing.

import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import * as SI from "simple-icons/icons";

const techMap = {
  React: { si: SI.siReact },
  Vite: { si: SI.siVite },
  "Tailwind CSS": { si: SI.siTailwindcss },
  "Framer Motion": { si: SI.siFramer },
  "shadcn/ui": { si: null, local: "/logos/shadcn.svg" },
  "lucide-react": { si: null, local: "/logos/lucide.svg" },
  Python: { si: SI.siPython },
  LangChain: { si: null, local: "/logos/langchain.svg" },
  "OpenAI API": { si: SI.siOpenai },
  FAISS: { si: null, local: "/logos/faiss.svg" },
  Pandas: { si: SI.siPandas },
  "Node.js": { si: SI.siNodedotjs },
  PostgreSQL: { si: SI.siPostgresql },
  "AWS S3": { si: null, local: "/logos/s3.svg" },
  "AWS Lambda": { si: null, local: "/logos/lambda.svg" },
  RDS: { si: null, local: "/logos/rds.svg" },
  CloudFront: { si: null, local: "/logos/cloudfront.svg" },
  WAF: { si: null, local: "/logos/waf.svg" },
  ALB: { si: null, local: "/logos/alb.svg" },
};

const groups = [
  { label: "Frontend", items: ["React", "Vite", "Tailwind CSS", "Framer Motion", "shadcn/ui", "lucide-react"] },
  { label: "Backend / AI Layer", items: ["Python", "LangChain", "OpenAI API", "FAISS", "Pandas", "Node.js"] },
  { label: "Infrastructure", items: ["PostgreSQL", "AWS S3", "AWS Lambda", "RDS", "CloudFront", "WAF", "ALB"] },
];

function BrandIcon({ name }) {
  const m = techMap[name] || {};

  if (m.local) {
    return (
      <img
        src={m.local}
        alt={name}
        className="h-6 w-6 object-contain opacity-80 transition-all hover:opacity-100"
        onError={(e) => {
          e.currentTarget.style.display = "none";
          const span = document.createElement("span");
          span.className = "text-[10px] font-medium text-slate-700";
          span.textContent = name;
          e.currentTarget.parentElement?.appendChild(span);
        }}
      />
    );
  }

  const si = m.si;
  if (si && si.svg) {
    return (
      <div
        role="img"
        aria-label={name}
        dangerouslySetInnerHTML={{ __html: si.svg }}
        className="h-6 w-6 opacity-80 transition-all grayscale hover:grayscale-0 hover:opacity-100 [&_svg]:h-6 [&_svg]:w-6 [&_path]:fill-current"
        style={{ color: `#${si.hex || "111827"}` }}
      />
    );
  }

  return <span className="text-[10px] font-medium text-slate-700">{name}</span>;
}

function LogoBadge({ name }) {
  return (
    <div className="group flex flex-col items-center gap-1 p-1 rounded-md hover:scale-[1.02] transition-transform">
      <BrandIcon name={name} />
      <span className="text-[10px] text-slate-700 text-center leading-tight">{name}</span>
    </div>
  );
}

export default function TechStack() {
  return (
    <Card className="rounded-2xl bg-white/90 backdrop-blur shadow-lg ring-1 ring-blue-100/70">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg text-slate-900">Tech Stack</CardTitle>
        <CardDescription className="text-sm text-slate-600">
          Frameworks and infrastructure behind Atlas.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {groups.map((g) => (
          <section key={g.label} className="space-y-1">
            <div className="text-[13px] font-semibold text-slate-700">{g.label}:</div>
            <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 lg:grid-cols-8 gap-x-4 gap-y-3">
              {g.items.map((n) => (
                <LogoBadge key={n} name={n} />
              ))}
            </div>
          </section>
        ))}
      </CardContent>
    </Card>
  );
}
