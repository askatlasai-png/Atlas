// ---------- KeyFeatures.jsx ----------
import React from "react";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Bot, FileSearch, TrendingUp } from "lucide-react";


export default function KeyFeatures() {
const items = [
{
icon: Bot,
title: "RAG-driven answers",
desc: "Multi-source retrieval over ERP tables, reports, and files—grounded with citations and example queries.",
},
{
icon: FileSearch,
title: "ERP-aware reasoning",
desc: "Understands POs, SOs, LPNs, on-hand, and reqs with domain heuristics and guardrails for safer outputs.",
},
{
icon: TrendingUp,
title: "Operations acceleration",
desc: "Cut time-to-answer for planners and buyers; reduce clicks, training effort, and context switching.",
},
];


return (
<section className="grid gap-4 md:grid-cols-3">
{items.map((item) => (
<Card key={item.title} className="rounded-2xl bg-white/90 backdrop-blur shadow ring-1 ring-blue-100/70">
<CardHeader className="pb-2">
<div className="flex items-center gap-2">
<item.icon className="h-5 w-5 text-slate-800" />
<CardTitle className="text-base text-slate-900">{item.title}</CardTitle>
</div>
<CardDescription className="pt-1 text-slate-600">{item.desc}</CardDescription>
</CardHeader>
</Card>
))}
</section>
);
}