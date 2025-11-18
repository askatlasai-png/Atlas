import React from "react";
import { Linkedin, Mail } from "lucide-react";

export default function FinalCTA() {
  return (
    <section
      id="connect"
      className="mx-auto max-w-5xl px-4 py-8 text-center"
    >
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-semibold text-slate-900 leading-snug">
          Let’s make operations smarter — together.
        </h2>

        <p className="mt-3 text-base text-slate-600 leading-relaxed">
          Atlas began as a supply chain experiment — but the idea is universal:
          every business can benefit from AI that truly understands how it runs.
          If you’re exploring ways to bring this thinking to your own operations,
          I’d love to connect.
        </p>

        <div className="mt-8 flex justify-center gap-3 flex-wrap">
          <a
            href="https://www.linkedin.com/in/naga-chaganti/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-full bg-gradient-to-r from-indigo-600 to-blue-600 px-5 py-2.5 text-white font-medium shadow hover:from-indigo-700 hover:to-blue-700 transition-all"
          >
            <Linkedin className="h-4 w-4" />
            Connect on LinkedIn
          </a>

          <a
            href="https://mail.google.com/mail/?view=cm&fs=1&to=sap4naga@gmail.com&su=Inquiry%20about%20Atlas"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center gap-2 rounded-full border border-slate-300 bg-white/70 px-5 py-2.5 text-slate-700 font-medium shadow-sm hover:bg-slate-50 transition-all"
          >
            <Mail className="h-4 w-4" />
            Send an Email
          </a>
        </div>

        <p className="mt-10 text-sm text-slate-500 italic">
          Atlas — AI built for your business.
        </p>
      </div>
    </section>
  );
}
