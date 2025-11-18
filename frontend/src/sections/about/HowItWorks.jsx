// HowItWorks.jsx
import React from "react";
import { UploadCloud, Braces, Brain, CheckCircle2 } from "lucide-react";

export default function HowItWorks() {
const steps = [
  {
    icon: UploadCloud,
    title: "We connect to your real data",
    desc:
      "Atlas plugs into the systems you already run — ERP, inventory, purchasing, POS, service logs. No rip-and-replace. It keeps what matters: orders, stock levels, suppliers, work orders, shipments.",
  },
  {
    icon: Braces,
    title: "We build business context, not just tables",
    desc:
      "Atlas understands relationships: which PO feeds which order, which supplier is slipping, which machine is idle. It keeps that context so you don’t have to chase it across five systems.",
  },
  {
    icon: Brain,
    title: "You ask a question in plain English",
    desc:
      "“Do we have enough to ship order 4819?”\n“What’s running late?”\n“Where are we exposed today?”\n\nAtlas uses your live data to generate an answer — not a guess.",
  },
  {
    icon: CheckCircle2,
    title: "You get an answer you can act on",
    desc:
      "You get a clear summary, the key risks, and next steps — in normal language. Atlas also shows the source data so you can trust it. No dashboards. No SQL. No screen-hopping.",
  },
];


  return (
    <section
      id="how-it-works"
      className="mt-8 space-y-8"
    >
      {/* header */}
      <div className="text-center mb-8">
        <p className="text-xs font-medium uppercase tracking-wide text-blue-700">
          How Atlas Works
        </p>

        <h2 className="mt-2 text-2xl font-semibold text-slate-900 leading-snug">
          From scattered systems to a clear answer you can act on.
        </h2>

        <p className="mt-3 text-base text-slate-600 leading-relaxed max-w-3xl mx-auto">
          Atlas pulls from the systems you already run, keeps the operational context,
          and turns it into answers you can actually use — in plain language anyone on the team can work with.
        </p>

      </div>

      {/* steps grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {steps.map((step) => (
          <div
            key={step.title}
            className="rounded-xl bg-white/90 backdrop-blur shadow ring-1 ring-slate-200 p-5"
          >
            <div className="flex items-center gap-2">
              <step.icon className="h-5 w-5 text-slate-800" />
              <p className="font-semibold text-slate-900 text-base">
                {step.title}
              </p>
            </div>
            <p className="mt-2 text-sm text-slate-600 leading-relaxed">
              {step.desc}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
