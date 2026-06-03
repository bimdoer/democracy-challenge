/* Nach iframe-Laden: Plotly an die iframe-Breite anpassen (wie im Blog). */
(function () {
  var presentationFooter = document.getElementById("presentation-footer");
  var globalAgendaNav = document.getElementById("global-agenda-nav");

  function footerHeight() {
    if (!presentationFooter || presentationFooter.hidden) return 0;
    return presentationFooter.offsetHeight || 0;
  }

  function findFooterEl(reveal) {
    return (
      reveal.querySelector(".footer") ||
      document.querySelector(".quarto-auto-generated-content .footer")
    );
  }

  function mountPresentationFooter() {
    var reveal = document.querySelector(".reveal");
    if (!reveal || !presentationFooter) return false;

    var meta = presentationFooter.querySelector(".presentation-footer-meta");
    var footer = findFooterEl(reveal);
    var slideNumber = reveal.querySelector(".slide-number");

    if (footer && footer.parentElement !== meta) meta.appendChild(footer);
    if (slideNumber && slideNumber.parentElement !== meta) meta.appendChild(slideNumber);
    if (presentationFooter.parentElement !== reveal) reveal.appendChild(presentationFooter);
    return !!(footer || slideNumber);
  }

  function updateFooterHeightVar() {
    var reveal = document.querySelector(".reveal");
    if (!reveal) return;
    var h = footerHeight();
    if (h > 0) {
      reveal.style.setProperty("--presentation-footer-height", h + "px");
    } else {
      reveal.style.removeProperty("--presentation-footer-height");
    }
  }

  function resizeThemaPlot(iframe) {
    var scaler = iframe.closest(".thema-plot-scaler");
    if (!scaler) return;
    var slide = iframe.closest("section.slide, section");
    if (!slide) return;
    var title = slide.querySelector("h2");
    var attrH = parseInt(iframe.getAttribute("height"), 10) || 1020;
    var chromeBottom = footerHeight() + 36;
    var available =
      slide.clientHeight - (title ? title.offsetHeight : 0) - chromeBottom;
    if (available < 120) return;
    var scale = Math.min(1, available / attrH);
    scale = Math.max(0.55, Math.round(scale * 1000) / 1000);
    scaler.style.setProperty("--thema-scale", String(scale));
    scaler.style.setProperty("--thema-plot-height", attrH + "px");
    scaler.style.height = Math.round(attrH * scale) + "px";
    iframe.style.height = attrH + "px";
    iframe.style.overflow = "hidden";
  }

  function resizePlot(iframe) {
    try {
      var win = iframe.contentWindow;
      var doc = win && win.document;
      var plot = doc && doc.querySelector(".plotly-graph-div");
      if (plot && win.Plotly) win.Plotly.Plots.resize(plot);

      if (iframe.classList.contains("slide-iframe--thema")) {
        resizeThemaPlot(iframe);
        return;
      }

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
        var chromeBottom = footerHeight() + 24;
        var maxH = slide
          ? slide.clientHeight - (title ? title.offsetHeight : 0) - chromeBottom
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

  function isFooterHiddenSlide(slide) {
    return (
      slide &&
      (slide.id === "title-slide" ||
        slide.id === "closing-slide" ||
        slide.querySelector(".closing-slide-content") ||
        (slide.classList.contains("quarto-title-block") &&
          slide.id !== "agenda"))
    );
  }

  function getAgendaStep(slide) {
    if (!slide) return null;
    var step = slide.getAttribute("data-agenda");
    if (step == null || step === "") return null;
    var n = parseInt(step, 10);
    return Number.isFinite(n) ? n : null;
  }

  function updatePresentationFooter() {
    var reveal = document.querySelector(".reveal");
    var slide = Reveal.getCurrentSlide();
    if (!presentationFooter || !reveal) return;

    var hideAll = isFooterHiddenSlide(slide);
    var step = hideAll ? null : getAgendaStep(slide);

    presentationFooter.hidden = hideAll;

    if (hideAll) {
      reveal.classList.remove("show-global-agenda", "has-presentation-footer");
      if (globalAgendaNav) globalAgendaNav.hidden = true;
    } else {
      reveal.classList.add("has-presentation-footer");
      if (globalAgendaNav) {
        if (step == null) {
          globalAgendaNav.hidden = true;
          reveal.classList.remove("show-global-agenda");
        } else {
          globalAgendaNav.hidden = false;
          reveal.classList.add("show-global-agenda");
          globalAgendaNav.querySelectorAll(".agenda-stop").forEach(function (stop) {
            var s = parseInt(stop.getAttribute("data-agenda-step"), 10);
            stop.classList.toggle("is-active", s === step);
            stop.setAttribute("aria-current", s === step ? "step" : "false");
          });
        }
      }
    }

    updateFooterHeightVar();
  }

  function initPresentationChrome() {
    mountPresentationFooter();
    updatePresentationFooter();
  }

  Reveal.on("ready", function () {
    document.querySelectorAll("iframe.slide-iframe").forEach(bindIframe);
    initPresentationChrome();
    requestAnimationFrame(initPresentationChrome);
    if (!findFooterEl(document.querySelector(".reveal"))) {
      setTimeout(initPresentationChrome, 150);
      setTimeout(initPresentationChrome, 500);
    }
  });

  Reveal.on("slidechanged", function (e) {
    updatePresentationFooter();
    e.currentSlide.querySelectorAll("iframe.slide-iframe").forEach(resizePlot);
    setTimeout(function () {
      updatePresentationFooter();
      Reveal.getCurrentSlide()
        .querySelectorAll("iframe.slide-iframe")
        .forEach(resizePlot);
    }, 50);
  });

  Reveal.on("resize", function () {
    updatePresentationFooter();
    Reveal.getCurrentSlide().querySelectorAll("iframe.slide-iframe").forEach(resizePlot);
  });
})();
