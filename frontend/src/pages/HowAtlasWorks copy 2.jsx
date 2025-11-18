import React from "react";
import { HowItWorks } from "@/sections/about";
import TechStack from "@/sections/about/TechStack.jsx";
import UnderTheHood from "@/sections/about/UnderTheHood.jsx";
import Navbar from "@/components/Navbar.jsx";   
import FinalCTA from "../sections/about/FinalCTA";

export default function HowAtlasWorksPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-white via-blue-50/40 to-teal-50/30 text-slate-900">

    {/* 🔹 Navbar at top */}
      <Navbar />
      <div className="mx-auto max-w-6xl px-4 md:px-6 py-16 space-y-28">

        {/* PAGE HEADER */}
        <section className="text-center space-y-6">
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-blue-700">
            How Atlas Works
          </p>

          <h1 className="text-3xl md:text-4xl font-semibold leading-tight tracking-tight text-slate-900 max-w-4xl mx-auto">
            From scattered systems to a{" "}
            <span className="bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 bg-clip-text text-transparent">
              clear answer you can trust
            </span>.
          </h1>

          <p className="text-base md:text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Atlas connects to the systems you already run, keeps operational
            context, and turns it into answers you can act on — with a transparent
            trail back to your underlying data.
          </p>

          <div className="h-1 w-20 bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 mx-auto rounded-full" />
        </section>

        {/* UNDER THE HOOD */}
        <section className="bg-white/80 backdrop-blur rounded-2xl shadow-xl ring-1 ring-slate-200/60 p-8 md:p-12 space-y-12">
          <div className="text-center space-y-4">
            <p className="text-xs uppercase tracking-wider text-blue-700 font-medium">
              Under the Hood
            </p>

            <h2 className="text-2xl md:text-3xl font-semibold text-slate-900">
              Built like an{" "}
              <span className="bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 bg-clip-text text-transparent">
                AI product
              </span>
              , not a dashboard.
            </h2>

            <p className="text-slate-600 max-w-2xl mx-auto text-sm md:text-base">
              Retrieval, reasoning, and domain-aware guardrails — designed for real
              operations, not demo data.
            </p>
          </div>

          <UnderTheHood />
        </section>

        {/* HOW IT WORKS */}
        <section className="bg-blue-50/60 rounded-2xl ring-1 ring-blue-100/70 shadow-lg p-8 md:p-12 space-y-12">
          <div className="text-center space-y-4">
            <p className="text-xs uppercase tracking-wider text-blue-700 font-medium">
              The Atlas Flow
            </p>

            <h2 className="text-2xl md:text-3xl font-semibold text-slate-900">
              How Atlas turns your data into{" "}
              <span className="bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-500 bg-clip-text text-transparent">
                real answers
              </span>
              .
            </h2>

            <p className="text-slate-600 max-w-2xl mx-auto text-sm md:text-base">
              These steps outline how Atlas retrieves, analyzes, and connects the
              information spread across your ERP and planning systems.
            </p>
          </div>

          <HowItWorks />
        </section>

        {/* TECH STACK */}
        <section className="bg-white/90 backdrop-blur rounded-2xl shadow-xl ring-1 ring-slate-200/60 p-8 md:p-12 space-y-12">
          <div className="text-center space-y-4">
            <p className="text-xs uppercase tracking-wider text-blue-700 font-medium">
              Tech Stack
            </p>

            <h2 className="text-2xl md:text-3xl font-semibold text-slate-900">
              Modern AI + cloud foundation.
            </h2>

            <p className="text-slate-600 max-w-2xl mx-auto text-sm md:text-base">
              React on the frontend, Python + LangChain on the backend, FAISS for
              vector search, and AWS as the backbone.
            </p>
          </div>

          <TechStack />
        </section>
      </div>

        {/* 🔹 Footer at bottom */}
      <FinalCTA />
      
    </main>
  );
}
