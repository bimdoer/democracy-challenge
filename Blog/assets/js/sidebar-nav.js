(function () {
  var sectionLinks = document.querySelectorAll(".sidebar-section-link");
  if (!sectionLinks.length) {
    return;
  }

  function setActiveFromHash() {
    var hash = window.location.hash;
    sectionLinks.forEach(function (link) {
      var href = link.getAttribute("href") || "";
      var linkHash = href.indexOf("#") >= 0 ? href.slice(href.indexOf("#")) : "";
      link.classList.toggle("active", hash && linkHash === hash);
    });
  }

  setActiveFromHash();
  window.addEventListener("hashchange", setActiveFromHash);

  var content = document.querySelector(".content");
  if (!content || !("IntersectionObserver" in window)) {
    return;
  }

  var currentChapter = document.querySelector(".sidebar-chapter-link.active");
  if (!currentChapter) {
    return;
  }

  var chapterPath = currentChapter.getAttribute("href");
  var pageLinks = Array.prototype.filter.call(sectionLinks, function (link) {
    return (link.getAttribute("href") || "").indexOf(chapterPath) === 0;
  });

  if (!pageLinks.length) {
    return;
  }

  var targets = pageLinks
    .map(function (link) {
      var hash = link.getAttribute("href").split("#")[1];
      if (!hash) {
        return null;
      }
      return document.getElementById(hash);
    })
    .filter(Boolean);

  if (!targets.length) {
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      var visible = entries
        .filter(function (entry) {
          return entry.isIntersecting;
        })
        .sort(function (a, b) {
          return a.boundingClientRect.top - b.boundingClientRect.top;
        });

      if (!visible.length) {
        return;
      }

      var id = visible[0].target.id;
      pageLinks.forEach(function (link) {
        link.classList.toggle("active", link.getAttribute("href").endsWith("#" + id));
      });
    },
    { rootMargin: "-20% 0px -70% 0px", threshold: 0 }
  );

  targets.forEach(function (target) {
    observer.observe(target);
  });
})();
