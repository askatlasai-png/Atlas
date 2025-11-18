import React from "react";
import { Database, ArrowUpRight, Eye, EyeOff } from "lucide-react";

export default function DatasetRailFloating({
  onOpenDatasets,
  debugContext,
  showDebug,
  onToggleDebug,
}) {
  return (
    <aside
      className="
        flex flex-col
        w-full min-w-0 max-h-[75vh]
        rounded-2xl bg-white/90 backdrop-blur
        ring-1 ring-blue-100/70 shadow-xl
        p-3
      "
    >
      {/* Clickable header block */}
      <button
        type="button"
        onClick={onOpenDatasets}
        className={`
          w-full
          flex items-start gap-3 justify-between
          rounded-xl
          p-2
          border border-slate-300/70 bg-white
          shadow-sm
          text-left
          cursor-pointer
          transition
          hover:bg-slate-50/80 hover:border-slate-400 hover:shadow
          active:bg-slate-100 active:border-slate-500
          focus:outline-none
        `}
      >
        {/* Left: icon + text */}
        <div className="flex items-start gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white text-blue-700 ring-1 ring-blue-200 shadow-sm">
            <Database className="h-4 w-4" />
          </div>

          <div className="flex flex-col leading-tight text-slate-800">
            <div className="font-semibold text-slate-900 text-[14px] leading-snug flex items-start gap-1">
              <span>Data Sources in this Demo</span>
            </div>

            <div className="mt-1 text-[11px] font-medium text-slate-500 leading-none">
              View data sources
            </div>
          </div>
        </div>

        {/* Arrow indicator on the far right */}
        <div className="pt-1 text-slate-400">
          <ArrowUpRight className="h-4 w-4" />
        </div>
      </button>

      {/* Body copy */}
      <div className="mt-4 text-[12px] leading-relaxed text-slate-700">
        Atlas is grounded in your operational ERP data — purchase orders,
        inventory, deliveries, and shipments.
        <br />
        <br />
        Tap “Data Sources in this Demo” above to explore those tables, search
        live rows, and copy IDs (PO numbers, SO numbers, LPNs, SKUs) directly
        into chat.
      </div>

      {/* Footer line above debug toggle */}
      <div className="mt-4 text-[11px] leading-snug text-slate-400">
        All answers are grounded in your ERP system.
      </div>

      {/* Toggle button for retrieval context */}
      <div className="mt-4">
        <button
          type="button"
          onClick={onToggleDebug}
          className={`
            inline-flex items-center gap-1.5
            rounded-md border border-slate-300 bg-white
            px-2.5 py-1.5 text-[11px] font-medium text-slate-700
            shadow-sm hover:bg-slate-50 active:bg-slate-100
            w-full justify-center
          `}
        >
          {showDebug ? (
            <>
              <EyeOff className="h-3.5 w-3.5 text-slate-500" />
              <span>Hide context</span>
            </>
          ) : (
            <>
              <Eye className="h-3.5 w-3.5 text-slate-500" />
              <span>Show context used by Atlas</span>
            </>
          )}
        </button>
      </div>

      {/* Retrieval / context debug panel (collapsible) */}
      {showDebug && (
        <div
          className="
            mt-4 flex-1 min-h-0 overflow-y-auto
            rounded-lg border border-slate-300 bg-slate-50/60
            text-[11px] text-slate-700 font-mono leading-snug
            shadow-inner
          "
          style={{
            maxHeight: "160px",
          }}
        >
          <div className="px-3 py-2 border-b border-slate-300/60 bg-slate-100 text-[10px] font-semibold text-slate-600 uppercase tracking-wide">
            Most Recent Retrieval
          </div>

          <pre className="px-3 py-2 whitespace-pre-wrap break-words">
            {debugContext
              ? debugContext
              : "No retrieval context yet. Ask Atlas a question first."}
          </pre>
        </div>
      )}
    </aside>
  );
}
