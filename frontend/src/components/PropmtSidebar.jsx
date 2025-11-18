import React from "react";
import { X, PanelRightOpen } from "lucide-react";
import AtlasPromptChips from "./AtlasPromptChips";

// Optional: narrow layout for sidebar
function SidebarInner({ onSelect }) {
  return (
    <div className="h-full overflow-y-auto">
      <div className="p-3">
        {/* AtlasPromptChips already renders nicely; leave as-is or make compact (see note below) */}
        <AtlasPromptChips onSelect={onSelect} />
      </div>
    </div>
  );
}

export default function PromptSidebar({ open, onClose, onSelect }) {
  return (
    <div
      className={`fixed inset-y-0 right-0 z-50 pointer-events-none`}
      aria-hidden={!open}
    >
      {/* Backdrop for small screens */}
      <div
        className={`absolute inset-0 bg-black/20 transition-opacity md:hidden ${open ? "opacity-100 pointer-events-auto" : "opacity-0"}`}
        onClick={onClose}
      />

      {/* Drawer */}
      <div
        className={`absolute right-0 top-0 h-full w-full md:w-[420px] bg-white border-l border-zinc-200 shadow-xl transition-transform duration-200 pointer-events-auto
        ${open ? "translate-x-0" : "translate-x-full"}`}
      >
        <div className="flex items-center justify-between border-b border-zinc-200 px-3 py-2">
          <div className="text-sm font-semibold">Atlas — Prompt Library</div>
          <button
            onClick={onClose}
            className="rounded-lg p-1 hover:bg-zinc-100"
            aria-label="Close prompt library"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <SidebarInner onSelect={onSelect} />
      </div>

      {/* Toggle pill for desktop when closed */}
      <button
        onClick={() => (open ? onClose() : null)}
        className={`hidden md:flex absolute right-[420px] top-1/2 -translate-y-1/2 rounded-l-lg border border-r-0 border-zinc-200 bg-white shadow px-2 py-2 items-center gap-2 ${open ? "pointer-events-auto" : "opacity-0 pointer-events-none"}`}
        aria-label="Close library"
        title="Close library"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

/* Floating open button (put this wherever you render the page; exported for reuse) */
export function PromptSidebarToggle({ onClick }) {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-4 right-4 z-40 rounded-full border border-zinc-200 bg-white px-3 py-2 shadow hover:bg-zinc-50"
      aria-label="Open prompt library"
      title="Open prompt library"
    >
      <div className="flex items-center gap-2 text-sm">
        <PanelRightOpen className="h-4 w-4" />
        Prompts
      </div>
    </button>
  );
}
