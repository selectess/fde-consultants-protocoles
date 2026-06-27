(function () {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const revealEls = Array.from(document.querySelectorAll("[data-reveal]"));
  const steps = Array.from(document.querySelectorAll(".story-step"));
  const artifacts = Array.from(document.querySelectorAll(".artifact"));

  if (!reduce && "IntersectionObserver" in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: "0px 0px -40px 0px" });
    revealEls.forEach((el) => observer.observe(el));
  } else {
    revealEls.forEach((el) => el.classList.add("in"));
  }

  function updateScrollStory() {
    if (!steps.length) return;
    const center = window.innerHeight * 0.52;
    let activeIndex = 0;
    let best = Infinity;
    steps.forEach((step, index) => {
      const rect = step.getBoundingClientRect();
      const distance = Math.abs(rect.top + rect.height * 0.5 - center);
      if (distance < best) {
        best = distance;
        activeIndex = index;
      }
    });
    steps.forEach((step, index) => step.classList.toggle("active", index === activeIndex));
    if (!reduce) {
      artifacts.forEach((artifact, index) => {
        const offset = (index - activeIndex) * 16;
        const scale = index === activeIndex ? 1.04 : 0.96;
        artifact.style.transform = "translate3d(0," + offset + "px,0) scale(" + scale + ")";
        artifact.style.opacity = index === activeIndex ? "1" : "0.58";
      });
    }
  }

  window.addEventListener("scroll", updateScrollStory, { passive: true });
  window.addEventListener("resize", updateScrollStory);
  updateScrollStory();

  document.querySelectorAll(".waitlist").forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const button = form.querySelector("button");
      if (button) button.textContent = "Beta request captured";
      form.classList.add("submitted");
    });
  });
})();
