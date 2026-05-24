(function () {
  var tocRoot = document.getElementById("page-toc");
  var content = document.querySelector(".content");
  if (!tocRoot || !content) {
    return;
  }

  var headings = content.querySelectorAll("h2, h3");
  if (!headings.length) {
    tocRoot.closest(".sidebar-toc").classList.add("is-empty");
    return;
  }

  var list = document.createElement("ul");
  list.className = "toc-list";
  var links = [];

  headings.forEach(function (heading) {
    if (!heading.id) {
      heading.id = heading.textContent
        .trim()
        .toLowerCase()
        .replace(/\s+/g, "-")
        .replace(/[^a-z0-9äöüß\-]/gi, "");
    }

    var item = document.createElement("li");
    item.className = heading.tagName === "H3" ? "toc-h3" : "toc-h2";

    var link = document.createElement("a");
    link.href = "#" + heading.id;
    link.textContent = heading.textContent;
    links.push({ link: link, heading: heading });

    item.appendChild(link);
    list.appendChild(item);
  });

  tocRoot.appendChild(list);

  function setActiveLink(active) {
    links.forEach(function (entry) {
      entry.link.classList.toggle("active", entry.link === active);
    });
  }

  if ("IntersectionObserver" in window) {
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

        var match = links.find(function (entry) {
          return entry.heading === visible[0].target;
        });
        if (match) {
          setActiveLink(match.link);
        }
      },
      { rootMargin: "-20% 0px -70% 0px", threshold: 0 }
    );

    links.forEach(function (entry) {
      observer.observe(entry.heading);
    });
  } else if (links.length) {
    setActiveLink(links[0].link);
  }
})();
