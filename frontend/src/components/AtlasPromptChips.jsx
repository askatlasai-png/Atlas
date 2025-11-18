import React, { useState } from "react";
import { motion } from "framer-motion";
import { Copy, ClipboardCheck, RefreshCw, PlayCircle, Boxes, PackageSearch, Truck, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

/**
 * AtlasPromptChips
 * - mode="tabs": shows tabs and renders only active group
 * - compact: hides big header (ideal for sidebar embedding)
 */

const PROMPTS = {
  "Procurement & Purchase Orders": {
    icon: <Boxes className="h-5 w-5 text-blue-600" />,
    desc: "Morning buyer view: confirm inbound, spot delays, and compare receipts.",
    color: "blue",
    items: [
      "Show the status and expected receipt date for PO-0000155 — I want to confirm if it’s still on track.",
      "List all open purchase orders expected to arrive this week — highlight any delayed ones.",
      "What items are included in PO-0000234, and which suppliers are fulfilling them?",
      "Compare the received vs ordered quantities for PO-0000155 — any shortages?",
      "Which POs were approved but not yet released to suppliers in the last 3 days?",
    ],
  },
  "Inventory & Stock Management": {
    icon: <PackageSearch className="h-5 w-5 text-emerald-600" />,
    desc: "Inventory controller view: on-hand vs reserved, aging, safety stock.",
    color: "emerald",
    items: [
      "Show me the on-hand vs reserved quantity for ITEM-00047.",
      "List top 10 SKUs by available quantity in the warehouse.",
      "Which items are below safety stock levels?",
      "For ITEM-00047, show its inventory aging summary — how long has stock been sitting idle?",
      "Which lots or batches for ITEM-00012 are expiring soon or need rotation?",
    ],
  },
  "Sales Orders & Outbound (LPN Focus)": {
    icon: <Truck className="h-5 w-5 text-amber-600" />,
    desc: "Warehouse/fulfillment view: SO status, LPNs, staging, and shipments.",
    color: "amber",
    items: [
      "What’s the current status of SO-100078 and its scheduled ship date?",
      "Which sales orders are delayed because items are not yet picked?",
      "Show me all LPNs created for SO-100078 and their shipment status.",
      "Which LPNs are still in staging area D4 and waiting for dispatch?",
      "List all LPNs shipped today, with carrier and tracking numbers.",
      "For LPN12345, show its items, serials, and destination customer.",
      "Which LPNs were partially shipped or cancelled in the last 24 hours?",
    ],
  },
  "Analytics & Exceptions": {
    icon: <BarChart3 className="h-5 w-5 text-violet-600" />,
    desc: "Ops lead view: late deliveries, supplier impact, movement trends.",
    color: "violet",
    items: [
      "Summarize late deliveries or missed shipments in the last 7 days.",
      "Show sales orders impacted by supplier delays this week.",
      "Give me a summary of inventory movement by item category for this month.",
    ],
  },
};

function Chip({ label, onClick, selected, color }) {
  const colorMap = {
    blue: "border-blue-300 bg-blue-50 text-blue-800 hover:bg-blue-100",
    emerald: "border-emerald-300 bg-emerald-50 text-emerald-800 hover:bg-emerald-100",
    amber: "border-amber-300 bg-amber-50 text-amber-800 hover:bg-amber-100",
    violet: "border-violet-300 bg-violet-50 text-violet-800 hover:bg-violet-100",
  };
  const base = selected ? `border-${color}-600 bg-${color}-50` : colorMap[color] || "border-zinc-300 bg-white hover:bg-zinc-50";
  return (
    <motion.button
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`px-3 py-2 rounded-full border text-sm text-left transition ${base}`}
      title={label}
    >
      {label}
    </motion.button>
  );
}

export default function AtlasPromptChips({
  onSelect,
  mode = "tabs",      // "tabs" | "all"
  initialTab,
  groupsOrder,
  compact = true,
}) {
  const [copied, setCopied] = useState(null);
  const [activePrompt, setActivePrompt] = useState("");
  const order = (groupsOrder?.filter((g) => PROMPTS[g]) ?? Object.keys(PROMPTS));
  const [activeTab, setActiveTab] = useState(initialTab && PROMPTS[initialTab] ? initialTab : order[0]);

  async function handlePick(prompt) {
    setActivePrompt(prompt);
    try {
      await navigator.clipboard.writeText(prompt);
      setCopied(prompt);
      setTimeout(() => setCopied(null), 1500);
    } catch (e) {
      console.warn("Clipboard not available", e);
    }
    onSelect?.(prompt);
  }

  function copyAll() {
    const pool = mode === "tabs" ? [activeTab] : order;
    const all = pool.flatMap((k) => PROMPTS[k].items).join("\n\n");
    handlePick(all);
  }

  function reset() {
    setActivePrompt("");
    setCopied(null);
  }

  const visibleEntries = mode === "tabs"
    ? [[activeTab, PROMPTS[activeTab]]]
    : order.map((k) => [k, PROMPTS[k]]);

  return (
    <div className={`w-full ${compact ? "p-2 space-y-4" : "p-6 space-y-6"}`}>
      {/* Optional header (hidden in compact mode) */}
      {!compact && (
        <Card className="shadow-sm">
          <CardHeader className="pb-2">
            <CardTitle className="text-xl">Atlas – Prompt Library</CardTitle>
            <CardDescription>Click any prompt to copy it and prefill your chat box. Organized by role and workflow.</CardDescription>
          </CardHeader>
          <CardContent className="flex flex-col gap-3 md:flex-row md:items-center">
            <div className="flex-1">
              <Input value={activePrompt} onChange={(e) => setActivePrompt(e.target.value)} placeholder="Selected prompt appears here…" />
            </div>
            <div className="flex gap-2">
              <Button variant="secondary" onClick={copyAll} className="gap-2"><Copy className="h-4 w-4"/> Copy all</Button>
              <Button variant="ghost" onClick={reset} className="gap-2"><RefreshCw className="h-4 w-4"/> Reset</Button>
              <Button className="gap-2"><PlayCircle className="h-4 w-4"/> Run in Atlas</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs header (when mode=tabs) */}
      {mode === "tabs" && (
        <div className="sticky top-0 z-10 -mt-1 mb-1 bg-white/80 backdrop-blur supports-[backdrop-filter]:bg-white/60">
          <div className="flex items-center gap-2 border-b border-zinc-200 px-1">
            {order.map((k) => (
              <button
                key={k}
                onClick={() => setActiveTab(k)}
                className={`px-3 py-2 text-sm font-medium rounded-t-lg transition ${
                  activeTab === k ? "border-b-2 border-blue-600 text-blue-700" : "text-zinc-600 hover:text-zinc-800"
                }`}
              >
                {k}
              </button>
            ))}
            <div className="ml-auto flex items-center gap-2 py-2">
              <Button size="sm" variant="secondary" onClick={copyAll} className="gap-1"><Copy className="h-4 w-4"/>Copy</Button>
              <Button size="sm" variant="ghost" onClick={reset} className="gap-1"><RefreshCw className="h-4 w-4"/>Reset</Button>
            </div>
          </div>
        </div>
      )}

      {/* Visible group(s) */}
      <div className={`grid grid-cols-1 ${mode === "tabs" ? "" : "md:grid-cols-2 lg:grid-cols-3"} gap-6`}>
        {visibleEntries.map(([group, meta], idx) => (
          <Card key={group} className={`border-${meta.color}-200 shadow-md`}>
            <CardHeader>
              <div className={`flex items-center gap-2 text-${meta.color}-700`}>
                {meta.icon}
                <CardTitle className="text-lg">{group}</CardTitle>
              </div>
              <CardDescription>{meta.desc}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-2">
                {meta.items.map((p, i) => (
                  <div key={`${idx}-${i}`} className="flex items-center gap-2">
                    <Chip label={p} onClick={() => handlePick(p)} selected={activePrompt === p} color={meta.color} />
                    {copied === p ? (
                      <span className={`inline-flex items-center text-xs text-${meta.color}-700`}>
                        <ClipboardCheck className="h-4 w-4 mr-1" /> Copied
                      </span>
                    ) : null}
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

export { PROMPTS };
