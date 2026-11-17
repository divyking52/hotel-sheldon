/* Hotel Sheldon — PhotoSwipe lightbox (Elementor-matching UI) */
(function (w, d) {
  "use strict";

  var PSWP_HTML =
    '<div class="pswp" tabindex="-1" role="dialog" aria-hidden="true">' +
    '  <div class="pswp__bg"></div>' +
    '  <div class="pswp__scroll-wrap">' +
    '    <div class="pswp__container">' +
    '      <div class="pswp__item"></div>' +
    '      <div class="pswp__item"></div>' +
    '      <div class="pswp__item"></div>' +
    "    </div>" +
    '    <div class="pswp__ui pswp__ui--hidden">' +
    '      <div class="pswp__top-bar">' +
    '        <div class="pswp__counter"></div>' +
    /* float:right → visual L→R: fullscreen, zoom, share, close (matches Elementor) */
    '        <button class="pswp__button pswp__button--close" title="Close (Esc)"></button>' +
    '        <button class="pswp__button pswp__button--share" title="Share"></button>' +
    '        <button class="pswp__button pswp__button--zoom" title="Zoom in/out"></button>' +
    '        <button class="pswp__button pswp__button--fs" title="Toggle fullscreen"></button>' +
    '        <div class="pswp__preloader">' +
    '          <div class="pswp__preloader__icn">' +
    '            <div class="pswp__preloader__cut">' +
    '              <div class="pswp__preloader__donut"></div>' +
    "            </div>" +
    "          </div>" +
    "        </div>" +
    "      </div>" +
    '      <div class="pswp__share-modal pswp__share-modal--hidden pswp__single-tap">' +
    '        <div class="pswp__share-tooltip"></div>' +
    "      </div>" +
    '      <button class="pswp__button pswp__button--arrow--left" title="Previous (arrow left)"></button>' +
    '      <button class="pswp__button pswp__button--arrow--right" title="Next (arrow right)"></button>' +
    '      <div class="pswp__caption">' +
    '        <div class="pswp__caption__center"></div>' +
    "      </div>" +
    "    </div>" +
    "  </div>" +
    "</div>";

  var gallery = null;
  var sizeCache = Object.create(null);

  function ensureDom() {
    if (!d.querySelector(".pswp")) {
      d.body.insertAdjacentHTML("beforeend", PSWP_HTML);
    }
  }

  function getSrc(im) {
    return (im && (im.getAttribute("data-full") || im.currentSrc || im.getAttribute("src"))) || "";
  }

  function itemFromTile(tile) {
    var im = tile.querySelector("img") || tile;
    if (im.tagName !== "IMG") im = tile.querySelector("img");
    var src = getSrc(im);
    return {
      src: src,
      w: 0,
      h: 0,
      title: (tile.getAttribute && tile.getAttribute("data-caption")) || (im && im.alt) || "",
      msrc: (im && (im.currentSrc || im.getAttribute("src"))) || src,
    };
  }

  function loadSize(item) {
    return new Promise(function (resolve) {
      if (item.w > 0 && item.h > 0) {
        resolve(item);
        return;
      }
      if (sizeCache[item.src]) {
        item.w = sizeCache[item.src].w;
        item.h = sizeCache[item.src].h;
        resolve(item);
        return;
      }
      var img = new Image();
      img.onload = function () {
        item.w = img.naturalWidth || 1600;
        item.h = img.naturalHeight || 1067;
        sizeCache[item.src] = { w: item.w, h: item.h };
        resolve(item);
      };
      img.onerror = function () {
        item.w = 1600;
        item.h = 1067;
        resolve(item);
      };
      img.src = item.src;
    });
  }

  function openFromTiles(tiles, index) {
    if (!w.PhotoSwipe || !w.PhotoSwipeUI_Default) {
      console.warn("PhotoSwipe not loaded");
      return;
    }
    if (!tiles || !tiles.length) return;
    ensureDom();
    var items = Array.prototype.map.call(tiles, itemFromTile).filter(function (it) {
      return !!it.src;
    });
    if (!items.length) return;
    var start = Math.max(0, Math.min(index || 0, items.length - 1));

    Promise.all(items.map(loadSize)).then(function () {
      if (gallery) {
        try {
          gallery.close();
        } catch (e) {}
        gallery = null;
      }
      var el = d.querySelector(".pswp");
      gallery = new w.PhotoSwipe(el, w.PhotoSwipeUI_Default, items, {
        index: start,
        history: false,
        focus: true,
        modal: true,
        showHideOpacity: true,
        bgOpacity: 0.85,
        closeOnScroll: false,
        maxSpreadZoom: 4,
        shareEl: true,
        fullscreenEl: true,
        zoomEl: true,
        counterEl: true,
        arrowEl: true,
        preloaderEl: true,
        /* Original Elementor lightbox screenshot has no bottom caption bar */
        captionEl: false,
        tapToClose: false,
        tapToToggleControls: true,
        clickToCloseNonZoomable: true,
        shareButtons: [
          {
            id: "facebook",
            label: "Share on Facebook",
            url: "https://www.facebook.com/sharer/sharer.php?u={{url}}",
          },
          {
            id: "twitter",
            label: "Tweet",
            url: "https://twitter.com/intent/tweet?text={{text}}&url={{url}}",
          },
          {
            id: "pinterest",
            label: "Pin it",
            url:
              "http://www.pinterest.com/pin/create/button/" +
              "?url={{url}}&media={{image_url}}&description={{text}}",
          },
          {
            id: "download",
            label: "Download image",
            url: "{{raw_image_url}}",
            download: true,
          },
        ],
        getImageURLForShare: function (/* shareButtonData */) {
          return gallery.currItem.src || "";
        },
      });
      gallery.listen("destroy", function () {
        gallery = null;
        d.body.classList.remove("locked");
      });
      d.body.classList.add("locked");
      gallery.init();
    });
  }

  w.hsOpenLightbox = openFromTiles;
  w.hsCloseLightbox = function () {
    if (gallery) {
      try {
        gallery.close();
      } catch (e) {}
    }
  };
})(window, document);
