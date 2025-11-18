import { Link } from "react-router-dom";
import { Card, CardHeader, CardContent, CardTitle } from "@/components/ui/card";
import { ExternalLink, FileText, Share2, Database, Layers, PlayCircle } from "lucide-react";

export default function ExploreAtlas() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 via-blue-50/40 to-blue-100/30 pb-24 text-slate-800">
      <div className="mx-auto max-w-6xl px-4 py-16 space-y-16">

        {/* HEADER */}
        <section className="text-center space-y-4">
          <p className="text-xs font-medium uppercase tracking-wide text-blue-700">
            Explore Atlas
          </p>
          <h1 className="text-3xl font-semibold text-slate-900">
            Architecture, data model, and real operational use cases.
          </h1>
          <p className="text-base text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Atlas was built to answer real operational questions using real ERP,
            inventory, logistics, and supplier data — not demo numbers. This page
            goes deeper into how it works.
          </p>
        </section>

        {/* 1. ARCHITECTURE + FRAMEWORK */}
        <section className="grid gap-6 md:grid-cols-2">
          {/* Architecture Diagram Card */}
          <Card className="rounded-xl bg-white/80 backdrop-blur shadow ring-1 ring-blue-100/70 flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold text-slate-900">
                    Atlas Architecture
                  </CardTitle>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    High-level view of how Atlas ingests operational data,
                    builds context, reasons over it, and returns an answer you can trust.
                  </p>
                </div>
                <Layers className="h-5 w-5 text-blue-600 shrink-0" />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Screenshot / thumbnail placeholder - replace with your actual img/iframe */}
              <div className="rounded-lg border border-slate-200 bg-slate-50/60 text-center text-slate-400 text-sm p-12">
                {/* TODO: Replace this div with your actual <img src={...} /> or diagram preview */}
                [ Architecture Diagram Preview ]
              </div>

              <a
                href="#"
                className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:underline"
              >
                <ExternalLink className="h-4 w-4" />
                View full architecture
              </a>
            </CardContent>
          </Card>

          {/* Supply Chain Framework Card */}
          <Card className="rounded-xl bg-white/80 backdrop-blur shadow ring-1 ring-blue-100/70 flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold text-slate-900">
                    Supply Chain Framework & Architecture Notes
                  </CardTitle>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    How Atlas stitches together purchase orders, on-hand inventory,
                    replenishment, logistics events, and supplier risk — and keeps
                    the operational context intact.
                  </p>
                </div>
                <FileText className="h-5 w-5 text-blue-600 shrink-0" />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Inline doc/iframe preview placeholder */}
              <div className="rounded-lg border border-slate-200 bg-white text-slate-700 text-sm leading-relaxed p-4 max-h-40 overflow-hidden">
                {/* TODO: Drop your actual embedded notes / Notion / markdown summary here */}
                Atlas tracks relationships: which PO feeds which SO, which supplier
                is slipping, which item is at risk of stocking out, and what that
                means for the customer. It’s built for supply chain first, and
                expands to similar operational models in service, retail, and field ops.
              </div>

              <button
                className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white/70 px-3 py-2 text-sm text-slate-700 shadow-sm hover:bg-slate-50"
              >
                <Share2 className="h-4 w-4" />
                Copy sharable link
              </button>
            </CardContent>
          </Card>
        </section>

        {/* 2. USE CASES */}
        <section className="space-y-6">
          <div className="flex flex-col items-start md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-blue-700">
                What teams ask Atlas
              </p>
              <h2 className="text-xl font-semibold text-slate-900">
                Real questions from planners, buyers, and operations.
              </h2>
              <p className="text-sm text-slate-600 leading-relaxed max-w-2xl">
                Atlas is built for real work: inventory risk, late suppliers,
                fulfillment impact, throughput, service issues. You ask in plain English.
                Atlas answers with context and next steps.
              </p>
            </div>
          </div>

          {/* Use case cards grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card className="rounded-xl bg-white/80 backdrop-blur shadow ring-1 ring-blue-100/70">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-slate-900">
                  Planner / Allocation
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-slate-600 leading-relaxed space-y-2">
                <p>“Do we have enough stock to cover order 4819?”</p>
                <p>“Which customers will get hit if this PO slips?”</p>
                <p>“What’s the top driver behind low on-hand at DC-07?”</p>
              </CardContent>
            </Card>

            <Card className="rounded-xl bg-white/80 backdrop-blur shadow ring-1 ring-blue-100/70">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-slate-900">
                  Purchasing / Supplier Management
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-slate-600 leading-relaxed space-y-2">
                <p>“Which suppliers are chronically late this week?”</p>
                <p>“Show me open POs at risk of missing customer ship dates.”</p>
                <p>“Where are we exposed today?”</p>
              </CardContent>
            </Card>

            <Card className="rounded-xl bg-white/80 backdrop-blur shadow ring-1 ring-blue-100/70">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-semibold text-slate-900">
                  Operations / Fulfillment
                </CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-slate-600 leading-relaxed space-y-2">
                <p>“What’s running late right now and why?”</p>
                <p>“Which shipments are blocked because of inventory?”</p>
                <p>“Where are we going to miss SLA tomorrow?”</p>
              </CardContent>
            </Card>
          </div>
        </section>

        {/* 3. PRESENTATION DECK */}
        <section className="grid gap-6 md:grid-cols-2">
          <Card className="rounded-xl bg-white/80 backdrop-blur shadow ring-1 ring-blue-100/70 flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold text-slate-900">
                    Atlas Overview Deck
                  </CardTitle>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    Short walkthrough of the problem, the approach, and why Atlas
                    is different from dashboards or chatbots bolted to ERP.
                  </p>
                </div>
                <PlayCircle className="h-5 w-5 text-blue-600 shrink-0" />
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Deck preview placeholder */}
              <div className="rounded-lg border border-slate-200 bg-slate-50/60 text-center text-slate-400 text-sm p-12">
                {/* TODO: Embed your <iframe> deck preview here */}
                [ Deck Preview / Slides Embed ]
              </div>

              <a
                href="#"
                className="inline-flex items-center gap-2 text-sm font-medium text-blue-600 hover:underline"
              >
                <ExternalLink className="h-4 w-4" />
                View full deck
              </a>
            </CardContent>
          </Card>

          {/* 4. SAMPLE ERP DATA MODEL */}
          <Card className="rounded-xl bg-white/80 backdrop-blur shadow ring-1 ring-blue-100/70 flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-lg font-semibold text-slate-900">
                    Example ERP Data Model
                  </CardTitle>
                  <p className="text-sm text-slate-600 leading-relaxed">
                    Sanitized PO, SO, inventory, and logistics extracts — so you
                    can reproduce parts of the Atlas demo in your own sandbox.
                  </p>
                </div>
                <Database className="h-5 w-5 text-blue-600 shrink-0" />
              </div>
            </CardHeader>
            <CardContent className="space-y-4 text-sm text-slate-600 leading-relaxed">
              <p>
                Includes purchase orders, sales orders, on-hand by location,
                inbound shipments, supplier performance — aligned to how Atlas reasons.
              </p>
              <p>
                If you’d like early access to the dataset or data dictionary,
                reach out and I’ll share it.
              </p>

              <div className="flex flex-wrap gap-2">
                <a
                  href="mailto:sap4naga@gmail.com"
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-300 bg-white/70 px-3 py-2 text-sm text-slate-700 shadow-sm hover:bg-slate-50"
                >
                  <span>Email me for access</span>
                </a>

                <a
                  href="https://www.linkedin.com/in/sap4naga"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-indigo-600 to-blue-500 px-3 py-2 text-sm font-medium text-white shadow hover:opacity-95"
                >
                  <span>Connect on LinkedIn</span>
                </a>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* 5. CTA: TRY ATLAS */}
        <section className="text-center space-y-4 pt-8">
          <h2 className="text-xl font-semibold text-slate-900">
            Try Atlas
          </h2>
          <p className="text-sm text-slate-600 leading-relaxed max-w-xl mx-auto">
            Interact with the Atlas AI copilot. Ask operational questions in plain
            English and see how it responds with context, not guesses.
          </p>

          {/* Placeholder for your live chat / demo component */}
          <div className="mx-auto max-w-2xl rounded-xl bg-white/80 backdrop-blur shadow ring-1 ring-blue-100/70 p-6 text-left text-slate-700">
            [ Embed live Atlas chat / demo component here ]
          </div>

          <p className="text-xs text-slate-500 italic pt-4">
            Atlas — AI built for your business.
          </p>
        </section>
      </div>
    </main>
  );
}
