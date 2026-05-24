(function () {
  var chapterLinks = document.querySelectorAll('.sidebar-chapter-link[data-nav="chapter"]');
  var sectionLinks = document.querySelectorAll('.sidebar-section-link[data-nav="section"]');

  function normalizePath(pathname) {
    var path = pathname || "/";
    if (path.length > 1 && path.endsWith("/")) {
      path = path.slice(0, -1);
    }
    return path;
  }

  function linkPath(link) {
    return normalizePath(new URL(link.href, window.location.href).pathname);
  }

  function clearNavState() {
    chapterLinks.forEach(function (link) {
      link.classList.remove("active", "is-on-page");
      link.removeAttribute("aria-current");
    });
    sectionLinks.forEach(function (link) {
      link.classList.remove("active");
      link.removeAttribute("aria-current");
    });
  }

  function setNavState() {
    clearNavState();

    var path = normalizePath(window.location.pathname);
    var hash = window.location.hash;
    var hasSection = !!hash;

    chapterLinks.forEach(function (link) {
      var onPage = linkPath(link) === path;
      if (!onPage) {
        return;
      }

      link.classList.add("is-on-page");
      if (!hasSection) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
      }
    });

    if (!hasSection) {
      return;
    }

    sectionLinks.forEach(function (link) {
      var linkUrl = new URL(link.href, window.location.href);
      if (normalizePath(linkUrl.pathname) !== path) {
        return;
      }
      if (linkUrl.hash !== hash) {
        return;
      }

      link.classList.add("active");
      link.setAttribute("aria-current", "location");
    });
  }

  setNavState();
  window.addEventListener("hashchange", setNavState);

  sectionLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      window.setTimeout(setNavState, 0);
    });
  });

  var content = document.querySelector(".content");
  if (!content || !("IntersectionObserver" in window)) {
    return;
  }

  var currentPath = normalizePath(window.location.pathname);
  var pageSections = Array.prototype.filter.call(sectionLinks, function (link) {
    return linkPath(link) === currentPath;
  });

  if (!pageSections.length) {
    return;
  }

  var observed = pageSections
    .map(function (link) {
      var id = new URL(link.href, window.location.href).hash.slice(1);
      return id ? document.getElementById(id) : null;
    })
    .filter(Boolean);

  if (!observed.length) {
    return;
  }

  var observer = new IntersectionObserver(
    function (entries) {
      if (window.location.hash) {
        return;
      }

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

      var activeId = visible[0].target.id;
      clearNavState();

      chapterLinks.forEach(function (link) {
        if (linkPath(link) === currentPath) {
          link.classList.add("is-on-page");
        }
      });

      pageSections.forEach(function (link) {
        var id = new URL(link.href, window.location.href).hash.slice(1);
        if (id === activeId) {
          link.classList.add("active");
          link.setAttribute("aria-current", "location");
        }
      });
    },
    { rootMargin: "-15% 0px -75% 0px", threshold: 0 }
  );

  observed.forEach(function (target) {
    observer.observe(target);
  });
})();
