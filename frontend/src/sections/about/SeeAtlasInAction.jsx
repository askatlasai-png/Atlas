import React from "react";
import { MessageCircle, CheckCircle2, PlayCircle } from "lucide-react";

export default function SeeAtlasInAction() {
  return (
    <section className="w-full space-y-6 md:space-y-8">
      {/* Heading */}
      <div className="text-center">
        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">
          See Atlas in Action
        </p>

        <h2 className="mt-2 text-xl md:text-2xl lg:text-3xl font-semibold text-slate-900">
          Ask a question. Watch Atlas work.
        </h2>

        <p className="mt-2 text-sm md:text-base text-slate-600 max-w-3xl mx-auto leading-relaxed">
          Here’s what Atlas actually looks like in use — answering real
          operational questions over ERP and supply chain data.
        </p>
      </div>

      {/* Content grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5 md:gap-6">
        {/* Premium video frame */}
        <div className="relative">
          <div className="rounded-2xl bg-gradient-to-br from-slate-900 via-slate-950 to-slate-900 p-[1.5px] shadow-xl shadow-slate-900/25">
            <div className="relative h-[220px] sm:h-[260px] md:h-[300px] lg:h-[320px] rounded-[1.1rem] overflow-hidden bg-black">
              <iframe
                className="absolute inset-0 w-full h-full"
                src="https://www.youtube.com/embed/M5wxTALfgXM"
                title="Atlas AI Demo"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowFullScreen
              ></iframe>

              {/* Soft play overlay (doesn't block clicks) */}
              <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
                <div className="h-16 w-16 rounded-full bg-black/30 backdrop-blur-sm border border-white/40 flex items-center justify-center shadow-[0_0_25px_rgba(15,23,42,0.8)]">
                  <PlayCircle className="h-9 w-9 text-white/85" />
                </div>
              </div>

              {/* Bottom gradient fade */}
              <div className="pointer-events-none absolute inset-x-0 bottom-0 h-20 bg-gradient-to-t from-black/40 via-black/10 to-transparent" />
            </div>
          </div>
        </div>

        {/* Right side: example questions + what Atlas gives back */}
        <div className="flex flex-col gap-4 md:gap-5">
          {/* Example questions */}
          <div className="rounded-xl bg-white/90 backdrop-blur ring-1 ring-slate-200/70 p-4 md:p-5 shadow-sm">
            <div className="flex items-center gap-2 text-slate-900 font-medium">
              <MessageCircle className="h-4 w-4 text-blue-600" />
              <span>Example questions you can ask</span>
            </div>
            <ul className="mt-2 ml-5 list-disc text-sm text-slate-600 space-y-1.5">
              <li>“Do we have enough stock to ship order 4819?”</li>
              <li>“Which suppliers are running late this week?”</li>
              <li>“Where are we going to miss SLA tomorrow?”</li>
            </ul>
          </div>

          {/* What Atlas gives back */}
          <div className="rounded-xl bg-white/90 backdrop-blur ring-1 ring-slate-200/70 p-4 md:p-5 shadow-sm">
            <div className="flex items-center gap-2 text-slate-900 font-medium">
              <CheckCircle2 className="h-4 w-4 text-teal-600" />
              <span>What Atlas gives you back</span>
            </div>
            <ul className="mt-2 ml-5 list-disc text-sm text-slate-600 space-y-1.5">
              <li>A plain-English summary of what’s going on.</li>
              <li>The key risks and impacted customers or orders.</li>
              <li>A traceable trail back to the underlying rows and tables.</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
