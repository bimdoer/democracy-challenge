(function () {
  var chapterLinks = document.querySelectorAll(".sidebar-chapter-tab[data-nav='chapter']");
  var sectionLinks = document.querySelectorAll(".sidebar-section-link[data-nav='section']");
  var SCROLL_MARKER = 120;
  var CONTENT_SCROLL_THRESHOLD = 48;
  var scrollTicking = false;
  var userClickedSection = false;
  var clickResetTimer;

  function siteBasePath() {
    var base = document.body.getAttribute("data-baseurl") || "";
    if (!base) {
      return "";
    }
    return normalizePath(base);
  }

  function stripBasePath(path) {
    var base = siteBasePath();
    if (base && path.indexOf(base) === 0) {
      path = path.slice(base.length);
      if (!path) {
        path = "/";
      }
    }
    return normalizePath(path);
  }

  function normalizePath(pathname) {
    var path = pathname || "/";
    if (path.length > 1 && path.endsWith("/")) {
      path = path.slice(0, -1);
    }
    return path;
  }

  function linkPath(link) {
    return stripBasePath(new URL(link.href, window.location.href).pathname);
  }

  function currentPagePath() {
    return stripBasePath(window.location.pathname);
  }

  function hashIdFromLink(link) {
    var raw = new URL(link.href, window.location.href).hash.slice(1);
    if (!raw) {
      return "";
    }
    try {
      return decodeURIComponent(raw);
    } catch (err) {
      return raw;
    }
  }

  function hashIdFromLocation() {
    var raw = window.location.hash.slice(1);
    if (!raw) {
      return "";
    }
    try {
      return decodeURIComponent(raw);
    } catch (err) {
      return raw;
    }
  }

  function getPageSectionLinks() {
    var path = currentPagePath();
    return Array.prototype.filter.call(sectionLinks, function (link) {
      return linkPath(link) === path;
    });
  }

  function getSectionTargets(pageLinks) {
    return pageLinks
      .map(function (link) {
        var id = hashIdFromLink(link);
        var el = id ? document.getElementById(id) : null;
        return el ? { id: id, el: el, link: link } : null;
      })
      .filter(Boolean);
  }

  function findActiveSectionIdFromScroll(targets) {
    if (!targets.length) {
      return null;
    }

    var activeId = targets[0].id;
    targets.forEach(function (item) {
      if (item.el.getBoundingClientRect().top <= SCROLL_MARKER) {
        activeId = item.id;
      }
    });
    return activeId;
  }

  function resolveActiveSectionId(pageLinks, targets) {
    var hashId = hashIdFromLocation();
    if (hashId && pageLinks.some(function (link) { return hashIdFromLink(link) === hashId; })) {
      return hashId;
    }

    if (targets.length && window.scrollY > CONTENT_SCROLL_THRESHOLD) {
      return findActiveSectionIdFromScroll(targets);
    }

    return null;
  }

  function scrollElementIntoNav(link) {
    var nav = document.querySelector(".sidebar-chapters-nav");
    if (!nav || !link) {
      return;
    }

    var linkRect = link.getBoundingClientRect();
    var navRect = nav.getBoundingClientRect();
    if (linkRect.top < navRect.top + 8 || linkRect.bottom > navRect.bottom - 8) {
      link.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }

  function scrollCurrentChapterBlockIntoView() {
    var block = document.querySelector(".sidebar-chapter-item.is-current");
    if (block) {
      block.scrollIntoView({ block: "nearest" });
    }
  }

  function applyActiveSection(activeId) {
    var path = currentPagePath();
    var activeLink = null;

    chapterLinks.forEach(function (link) {
      var onPage = linkPath(link) === path;
      link.classList.toggle("is-on-page", onPage);
      link.classList.toggle("active", onPage && !activeId);
      if (onPage && !activeId) {
        link.setAttribute("aria-current", "page");
      } else {
        link.removeAttribute("aria-current");
      }
    });

    sectionLinks.forEach(function (link) {
      var linkUrl = new URL(link.href, window.location.href);
      var id = hashIdFromLink(link);
      var isActive =
        !!activeId && stripBasePath(linkUrl.pathname) === path && id === activeId;

      link.classList.toggle("active", isActive);
      if (isActive) {
        link.setAttribute("aria-current", "location");
        activeLink = link;
      } else {
        link.removeAttribute("aria-current");
      }
    });

    if (activeLink && userClickedSection) {
      scrollElementIntoNav(activeLink);
    }
  }

  function updateFromScroll() {
    var pageLinks = getPageSectionLinks();
    var targets = getSectionTargets(pageLinks);
    applyActiveSection(resolveActiveSectionId(pageLinks, targets));
  }

  function scheduleScrollUpdate() {
    if (scrollTicking) {
      return;
    }
    scrollTicking = true;
    window.requestAnimationFrame(function () {
      updateFromScroll();
      scrollTicking = false;
    });
  }

  updateFromScroll();
  scrollCurrentChapterBlockIntoView();

  window.addEventListener("scroll", scheduleScrollUpdate, { passive: true });
  window.addEventListener("resize", scheduleScrollUpdate, { passive: true });
  window.addEventListener("hashchange", scheduleScrollUpdate);

  sectionLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      userClickedSection = true;
      window.clearTimeout(clickResetTimer);
      clickResetTimer = window.setTimeout(function () {
        userClickedSection = false;
      }, 800);
      window.setTimeout(scheduleScrollUpdate, 50);
      window.setTimeout(scheduleScrollUpdate, 300);
    });
  });

  chapterLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      userClickedSection = false;
    });
  });
})();
