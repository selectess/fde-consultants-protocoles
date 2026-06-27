/**
 * ui-2026-cinematic — Pattern Library
 * Drop-in JavaScript patterns for cinematic landing pages in 2026.
 * All patterns respect prefers-reduced-motion and use IntersectionObserver
 * or GSAP/ScrollTrigger (whichever you load).
 */

const FDE_UI = (() => {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /**
   * Pattern 1: Section reveal on scroll (zero-deps, 60fps).
   * Usage: <div data-reveal>...</div>
   */
  function initRevealOnScroll() {
    if (prefersReducedMotion) return;
    const obs = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add('is-revealed');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -50px 0px' });
    document.querySelectorAll('[data-reveal]').forEach((el) => obs.observe(el));
  }

  /**
   * Pattern 2: Staggered hero intro (vanilla, no GSAP).
   * Animates children of [data-stagger] in sequence.
   */
  function initStaggerIntro(selector = '[data-stagger]') {
    if (prefersReducedMotion) return;
    const root = document.querySelector(selector);
    if (!root) return;
    const children = Array.from(root.children);
    children.forEach((child, i) => {
      child.style.opacity = '0';
      child.style.transform = 'translateY(20px)';
      child.style.transition = 'opacity 0.7s cubic-bezier(0.16, 1, 0.3, 1), transform 0.7s cubic-bezier(0.16, 1, 0.3, 1)';
      setTimeout(() => {
        child.style.opacity = '1';
        child.style.transform = 'translateY(0)';
      }, 120 * i + 100);
    });
  }

  /**
   * Pattern 3: Parallax on scroll (CSS var-driven, performant).
   * Usage: <div data-parallax="0.3">...</div>  (0=no parallax, 1=full sync)
   */
  function initParallax() {
    if (prefersReducedMotion) return;
    let ticking = false;
    const update = () => {
      const y = window.scrollY;
      document.querySelectorAll('[data-parallax]').forEach((el) => {
        const speed = parseFloat(el.dataset.parallax) || 0.3;
        const rect = el.getBoundingClientRect();
        const offset = (rect.top + y) * speed;
        el.style.setProperty('--parallax-y', `${offset}px`);
      });
      ticking = false;
    };
    window.addEventListener('scroll', () => {
      if (!ticking) {
        requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
    update();
  }

  /**
   * Pattern 4: Kinetic counter (count up when in view).
   * Usage: <span data-count="86">0</span>%
   */
  function initCounters() {
    const counters = document.querySelectorAll('[data-count]');
    if (prefersReducedMotion) {
      counters.forEach((c) => { c.textContent = c.dataset.count; });
      return;
    }
    counters.forEach((c) => {
      const target = parseFloat(c.dataset.count) || 0;
      const obs = new IntersectionObserver(([entry]) => {
        if (entry.isIntersecting) {
          const duration = 1500;
          const start = performance.now();
          const tick = (now) => {
            const t = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - t, 3); // ease-out-cubic
            c.textContent = Math.round(target * eased * 10) / 10;
            if (t < 1) requestAnimationFrame(tick);
            else c.textContent = target;
          };
          requestAnimationFrame(tick);
          obs.disconnect();
        }
      }, { threshold: 0.5 });
      obs.observe(c);
    });
  }

  /**
   * Pattern 5: Magnetic button (cursor-following hover effect).
   * Usage: <button data-magnetic>...</button>
   */
  function initMagnetic() {
    if (prefersReducedMotion) return;
    document.querySelectorAll('[data-magnetic]').forEach((el) => {
      el.addEventListener('mousemove', (e) => {
        const rect = el.getBoundingClientRect();
        const x = e.clientX - rect.left - rect.width / 2;
        const y = e.clientY - rect.top - rect.height / 2;
        el.style.transform = `translate(${x * 0.2}px, ${y * 0.2}px)`;
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = 'translate(0, 0)';
        el.style.transition = 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)';
        setTimeout(() => { el.style.transition = ''; }, 400);
      });
    });
  }

  /**
   * Pattern 6: Smooth scroll to anchor (Lenis alternative, vanilla).
   * Usage: <a href="#section" data-smooth>...</a>
   */
  function initSmoothAnchors() {
    document.querySelectorAll('a[href^="#"]').forEach((a) => {
      a.addEventListener('click', (e) => {
        const id = a.getAttribute('href');
        if (id.length < 2) return;
        const target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        target.scrollIntoView({ behavior: prefersReducedMotion ? 'auto' : 'smooth', block: 'start' });
      });
    });
  }

  /**
   * Pattern 7: Navbar shrink on scroll.
   * Adds `.is-scrolled` class to <header> when scroll > 20px.
   */
  function initNavScroll() {
    const header = document.querySelector('header.nav, nav.nav');
    if (!header) return;
    let lastY = 0;
    window.addEventListener('scroll', () => {
      const y = window.scrollY;
      header.classList.toggle('is-scrolled', y > 20);
      lastY = y;
    }, { passive: true });
  }

  /**
   * Initialize ALL patterns.
   */
  function init() {
    initRevealOnScroll();
    initStaggerIntro();
    initParallax();
    initCounters();
    initMagnetic();
    initSmoothAnchors();
    initNavScroll();
  }

  return { init, initRevealOnScroll, initStaggerIntro, initParallax, initCounters, initMagnetic, initSmoothAnchors, initNavScroll };
})();

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', FDE_UI.init);
} else {
  FDE_UI.init();
}
