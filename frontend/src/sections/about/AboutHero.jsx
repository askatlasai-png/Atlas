import React from "react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";

export default function AboutHero() {
  return (
    <Card className="rounded-2xl bg-white/90 backdrop-blur shadow-xl ring-1 ring-blue-100/70">
      <CardHeader>
        <div className="flex items-center gap-2">
          <img
            src="/logos/atlas-mark-dark-bg.png"
            alt="Atlas Logo"
            className="h-6 w-6 object-contain opacity-90 drop-shadow-[0_1px_2px_rgba(0,0,0,0.25)]"
            style={{ marginTop: "-2px" }}
          />
          <CardTitle>About Atlas</CardTitle>
        </div>
        <CardDescription>
          AI built for your business — born in supply chain, now adaptable to any industry.
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-6">
        <h2 className="text-3xl md:text-[2.2rem] font-display font-semibold leading-tight tracking-tight text-slate-900">
          Make complex operational data{" "}
          <span className="bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 bg-clip-text text-transparent font-semibold">
            instantly conversational
          </span>
          .
        </h2>

        {/* Three short cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <div className="rounded-xl bg-white/70 ring-1 ring-slate-200 p-4 text-sm leading-relaxed text-slate-700 shadow-sm">
            <p className="font-medium text-slate-900">Talk to your business data.</p>
            <p className="mt-2">
              Ask about purchase orders, sales, inventory, or suppliers in plain English —
              Atlas responds with real numbers and context.
            </p>
          </div>

          <div className="rounded-xl bg-white/70 ring-1 ring-slate-200 p-4 text-sm leading-relaxed text-slate-700 shadow-sm">
            <p className="font-medium text-slate-900">No more screen-hopping.</p>
            <p className="mt-2">
              Instead of jumping across ERP screens and dashboards, you ask one place and
              get a clear answer you can act on.
            </p>
          </div>

          <div className="rounded-xl bg-white/70 ring-1 ring-slate-200 p-4 text-sm leading-relaxed text-slate-700 shadow-sm">
            <p className="font-medium text-slate-900">Built for real operations.</p>
            <p className="mt-2">
              Designed for planners, buyers, and ops leads who need to know what’s
              happening, why, and what to do next.
            </p>
          </div>
        </div>

        {/* Simple 3-bullet proof line */}
        <ul className="mt-2 space-y-2 text-sm text-slate-600">
          <li>
            ✅ <span className="font-medium text-slate-800">Grounded in your data</span> —
            not demo numbers.
          </li>
          <li>
            ✅ <span className="font-medium text-slate-800">Understands operations</span> —
            orders, stock, suppliers, and risk.
          </li>
          <li>
            ✅ <span className="font-medium text-slate-800">Plain-English answers</span> —
            no dashboards, reports, or SQL needed.
          </li>
        </ul>
      </CardContent>
    </Card>
  );
}
