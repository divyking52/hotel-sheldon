/* Hotel Sheldon — shared custom footer mount + newsletter UI */
(function () {
  "use strict";

  var YEAR = new Date().getFullYear();

  var FOOTER_HTML =
    '<footer class="site-footer" id="site-footer" role="contentinfo">' +
    '  <div class="site-footer__hero">' +
    '    <div class="site-footer__inner">' +
    '      <div class="site-footer__col">' +
    '        <a class="site-footer__mono" href="/" aria-label="Hotel Sheldon home">' +
    '          <img src="/assets/footer/logo-mono.webp" alt="" width="70" height="70" decoding="async">' +
    "        </a>" +
    '        <img class="site-footer__wordmark" src="/assets/footer/logo-wordmark.webp" alt="Hotel Sheldon" width="300" height="18" decoding="async">' +
    '        <p class="site-footer__addr"><a href="https://maps.app.goo.gl/1KVfxk3YcLZJVvjR7" target="_blank" rel="noopener">1000 North Surf Rd, Hollywood, Florida US 33019</a></p>' +
    "      </div>" +
    '      <div class="site-footer__col">' +
    '        <ul class="site-footer__nav">' +
    '          <li><a href="/accommodations/">Accommodations</a></li>' +
    '          <li><a href="/attractions/">Attractions</a></li>' +
    '          <li><a href="/contact/">Contact</a></li>' +
    "        </ul>" +
    '        <ul class="site-footer__social">' +
    '          <li><a href="tel:+19549226020" aria-label="phone number"><svg viewBox="0 0 512 512" aria-hidden="true"><path d="M497.39 361.8l-112-48a24 24 0 0 0-28 6.9l-49.6 60.6A370.66 370.66 0 0 1 130.6 204.11l60.6-49.6a23.94 23.94 0 0 0 6.9-28l-48-112A24.16 24.16 0 0 0 122.6.61l-104 24A24 24 0 0 0 0 48c0 256.5 207.9 464 464 464a24 24 0 0 0 23.4-18.6l24-104a24.29 24.29 0 0 0-14.01-27.6z"></path></svg></a></li>' +
    '          <li><a href="mailto:reservations@hotelsheldon.com" aria-label="email address"><svg viewBox="0 0 512 512" aria-hidden="true"><path d="M502.3 190.8c3.9-3.1 9.7-.2 9.7 4.7V400c0 26.5-21.5 48-48 48H48c-26.5 0-48-21.5-48-48V195.6c0-5 5.7-7.8 9.7-4.7 22.4 17.4 52.1 39.5 154.1 113.6 21.1 15.4 56.7 47.8 92.2 47.6 35.7.3 72-32.8 92.3-47.6 102-74.1 131.6-96.3 154-113.7zM256 320c23.2.4 56.6-29.2 73.4-41.4 132.7-96.3 142.8-104.7 173.4-128.7 5.8-4.5 9.2-11.5 9.2-18.9v-19c0-26.5-21.5-48-48-48H48C21.5 64 0 85.5 0 112v19c0 7.4 3.4 14.3 9.2 18.9 30.6 23.9 40.7 32.4 173.4 128.7 16.8 12.2 50.2 41.8 73.4 41.4z"></path></svg></a></li>' +
    '          <li><a href="https://www.facebook.com/HotelSheldonHollywood/" target="_blank" rel="noopener" aria-label="facebook"><svg viewBox="0 0 448 512" aria-hidden="true"><path d="M400 32H48A48 48 0 0 0 0 80v352a48 48 0 0 0 48 48h137.25V327.69h-63V256h63v-54.64c0-62.15 37-96.48 93.67-96.48 27.14 0 55.52 4.84 55.52 4.84v61h-31.27c-30.81 0-40.42 19.12-40.42 38.73V256h68.78l-11 71.69h-57.78V480H400a48 48 0 0 0 48-48V80a48 48 0 0 0-48-48z"></path></svg></a></li>' +
    "        </ul>" +
    "      </div>" +
    '      <div class="site-footer__col site-footer__col--news">' +
    '        <h2 class="site-footer__title">Stay In Touch</h2>' +
    '        <div class="site-footer__news">' +
    '          <form class="site-footer__form" id="site-footer-news" action="#" method="post" novalidate>' +
    '            <label class="sr-only" for="site-footer-email">Email</label>' +
    '            <input class="site-footer__email" id="site-footer-email" name="email" type="email" placeholder="Email" required autocomplete="email">' +
    '            <input class="site-footer__honeypot" type="text" name="company" tabindex="-1" autocomplete="off" aria-hidden="true">' +
    '            <button class="site-footer__submit" type="submit">Sign Up</button>' +
    "          </form>" +
    '          <p class="site-footer__note" id="site-footer-note" hidden></p>' +
    "        </div>" +
    '        <ul class="site-footer__legal">' +
    '          <li><a href="/privacy-policy/">Privacy Policy</a></li>' +
    '          <li><a href="/accessibility-statement/">Accessibility Statement</a></li>' +
    "        </ul>" +
    "      </div>" +
    "    </div>" +
    "  </div>" +
    '  <div class="site-footer__bar">' +
    '    <div class="site-footer__bar-inner">' +
    '      <p class="site-footer__copy">&copy; ' +
    YEAR +
    ' - Hotel Sheldon. All rights reserved, <a href="https://razibmarketing.com/" target="_blank" rel="noopener">Hotel Website Design by Razib Marketing</a></p>' +
    "    </div>" +
    "  </div>" +
    "</footer>";

  function ensureSrOnly() {
    if (document.getElementById("site-footer-sr-style")) return;
    var s = document.createElement("style");
    s.id = "site-footer-sr-style";
    s.textContent =
      ".sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}";
    document.head.appendChild(s);
  }

  function mount() {
    ensureSrOnly();
    var root = document.getElementById("site-footer-root");
    if (!root) {
      root = document.createElement("div");
      root.id = "site-footer-root";
      var main = document.getElementById("main") || document.querySelector("main");
      if (main && main.parentNode) main.parentNode.insertBefore(root, main.nextSibling);
      else document.body.appendChild(root);
    }
    // Remove any duplicate footers before mounting the shared one
    document.querySelectorAll("footer.site-footer").forEach(function (el) {
      if (!root.contains(el)) el.remove();
    });
    root.innerHTML = FOOTER_HTML;
    wireNews(root.querySelector("#site-footer-news"), root.querySelector("#site-footer-note"));
  }

  function wireNews(form, note) {
    if (!form) return;
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var honey = form.querySelector('[name="company"]');
      if (honey && honey.value) return;
      var email = (form.querySelector('[name="email"]').value || "").trim();
      if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
        if (note) {
          note.hidden = false;
          note.textContent = "Please enter a valid email address.";
        }
        return;
      }
      if (note) {
        note.hidden = false;
        note.textContent =
          "Thanks — newsletter signup isn’t connected to a live service in this build. Email reservations@hotelsheldon.com to join the list.";
      }
      form.reset();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", mount);
  else mount();
})();
