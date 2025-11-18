import React from "react";
import AtlasChatUI from "./AtlasChatUI.jsx";
import PersonaRailFloating from "./PersonaRailFloating.jsx";
import DatasetRailFloating from "./DatasetRailFloating.jsx";

export default function AtlasDemoScreen({ onClose }) {
  const [showDatasetsView, setShowDatasetsView] = React.useState(false);
  const [openDataset, setOpenDataset] = React.useState(null);
  const [stagedPrompt, setStagedPrompt] = React.useState("");
  const [debugContext, setDebugContext] = React.useState("");

  const contentRef = React.useRef(null);
  React.useEffect(() => {
    function handleClickOutside(e) {
      if (!showDatasetsView && contentRef.current && !contentRef.current.contains(e.target)) {
        onClose?.();
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showDatasetsView, onClose]);

  const DATASETS = [
    {
      fileName: "idx_v_ir_status_enriched.csv",
      domain: "PO Status",
      columns: [
        "po_number","item","ordered_qty","received_qty","need_by_date",
        "last_receipt_date","po_status","Context_Summary",
      ],
      example: 'Ask: "Show the status and expected receipt date for PO-0000155."',
      previewRows: [
        { po_number:"PO-0000155", item:"ITEM-00108", ordered_qty:"35", received_qty:"35",
          need_by_date:"2025-10-04", last_receipt_date:"2025-10-08",
          po_status:"REQUIRES REAPPROVAL",
          Context_Summary:"PO PO-0000155 for 35 ITEM-00108s... Delay: 4 days. SLA_BREACH." },
        { po_number:"PO-0000221", item:"ITEM-00014", ordered_qty:"184", received_qty:"186",
          need_by_date:"2025-09-07", last_receipt_date:"2025-10-11",
          po_status:"REQUIRES REAPPROVAL",
          Context_Summary:"PO PO-0000221 for 184 ITEM-00014s... Delay: 34 days. SLA_BREACH." },
        { po_number:"PO-0000179", item:"ITEM-00198", ordered_qty:"122", received_qty:"120",
          need_by_date:"2025-06-19", last_receipt_date:"2025-09-16",
          po_status:"REJECTED",
          Context_Summary:"PO PO-0000179 for 122 ITEM-00198s... Delay: 121 days. SLA_BREACH." },
      ],
    },
    {
      fileName: "onhand_inventory_enriched.csv",
      domain: "Inventory",
      columns: [
        "item","organization_id","onhand_qty","reserved_qty","available_qty",
        "subinventory_code","locator_code","last_update_date","Context_Summary",
      ],
      example: 'Ask: "Show me the on-hand vs reserved quantity for ITEM-00047."',
      previewRows: [
        { item:"ITEM-00001", organization_id:"201", onhand_qty:"107", reserved_qty:"19",
          available_qty:"88", subinventory_code:"WIP", locator_code:"A01-B01-C02",
          last_update_date:"2025-09-22",
          Context_Summary:"ITEM ITEM-00001 has 107 units in WH WIP. Available: 88; Reserved: 19." },
        { item:"ITEM-00005", organization_id:"301", onhand_qty:"161", reserved_qty:"4",
          available_qty:"157", subinventory_code:"RM", locator_code:"A01-B02-C01",
          last_update_date:"2025-10-01",
          Context_Summary:"ITEM ITEM-00005 has 161 units in WH RM. Available: 157; Reserved: 4." },
        { item:"ITEM-00022", organization_id:"101", onhand_qty:"85", reserved_qty:"14",
          available_qty:"71", subinventory_code:"RM", locator_code:"A05-B01-C02",
          last_update_date:"2025-09-12",
          Context_Summary:"ITEM ITEM-00022 has 85 units in WH RM. Available: 71; Reserved: 14." },
      ],
    },
    {
      fileName: "lpn_tracking_enriched.csv",
      domain: "Fulfillment",
      columns: [
        "lpn_number","delivery_number","carrier_name","ship_from_location_id",
        "ship_to_location_id","delivery_status","tracking_number","requested_quantity",
        "shipped_quantity","customer_or_site_name","Context_Summary",
      ],
      example: 'Ask: "Show all LPNs created for SO-100078 and their shipment status."',
      previewRows: [
        { lpn_number:"LPN-0000242", delivery_number:"DEL-000222", carrier_name:"UPS",
          ship_from_location_id:"102", ship_to_location_id:"201", delivery_status:"CL",
          tracking_number:"1Z847416741595523", requested_quantity:"160", shipped_quantity:"161",
          customer_or_site_name:"KNOXVILLE_SITE",
          Context_Summary:"LPN-0000242 for 161 ITEM-00035s via UPS from WH 102 → KNOXVILLE_SITE. Status: CLOSED." },
        { lpn_number:"LPN-0000160", delivery_number:"DEL-000200", carrier_name:"UPS",
          ship_from_location_id:"101", ship_to_location_id:"101", delivery_status:"STAGED",
          tracking_number:"1Z853710349083933", requested_quantity:"190", shipped_quantity:"190",
          customer_or_site_name:"KNOXVILLE_SITE",
          Context_Summary:"LPN-0000160 for 190 ITEM-00095s via UPS from WH 101 → KNOXVILLE_SITE. Status: STAGED. SLA_BREACH." },
        { lpn_number:"LPN-0000201", delivery_number:"DEL-000053", carrier_name:"FedEx",
          ship_from_location_id:"201", ship_to_location_id:"201", delivery_status:"IN_TRANSIT",
          tracking_number:"1Z567692741154444", requested_quantity:"170", shipped_quantity:"168",
          customer_or_site_name:"KNOXVILLE_SITE",
          Context_Summary:"LPN-0000201 for 168 ITEM-00293s via FedEx from WH 201 → KNOXVILLE_SITE. Status: IN_TRANSIT." },
      ],
    },
  ];

  const previewMap = React.useMemo(() => {
    const map = {};
    for (const ds of DATASETS) {
      map[ds.fileName] = { columns: ds.columns, rows: ds.previewRows };
    }
    return map;
  }, [DATASETS]);

  function ChatView() {
    return (
      <div
        ref={contentRef}
        className="
          grid
          grid-cols-[140px_minmax(400px,1fr)_580px]
          gap-3
          w-full max-w-[min(100vw-1rem,1600px)]
          overflow-x-hidden
        "
      >
        {/* LEFT rail (Personas) */}
        <div className="hidden xl:flex flex-col max-h-[85vh]">
          <div className="flex-1 rounded-2xl bg-white/90 backdrop-blur ring-1 ring-blue-100/70 shadow-xl p-2.5 flex flex-col overflow-hidden">
            <div className="flex-1 min-h-0 overflow-y-auto">
              <PersonaRailFloating
                onSelectPrompt={(promptText) => setStagedPrompt(promptText)}
              />
            </div>
          </div>
        </div>

        {/* MIDDLE chat */}
        <div
          className="
            flex flex-col
            min-w-0 max-w-full max-h-[85vh]
            rounded-2xl bg-white shadow-2xl ring-1 ring-slate-200
          "
        >
          {/* header */}
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 border-b border-slate-200 bg-white/80 backdrop-blur px-4 py-3 rounded-t-2xl">
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <img src="/logos/atlas-mark-dark-bg.png" alt="Atlas Logo" className="h-6 w-6 object-contain filter brightness-0 opacity-90" />
                <div className="text-slate-900 text-lg font-semibold leading-tight tracking-tight">
                  Atlas – Live Demo for
                </div>
                <span className="ml-2 rounded-full bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 px-2.5 py-0.5 text-[11px] font-medium text-white shadow-sm shadow-[0_0_6px_rgba(59,130,246,0.35)]">
                  Supply Chain Operations
                </span>
              </div>
              <div className="text-[12px] text-slate-500 leading-snug">
                Ask Atlas anything about purchase orders, inventory, or shipments. Sample Prompts on the left.
              </div>
            </div>

            <button
              onClick={onClose}
              className="self-start md:self-auto rounded-lg bg-blue-600 text-white text-sm font-medium px-3 py-1.5 hover:bg-blue-700"
            >
              Close
            </button>
          </div>

          {/* body */}
          <div className="flex-1 min-w-0 overflow-hidden p-4">
            <AtlasChatUI
              incomingPrompt={stagedPrompt}
              onContextUpdate={(ctx) => setDebugContext(ctx)}
            />
          </div>
        </div>

        {/* RIGHT rail (Data Sources) */}
        <div className="hidden xl:flex flex-col max-h-[85vh]">
          <div className="flex-1 rounded-2xl bg-white/90 backdrop-blur ring-1 ring-blue-100/70 shadow-xl p-3 flex flex-col overflow-hidden">
            <DatasetRailFloating
              datasetsList={DATASETS.map((ds) => ({
                name: ds.fileName, domain: ds.domain, example: ds.example, columns: ds.columns,
              }))}
              debugContext={debugContext}
              onOpenDatasets={() => {
                setShowDatasetsView(true);
                setOpenDataset(null);
              }}
            />
          </div>
        </div>
      </div>
    );
  }

  function DatasetExplorerOverlay() {
    return (
      <div
        className="
          flex flex-col
          w-full max-w-[1400px]
          max-h-[85vh]
          rounded-2xl bg-white/95 backdrop-blur
          ring-1 ring-blue-100/70 shadow-2xl
        "
      >
        {/* header */}
        <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 border-b border-slate-200 bg-white/70 backdrop-blur px-5 py-4 rounded-t-2xl">
          <div className="flex flex-col">
            <div className="text-slate-900 text-lg font-semibold leading-tight tracking-tight flex items-center gap-2">
              <img src="/logos/atlas-mark-dark-bg.png" alt="Atlas Logo" className="h-6 w-6 object-contain filter brightness-0 opacity-90" />
              <span>Data Sources in this Demo</span>
              <span className="rounded-full bg-blue-600 text-white px-2 py-[2px] text-[10px] font-medium leading-none">Read-only</span>
            </div>
            <div className="text-[12px] text-slate-500 leading-snug mt-1">
              These are the actual tables/files Atlas is allowed to answer from.
              Click one to inspect real rows, then copy an ID and ask Atlas.
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setShowDatasetsView(false)}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-[12px] font-medium text-slate-700 shadow-sm hover:bg-slate-50 active:bg-slate-100"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7 7-7" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 12h18" />
              </svg>
              <span>Back to Chat</span>
            </button>

            <button
              onClick={onClose}
              className="inline-flex items-center rounded-lg bg-blue-600 text-white text-sm font-medium px-3 py-1.5 hover:bg-blue-700"
            >
              Close
            </button>
          </div>
        </div>

        {/* body */}
        <div className="flex-1 min-h-0 overflow-y-auto px-5 pb-5 pt-4">
          <div className="rounded-xl bg-white ring-1 ring-slate-200 shadow-sm overflow-hidden text-[13px] text-slate-700">
            <table className="w-full border-collapse text-left min-w-[800px]">
              <thead className="text-[11px] uppercase text-slate-500 border-b border-slate-200 bg-slate-50/60">
                <tr>
                  <th className="py-3 pl-4 pr-3 font-medium text-slate-600">File / Table</th>
                  <th className="py-3 pr-3 font-medium text-slate-600">Domain</th>
                  <th className="py-3 pr-3 font-medium text-slate-600">Column Highlights</th>
                  <th className="py-3 pr-4 font-medium text-slate-600">Example Prompt</th>
                </tr>
              </thead>
              <tbody className="align-top text-[12px] text-slate-800">
                {DATASETS.map((ds) => (
                  <React.Fragment key={ds.fileName}>
                    <tr
                      className={`border-b border-slate-200 cursor-pointer hover:bg-slate-50 ${openDataset === ds.fileName ? "bg-slate-50/80" : ""}`}
                      onClick={() => setOpenDataset(openDataset === ds.fileName ? null : ds.fileName)}
                    >
                      <td className="py-3 pl-4 pr-3 font-mono text-[12px] text-slate-900 break-all align-top">{ds.fileName}</td>
                      <td className="py-3 pr-3 align-top">
                        <span className="inline-flex items-center rounded-full bg-slate-900 text-white px-2 py-[2px] text-[10px] font-medium leading-none">
                          {ds.domain}
                        </span>
                      </td>
                      <td className="py-3 pr-3 text-slate-600 align-top">{ds.columns.join(", ")}</td>
                      <td className="py-3 pr-4 text-slate-700 align-top">{ds.example}</td>
                    </tr>

                    {openDataset === ds.fileName && (
                      <tr className="border-b border-slate-200 bg-slate-50/40">
                        <td className="pl-4 pr-4 py-4 align-top" colSpan={4}>
                          <div className="border border-slate-200 rounded-xl overflow-x-auto overflow-y-auto max-h-[260px] bg-white shadow-inner text-[12px] leading-tight font-mono text-slate-900">
                            <table className="min-w-full border-collapse">
                              <thead className="bg-slate-100 text-slate-600 text-[10px] uppercase tracking-wide sticky top-0 z-[1] border-b border-slate-200">
                                <tr>
                                  {previewMap[ds.fileName].columns.map((col) => (
                                    <th key={col} className="text-left font-medium px-3 py-2 border-r border-slate-200 last:border-r-0 whitespace-nowrap">
                                      {col}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody className="text-[11px] text-slate-800">
                                {previewMap[ds.fileName].rows.map((rowObj, ridx) => (
                                  <tr key={ridx} className={ridx % 2 === 0 ? "bg-white" : "bg-slate-50/60"}>
                                    {previewMap[ds.fileName].columns.map((col) => (
                                      <td key={col} className="align-top px-3 py-2 border-b border-slate-100 border-r border-slate-200 last:border-r-0 whitespace-nowrap">
                                        {rowObj[col]}
                                      </td>
                                    ))}
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                          <div className="text-[11px] text-slate-500 mt-2 leading-snug">
                            These rows are from the actual demo data Atlas is allowed to read. Copy an ID (PO number, ITEM, LPN) and ask Atlas in plain English.
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))}
              </tbody>
            </table>

            <div className="text-[11px] text-slate-500 leading-snug px-4 py-3 border-t border-slate-200 bg-white">
              Tip: copy an ID (PO number, item ID, LPN) and ask: “Show received vs ordered qty for PO-0000155.”
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      className="
        fixed inset-0 z-[9999]
        flex items-start justify-center
        bg-slate-900/40 backdrop-blur-sm
        p-4 overflow-x-hidden
      "
    >
      <div className="flex items-start justify-center w-full pt-16">
        {showDatasetsView ? <DatasetExplorerOverlay /> : <ChatView />}
      </div>
    </div>
  );
}
