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

    item.appendChild(link);
    list.appendChild(item);
  });

  tocRoot.appendChild(list);
})();
