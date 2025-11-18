import React from "react";
import { PlayCircle, MessageCircle, LineChart } from "lucide-react";

export default function SeeAtlasInAction() {
  return (
    <section
      id="see-atlas-in-action"
      className="mt-12 mx-auto max-w-6xl px-4 space-y-8 scroll-mt-24"
    >
      {/* Header */}
      <div className="text-center space-y-3">
        <p className="text-xs font-medium uppercase tracking-wide text-blue-700">
          See Atlas in Action
        </p>
        <h2 className="text-2xl font-semibold text-slate-900 leading-snug">
          Ask a question. Watch Atlas work.
        </h2>
        <p className="text-base text-slate-600 max-w-3xl mx-auto leading-relaxed">
          Here’s what Atlas actually looks like in use — answering real
          operational questions over ERP and supply chain data.
        </p>
      </div>

      {/* Layout: left = visual, right = what’s happening */}
      <div className="grid gap-6 md:grid-cols-[minmax(0,1.3fr)_minmax(0,1fr)] items-start">
        {/* Visual / screenshot placeholder */}
        <div className="rounded-2xl bg-white/90 backdrop-blur shadow-lg ring-1 ring-blue-100/70 p-4 md:p-5">
          {/* Replace this with your real GIF / screenshot */}
          <div className="aspect-video rounded-xl border border-slate-200 bg-slate-950/95 flex flex-col justify-center items-center text-slate-400 text-sm">
            {/* TODO: swap for <img src="/images/atlas-chat-demo.png" ... /> or an embedded video */}
            <PlayCircle className="h-10 w-10 mb-2 opacity-80" />
            <p className="font-medium text-slate-100">
              [ Atlas live chat / demo preview ]
            </p>
            <p className="mt-1 text-xs text-slate-400">
              Ask: “Which POs are late this week and who is impacted?”
            </p>
          </div>

          <p className="mt-3 text-xs text-slate-500 text-center">
            Replace this placeholder with your actual screenshot or screen
            recording of the Atlas chat UI.
          </p>
        </div>

        {/* What you can ask / what Atlas returns */}
        <div className="space-y-4">
          <div className="rounded-2xl bg-white/90 backdrop-blur shadow ring-1 ring-slate-200 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <MessageCircle className="h-4 w-4 text-slate-800" />
              <span>Example questions you can ask</span>
            </div>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>• “Do we have enough stock to ship order 4819?”</li>
              <li>• “Which suppliers are running late this week?”</li>
              <li>• “Where are we going to miss SLA tomorrow?”</li>
            </ul>
          </div>

          <div className="rounded-2xl bg-white/90 backdrop-blur shadow ring-1 ring-slate-200 p-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
              <LineChart className="h-4 w-4 text-slate-800" />
              <span>What Atlas gives you back</span>
            </div>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>• A plain-English summary of what’s going on.</li>
              <li>• The key risks and impacted customers or orders.</li>
              <li>• A traceable trail back to the underlying rows and tables.</li>
            </ul>
          </div>

          <p className="text-xs text-slate-500">
            You can also embed a short Loom/YouTube demo here later — but even a
            clean static screenshot reduces the “too much text” feeling.
          </p>
        </div>
      </div>
    </section>
  );
}
