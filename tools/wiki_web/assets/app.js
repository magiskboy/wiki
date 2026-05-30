(function () {
  const STORAGE_KEY = "my-brain-theme";
  const THEMES = ["light", "dark", "paper"];
  const root = document.documentElement;

  function getPreferred() {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved && THEMES.includes(saved)) return saved;
    if (window.matchMedia("(prefers-color-scheme: dark)").matches) return "dark";
    return "light";
  }

  function mermaidTheme() {
    return root.getAttribute("data-theme") === "dark" ? "dark" : "default";
  }

  async function renderMermaid() {
    if (typeof mermaid === "undefined") return;
    mermaid.initialize({
      startOnLoad: false,
      theme: mermaidTheme(),
      securityLevel: "loose",
      fontFamily: "inherit",
    });
    await mermaid.run({ querySelector: ".mermaid" }).catch(() => {});
  }

  function applyTheme(name) {
    root.setAttribute("data-theme", name);
    localStorage.setItem(STORAGE_KEY, name);
    document.querySelectorAll("[data-theme-btn]").forEach((btn) => {
      btn.setAttribute(
        "aria-pressed",
        btn.dataset.themeBtn === name ? "true" : "false"
      );
    });
    renderMermaid();
  }

  document.querySelectorAll("[data-theme-btn]").forEach((btn) => {
    btn.addEventListener("click", () => applyTheme(btn.dataset.themeBtn));
  });

  applyTheme(getPreferred());
})();
