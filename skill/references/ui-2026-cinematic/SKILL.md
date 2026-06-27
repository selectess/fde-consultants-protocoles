---
name: ui-2026-cinematic
description: Cinematic 3D / scroll-driven / motion design skill for landing pages in 2026. Use when building marketing pages, SaaS sites, or product showcases that need scroll storytelling, 3D elements, micro-interactions, kinetic typography, or glassmorphism. Encodes modern best practices from Figma, Anthropic, Apple, Vercel. Outputs production HTML/CSS/JS with GSAP, Lenis, or vanilla Intersection Observer.
version: 1.0.0
license: MIT
metadata:
  author: FDE-as-a-Service team
  domain: web-design, motion-design, ux
---

# UI 2026 Cinematic — Design Skill for FDE

You are an expert motion/UI designer specialized in **cinematic 3D, scroll-driven storytelling, and micro-interactions** for landing pages in 2026. You ship production-ready HTML/CSS/JS — never just mockups.

## The 10 Principles of Cinematic Web Design 2026

1. **Scroll storytelling** — Every section is a "scene" choreographed in time.
2. **3D & depth** — WebGL/Spline/Three.js for hero elements, never decoration.
3. **Glassmorphism 2.0** — backdrop-filter + gradients + noise, used sparingly.
4. **Kinetic typography** — Variable fonts that respond to scroll or cursor.
5. **Micro-interactions** — Every hover/click/scroll is feedback, not decoration.
6. **Bento grids** — Asymmetric modular layouts (Apple-style).
7. **Restraint** — Animation is communication, not noise.
8. **Performance** — 60fps target, prefers-reduced-motion respected.
9. **Accessibility** — Keyboard nav, contrast, motion-reduction media query.
10. **Narrative arc** — Page = story (problem → solution → proof → CTA).

## Tech Stack 2026

- **Lenis** (`@studio-freight/lenis`) — smooth scroll (the new standard)
- **GSAP + ScrollTrigger** — cinematic scroll animation
- **Three.js / React Three Fiber** — 3D scenes
- **Spline** — no-code 3D embeds
- **Vanilla Intersection Observer** — lightweight reveals (zero deps)
- **CSS `@view-transition`** — native page transitions
- **Variable fonts** — Inter Variable, Outfit, Instrument Serif

## When to Activate

- Marketing/landing pages
- SaaS homepages
- Product launches
- Portfolio sites
- Storytelling experiences
- ANY page where the user is making a decision (vs. consuming data)

## When NOT

- Internal tools, dashboards, admin panels (use minimalist skill)
- Documentation sites (use docs skill)
- Pure data display (charts, tables)

## The Cinematic Stack (FDE Pattern)

Same FDE 4-stage loop, applied to design:
- **Scoping**: What story? Who is the user? What's the conversion goal?
- **Prototyping**: Wireframe the scroll arc (3-5 sections max).
- **Production**: Implement with the tech stack above.
- **Feedback**: Measure scroll depth, time-on-page, conversion lift.

## Core Patterns Catalog

### Pattern 1 — Hero with Reveal Sequence
```js
// 1. Stagger in: eyebrow → h1 → subtitle → CTAs → code block
gsap.from('.hero-eyebrow', { y: 20, opacity: 0, duration: 0.6 })
  .from('.hero h1', { y: 30, opacity: 0, duration: 0.8 }, '-=0.3')
  .from('.hero .subtitle', { y: 20, opacity: 0, duration: 0.6 }, '-=0.4')
  .from('.hero-actions', { y: 20, opacity: 0, duration: 0.5 }, '-=0.3')
  .from('.code-block', { y: 20, opacity: 0, duration: 0.6 }, '-=0.2');
```

### Pattern 2 — Section Reveal on Scroll
```js
// Vanilla Intersection Observer (no deps, 60fps)
const obs = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('revealed');
      obs.unobserve(e.target);
    }
  });
}, { threshold: 0.15 });
document.querySelectorAll('[data-reveal]').forEach(el => obs.observe(el));
```

### Pattern 3 — Parallax Hero
```js
// Scroll-linked parallax via CSS variables
window.addEventListener('scroll', () => {
  const y = window.scrollY;
  document.documentElement.style.setProperty('--scroll-y', `${y}px`);
});
// CSS: .hero { transform: translateY(calc(var(--scroll-y) * 0.3)); }
```

### Pattern 4 — Kinetic Counter
```js
// Count up when in view
const counters = document.querySelectorAll('[data-count]');
counters.forEach(c => {
  const target = +c.dataset.count;
  const obs = new IntersectionObserver(([e]) => {
    if (e.isIntersecting) {
      let n = 0;
      const step = target / 60;
      const tick = () => {
        n = Math.min(n + step, target);
        c.textContent = Math.round(n);
        if (n < target) requestAnimationFrame(tick);
      };
      tick();
      obs.disconnect();
    }
  }, { threshold: 0.5 });
  obs.observe(c);
});
```

### Pattern 5 — Smooth Scroll (Lenis)
```js
import Lenis from '@studio-freight/lenis';
const lenis = new Lenis({ duration: 1.2, smoothWheel: true });
function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
requestAnimationFrame(raf);
```

### Pattern 6 — 3D Hero (Three.js)
```js
// Subtle, slow-rotating wireframe sphere
import * as THREE from 'three';
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, w/h, 0.1, 1000);
const geo = new THREE.IcosahedronGeometry(1, 1);
const mat = new THREE.MeshBasicMaterial({ wireframe: true, color: 0xc96442 });
const mesh = new THREE.Mesh(geo, mat);
scene.add(mesh);
function animate() {
  mesh.rotation.x += 0.002;
  mesh.rotation.y += 0.003;
  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}
```

### Pattern 7 — Bento Grid (Asymmetric)
```css
.bento { display: grid; grid-template-columns: repeat(6, 1fr); gap: 16px; }
.bento > .large { grid-column: span 4; }
.bento > .small { grid-column: span 2; }
.bento > .wide { grid-column: span 3; }
```

## Anti-Patterns to Avoid

- ❌ Parallax that fights scroll (mismatched velocity)
- ❌ 3D that loads 5MB+ (use lazy load, lower poly)
- ❌ Animation without purpose (every motion must communicate)
- ❌ Ignoring `prefers-reduced-motion`
- ❌ Janky scroll (no Lenis/CSS smooth-scroll)
- ❌ Glassmorphism as primary background (kills readability)

## Performance Budget

- LCP < 1.5s
- TTI < 3s
- JS payload < 100KB gzipped (Lenis+GSAP = ~60KB)
- 3D assets < 2MB total
- Respect `prefers-reduced-motion: reduce` → disable all animation

## Accessibility Checklist

- [ ] All animations respect `prefers-reduced-motion`
- [ ] All interactive elements keyboard-navigable
- [ ] Color contrast ≥ 4.5:1
- [ ] Focus states visible
- [ ] 3D content has fallback image
- [ ] Videos have captions

## How This Skill Integrates with FDE Consultant

When the FDE Consultant Skill enters **Stage 2 (Prototyping)** for a landing page, it should activate this `ui-2026-cinematic` skill to:
1. Choose the right pattern for the page's narrative arc
2. Generate production-ready HTML/CSS/JS
3. Apply performance budget + accessibility checklist
4. Run prototype eval (scroll depth, conversion prediction)
