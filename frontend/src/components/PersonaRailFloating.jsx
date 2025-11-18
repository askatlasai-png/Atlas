// PersonaRailFloating.jsx
import React, { useState } from "react";

/* --- Persona prompt data --- */
const PROMPTS = {
  "Procurement & Purchase Orders": {
    icon: "📦",
    desc: "Monitor inbound POs, supplier receipts, and pricing exceptions.",
    prompts: [
      "What’s the status and expected receipt date for PO-0000155?",
      "Which buyer is responsible for PO-0000118? ",
      "For PO-0000165, show any items still pending receipt.",
      "Which suppliers have the highest number of overdue purchase orders? .",
      "List Purchase orders that were received after their promised delivery date",
    ],
  },
  "Inventory & Stock Management": {
    icon: "🏬",
    desc: "Track stock levels, reserved quantities, and replenishment triggers.",
    prompts: [
      "Show on-hand vs reserved quantity for ITEM-00047.",
      "Compare available quantities for the ITEM-00033 across all warehouses.",
      "List top 10 SKUs by available quantity.",
      "Which items have zero or negative available stock? ",
      "Show SKUs where received quantity exceeded ordered quantity.",
    ],
  },
  "Sales Orders & Outbound (LPN Focus)": {
    icon: "🚚",
    desc: "Manage outbound shipments, LPN tracking, and carrier handoffs.",
    prompts: [
      "For SO-0000093, show its line items, quantities, and current status.",
      "What is the tracking number associated to SO-0000011 ? ",
      "What are all the sales order that are cut for ITEM-0024 ",
      "What products and quantities are included in the sales order shipped under tracking number 1Z107618644626284?",
    ],
  },
  "Analytics & Exceptions": {
    icon: "📊",
    desc: "Analyze performance metrics, SLA breaches, and daily trends.",
    prompts: [
      "Show any inbound POs past SLA or at risk.",
      "Which carriers have the highest percentage of late shipments?.",
    ],
  },
};

const personaMap = {
  "Procurement & Purchase Orders": { label: "Procurement Manager", dot: "bg-blue-500" },
  "Inventory & Stock Management": { label: "Inventory Controller", dot: "bg-teal-500" },
  "Sales Orders & Outbound (LPN Focus)": { label: "Fulfillment Lead", dot: "bg-cyan-500" },
  "Analytics & Exceptions": { label: "Operations Analyst", dot: "bg-indigo-600" },
};

/* --- Atlas-theme tab colors --- */
const TAB_COLORS = {
  "Procurement & Purchase Orders": {
    active: "from-blue-600 to-cyan-500",
    idle: "text-blue-700 border-blue-200 bg-blue-50",
  },
  "Inventory & Stock Management": {
    active: "from-teal-600 to-emerald-500",
    idle: "text-teal-700 border-teal-200 bg-teal-50",
  },
  "Sales Orders & Outbound (LPN Focus)": {
    active: "from-sky-600 to-cyan-500",
    idle: "text-sky-700 border-sky-200 bg-sky-50",
  },
  "Analytics & Exceptions": {
    active: "from-indigo-600 to-blue-600",
    idle: "text-indigo-700 border-indigo-200 bg-indigo-50",
  },
};

export default function PersonaRailFloating({ onSelectPrompt }) {
  const groups = Object.keys(PROMPTS);
  const [active, setActive] = useState(groups[0]);
  const handleSelect = (p) => onSelectPrompt?.(p);

  return (
    <aside
      className="
        h-full w-full
        rounded-2xl border border-zinc-200/70
        bg-white/80 backdrop-blur
        shadow-[0_6px_18px_rgba(2,8,23,0.06)]
        flex flex-col
        overflow-hidden overflow-x-hidden
        text-slate-800
        min-w-0
      "
    >
      {/* Header */}
      <div className="px-3 py-2.5 border-b border-zinc-200/70 bg-white/70">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 flex items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 text-white text-[11px] font-semibold">
            ✳
          </div>
          <div className="leading-tight">
            <div className="text-[13px] font-semibold">Personas &amp; Sample Prompts</div>
            <div className="text-[11px] text-slate-500">Click a prompt to prefill Atlas.</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="sticky top-0 z-10 bg-white/90 backdrop-blur border-b border-slate-200">
        <div
          className="flex items-center gap-1.5 overflow-x-auto px-2 py-1 whitespace-nowrap"
          style={{ scrollbarWidth: "none" }}
        >
          {groups.map((g) => (
            <button
              key={g}
              onClick={() => setActive(g)}
              title={g}
              className={[
                "shrink-0 rounded-full px-3 py-1.5 text-[12px] transition border",
                active === g
                  ? `text-white border-transparent bg-gradient-to-r ${TAB_COLORS[g].active} shadow-sm shadow-[0_0_6px_rgba(59,130,246,0.25)]`
                  : `${TAB_COLORS[g].idle} hover:bg-white`,
              ].join(" ")}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      {/* Body */}
      <div className="flex-1 min-h-0 overflow-y-auto p-3">
        {(() => {
          const group = active;
          const meta = PROMPTS[group];
          const persona = personaMap[group];

          // gradient bar color based on persona
          const underlineGradient =
            persona.label === "Procurement Manager"
              ? "from-blue-500 to-cyan-400"
              : persona.label === "Inventory Controller"
              ? "from-teal-500 to-emerald-400"
              : persona.label === "Fulfillment Lead"
              ? "from-sky-500 to-cyan-400"
              : "from-indigo-500 to-blue-400";

          return (
            <div className="rounded-2xl border border-zinc-200 bg-white/90 shadow-sm p-3">
              {/* Sub-header */}
              <div className="flex items-start gap-2">
                <div className="h-6 w-6 flex items-center justify-center rounded-md bg-zinc-100 text-[13px]">
                  {meta.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap relative">
                    <div className="text-[13px] font-semibold relative pb-1">
                      {persona.label}
                      <div
                        className={`absolute left-0 bottom-0 h-[2px] w-full bg-gradient-to-r ${underlineGradient} rounded-full`}
                      />
                    </div>
                    <span className="inline-flex items-center gap-1 text-[10px] font-medium rounded-full bg-zinc-100 text-slate-700 px-1.5 py-[2px] leading-none">
                      <span className={`h-1.5 w-1.5 rounded-full ${persona.dot}`} />
                      Persona
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-500 leading-snug mt-1">
                    {meta.desc}
                  </div>
                </div>
              </div>

              {/* Prompts */}
              <div className="mt-3 space-y-2.5">
                {meta.prompts.map((prompt, i) => (
                  <div
                    key={i}
                    className={`
                      group relative rounded-xl border border-zinc-200
                      shadow-[0_1px_0_rgba(2,8,23,0.04)] transition
                      bg-gradient-to-r
                      ${persona.label === "Procurement Manager" ? "from-blue-50 to-cyan-100" : ""}
                      ${persona.label === "Inventory Controller" ? "from-teal-50 to-emerald-100" : ""}
                      ${persona.label === "Fulfillment Lead" ? "from-sky-50 to-cyan-100" : ""}
                      ${persona.label === "Operations Analyst" ? "from-indigo-50 to-blue-100" : ""}
                      hover:from-white hover:to-zinc-50
                    `}
                    style={{
                      opacity: 0.6 + i * 0.1,
                      transition: "opacity 0.3s ease",
                    }}
                  >
                    <button
                      type="button"
                      onClick={() => handleSelect(prompt)}
                      className="block w-full text-left px-3 py-3 text-[13px] text-slate-800 transition-colors"
                    >
                      {prompt}
                      <div className="mt-1.5 text-[11px] text-slate-500">Click to copy & prefill</div>
                    </button>

                    {/* Copy icon */}
                    <button
                      type="button"
                      onClick={() => {
                        navigator.clipboard?.writeText(prompt);
                        handleSelect(prompt);
                      }}
                      title="Copy & prefill"
                      className="
                        absolute right-2 top-2
                        inline-flex h-6 w-6 items-center justify-center
                        rounded-md border border-zinc-200 bg-white text-slate-500
                        hover:bg-white/90 hover:border-blue-200 hover:text-blue-700
                        shadow-sm
                      "
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4">
                        <path d="M6 2.75A2.75 2.75 0 0 1 8.75 0h5.5A2.75 2.75 0 0 1 17 2.75v5.5A2.75 2.75 0 0 1 14.25 11h-5.5A2.75 2.75 0 0 1 6 8.25v-5.5Z" />
                        <path d="M3.5 6.5A2.5 2.5 0 0 1 6 4h.25v4.25A3.75 3.75 0 0 0 10 12h4a2.5 2.5 0 0 1-2.5 2.5h-5A2.5 2.5 0 0 1 4 12v-5Z" />
                      </svg>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          );
        })()}
      </div>
    </aside>
  );
}
