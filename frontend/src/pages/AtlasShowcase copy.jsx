import { Layers } from "lucide-react";
import { Link } from "react-router-dom";

import React, { useEffect, useState, useRef } from "react";
import { motion } from "framer-motion";
import AtlasChatUI from "@/components/AtlasChatUI.jsx";
import SeeAtlasInAction from "@/sections/about/SeeAtlasInAction.jsx"; // adjust path to match your structure
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  AboutHero,
  KeyFeatures,
  HowItWorks,
  TechStack,
} from "@/sections/about";
import {
  Video,
  FileText,
  Linkedin,
  MessageCircle,
  Copy,
  Check,
  BarChart3,
  Briefcase,
  Cog,
  Coins,
  Filter,
  Search,
  Link2,
} from "lucide-react";
import SupplyChainDeepDive from "@/sections/about/SupplyChainDeepDive.jsx";
import IndustriesPreview from "@/sections/about/IndustriesPreview.jsx";
import UnderTheHood from "@/sections/about/UnderTheHood.jsx";
import BehindAtlas from "@/sections/about/BehindAtlas.jsx";
import FinalCTA from "@/sections/about/FinalCTA.jsx";
import SectionNav from "@/components/Navbar.jsx";
import PersonaRailFloating from "@/components/PersonaRailFloating.jsx";
import DatasetRailFloating from "@/components/DatasetRailFloating.jsx";

/* ---------------- Page assets ---------------- */
const ASSETS = {
  title: "Atlas – AI built for your business.",
  tagline:
    "Atlas turns your real operational data — supply chain, retail, service, logistics — into an AI assistant that helps you run smarter every day.",
  youtubeUrl: "https://www.youtube.com/watch?v=p_70O0TdJLM",
  linkedinUrl: "https://www.linkedin.com/in/naga-chaganti/",
  archDiagramUrl: "/assets/atlas-architecture.png",
  whitepaperUrl: "/assets/atlas-whitepaper.pdf",
  deckUrl: "https://docs.google.com/presentation/d/YOUR_SLIDES_ID/preview",
  pageUrl: "https://www.atlasaicopilot.com/",
  // (You can wire these up later if you want download CTAs etc.)
  datasetsUrl: "/assets/atlas-sample-erp.zip",
  profileImageUrl: "/images/naga.jpg",
};

/* ---------------- Small helpers that Hero and footer use ---------------- */

function ResponsiveYouTube({ url }) {
  // turn watch?v=... into embed/... so it will iframe nicely
  const embedUrl = (url || "")
    .replace("watch?v=", "embed/")
    .split("&")[0];

  return (
    <div className="relative w-full h-full overflow-hidden rounded-2xl shadow ring-1 ring-white/40 bg-white/70 backdrop-blur">
      <iframe
        src={`${embedUrl}?rel=0&modestbranding=1`}
        className="absolute inset-0 h-full w-full block"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        allowFullScreen
        title="Atlas Demo"
      />
    </div>
  );
}

// single-line “copy link” pill used in the hero
function CopyShare() {
  const [copied, setCopied] = React.useState(false);

  // Always use the main public domain
  const shareUrl = "https://atlasaicopilot.com";

  return (
    <div className="w-auto inline-block">
      <button
        type="button"
        onClick={() => {
          navigator.clipboard.writeText(shareUrl);
          setCopied(true);
          setTimeout(() => setCopied(false), 1200);
        }}
        className={`inline-flex items-center gap-1 rounded-full px-3 py-[3px] text-xs font-medium text-slate-100 
          ring-1 ring-white/25 bg-white/15 hover:bg-white/25 transition-all duration-300
          ${copied ? "animate-pulse ring-2 ring-cyan-400/60" : ""}`}
        aria-label="Copy site link"
        title={copied ? "Copied!" : "Copy Atlas website link"}
        style={{ width: "fit-content" }}
      >
        <Link2 className="h-3.5 w-3.5 shrink-0" />
        <span>{copied ? "Copied" : "Copy link"}</span>
      </button>
    </div>
  );
}


// generic "copy this value" field – not currently rendered in your hero,
// but you referenced it before so I'll keep it for completeness
function CopyField({ label, value }) {
  const [copied, setCopied] = React.useState(false);
  return (
    <div className="space-y-2">
      <div className="text-sm text-slate-600">{label}</div>
      <div className="flex items-center gap-2">
        <input
          readOnly
          value={value}
          className="font-mono w-full h-10 rounded-md border border-slate-300 px-3 bg-white/90"
        />
        <Button
          variant="secondary"
          onClick={() => {
            navigator.clipboard.writeText(value || "");
            setCopied(true);
            setTimeout(() => setCopied(false), 1100);
          }}
        >
          {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}

/* Simple Avatar for the Architect / founder card */
function Avatar({ src, name = "", size = 56 }) {
  const initials = name
    .split(" ")
    .filter(Boolean)
    .map((s) => s[0]?.toUpperCase())
    .slice(0, 2)
    .join("");
  const base =
    "rounded-full bg-gradient-to-br from-blue-100 to-teal-100 flex items-center justify-center text-slate-700";
  const style = {
    width: size,
    height: size,
    fontSize: Math.max(12, Math.floor(size / 3)),
  };

  if (src) {
    return (
      <img
        src={src}
        alt={name || "Avatar"}
        className="rounded-full object-cover ring-2 ring-blue-100"
        style={{ width: size, height: size }}
        loading="lazy"
        referrerPolicy="no-referrer"
      />
    );
  }
  return (
    <div className={base} style={style}>
      {initials || "N"}
    </div>
  );
}

/* ---------------- Tech Stack Strip (optional section) ---------------- */
function TechStackStrip() {
  const groups = [
    {
      label: "Frontend",
      color: "text-sky-600",
      techs: [
        "React",
        "Vite",
        "Tailwind CSS",
        "Framer Motion",
        "shadcn/ui",
        "lucide-react",
      ],
    },
    {
      label: "Backend / AI Layer",
      color: "text-teal-600",
      techs: [
        "Python",
        "LangChain",
        "OpenAI API",
        "FAISS",
        "Pandas",
        "Node.js",
      ],
    },
    {
      label: "Infrastructure",
      color: "text-indigo-600",
      techs: [
        "PostgreSQL",
        "AWS S3",
        "AWS Lambda",
        "RDS",
        "CloudFront",
        "WAF",
        "ALB",
      ],
    },
  ];

  return (
    <div className="mt-8 flex justify-center">
      <div className="flex flex-col gap-3 rounded-2xl bg-white/85 backdrop-blur ring-1 ring-blue-100/70 shadow px-6 py-4 text-sm text-slate-700">
        {groups.map((g) => (
          <div
            key={g.label}
            className="flex flex-wrap items-center justify-center gap-2"
          >
            <span className={`font-semibold ${g.color}`}>{g.label}:</span>
            {g.techs.map((t) => (
              <span
                key={t}
                className="rounded-full border border-blue-100/70 bg-white/90 px-3 py-1 text-xs sm:text-sm shadow-sm"
              >
                {t}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ---------------- Hover-enhanced Use Cases ---------------- */

const personaUseCases = [
  {
    key: "planner",
    label: "Planner",
    icon: BarChart3,
    gradient: "from-sky-50 to-blue-100/40",
    ring: "ring-sky-200/70",
    points: [
      "Detect forecast error and bias vs. last 12 weeks",
      "Spot stock-outs and impending backorders",
      "Rebalance inventory across DCs using transfer candidates",
    ],
    sample:
      '"Which SKUs in Region East are likely to stock out in 7 days given current ATP?"',
  },
  {
    key: "buyer",
    label: "Buyer",
    icon: Briefcase,
    gradient: "from-indigo-50 to-blue-100/40",
    ring: "ring-indigo-200/70",
    points: [
      "Identify late POs and ASN slippage",
      "Supplier scorecards with on-time & fill-rate",
      "Auto-draft supplier emails with context",
    ],
    sample:
      '"List POs past due by >5 days for Top 20 suppliers and suggest outreach."',
  },
  {
    key: "ops",
    label: "Operations",
    icon: Cog,
    gradient: "from-teal-50 to-green-100/30",
    ring: "ring-teal-200/70",
    points: [
      "Trace LPNs end-to-end and surface blockers",
      "View ASN exceptions and receiving queues",
      "Cycle-count anomalies and putaway delays",
    ],
    sample:
      '"Trace LPN 123… across sites and show last scan with handler."',
  },
  {
    key: "finance",
    label: "Finance",
    icon: Coins,
    gradient: "from-purple-50 to-indigo-100/30",
    ring: "ring-purple-200/70",
    points: [
      "Reconcile landed cost variances",
      "Inventory turns by location & age buckets",
      "GL mismatch triage with drill-through",
    ],
    sample:
      '"Show items with negative margin after landed cost this quarter."',
  },
];

function UseCaseCard({ uc }) {
  const Icon = uc.icon;
  return (
    <motion.li
      initial={{ y: 4, opacity: 0 }}
      whileInView={{ y: 0, opacity: 1 }}
      viewport={{ once: true, margin: "-10%" }}
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 260, damping: 24 }}
      className={`group relative rounded-2xl border bg-gradient-to-br ${uc.gradient} p-4 shadow-sm ring-1 ${uc.ring}`}
    >
      <div className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 bg-[radial-gradient(80%_80%_at_50%_0%,rgba(59,130,246,0.20),rgba(59,130,246,0)_70%)]" />
      <div className="relative z-10">
        <div className="flex items-center gap-2 font-medium text-slate-800">
          <Icon className="h-4 w-4 text-slate-700" />
          {uc.label}
          <span className="ml-auto text-[11px] rounded-full bg-white/70 px-2 py-0.5 ring-1 ring-slate-200 text-slate-600">
            Persona
          </span>
        </div>
        <ul className="mt-2 space-y-1.5 text-sm text-slate-700 list-disc pl-5">
          {uc.points.map((p) => (
            <li key={p}>{p}</li>
          ))}
        </ul>
        <div className="mt-3">
          <div className="text-[11px] uppercase tracking-wide text-slate-500">
            Sample Prompt
          </div>
          <div className="mt-1 rounded-lg bg-white/80 ring-1 ring-slate-200 p-2 text-[13px] text-slate-800 font-mono">
            {uc.sample}
          </div>
        </div>
        <div className="mt-3 flex items-center gap-2">
          <a
            href="#try-atlas"
            className="inline-flex items-center gap-2 rounded-lg bg-white px-3 py-1.5 text-xs font-medium ring-1 ring-slate-200 shadow hover:bg-slate-50"
          >
            <MessageCircle className="h-3.5 w-3.5" /> Try in Chat
          </a>
          <button
            type="button"
            className="inline-flex items-center gap-2 rounded-lg bg-white/70 px-2.5 py-1.5 text-[12px] ring-1 ring-slate-200 hover:bg-white"
            onClick={() => navigator.clipboard.writeText(uc.sample)}
          >
            <Copy className="h-3.5 w-3.5" /> Copy Prompt
          </button>
        </div>
      </div>
    </motion.li>
  );
}

function UseCasesSection() {
  const [query, setQuery] = React.useState("");
  const [active, setActive] = React.useState("all");

  const filtered = personaUseCases.filter((u) => {
    const inTab = active === "all" || u.key === active;
    const inQuery =
      !query ||
      u.label.toLowerCase().includes(query.toLowerCase()) ||
      u.points.some((p) =>
        p.toLowerCase().includes(query.toLowerCase())
      );
    return inTab && inQuery;
  });

  return (
    <Card className="rounded-2xl bg-white/90 backdrop-blur shadow-xl ring-1 ring-blue-100/70">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          Use Cases
        </CardTitle>
        <CardDescription>
          What stakeholders do with Atlas day-to-day.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <div className="flex items-center gap-2 rounded-xl ring-1 ring-slate-200 bg-white px-2 py-1">
            <Filter className="h-4 w-4 text-slate-500" />
            {[
              { key: "all", label: "All" },
              { key: "planner", label: "Planner" },
              { key: "buyer", label: "Buyer" },
              { key: "ops", label: "Operations" },
              { key: "finance", label: "Finance" },
            ].map((t) => (
              <button
                key={t.key}
                onClick={() => setActive(t.key)}
                className={`text-xs rounded-lg px-2 py-1 transition ${
                  active === t.key
                    ? "bg-slate-900 text-white"
                    : "hover:bg-slate-100"
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>

          <div className="ml-auto flex items-center gap-2 rounded-xl ring-1 ring-slate-200 bg-white px-2 py-1">
            <Search className="h-4 w-4 text-slate-500" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search points…"
              className="h-8 w-40 sm:w-60 bg-transparent outline-none text-sm"
            />
          </div>
        </div>

        <ul className="grid sm:grid-cols-2 gap-4">
          {filtered.map((uc) => (
            <UseCaseCard key={uc.key} uc={uc} />
          ))}
        </ul>
      </CardContent>
    </Card>
  );
}

/* ---------------- Floating full-screen overlay (chat + datasets) ---------------- */
  function ModalOverlayWithRails({ onClose }) {
    const [debugContext, setDebugContext] = React.useState("");
    const [stagedPrompt, setStagedPrompt] = React.useState("");
    const contentRef = React.useRef(null);
    const [showDebug, setShowDebug] = React.useState(false);


    // toggle between chat vs dataset browser
    const [showDatasetsView, setShowDatasetsView] = React.useState(false);

    // which dataset is expanded
    const [openDataset, setOpenDataset] = React.useState(null);

    // cache of full CSV contents
    const [fullRowsByFile, setFullRowsByFile] = React.useState({});
    
    // NEW: global search in dataset explorer
    const [searchQuery, setSearchQuery] = React.useState("");

    const [chatMessages, setChatMessages] = React.useState([]);


    const [copiedValue, setCopiedValue] = React.useState(null);


    function handleCopyCell(val) {
      if (!val) return;
      navigator.clipboard.writeText(val);
      setCopiedValue(val);
      setTimeout(() => {
        setCopiedValue(null);
      }, 1200);
    }


  // dataset metadata (same as before)
  const DATASETS = React.useMemo(
    () => [
      {
        fileName: "idx_v_ir_status_enriched.csv",
        folder: "idx_v_ir_status_enriched",
        domain: "PO Status",
        columns: [
          "po_number",
          "item",
          "ordered_qty",
          "received_qty",
          "need_by_date",
          "last_receipt_date",
          "po_status",
          "Context_Summary",
        ],
        example:
          'Ask: "Show the status and expected receipt date for PO-0000155."',
      },
      {
        fileName: "onhand_inventory_enriched.csv",
        folder: "idx_v_onhand_status_enriched",
        domain: "Inventory",
        columns: [
          "item",
          "organization_id",
          "onhand_qty",
          "reserved_qty",
          "available_qty",
          "subinventory_code",
          "locator_code",
          "last_update_date",
          "Context_Summary",
        ],
        example:
          'Ask: "Show me the on-hand vs reserved quantity for ITEM-00047."',
      },

      {
        fileName: "so_delivery_status_enriched.csv",
        folder: "idx_v_so_delivery_status_enriched",
        domain: "Outbound / Deliveries",
        columns: [
          "so_number",
          "delivery_number",
          "delivery_status",
          "carrier_name",
          "tracking_number",
          "ship_from_location_id",
          "ship_to_location_id",
          "requested_quantity",
          "shipped_quantity",
          "actual_ship_date",
          "Context_Summary",
        ],
        example:
          'Ask: "Show all deliveries and their shipment status for SO-100078."',
      },

      {
        fileName: "lpn_tracking_enriched.csv",
        folder: "idx_v_lpn_serials_se_enriched", // <-- matches your actual folder
        domain: "Fulfillment",
        columns: [
          "lpn_number",
          "delivery_number",
          "carrier_name",
          "ship_from_location_id",
          "ship_to_location_id",
          "delivery_status",
          "tracking_number",
          "requested_quantity",
          "shipped_quantity",
          "customer_or_site_name",
          "Context_Summary",
        ],
        example:
          'Ask: "Show all LPNs created for SO-100078 and their shipment status."',
      },

     {
        fileName: "po_status_enriched.csv",
        folder: "idx_v_po_status_enriched",
        domain: "Purchase Orders",
        columns: [
          "po_number",
          "item",
          "ordered_qty",
          "received_qty",
          "need_by_date",
          "last_receipt_date",
          "po_status",
          "Context_Summary",
        ],
        example:
          'Ask: "Show all open purchase orders delayed past their need-by date."',
      },

      {
      fileName: "lpn_status_enriched.csv",
      folder: "idx_v_lpn_status_se_enriched",
      domain: "Fulfillment Status",
      columns: [
        "lpn_number",
        "delivery_number",
        "carrier_name",
        "ship_from_location_id",
        "ship_to_location_id",
        "delivery_status",
        "tracking_number",
        "requested_quantity",
        "shipped_quantity",
        "customer_or_site_name",
        "Context_Summary",
      ],
      example:
        'Ask: "Which LPNs are staged or in transit, and where are they now?"',
     },

     {
      fileName: "lpn_serials_agg_enriched.csv",
      folder: "idx_v_lpn_serials_agg_se_enriched",
      domain: "Fulfillment (Aggregated Serials)",
      columns: [
        "lpn_number",
        "delivery_number",
        "carrier_name",
        "ship_from_location_id",
        "ship_to_location_id",
        "delivery_status",
        "tracking_number",
        "requested_quantity",
        "shipped_quantity",
        "customer_or_site_name",
        "Context_Summary",
      ],
      example:
        'Ask: "Show aggregated shipment details for each LPN by carrier."',
    },




    ],
    []
  );

  // map of dataset → file path
    const csvPathMap = {
      idx_v_so_delivery_status_enriched:
        "/data/idx_v_so_delivery_status_enriched/v_so_delivery_status.csv",

      idx_v_ir_status_enriched:
        "/data/idx_v_ir_status_enriched/v_ir_status.csv",

      idx_v_onhand_status_enriched:
        "/data/idx_v_onhand_status_enriched/v_onhand_status.csv",

      idx_v_lpn_serials_se_enriched:
        "/data/idx_v_lpn_serials_se_enriched/v_lpn_serials_se.csv",
          
      idx_v_po_status_enriched:
       "/data/idx_v_po_status_enriched/v_po_status.csv", // 👈 new line

      idx_v_lpn_status_se_enriched:   
      "/data/idx_v_lpn_status_se_enriched/v_lpn_status_se.csv",

      idx_v_lpn_serials_agg_se_enriched:
      "/data/idx_v_lpn_serials_agg_se_enriched/v_lpn_serials_agg_se.csv", 

    };


  // helper: fetch CSV and parse to objects
  async function ensureDatasetLoaded(folder) {
    if (fullRowsByFile[folder]) return;
    const csvPath = csvPathMap[folder];
    if (!csvPath) return;
    try {
      const res = await fetch(csvPath);
      const text = await res.text();
      const lines = text.split(/\r?\n/).filter((l) => l.trim());
      if (!lines.length) return;

      const headers = lines[0].split(",").map((h) => h.trim());
      const rows = lines.slice(1).map((ln) => {
        const cells = ln.split(",");
        const obj = {};
        headers.forEach((h, i) => (obj[h] = cells[i]?.trim() ?? ""));
        return obj;
      });

      setFullRowsByFile((prev) => ({
        ...prev,
        [folder]: { columns: headers, rows },
      }));
    } catch (err) {
      console.error("CSV load failed", folder, err);
    }
  }

  // toggle expand/collapse
  function handleToggleDataset(ds) {
    if (openDataset === ds.folder) {
      setOpenDataset(null);
      return;
    }
    setOpenDataset(ds.folder);
    ensureDatasetLoaded(ds.folder);
  }

  // close overlay if click outside (chat only)
  React.useEffect(() => {
    function handleClickOutside(e) {
      if (
        !showDatasetsView &&
        contentRef.current &&
        !contentRef.current.contains(e.target)
      )
        onClose();
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [onClose, showDatasetsView]);

  // dataset browser overlay
function DatasetExplorerOverlay() {
  return (
    <div className="flex flex-col w-full max-w-[1400px] max-h-[85vh] rounded-none sm:rounded-2xl bg-white/95 backdrop-blur ring-1 ring-blue-100/70 shadow-2xl p-0 overflow-hidden">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-4 border-b border-slate-200 bg-white/70 backdrop-blur px-5 py-4 rounded-t-2xl">
        {/* Left: title / explainer */}
        <div className="flex-1 min-w-0">
          <div className="text-slate-900 text-lg font-semibold flex items-center gap-2">
            <img
              src="/logos/atlas-mark-dark-bg.png"
              alt="Atlas Logo"
              className="h-6 w-6 object-contain filter brightness-0 opacity-90"
            />
            <span>Data Sources in this Demo</span>
            <span className="rounded-full bg-blue-600 text-white px-2 py-[2px] text-[10px] font-medium leading-none">
              Read-only
            </span>
          </div>
          <p className="text-[12px] text-slate-500 mt-1 leading-snug">
            Click a dataset to inspect live ERP rows. You can filter by PO #,
            SO #, LPN, item / SKU, warehouse, carrier, or tracking number.
          </p>
        </div>

        {/* Middle: search box */}
        <div className="flex items-center gap-2 rounded-xl ring-1 ring-slate-200 bg-white px-3 py-2 text-[12px] text-slate-700 shadow-sm lg:w-[260px]">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-4 w-4 text-slate-500 shrink-0"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M21 21l-4.35-4.35M9.5 17a7.5 7.5 0 100-15 7.5 7.5 0 000 15z"
            />
          </svg>

          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search PO / SO / LPN / Item / Tracking…"
            className="flex-1 bg-transparent outline-none text-[12px] text-slate-700 placeholder:text-slate-400"
          />

          {searchQuery && (
            <button
              className="text-[11px] text-slate-500 hover:text-slate-700"
              onClick={() => setSearchQuery("")}
              title="Clear search"
            >
              ✕
            </button>
          )}
        </div>

        {/* Right: controls */}
        <div className="flex gap-2 shrink-0">
          <button
            onClick={() => setShowDatasetsView(false)}
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-[12px] font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            ← Back to Chat
          </button>
          <button
            onClick={onClose}
            className="rounded-lg bg-blue-600 text-white text-sm font-medium px-3 py-1.5 hover:bg-blue-700"
          >
            Close
          </button>
        </div>
      </div>

      {/* Table of datasets */}
      <div className="flex-1 min-h-0 overflow-y-auto px-5 pb-5 pt-4">
        <div className="rounded-xl bg-white ring-1 ring-slate-200 shadow-sm overflow-x-auto overflow-y-visible text-[13px] text-slate-700">
          <table className="w-full border-collapse text-left min-w-[800px]">
            <thead className="text-[11px] uppercase text-slate-500 border-b border-slate-200 bg-slate-50/60">
              <tr>
                <th className="py-3 pl-4 pr-3 font-medium">FILE / TABLE</th>
                <th className="py-3 pr-3 font-medium">DOMAIN</th>
                <th className="py-3 pr-3 font-medium">COLUMN HIGHLIGHTS</th>
                <th className="py-3 pr-4 font-medium">EXAMPLE PROMPT</th>
              </tr>
            </thead>

            <tbody className="align-top text-[12px] text-slate-800">
              {DATASETS.map((ds) => {
                const open = openDataset === ds.folder;
                const loaded = fullRowsByFile[ds.folder];

                // does this dataset contain ANY row that matches the current searchQuery?
                const datasetHasHit = React.useMemo(() => {
                  if (!searchQuery.trim()) return false;
                  if (!loaded || !loaded.rows) return false;

                  const q = searchQuery.trim().toLowerCase();
                  return loaded.rows.some((rowObj) =>
                    loaded.columns.some((colName) => {
                      const cellVal = rowObj[colName];
                      if (cellVal === null || cellVal === undefined) return false;
                      return String(cellVal).toLowerCase().includes(q);
                    })
                  );
                }, [loaded, searchQuery]);

                // filter rows for expanded view (respects searchQuery)
                const filteredRows = React.useMemo(() => {
                  if (!loaded || !loaded.rows) return [];
                  if (!searchQuery.trim()) return loaded.rows;

                  const q = searchQuery.trim().toLowerCase();

                  return loaded.rows.filter((rowObj) => {
                    return loaded.columns.some((colName) => {
                      const cellVal = rowObj[colName];
                      if (cellVal === null || cellVal === undefined) return false;
                      return String(cellVal).toLowerCase().includes(q);
                    });
                  });
                }, [loaded, searchQuery]);

                return (
                  <React.Fragment key={ds.fileName}>
                    {/* Summary row for this dataset */}
                    <tr
                      className={[
                        "border-b border-slate-200 cursor-pointer hover:bg-slate-50",
                        open ? "bg-slate-50/80" : "",
                        datasetHasHit
                          ? "ring-2 ring-blue-400/60 ring-offset-0 bg-blue-50/40"
                          : ""
                      ].join(" ")}
                      onClick={() => handleToggleDataset(ds)}
                    >
                      <td className="py-3 pl-4 pr-3 font-mono text-[12px] text-slate-900">
                        {ds.fileName}
                      </td>

                      <td className="py-3 pr-3">
                        <span
                          className={[
                            "inline-flex rounded-full px-2 py-[2px] text-[10px] font-medium",
                            datasetHasHit
                              ? "bg-blue-600 text-white shadow-[0_0_8px_rgba(37,99,235,0.6)]"
                              : "bg-slate-900 text-white"
                          ].join(" ")}
                        >
                          {ds.domain}
                        </span>
                      </td>

                      <td className="py-3 pr-3 text-slate-600">
                        {ds.columns.join(", ")}
                      </td>

                      <td className="py-3 pr-4 text-slate-700">
                        {ds.example}
                      </td>
                    </tr>

                    {/* Expanded detail rows for this dataset */}
                    {open && (
                      <tr className="border-b border-slate-200 bg-slate-50/40">
                        <td colSpan={4} className="pl-4 pr-4 py-4">
                          <div className="border border-slate-200 rounded-xl overflow-x-auto overflow-y-auto max-h-[260px] bg-white shadow-inner text-[12px] font-mono text-slate-900" style={{ WebkitOverflowScrolling: 'touch' }}>
                            <table className="min-w-full border-collapse">
                              <thead className="bg-slate-100 text-slate-600 text-[10px] uppercase sticky top-0 z-[1] border-b border-slate-200">
                                <tr>
                                  {(loaded ? loaded.columns : ds.columns).map(
                                    (col, colIdx) => (
                                      <th
                                        key={col}
                                        className={[
                                          "text-left font-medium px-3 py-2 border-r border-slate-200 last:border-r-0 whitespace-nowrap bg-slate-100",
                                          colIdx === 0
                                            ? "sticky left-0 z-[2] shadow-[2px_0_2px_rgba(0,0,0,0.04)]"
                                            : "",
                                        ].join(" ")}
                                      >
                                        {col}
                                      </th>
                                    )
                                  )}
                                </tr>
                              </thead>

                              <tbody className="text-[11px] text-slate-800">
                                {loaded ? (
                                  filteredRows.length > 0 ? (
                                    filteredRows.map((r, i) => (
                                      <tr
                                        key={i}
                                        className={
                                          i % 2 === 0
                                            ? "bg-white"
                                            : "bg-slate-50/60"
                                        }
                                      >
                                        {loaded.columns.map(
                                          (col, colIdx) => {
                                            const cellVal = r[col];
                                            const isJustCopied =
                                              copiedValue === cellVal;

                                            // Sticky + copy pill for first column
                                            if (colIdx === 0) {
                                              return (
                                                <td
                                                  key={col}
                                                  className={[
                                                    "px-3 py-2 border-b border-slate-100 border-r border-slate-200 last:border-r-0 whitespace-nowrap align-top",
                                                    "sticky left-0 z-[1] bg-white/95 backdrop-blur-sm shadow-[2px_0_2px_rgba(0,0,0,0.04)]",
                                                  ].join(" ")}
                                                >
                                                  <div className="flex items-start gap-2">
                                                    <span className="text-slate-900 font-semibold">
                                                      {cellVal}
                                                    </span>

                                                    <button
                                                      onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleCopyCell(cellVal);
                                                      }}
                                                      className={[
                                                        "text-[10px] leading-none rounded-md border px-1.5 py-[2px] font-medium",
                                                        "border-slate-300 bg-white text-slate-500 hover:bg-slate-50 hover:text-slate-700",
                                                        "active:bg-slate-100 active:text-slate-900",
                                                        isJustCopied
                                                          ? "border-green-400 bg-green-50 text-green-600"
                                                          : "",
                                                      ].join(" ")}
                                                      title="Copy to clipboard"
                                                    >
                                                      {isJustCopied
                                                        ? "Copied"
                                                        : "Copy"}
                                                    </button>
                                                  </div>
                                                </td>
                                              );
                                            }

                                            // normal cells
                                            return (
                                              <td
                                                key={col}
                                                className="px-3 py-2 border-b border-slate-100 border-r border-slate-200 last:border-r-0 whitespace-nowrap align-top"
                                              >
                                                {cellVal}
                                              </td>
                                            );
                                          }
                                        )}
                                      </tr>
                                    ))
                                  ) : (
                                    <tr>
                                      <td
                                        colSpan={loaded.columns.length}
                                        className="px-3 py-6 text-center text-slate-500 text-[11px]"
                                      >
                                        No matches for “{searchQuery}”.
                                      </td>
                                    </tr>
                                  )
                                ) : (
                                  <tr>
                                    <td
                                      colSpan={ds.columns.length}
                                      className="px-3 py-4 text-slate-500 text-[11px]"
                                    >
                                      Loading data…
                                    </td>
                                  </tr>
                                )}
                              </tbody>
                            </table>
                          </div>

                          <div className="text-[11px] text-slate-500 mt-2 leading-snug">
                            This is real ERP data. Filter it live, copy any ID,
                            and then paste into Atlas on the right.
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}



  // main chat view (unchanged)
  function ChatView() {
  return (
    <div
      ref={contentRef}
      className="flex items-start gap-2 sm:gap-4 w-full max-w-[1600px]"
    >
      {/* LEFT PANEL */}
      <div className="hidden 2xl:flex flex-col w-[540px] max-h-[85vh]">
        <div className="flex-1 rounded-2xl bg-white/90 backdrop-blur ring-1 ring-blue-100/70 shadow-xl p-4 overflow-hidden">
          <div className="overflow-y-auto pr-2 max-h-[75vh]">
            <PersonaRailFloating
              onSelectPrompt={(promptText) => setStagedPrompt(promptText)}
            />
          </div>
        </div>
      </div>

      {/* MIDDLE PANEL */}
      <div className="flex flex-col w-full h-[90vh] sm:h-[85vh] max-h-[90vh] sm:max-h-[85vh] sm:max-w-[700px] sm:min-w-[600px] md:min-w-[700px] rounded-none sm:rounded-2xl bg-white shadow-2xl ring-1 ring-slate-200">
        {/* Header Bar */}
        <div className="flex flex-col gap-2 sm:gap-3 border-b border-slate-200 bg-white/80 backdrop-blur px-3 sm:px-4 py-2 sm:py-3 rounded-t-none sm:rounded-t-2xl">
          <div className="flex items-start justify-between gap-2">
            <div className="flex flex-col flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <img
                  src="/logos/atlas-mark-dark-bg.png"
                  alt="Atlas Logo"
                  className="h-5 w-5 sm:h-6 sm:w-6 object-contain filter brightness-0 opacity-90 flex-shrink-0"
                />
                <div className="text-slate-900 text-base sm:text-lg font-semibold">
                  Atlas – Live Demo
                </div>
                <span className="rounded-full bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 px-2 py-0.5 text-[10px] sm:text-[11px] font-medium text-white whitespace-nowrap">
                  Supply Chain
                </span>
              </div>
              <div className="text-[11px] sm:text-[12px] text-slate-500 mt-1">
                Ask about POs, inventory, or shipments
              </div>
            </div>
            <button
              onClick={onClose}
              className="flex-shrink-0 rounded-lg bg-blue-600 text-white text-xs sm:text-sm font-medium px-3 py-1.5 hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 min-h-0 p-4">
          <div className="relative flex flex-col h-full min-h-0">
            <AtlasChatUI
              incomingPrompt={stagedPrompt}
              onContextUpdate={(ctx) => setDebugContext(ctx)}
              messages={chatMessages}
              setMessages={setChatMessages}
              onPromptConsumed={() => setStagedPrompt("")}
              onOpenDataSources={() => {
                setShowDatasetsView(true);
                setOpenDataset(null);
              }}
              className="flex-1 min-h-0 flex flex-col"
            />
          </div>
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="hidden xl:flex flex-col w-[300px] max-h-[85vh]">
        <div className="flex-1 overflow-hidden">
          <DatasetRailFloating
            onOpenDatasets={() => {
              setShowDatasetsView(true);
              setOpenDataset(null);
            }}
            debugContext={debugContext}
            showDebug={showDebug}
            onToggleDebug={() => setShowDebug((v) => !v)}
          />
        </div>
      </div>
    </div>
  );
}


  return (
    <div className="fixed inset-0 z-[9999] flex items-start justify-center bg-slate-900/40 backdrop-blur-sm p-0 sm:p-4 overflow-y-auto">
      <div className="flex items-start justify-center w-full pt-0 sm:pt-8 md:pt-16">
        {showDatasetsView ? <DatasetExplorerOverlay /> : <ChatView />}
      </div>
    </div>
  );
}


/* ---------------- Main Page ---------------- */
export default function AtlasShowcase() {
  const [chatOpen, setChatOpen] = useState(false);
  const chatRef = useRef(null);
  const [chatInView, setChatInView] = useState(false);

  useEffect(() => {
    const node = chatRef.current;
    if (!node) return;
    const io = new IntersectionObserver(
      ([entry]) =>
        setChatInView(
          entry.isIntersecting && entry.intersectionRatio > 0.2
        ),
      { threshold: [0.2] }
    );
    io.observe(node);
    return () => io.disconnect();
  }, []);

  return (
    <div className="relative min-h-screen overflow-hidden">
      {/* Top nav pinned */}
      <SectionNav
        onOpenChat={() => setChatOpen(true)}
        hideNav={chatOpen}
      />

      {/* Background gradients */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-sky-100 to-teal-50" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_30%,rgba(59,130,246,0.15),transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_70%,rgba(20,184,166,0.15),transparent_50%)]" />

      {/* Foreground content */}
      <div className="relative z-10 ">
        {/* Hero */}
        <header className="mx-auto max-w-6xl px-4 py-8 sm:py-12">
          <div className="grid gap-8 md:grid-cols-2 items-stretch">
            {/* LEFT: Title / CTAs */}
            <div className="flex">
              <div className="flex flex-col justify-between rounded-2xl p-6 md:p-8 w-full bg-gradient-to-r from-slate-900 to-slate-800 text-white shadow-lg ring-1 ring-white/10 min-h-[480px]">
                <div>
                  <CopyShare url={ASSETS.pageUrl} />
                  <div className="text-xs text-slate-500">
                  </div>

                  <h1 className="mt-6 text-4xl md:text-5xl font-display font-semibold leading-[1.15] tracking-tight text-balance">
                    {ASSETS.title}
                  </h1>
                  <p className="mt-4 text-lg text-slate-200/90 max-w-2xl leading-relaxed">
                    {ASSETS.tagline}
                  </p>
                  <p className="mt-3 text-sm text-slate-400 max-w-xl leading-relaxed">
                    Born in supply chain. Built to scale across
                    industries.
                  </p>
                </div>

                <div className="mt-8 flex flex-wrap gap-3">
                  <a
                    href={ASSETS.youtubeUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 px-4 py-2 text-sm font-medium text-white shadow-lg hover:brightness-110"
                  >
                    <Video className="h-4 w-4" />
                    See Atlas in Action
                  </a>
                  <a
                    href={ASSETS.linkedinUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 rounded-xl bg-white/10 px-4 py-2 text-sm font-medium text-white ring-1 ring-white/20 hover:bg-white/15"
                  >
                    <Linkedin className="h-4 w-4" />
                    Connect on LinkedIn
                  </a>
                  <a
                    href={ASSETS.whitepaperUrl}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-2 rounded-xl bg-transparent px-4 py-2 text-sm font-medium text-white ring-1 ring-white/25 hover:bg-white/10"
                  >
                    {/* <FileText className="h-4 w-4" />
                    Dive into the Atlas Architecture */}
                    <Link to="/how-atlas-works">How Atlas Works</Link>
                  </a>
                </div>
              </div>
            </div>

            {/* RIGHT: Video */}
            <div className="flex min-h-[480px]">
              <div className="rounded-2xl overflow-hidden ring-1 ring-white/40 bg-white/70 shadow-lg backdrop-blur flex-grow">
                <ResponsiveYouTube url={ASSETS.youtubeUrl} />
              </div>
            </div>
          </div>

          <>
            {/* ===== About / Hero ===== */}
            <section id="about" className="mt-8 space-y-8">
              <AboutHero />
              <div className="text-center text-slate-500 text-sm italic py-4">
                Built for real operations — starting in supply
                chain, ready for every industry.
              </div>
            </section>

           {/* ===== See Atlas in Action ===== */}
            <SeeAtlasInAction />

            {/* ===== Supply Chain Deep Dive ===== */}
            <section
              id="supply-chain"
              className="mt-8 space-y-8"
            >
              <SupplyChainDeepDive />
            </section>



            {/* ===== Atlas for Everyday Businesses ===== */}
            <section
              id="everyday-businesses"
              className="mt-8 space-y-8"
            >
              <IndustriesPreview />
            </section>
            


            {/* ===== Behind Atlas / Founder Story ===== */}
            <section
              id="behind-atlas"
              className="mt-8 space-y-8"
            >
              <BehindAtlas />
            </section>

            {/* ===== Contact / Architecture link ===== */}
            <section
              id="contact"
              className="mt-8 space-y-8"
            >
              <div className="text-center">
                <Link
                  to="/explore"
                  className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:underline"
                >
                  <Layers className="h-4 w-4 text-blue-600" />
                  <span>
                    Explore the Atlas architecture →
                  </span>
                </Link>
              </div>
            </section>

            {/* ===== Try Atlas / CTA ===== */}
            <section
              id="try-atlas"
              className="mt-8 space-y-8 mb-2"
            >
              <FinalCTA />
            </section>
          </>
        </header>

        {/* Floating CTA + Modal (opens chatbot) */}
        <div className="fixed right-3 bottom-3 sm:right-6 sm:bottom-6 z-50">
          <button
            data-testid="try-chat-btn"
            onClick={() => setChatOpen(true)}
            aria-label="Open Atlas demo"
            className="inline-flex items-center gap-2 sm:gap-3 rounded-full bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 px-4 py-2.5 sm:px-6 sm:py-3 text-sm sm:text-base font-semibold text-white shadow-lg hover:brightness-110 transition-transform focus:outline-none focus:ring-4 focus:ring-blue-300"
          >
            <img
              src="/logos/atlas-mark-dark-bg.png"
              alt="Atlas Logo"
              className="h-5 w-5 sm:h-6 sm:w-6 object-contain filter brightness-0 invert opacity-90"
            />
            <span className="hidden sm:inline">Try Atlas Now</span>
            <span className="sm:hidden">Try Atlas</span>
          </button>

          {chatOpen && (
            <ModalOverlayWithRails
              onClose={() => setChatOpen(false)}
            />
          )}
        </div>

        {/* Footer */}
        <footer className="mx-auto max-w-6xl px-2 pb-8">
          <div className="mx-auto max-w-md rounded-2xl bg-white/80 backdrop-blur ring-1 ring-slate-200 shadow-sm p-5 text-center">
            {/* Logo badge */}
            <div className="flex items-center justify-center gap-3">
              <img
                src="/logos/atlas-mark-dark-bg.png"
                alt="Atlas Logo"
                className="h-10 w-10 object-contain drop-shadow-[0_1px_2px_rgba(0,0,0,0.25)]"
              />
              <div className="text-left leading-tight">
                <div className="text-slate-800 text-base font-semibold tracking-tight">
                  ATLAS
                </div>
                <div className="text-[11px] tracking-wide text-[#4d7c9e]">
                  AI built for{" "}
                  <span className="italic">your</span>{" "}
                  business.
                </div>
              </div>
            </div>

            {/* Copyright */}
            <div className="text-[11px] text-slate-600 pt-3">
              © {new Date().getFullYear()} Atlas. Built by
              Naga Chaganti. All rights reserved.
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
