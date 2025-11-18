import React from "react";
import { Linkedin, Mail, Github, BadgeCheck } from "lucide-react";

export default function BehindAtlas() {
  return (
    <section
      id="behind-atlas"
      className="mx-auto max-w-6xl px-4 pt-16 pb-24 text-center"
    >
      {/* Section label */}
      <p className="text-xs font-medium uppercase tracking-wide text-blue-700">
        Behind Atlas
      </p>

      {/* Headline */}
      <h2 className="mt-2 text-2xl font-semibold text-slate-900 leading-snug">
        Built &amp; Architected by Naga Chaganti
      </h2>

      {/* Top paragraph (slightly trimmed) */}
      <p className="mt-3 text-base text-slate-600 leading-relaxed max-w-4xl mx-auto">
        I’m a Supply Chain Solution Architect with 15+ years designing and
        scaling ERP and operations systems at global scale. My focus is using
        Retrieval-Augmented Generation and contextual AI to give operators
        instant, trustworthy answers — starting with supply chain and expanding
        into real-world industries like car washes, gas stations, laundromats,
        and restaurants.
      </p>

      {/* Card */} 
      <div className="mt-10 text-left rounded-2xl bg-white/90 backdrop-blur shadow ring-1 ring-slate-200 p-6 md:p-7">
        {/* Header row with badge + tagline + CTAs */}
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="flex-1">
            <div className="text-xs font-semibold uppercase tracking-wide text-slate-800 flex items-center gap-2">
              <BadgeCheck className="h-4 w-4 text-blue-700" />
              <span>Built &amp; Architected by Naga Chaganti</span>
            </div>
            <div className="mt-1 text-[13px] text-slate-500 leading-relaxed">
              AI + Supply Chain Solution Architect • Using AI to make global
              operations faster, simpler, and more resilient — one system at a
              time.
            </div>
          </div>

          {/* CTAs */}
          <div className="flex flex-col sm:flex-row sm:items-start gap-3 text-sm font-medium">
            <a
              href="https://www.linkedin.com/in/naga-chaganti/"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-indigo-600 to-blue-600 px-4 py-2 text-white shadow hover:from-indigo-700 hover:to-blue-700 transition-colors"
            >
              {/* LinkedIn icon */}
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="h-4 w-4"
              >
                <path d="M4.98 3.5C4.98 4.88 3.88 6 2.5 6S0 4.88 0 3.5 1.12 1 2.5 1s2.48 1.12 2.48 2.5zM.5 8h4V24h-4V8zm7.5 0h3.8v2.2h.1c.5-1 1.9-2.2 3.9-2.2 4.2 0 5 2.8 5 6.4V24h-4v-7.4c0-1.8 0-4.2-2.6-4.2-2.6 0-3 2-3 4V24h-4V8z" />
              </svg>
              <span>Connect on LinkedIn</span>
            </a>

            <a
            href="https://mail.google.com/mail/?view=cm&fs=1&to=sap4naga@gmail.com&su=Inquiry%20about%20Atlas"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white/70 px-4 py-2 text-slate-700 shadow-sm hover:bg-slate-50 transition-colors"
            >
            <Mail className="h-4 w-4" />
            <span>Email</span>
            </a>



            <a
              href="https://github.com/your-github-here"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-2 rounded-lg border border-slate-300 bg-white/70 px-4 py-2 text-slate-700 shadow-sm hover:bg-slate-50 transition-colors"
            >
              <Github className="h-4 w-4" />
              <span>GitHub</span>
            </a>
          </div>
        </div>

        {/* Profile row */}
        <div className="mt-6 flex flex-col sm:flex-row sm:items-start sm:gap-4">
          {/* Photo */}
          <img
            src="/images/naga.jpg"
            alt="Naga Chaganti"
            className="h-16 w-16 rounded-full ring-1 ring-slate-300 object-cover bg-slate-200"
          />

          {/* Name + title */}
          <div className="mt-4 sm:mt-0">
            <p className="text-slate-900 font-semibold text-lg leading-tight">
              Naga Chaganti
            </p>
            <p className="text-sm text-slate-600 leading-snug">
              Solutions Architect • AI for ERP &amp; Supply Chain
            </p>
          </div>
        </div>

        {/* Divider */}
        <hr className="mt-6 border-slate-200/70" />

        {/* Founder note */}
        <p className="mt-6 text-[15px] leading-relaxed text-slate-700">
          After years of watching teams wrestle with ERP screens and endless
          reports, I wanted a better way for people to just ask a question and
          get an answer they can trust. That’s why I built{" "}
          <span className="font-semibold text-slate-900">Atlas</span> — an
          intelligent operational copilot that brings together everything I’ve
          learned in supply chain and applied AI.
        </p>

   <p className="mt-4 text-sm text-slate-500 italic">
  Building AI systems that make businesses run smarter, faster, and more human every day.
</p>

      </div>

    </section>
  );
}
