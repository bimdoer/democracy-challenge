/* Nach iframe-Laden: Plotly an die iframe-Breite anpassen (wie im Blog). */
(function () {
  function resizePlot(iframe) {
    try {
      var win = iframe.contentWindow;
      var doc = win && win.document;
      var plot = doc && doc.querySelector(".plotly-graph-div");
      if (plot && win.Plotly) win.Plotly.Plots.resize(plot);

      if (!doc) return;
      var embed = doc.querySelector(".phase-heatmap-embed");
      var contentH = embed
        ? embed.offsetHeight
        : doc.documentElement.scrollHeight;
      var attrH = parseInt(iframe.getAttribute("height"), 10);
      var needH = Math.max(contentH, attrH || 0);
      if (needH > 0) {
        var slide = iframe.closest("section.slide, section");
        var title = slide && slide.querySelector("h2");
        var maxH = slide
          ? slide.clientHeight - (title ? title.offsetHeight : 0) - 16
          : needH;
        if (maxH > 80 && needH > maxH) {
          iframe.style.height = maxH + "px";
          iframe.style.overflow = "auto";
        } else {
          iframe.style.height = needH + "px";
          iframe.style.overflow = "hidden";
        }
      }
    } catch (e) {
      /* ignore */
    }
  }

  function bindIframe(iframe) {
    iframe.addEventListener("load", function () {
      resizePlot(iframe);
      setTimeout(function () {
        resizePlot(iframe);
      }, 120);
    });
  }

  function isChromeHiddenSlide(slide) {
    return (
      slide &&
      (slide.id === "title-slide" ||
        slide.id === "closing-slide" ||
        slide.querySelector("#closing-slide") ||
        slide.classList.contains("quarto-title-block"))
    );
  }

  function updateSlideChromeVisibility() {
    var hide = isChromeHiddenSlide(Reveal.getCurrentSlide());
    document.querySelectorAll(".reveal .footer, .reveal .slide-number").forEach(function (el) {
      el.style.visibility = hide ? "hidden" : "visible";
    });
  }

  Reveal.on("ready", function (e) {
    document.querySelectorAll("iframe.slide-iframe").forEach(bindIframe);
    updateSlideChromeVisibility();
  });

  Reveal.on("slidechanged", function (e) {
    e.currentSlide.querySelectorAll("iframe.slide-iframe").forEach(resizePlot);
    updateSlideChromeVisibility();
  });

  Reveal.on("resize", function () {
    Reveal.getCurrentSlide().querySelectorAll("iframe.slide-iframe").forEach(resizePlot);
  });
})();
