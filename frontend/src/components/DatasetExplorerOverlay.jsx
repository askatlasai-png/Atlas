import React from "react";

export default function DatasetExplorerOverlay({
  DATASETS,
  previewMap,
  openDataset,
  setOpenDataset,
  onBackToChat,
  onClose,
}) {
  return (
    <div className="flex flex-col w-full max-w-[1400px] max-h-[85vh] rounded-2xl bg-white/95 backdrop-blur ring-1 ring-blue-100/70 shadow-2xl p-0">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 border-b border-slate-200 bg-white/70 backdrop-blur px-5 py-4 rounded-t-2xl">
        <div className="flex flex-col">
          <div className="text-slate-900 text-lg font-semibold leading-tight tracking-tight flex items-center gap-2">
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
          <div className="text-[12px] text-slate-500 leading-snug mt-1">
            These are the actual tables/files Atlas is allowed to answer from.
            Click one to inspect real rows. Copy an ID and ask Atlas.
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <button
            onClick={onBackToChat}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-[12px] font-medium text-slate-700 shadow-sm hover:bg-slate-50 active:bg-slate-100"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth="2"
            >
              <path
                d="M10 19l-7-7 7-7"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <path
                d="M3 12h18"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
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

      {/* Body */}
      <div className="flex-1 min-h-0 overflow-y-auto px-5 pb-5 pt-4">
        <div className="rounded-xl bg-white ring-1 ring-slate-200 shadow-sm overflow-hidden text-[13px] text-slate-700">
          <table className="w-full border-collapse text-left min-w-[800px]">
            <thead className="text-[11px] uppercase text-slate-500 border-b border-slate-200 bg-slate-50/60">
              <tr>
                <th className="py-3 pl-4 pr-3 font-medium text-slate-600">
                  File / Table
                </th>
                <th className="py-3 pr-3 font-medium text-slate-600">Domain</th>
                <th className="py-3 pr-3 font-medium text-slate-600">
                  Column Highlights
                </th>
                <th className="py-3 pr-4 font-medium text-slate-600">
                  Example Prompt
                </th>
              </tr>
            </thead>

            <tbody className="align-top text-[12px] text-slate-800">
              {DATASETS.map((ds) => (
                <React.Fragment key={ds.fileName}>
                  {/* clickable summary row */}
                  <tr
                    className={`border-b border-slate-200 cursor-pointer hover:bg-slate-50 ${
                      openDataset === ds.fileName ? "bg-slate-50/80" : ""
                    }`}
                    onClick={() => {
                      setOpenDataset(
                        openDataset === ds.fileName ? null : ds.fileName
                      );
                    }}
                  >
                    <td className="py-3 pl-4 pr-3 font-mono text-[12px] text-slate-900 break-all align-top">
                      {ds.fileName}
                    </td>

                    <td className="py-3 pr-3 align-top">
                      <span className="inline-flex items-center rounded-full bg-slate-900 text-white px-2 py-[2px] text-[10px] font-medium leading-none">
                        {ds.domain}
                      </span>
                    </td>

                    <td className="py-3 pr-3 text-slate-600 align-top">
                      {ds.columns.join(", ")}
                    </td>

                    <td className="py-3 pr-4 text-slate-700 align-top">
                      {ds.example}
                    </td>
                  </tr>

                  {/* expanded spreadsheet preview */}
                  {openDataset === ds.fileName && (
                    <tr className="border-b border-slate-200 bg-slate-50/40">
                      <td className="pl-4 pr-4 py-4 align-top" colSpan={4}>
                        <div className="border border-slate-200 rounded-xl overflow-x-auto overflow-y-auto max-h-[260px] bg-white shadow-inner text-[12px] leading-tight font-mono text-slate-900">
                          <table className="min-w-full border-collapse">
                            <thead className="bg-slate-100 text-slate-600 text-[10px] uppercase tracking-wide sticky top-0 z-[1] border-b border-slate-200">
                              <tr>
                                {previewMap[ds.fileName].columns.map((col) => (
                                  <th
                                    key={col}
                                    className="text-left font-medium px-3 py-2 border-r border-slate-200 last:border-r-0 whitespace-nowrap"
                                  >
                                    {col}
                                  </th>
                                ))}
                              </tr>
                            </thead>

                            <tbody className="text-[11px] text-slate-800">
                              {previewMap[ds.fileName].rows.map(
                                (rowObj, ridx) => (
                                  <tr
                                    key={ridx}
                                    className={
                                      ridx % 2 === 0
                                        ? "bg-white"
                                        : "bg-slate-50/60"
                                    }
                                  >
                                    {previewMap[ds.fileName].columns.map(
                                      (col) => (
                                        <td
                                          key={col}
                                          className="align-top px-3 py-2 border-b border-slate-100 border-r border-slate-200 last:border-r-0 whitespace-nowrap"
                                        >
                                          {rowObj[col]}
                                        </td>
                                      )
                                    )}
                                  </tr>
                                )
                              )}
                            </tbody>
                          </table>
                        </div>

                        <div className="text-[11px] text-slate-500 mt-2 leading-snug font-normal not-italic">
                          These rows are from the actual demo data Atlas is
                          allowed to read. Copy an ID (PO number, ITEM, LPN)
                          and ask Atlas in plain English.
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>

          <div className="text-[11px] text-slate-500 leading-snug px-4 py-3 border-t border-slate-200 bg-white">
            Tip: copy an ID (PO number, item ID, LPN) and ask:
            “Show received vs ordered qty for PO-0000155.”
          </div>
        </div>
      </div>
    </div>
  );
}
