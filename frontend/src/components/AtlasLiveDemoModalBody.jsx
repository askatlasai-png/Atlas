import React from "react";
import AtlasChatUI from "./AtlasChatUI";
import DatasetRailFloating from "./DatasetRailFloating";

export default function AtlasLiveDemoModalBody() {
  const [debugContext, setDebugContext] = React.useState("");

  const DATASETS = [
    {
      name: "idx_v_ir_status_enriched.csv",
      domain: "PO Status",
      example: `Ask: "Show the status and expected receipt date for PO-0000155."`,
    },
    {
      name: "onhand_inventory_enriched.csv",
      domain: "Inventory",
      example: `Ask: "Show me the on-hand vs reserved quantity for ITEM-00047."`,
    },
    {
      name: "lpn_tracking_enriched.csv",
      domain: "Fulfillment",
      example: `Ask: "Show all LPNs created for SO-100078 and their shipment status."`,
    },
  ];

  return (
    <div
      className="
        flex flex-col lg:flex-row
        gap-4
        max-h-[75vh]
      "
    >
      {/* CENTER CHAT takes most of the width */}
      <div className="flex-1 min-w-0 flex justify-center">
        <AtlasChatUI
          onContextUpdate={(ctx) => {
            setDebugContext(ctx);
          }}
        />
      </div>

      {/* RIGHT DATASETS stays narrow on desktop, hidden on small screens? (your call) */}
      <div className="hidden lg:block w-[260px] flex-shrink-0">
        <DatasetRailFloating
          datasetsList={DATASETS}
          debugContext={debugContext}
        />
      </div>
    </div>
  );
}
