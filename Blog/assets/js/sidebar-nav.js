(function () {
  var chapterLinks = document.querySelectorAll(".sidebar-chapter-tab[data-nav='chapter']");
  var sectionLinks = document.querySelectorAll(".sidebar-section-link[data-nav='section']");
  var SCROLL_MARKER = 120;
  var scrollTicking = false;
  var userClickedNav = false;
  var clickResetTimer;

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

  /** Sections in the sidebar belong to the current page only (Liquid). */
  function getPageSectionLinks() {
    return Array.prototype.slice.call(sectionLinks);
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

    if (targets.length) {
      return findActiveSectionIdFromScroll(targets);
    }

    if (pageLinks.length) {
      return hashIdFromLink(pageLinks[0]);
    }

    return null;
  }

  function scrollNavLinkIntoView(link) {
    var nav = document.querySelector(".sidebar-sections-nav");
    if (!nav || !link) {
      return;
    }

    var linkRect = link.getBoundingClientRect();
    var navRect = nav.getBoundingClientRect();
    if (linkRect.top < navRect.top + 8 || linkRect.bottom > navRect.bottom - 8) {
      link.scrollIntoView({ block: "nearest", behavior: "smooth" });
    }
  }

  function applyActiveSection(activeId) {
    var path = normalizePath(window.location.pathname);
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
        !!activeId && normalizePath(linkUrl.pathname) === path && id === activeId;

      link.classList.toggle("active", isActive);
      if (isActive) {
        link.setAttribute("aria-current", "location");
        activeLink = link;
      } else {
        link.removeAttribute("aria-current");
      }
    });

    if (activeLink && !userClickedNav) {
      scrollNavLinkIntoView(activeLink);
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
  window.addEventListener("scroll", scheduleScrollUpdate, { passive: true });
  window.addEventListener("resize", scheduleScrollUpdate, { passive: true });
  window.addEventListener("hashchange", scheduleScrollUpdate);

  sectionLinks.forEach(function (link) {
    link.addEventListener("click", function () {
      userClickedNav = true;
      window.clearTimeout(clickResetTimer);
      clickResetTimer = window.setTimeout(function () {
        userClickedNav = false;
      }, 800);
      window.setTimeout(scheduleScrollUpdate, 50);
      window.setTimeout(scheduleScrollUpdate, 300);
    });
  });
})();
