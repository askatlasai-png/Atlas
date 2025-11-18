import React from "react";
import { Truck, PackageSearch, AlertTriangle } from "lucide-react";

export default function SupplyChainDeepDive() {
  return (
    <section id="supply-chain" className="space-y-8 scroll-mt-24">
      {/* Header block – perfectly matched to Everyday Businesses */}
      <div className="text-center space-y-3">
        <div className="text-xs font-medium uppercase tracking-wide text-blue-700">
          Atlas for Supply Chain
        </div>

        <h2 className="mt-2 text-2xl font-semibold text-slate-900 leading-snug">
          Atlas for supply chain operations.
        </h2>

        <p className="text-slate-600 text-base max-w-3xl mx-auto leading-relaxed">
          End-to-end visibility for planners, buyers, and logistics — see what’s
          happening, why it’s happening, and what to do next.
        </p>
      </div>

      {/* Row of capability cards */}
      <div className="grid gap-4 md:grid-cols-3">
        {/* Inventory & availability */}
        <div className="rounded-xl bg-white/90 backdrop-blur shadow ring-1 ring-slate-200 p-5">
          <div className="text-[11px] font-medium text-emerald-700 bg-emerald-50 ring-1 ring-emerald-200 inline-block px-2 py-1 rounded-md">
            “Do we have stock to cover this order?”
          </div>

          <div className="flex items-start gap-2 mt-3">
            <PackageSearch className="h-5 w-5 text-slate-800 shrink-0" />
            <p className="font-semibold text-slate-900 text-base leading-snug">
              Inventory &amp; availability
            </p>
          </div>

          <p className="mt-2 text-sm text-slate-600 leading-relaxed">
            Atlas can answer across on-hand, on-order, in-transit, and
            allocations — instantly — without digging through ERP screens
            or waiting on a planner to build a spreadsheet.
          </p>
        </div>

        {/* Inbound & supplier performance */}
        <div className="rounded-xl bg-white/90 backdrop-blur shadow ring-1 ring-slate-200 p-5">
          <div className="text-[11px] font-medium text-blue-700 bg-blue-50 ring-1 ring-blue-200 inline-block px-2 py-1 rounded-md">
            “What’s running late and who’s causing it?”
          </div>

          <div className="flex items-start gap-2 mt-3">
            <Truck className="h-5 w-5 text-slate-800 shrink-0" />
            <p className="font-semibold text-slate-900 text-base leading-snug">
              Inbound &amp; supplier performance
            </p>
          </div>

          <p className="mt-2 text-sm text-slate-600 leading-relaxed">
            Atlas surfaces delayed POs, slipping suppliers, and at-risk
            inbound shipments — and gives you a clean summary you can
            drop straight into an escalation email or a standup.
          </p>
        </div>

        {/* Risk & next steps */}
        <div className="rounded-xl bg-white/90 backdrop-blur shadow ring-1 ring-slate-200 p-5">
          <div className="text-[11px] font-medium text-amber-700 bg-amber-50 ring-1 ring-amber-200 inline-block px-2 py-1 rounded-md">
            “Where are we about to get burned?”
          </div>

          <div className="flex items-start gap-2 mt-3">
            <AlertTriangle className="h-5 w-5 text-amber-600 shrink-0" />
            <p className="font-semibold text-slate-900 text-base leading-snug">
              Risk &amp; next steps
            </p>
          </div>

          <p className="mt-2 text-sm text-slate-600 leading-relaxed">
            Atlas flags shortages, expediting risk, missed ship commits,
            and customer-impacting issues — and tells planners and ops
            leads what needs attention now.
          </p>
        </div>
      </div>
    </section>
  );
}
