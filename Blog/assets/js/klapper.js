(function () {
  function toggleKlapper(btn) {
    var klapper = btn.closest(".klapper");
    var panelId = btn.getAttribute("aria-controls");
    var panel = panelId ? document.getElementById(panelId) : klapper.querySelector(".klapper-panel");
    if (!panel) return;

    var open = !klapper.classList.contains("is-open");
    klapper.classList.toggle("is-open", open);
    btn.setAttribute("aria-expanded", open ? "true" : "false");
    panel.hidden = !open;
  }

  document.querySelectorAll(".klapper-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      toggleKlapper(btn);
    });
  });

  function openKlapperFromHash() {
    var id = window.location.hash.replace(/^#/, "");
    if (!id) {
      return;
    }
    var btn = document.getElementById(id);
    if (!btn || !btn.classList.contains("klapper-btn")) {
      return;
    }
    var klapper = btn.closest(".klapper");
    if (klapper && !klapper.classList.contains("is-open")) {
      toggleKlapper(btn);
    }
  }

  openKlapperFromHash();
  window.addEventListener("hashchange", openKlapperFromHash);
})();
