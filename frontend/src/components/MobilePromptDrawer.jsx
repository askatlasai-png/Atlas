// MobilePromptDrawer.jsx
import React, { useState, useEffect } from "react";
import { X } from "lucide-react";

/* --- Same prompt data as PersonaRailFloating --- */
const PROMPTS = {
  "Procurement & Purchase Orders": {
    icon: "📦",
    desc: "Monitor inbound POs, supplier receipts, and pricing exceptions.",
    prompts: [
      "What's the status and expected receipt date for PO-0000155?",
      "Which buyer is responsible for PO-0000118?",
      "For PO-0000165, show any items still pending receipt.",
      "Which suppliers have the highest number of overdue purchase orders?",
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
      "Which items have zero or negative available stock?",
      "Show SKUs where received quantity exceeded ordered quantity.",
    ],
  },
  "Sales Orders & Outbound (LPN Focus)": {
    icon: "🚚",
    desc: "Manage outbound shipments, LPN tracking, and carrier handoffs.",
    prompts: [
      "For SO-0000093, show its line items, quantities, and current status.",
      "What is the tracking number associated to SO-0000011?",
      "What are all the sales order that are cut for ITEM-0024",
      "What products and quantities are included in the sales order shipped under tracking number 1Z107618644626284?",
    ],
  },
  "Analytics & Exceptions": {
    icon: "📊",
    desc: "Analyze performance metrics, SLA breaches, and daily trends.",
    prompts: [
      "Show any inbound POs past SLA or at risk.",
      "Which carriers have the highest percentage of late shipments?",
    ],
  },
};

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

export default function MobilePromptDrawer({ isOpen, onClose, onSelectPrompt }) {
  const groups = Object.keys(PROMPTS);
  const [active, setActive] = useState(groups[0]);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsAnimating(true);
      // Prevent body scroll when drawer is open
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isOpen]);

  const handleSelectPrompt = (prompt) => {
    onSelectPrompt?.(prompt);
    onClose?.();
  };

  const handleClose = () => {
    setIsAnimating(false);
    setTimeout(() => onClose?.(), 300); // Wait for animation
  };

  if (!isOpen && !isAnimating) return null;

  return (
    <>
      {/* Backdrop overlay */}
      <div
        className={`fixed inset-0 z-[9998] bg-slate-900/40 backdrop-blur-sm transition-opacity duration-300 ${
          isAnimating ? "opacity-100" : "opacity-0"
        }`}
        onClick={handleClose}
      />

      {/* Bottom sheet drawer */}
      <div
        className={`fixed bottom-0 left-0 right-0 z-[9999] bg-white rounded-t-3xl shadow-2xl transition-transform duration-300 ease-out ${
          isAnimating ? "translate-y-0" : "translate-y-full"
        }`}
        style={{ maxHeight: "80vh" }}
      >
        {/* Handle bar (swipe indicator) */}
        <div className="flex justify-center pt-2 pb-1">
          <div className="w-12 h-1 rounded-full bg-slate-300" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 flex items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 text-white text-sm font-semibold">
              💡
            </div>
            <div className="leading-tight">
              <div className="text-sm font-semibold text-slate-900">Sample Questions</div>
              <div className="text-xs text-slate-500">Tap to try</div>
            </div>
          </div>
          <button
            onClick={handleClose}
            className="h-8 w-8 flex items-center justify-center rounded-full hover:bg-slate-100 active:bg-slate-200 transition-colors"
            aria-label="Close"
          >
            <X className="h-5 w-5 text-slate-600" />
          </button>
        </div>

        {/* Tabs */}
        <div className="sticky top-0 z-10 bg-white border-b border-slate-200">
          <div
            className="flex items-center gap-2 overflow-x-auto px-3 py-2 scrollbar-hide"
            style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
          >
            {groups.map((g) => (
              <button
                key={g}
                onClick={() => setActive(g)}
                className={[
                  "shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition border whitespace-nowrap",
                  active === g
                    ? `text-white border-transparent bg-gradient-to-r ${TAB_COLORS[g].active} shadow-sm`
                    : `${TAB_COLORS[g].idle} hover:bg-white`,
                ].join(" ")}
              >
                {PROMPTS[g].icon} {g.split(" ")[0]}
              </button>
            ))}
          </div>
        </div>

        {/* Scrollable prompt list */}
        <div className="overflow-y-auto px-4 py-3" style={{ maxHeight: "calc(80vh - 140px)" }}>
          {(() => {
            const meta = PROMPTS[active];
            
            // Determine gradient based on active category (matching desktop)
            const gradientMap = {
              "Procurement & Purchase Orders": "from-blue-50 to-cyan-100",
              "Inventory & Stock Management": "from-teal-50 to-emerald-100",
              "Sales Orders & Outbound (LPN Focus)": "from-sky-50 to-cyan-100",
              "Analytics & Exceptions": "from-indigo-50 to-blue-100",
            };
            
            const categoryGradient = gradientMap[active] || "from-slate-50 to-slate-100";
            
            return (
              <div className="space-y-2">
                {/* Category description */}
                <div className="flex items-start gap-2 mb-3">
                  <div className="h-8 w-8 flex items-center justify-center rounded-lg bg-slate-100 text-lg">
                    {meta.icon}
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-slate-900">{active}</div>
                    <div className="text-xs text-slate-600 mt-0.5">{meta.desc}</div>
                  </div>
                </div>

                {/* Prompt buttons */}
                {meta.prompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSelectPrompt(prompt)}
                    className={`w-full text-left rounded-xl border border-slate-200 bg-gradient-to-r ${categoryGradient} hover:from-white hover:to-slate-50 active:bg-slate-100 transition-all p-3 group shadow-sm`}
                    style={{
                      opacity: 0.6 + idx * 0.1,
                    }}
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-slate-500 group-hover:text-slate-700 text-xs font-medium mt-0.5 shrink-0">
                        {idx + 1}
                      </span>
                      <span className="text-sm text-slate-700 group-hover:text-slate-900 leading-relaxed flex-1">
                        {prompt}
                      </span>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        className="h-4 w-4 text-slate-400 group-hover:text-slate-600 shrink-0 mt-0.5"
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 5l7 7-7 7"
                        />
                      </svg>
                    </div>
                    <div className="text-[11px] text-slate-500 mt-1.5 ml-5">Tap to ask Atlas</div>
                  </button>
                ))}
              </div>
            );
          })()}
        </div>
      </div>
    </>
  );
}
