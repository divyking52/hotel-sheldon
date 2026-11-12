/* Reveal leftover Elementor-style entrance animations without WP runtime. */
(function () {
  var reduced = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function settingsOf(el) {
    var raw = el.getAttribute("data-settings") || "";
    try {
      return raw ? JSON.parse(raw) : {};
    } catch (e) {
      return {};
    }
  }

  function reveal(el) {
    if (!el || el.dataset.hsuiRevealed === "1") return;
    el.dataset.hsuiRevealed = "1";
    var s = settingsOf(el);
    var name = s._animation || s.animation || "fadeIn";
    var delayMs = Number(s._animation_delay || s.animation_delay || 0);
    // Room CTAs: keep on-card (fadeInUp was translating them out of view)
    if (el.classList.contains("hsui-widget-button") || el.classList.contains("elementor-widget-button")) {
      name = "fadeIn";
      delayMs = Math.min(delayMs || 0, 150);
    }
    el.classList.remove("hsui-invisible", "elementor-invisible");
    el.style.visibility = "visible";
    if (reduced) {
      el.style.opacity = "1";
      el.style.transform = "none";
      return;
    }
    if (delayMs) el.style.animationDelay = delayMs / 1000 + "s";
    el.classList.add("animated", name);
    el.addEventListener(
      "animationend",
      function () {
        el.style.opacity = "1";
        el.style.transform = "none";
        el.style.visibility = "visible";
      },
      { once: true }
    );
  }

  function inView(el, slack) {
    var r = el.getBoundingClientRect();
    var top = -slack;
    var bottom = window.innerHeight + slack;
    return r.bottom > top && r.top < bottom;
  }

  function boot() {
    // Always show body copy — never leave text-editors stuck on visibility:hidden
    [].slice.call(document.querySelectorAll(".hsui-widget-text-editor.hsui-invisible, .elementor-widget-text-editor.elementor-invisible")).forEach(reveal);

    var nodes = [].slice.call(document.querySelectorAll(".hsui-invisible, .elementor-invisible"));
    if (!nodes.length) return;

    function scan() {
      nodes.forEach(function (el) {
        if (el.dataset.hsuiRevealed === "1") return;
        // Reveal when the widget OR its room/card parent is on screen
        var parent = el.closest(".e-con, .hs-con-full, .hsui-element.e-con, [data-element_type='container']") || el;
        if (inView(el, 120) || inView(parent, 80)) reveal(el);
      });
    }

    if (reduced || !("IntersectionObserver" in window)) {
      nodes.forEach(reveal);
      return;
    }

    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          reveal(en.target);
          io.unobserve(en.target);
        });
      },
      { rootMargin: "120px 0px 30% 0px", threshold: 0 }
    );

    nodes.forEach(function (el) {
      if (inView(el, 120) || inView(el.parentElement || el, 80)) reveal(el);
      else io.observe(el);
    });

    // Catch room-card buttons that sit just under the fold inside a visible card
    scan();
    window.addEventListener("scroll", scan, { passive: true });
    window.addEventListener("resize", scan);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
