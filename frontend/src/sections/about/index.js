// ---------- index.js (barrel) ----------
export { default as AboutHero } from "./AboutHero.jsx";
export { default as KeyFeatures } from "./KeyFeatures.jsx";
export { default as HowItWorks } from "./HowItWorks.jsx";
export { default as TechStack } from "./TechStack.jsx";



// ---------- Usage (patch) ----------
// In AtlasShowcase.jsx (inside the existing About section container), import and place:
// import { AboutHero, KeyFeatures, HowItWorks } from "@/sections/about"; // adjust path
// ...
// <section id="about" className="mt-8 space-y-8">
// <AboutHero />
// <KeyFeatures />
// <HowItWorks />
// </section>