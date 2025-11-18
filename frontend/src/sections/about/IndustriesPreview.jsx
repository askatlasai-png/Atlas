// IndustriesPreview.jsx
import React from "react";
import { Car, Fuel, Wrench, Utensils } from "lucide-react";

export default function IndustriesPreview() {
  const industries = [
    {
      icon: Car,
      name: "Car Washes",
      desc: "Track traffic peaks, chemical usage, and membership trends — Atlas helps owners see what's driving revenue and where to improve operations.",
    },
    {
      icon: Utensils,
      name: "Restaurants",
      desc: "Stay on top of ingredient inventory, order delays, and staffing performance — Atlas helps managers make smarter daily decisions.",
    },
    {
      icon: Fuel,
      name: "Gas Stations",
      desc: "Get daily insights on fuel sales, convenience-store margins, and equipment downtime — all summarized automatically.",
    },
    {
      icon: Wrench,
      name: "Oil Change Shops",
      desc: "Monitor service times, inventory usage, and upsell performance — Atlas highlights ways to boost efficiency and revenue without manual tracking.",
    },

  ];

  return (
    <section className="mt-8 space-y-8">
      <div className="text-center mb-6">
        <p className="text-xs font-medium uppercase tracking-wide text-blue-700">
          Expanding Beyond Supply Chain
        </p>
        <h2 className="mt-2 text-2xl font-semibold text-slate-900 leading-snug">
          Atlas for everyday businesses.
        </h2>
        <p className="mt-3 text-base text-slate-600 leading-relaxed max-w-3xl mx-auto">
          Small and medium industries are the backbone of the economy — but they rarely have the tools to see and act on their data. Atlas brings AI-driven clarity to real-world operations like car washes, gas stations, oil change shops, and restaurants.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {industries.map((ind) => (
          <div
            key={ind.name}
            className="rounded-xl bg-white/90 backdrop-blur shadow ring-1 ring-slate-200 p-5 hover:shadow-md transition-all"
          >
            <div className="flex items-center gap-2">
              <ind.icon className="h-5 w-5 text-slate-800" />
              <p className="font-semibold text-slate-900 text-base">
                {ind.name}
              </p>
            </div>
            <p className="mt-2 text-sm text-slate-600 leading-relaxed">
              {ind.desc}
            </p>
          </div>
        ))}
      </div>

      <p className="text-center text-slate-500 text-sm italic mt-6">
        And this is just the beginning — Atlas adapts to any business that runs on data and daily decisions.
      </p>
    </section>
  );
}
