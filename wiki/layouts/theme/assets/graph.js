(function () {
  var root = window.KB_ROOT || "";
  var el = document.getElementById("kb-graph");
  if (!el || typeof cytoscape === "undefined") return;
  if (window.cytoscapeFcose) {
    try { cytoscape.use(window.cytoscapeFcose); } catch (e) {}
  }

  // Màu theo lĩnh vực (tag). Node nhiều tag => gradient pha trộn.
  var TAG_COLORS = {
    python: "#3b6ea5",
    web: "#2f8f9d",
    "web-performance": "#3f9c8c",
    frontend: "#5aa9d6",
    ai: "#7a5cc0",
    llm: "#9b6dd6",
    "llm-inference": "#6a51b0",
    infrastructure: "#5f7088",
    "software-engineering": "#4f9e6a",
    mindset: "#d08a3e",
    career: "#c75d56",
    learning: "#8aa84b",
    philosophy: "#9c7b4d",
    finance: "#c9a23a",
    webrtc: "#2c8a4a",
    petrophysics: "#a06b3a",
    game: "#b14a8a",
  };
  var FALLBACK_COLOR = "#8a909b";

  function cssVar(name) {
    return getComputedStyle(document.documentElement)
      .getPropertyValue(name)
      .trim();
  }

  function tagColors(tags) {
    var cols = (tags || []).map(function (t) { return TAG_COLORS[t] || FALLBACK_COLOR; });
    if (cols.length === 0) cols = [FALLBACK_COLOR];
    if (cols.length === 1) cols = [cols[0], cols[0]];
    return cols;
  }

  var cy, degMin = 0, degMax = 1, showLabels = false;
  var tfIdfOn = false;
  var dataCache = null;
  var is3D = false;
  var fg3d = null;
  var el3d = null;
  var libs3dLoaded = false;
  var node3dById = {};
  var adj3d = {};
  var KB_3D_KEY = "kb-graph-3d";
  var KB_DIR_KEY = "kb-graph-dir";
  var dirOn = false;
  var dashTimer = 0;
  var dashOffset = 0;
  var LIB_THREE = "https://unpkg.com/three@0.157.0/build/three.min.js";
  var LIB_SPRITETEXT = "https://unpkg.com/three-spritetext@1.8.2/dist/three-spritetext.min.js";
  var LIB_FG3D = "https://unpkg.com/3d-force-graph@1.73.4/dist/3d-force-graph.min.js";
  var BASE_EDGE_LEN = 95;
  function edgeLen(edge) {
    var w = edge.data("weight") || 0;
    return BASE_EDGE_LEN / (1 + 0.5 * w);
  }
  var panel = document.getElementById("graph-panel");
  var tooltip = document.createElement("div");
  tooltip.className = "graph-tooltip";
  tooltip.hidden = true;
  document.body.appendChild(tooltip);

  var embedded = document.getElementById("graph-data");
  if (embedded) {
    try { init(JSON.parse(embedded.textContent)); }
    catch (e) { el.innerHTML = '<p class="graph-empty">Dữ liệu đồ thị lỗi.</p>'; }
  } else {
    fetch(root + "assets/graph.json")
      .then(function (r) { return r.json(); })
      .then(init)
      .catch(function () {
        el.innerHTML = '<p class="graph-empty">Không tải được dữ liệu đồ thị. Hãy chạy qua web server.</p>';
      });
  }

  function styleSheet() {
    var high = cssVar("--accent") || "#2f6e4a";
    var text = cssVar("--text") || "#1b1f24";
    var edge = cssVar("--border") || "#dddddd";
    var bg = cssVar("--bg-elevated") || "#ffffff";
    return [
      {
        selector: "node",
        style: {
          "background-fill": "linear-gradient",
          "background-gradient-stop-colors": "data(grad)",
          "background-gradient-direction": "to-bottom-right",
          width: "mapData(deg, " + degMin + ", " + degMax + ", 12, 46)",
          height: "mapData(deg, " + degMin + ", " + degMax + ", 12, 46)",
          "border-width": 1.5,
          "border-color": bg,
          label: "data(label)",
          color: text,
          "font-family": "system-ui, sans-serif",
          "font-size": 11,
          "text-wrap": "wrap",
          "text-max-width": 110,
          "text-valign": "bottom",
          "text-margin-y": 4,
          "text-opacity": 0,
          "text-background-color": bg,
          "text-background-opacity": 0.85,
          "text-background-padding": 2,
          "transition-property": "opacity, text-opacity, background-color",
          "transition-duration": "0.12s",
        },
      },
      { selector: "node.show-label, node.hl, node:selected", style: { "text-opacity": 1 } },
      { selector: "node:selected", style: { "border-color": high, "border-width": 3 } },
      {
        selector: "edge",
        style: {
          width: 1,
          "line-color": edge,
          "curve-style": "bezier",
          opacity: 0.55,
          "transition-property": "opacity, line-color, width",
          "transition-duration": "0.12s",
        },
      },
      { selector: "edge.hl", style: { "line-color": high, opacity: 0.95, width: 2 } },
      { selector: "edge.dir", style: {
          "target-arrow-shape": "triangle",
          "target-arrow-color": edge,
          "arrow-scale": 0.9,
          "line-style": "dashed",
          "line-dash-pattern": [6, 4],
        } },
      { selector: "edge.dir.bidi", style: {
          "source-arrow-shape": "triangle",
          "source-arrow-color": edge,
        } },
      { selector: "edge.dir.hl", style: {
          "target-arrow-color": high,
          "source-arrow-color": high,
        } },
      { selector: ".faded", style: { opacity: 0.12, "text-opacity": 0 } },
    ];
  }

  function init(data) {
    dataCache = data;
    var degs = data.nodes.map(function (n) { return n.degree; });
    degMin = Math.min.apply(null, degs);
    degMax = Math.max.apply(null, degs) || 1;

    var N = data.nodes.length;
    var df = {};
    var tagsBy = {};
    data.nodes.forEach(function (n) {
      var ts = n.tags || [];
      tagsBy[n.id] = ts;
      ts.forEach(function (t) { df[t] = (df[t] || 0) + 1; });
    });
    var idf = {};
    Object.keys(df).forEach(function (t) { idf[t] = Math.log(N / df[t]); });

    var elements = [];
    data.nodes.forEach(function (n) {
      elements.push({
        data: {
          id: n.id,
          label: n.title,
          url: n.url,
          tags: (n.tags || []).join(", "),
          grad: tagColors(n.tags).join(" "),
          group: n.group,
          deg: n.degree,
        },
      });
    });
    data.edges.forEach(function (e, i) {
      var a = tagsBy[e.source] || [];
      var b = tagsBy[e.target] || [];
      var setB = {};
      b.forEach(function (t) { setB[t] = true; });
      var w = 0;
      a.forEach(function (t) { if (setB[t]) w += idf[t] || 0; });
      elements.push({
        data: {
          id: "e" + i,
          source: e.source,
          target: e.target,
          reason: (e.labels || []).join(" · "),
          weight: w,
          bidi: !!e.bidirectional,
        },
      });
    });

    cy = cytoscape({
      container: el,
      elements: elements,
      style: styleSheet(),
      minZoom: 0.2,
      maxZoom: 3,
      wheelSensitivity: 0.2,
    });

    setupField();
    wireEvents();
    populateTagFilter(data.nodes);
    buildLegend(data.nodes);
    runLayout();

    var mo = new MutationObserver(function () {
      cy.style(styleSheet());
    });
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });
  }

  function layoutOpts() {
    var hasFcose = !!window.cytoscapeFcose;
    return hasFcose
      ? { name: "fcose", quality: "proof", animate: false, randomize: true,
          packComponents: true, nodeSeparation: 130,
          idealEdgeLength: tfIdfOn ? edgeLen : BASE_EDGE_LEN,
          nodeRepulsion: 7000, padding: 30 }
      : { name: "cose", animate: false, padding: 30 };
  }

  function runLayout() {
    var lay = cy.layout(layoutOpts());
    lay.one("layoutstop", function () {
      packComponents();
      cy.fit(undefined, 30);
    });
    lay.run();
  }

  // Tách các thành phần liên thông và xếp theo hàng để không vẽ đè lên nhau.
  function packComponents() {
    var comps = cy.elements().components();
    if (comps.length <= 1) return;
    comps.sort(function (a, b) { return b.nodes().length - a.nodes().length; });

    var gap = 70;
    var boxes = comps.map(function (c) { return c.boundingBox(); });
    var totalArea = 0, maxW = 0;
    boxes.forEach(function (b) {
      totalArea += (b.w + gap) * (b.h + gap);
      if (b.w > maxW) maxW = b.w;
    });
    var rowLimit = Math.max(maxW, Math.sqrt(totalArea) * 1.3);

    var cursorX = 0, rowY = 0, rowH = 0;
    comps.forEach(function (comp, i) {
      var b = boxes[i];
      if (cursorX > 0 && cursorX + b.w > rowLimit) {
        cursorX = 0;
        rowY += rowH + gap;
        rowH = 0;
      }
      var dx = cursorX - b.x1;
      var dy = rowY - b.y1;
      comp.nodes().forEach(function (n) {
        var p = n.position();
        n.position({ x: p.x + dx, y: p.y + dy });
      });
      cursorX += b.w + gap;
      if (b.h > rowH) rowH = b.h;
    });
  }

  // Lớp "trường màu" (contour) phía sau đồ thị.
  var field, fieldCtx, fieldRaf = 0, fieldOn = true;
  var FIELD_SPREAD = 7;

  function hexA(hex, a) {
    hex = hex.replace("#", "");
    if (hex.length === 3) hex = hex[0] + hex[0] + hex[1] + hex[1] + hex[2] + hex[2];
    var r = parseInt(hex.slice(0, 2), 16),
      g = parseInt(hex.slice(2, 4), 16),
      b = parseInt(hex.slice(4, 6), 16);
    return "rgba(" + r + "," + g + "," + b + "," + a + ")";
  }

  function setupField() {
    var stage = el.parentNode;
    field = document.createElement("canvas");
    field.className = "graph-field";
    stage.insertBefore(field, el);
    fieldCtx = field.getContext("2d");
    cy.on("render", scheduleField);
    var btn = document.getElementById("graph-field-toggle");
    if (btn) btn.addEventListener("click", function () {
      fieldOn = !fieldOn;
      btn.setAttribute("aria-pressed", fieldOn ? "true" : "false");
      field.style.display = fieldOn ? "" : "none";
      if (fieldOn) scheduleField();
    });
  }

  function scheduleField() {
    if (fieldRaf) return;
    fieldRaf = requestAnimationFrame(function () {
      fieldRaf = 0;
      drawField();
    });
  }

  function drawField() {
    if (!fieldCtx || !fieldOn) return;
    var dpr = window.devicePixelRatio || 1;
    var w = el.clientWidth, h = el.clientHeight;
    if (field.width !== w * dpr || field.height !== h * dpr) {
      field.width = w * dpr;
      field.height = h * dpr;
    }
    fieldCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
    fieldCtx.clearRect(0, 0, w, h);
    cy.nodes().forEach(function (n) {
      var p = n.renderedPosition();
      var r = Math.max(n.renderedWidth(), n.renderedHeight()) / 2;
      var radius = r * FIELD_SPREAD;
      var cols = (n.data("grad") || "").split(" ").filter(Boolean);
      var uniq = cols.filter(function (c, i) { return cols.indexOf(c) === i; });
      var a = 0.5 / Math.sqrt(uniq.length || 1);
      uniq.forEach(function (c) {
        var grd = fieldCtx.createRadialGradient(p.x, p.y, r * 0.4, p.x, p.y, radius);
        grd.addColorStop(0, hexA(c, a));
        grd.addColorStop(1, hexA(c, 0));
        fieldCtx.fillStyle = grd;
        fieldCtx.beginPath();
        fieldCtx.arc(p.x, p.y, radius, 0, 2 * Math.PI);
        fieldCtx.fill();
      });
    });
  }

  function neighborhood(node) {
    return node.closedNeighborhood();
  }

  function focus(node) {
    cy.elements().addClass("faded");
    var nb = neighborhood(node);
    nb.removeClass("faded").addClass("hl");
  }

  function clearFocus() {
    cy.elements().removeClass("faded hl");
    if (activeLegendTag) applyTagFilter(activeLegendTag);
  }

  function wireEvents() {
    cy.on("mouseover", "node", function (ev) {
      focus(ev.target);
    });
    cy.on("mouseout", "node", function () {
      if (!cy.$(":selected").length) clearFocus();
    });

    cy.on("mouseover", "edge", function (ev) {
      var r = ev.target.data("reason");
      if (!r) return;
      tooltip.textContent = r;
      tooltip.hidden = false;
    });
    cy.on("mousemove", "edge", function (ev) {
      tooltip.style.left = ev.originalEvent.pageX + 12 + "px";
      tooltip.style.top = ev.originalEvent.pageY + 12 + "px";
    });
    cy.on("mouseout", "edge", function () {
      tooltip.hidden = true;
    });

    cy.on("tap", "node", function (ev) {
      var node = ev.target;
      cy.$(":selected").unselect();
      node.select();
      focus(node);
      showPanel(node);
    });

    cy.on("tap", function (ev) {
      if (ev.target === cy) {
        cy.$(":selected").unselect();
        clearFocus();
        hidePanel();
      }
    });

    var search = document.getElementById("graph-search");
    if (search) search.addEventListener("input", function () { runSearch(search.value); });

    var tag = document.getElementById("graph-tag");
    if (tag) tag.addEventListener("change", function () { runTagFilter(tag.value); });

    var labels = document.getElementById("graph-labels");
    if (labels) labels.addEventListener("click", function () {
      showLabels = !showLabels;
      labels.setAttribute("aria-pressed", showLabels ? "true" : "false");
      cy.nodes().toggleClass("show-label", showLabels);
    });

    var tfBtn = document.getElementById("graph-tfidf-toggle");
    if (tfBtn) tfBtn.addEventListener("click", function () {
      tfIdfOn = !tfIdfOn;
      tfBtn.setAttribute("aria-pressed", tfIdfOn ? "true" : "false");
      runLayout();
    });

    var btnDir = document.getElementById("graph-dir-toggle");
    if (btnDir) {
      btnDir.addEventListener("click", function () {
        setDirOn(!dirOn);
        btnDir.setAttribute("aria-pressed", dirOn ? "true" : "false");
      });
      var restoreDir = false;
      try { restoreDir = localStorage.getItem(KB_DIR_KEY) === "1"; } catch (e) {}
      if (restoreDir) {
        setDirOn(true);
        btnDir.setAttribute("aria-pressed", "true");
      }
    }

    var btn3d = document.getElementById("graph-3d-toggle");
    if (btn3d) {
      btn3d.addEventListener("click", function () {
        if (is3D) {
          exit3D();
          btn3d.setAttribute("aria-pressed", "false");
        } else {
          btn3d.setAttribute("aria-pressed", "true");
          enter3D().catch(function (err) {
            console.error("3D init failed", err);
            btn3d.setAttribute("aria-pressed", "false");
          });
        }
      });
      var restore = false;
      try { restore = localStorage.getItem(KB_3D_KEY) === "1"; } catch (e) {}
      if (restore) {
        btn3d.setAttribute("aria-pressed", "true");
        enter3D().catch(function (err) {
          console.error("3D init failed", err);
          btn3d.setAttribute("aria-pressed", "false");
        });
      }
    }

    var legendBox = document.getElementById("graph-legend");
    if (legendBox) legendBox.addEventListener("click", function (ev) {
      var btn = ev.target.closest && ev.target.closest(".graph-legend-item");
      if (!btn) return;
      var tag = btn.getAttribute("data-tag");
      setLegendTag(activeLegendTag === tag ? null : tag);
    });

    var reset = document.getElementById("graph-reset");
    if (reset) reset.addEventListener("click", function () {
      cy.$(":selected").unselect();
      clearFocus();
      hidePanel();
      if (search) search.value = "";
      if (tag) tag.value = "";
      cy.animate({ fit: { padding: 30 } }, { duration: 250 });
    });
  }

  function runSearch(q) {
    q = (q || "").trim().toLowerCase();
    if (!q) { clearFocus(); return; }
    var matches = cy.nodes().filter(function (n) {
      return n.data("label").toLowerCase().indexOf(q) !== -1;
    });
    cy.elements().addClass("faded");
    matches.removeClass("faded").addClass("hl");
    if (matches.length) cy.animate({ fit: { eles: matches, padding: 80 } }, { duration: 250 });
  }

  function runTagFilter(tag) {
    if (!tag) { clearFocus(); return; }
    cy.elements().addClass("faded");
    var keep = cy.nodes().filter(function (n) {
      return ("," + n.data("tags").replace(/\s/g, "") + ",").indexOf("," + tag + ",") !== -1;
    });
    keep.removeClass("faded").addClass("hl");
    keep.connectedEdges().forEach(function (e) {
      if (!e.source().hasClass("faded") && !e.target().hasClass("faded")) e.removeClass("faded");
    });
  }

  function populateTagFilter(nodes) {
    var sel = document.getElementById("graph-tag");
    if (!sel) return;
    var set = {};
    nodes.forEach(function (n) { (n.tags || []).forEach(function (t) { set[t] = (set[t] || 0) + 1; }); });
    Object.keys(set).sort().forEach(function (t) {
      var o = document.createElement("option");
      o.value = t;
      o.textContent = t + " (" + set[t] + ")";
      sel.appendChild(o);
    });
  }

  function buildLegend(nodes) {
    var box = document.getElementById("graph-legend");
    if (!box) return;
    var present = {};
    nodes.forEach(function (n) { (n.tags || []).forEach(function (t) { present[t] = true; }); });
    var items = Object.keys(TAG_COLORS).filter(function (t) { return present[t]; });
    box.innerHTML = items.map(function (t) {
      return '<button type="button" class="graph-legend-item" data-tag="' + escapeHtml(t) +
        '" aria-pressed="false"><span class="graph-legend-dot" style="background:' +
        TAG_COLORS[t] + '"></span>' + escapeHtml(t) + "</button>";
    }).join("");
  }

  var activeLegendTag = null;

  function setLegendTag(tag) {
    activeLegendTag = tag;
    var box = document.getElementById("graph-legend");
    if (box) {
      Array.prototype.forEach.call(box.querySelectorAll(".graph-legend-item"), function (b) {
        b.setAttribute("aria-pressed", b.getAttribute("data-tag") === tag ? "true" : "false");
      });
    }
    if (tag) applyTagFilter(tag);
    else cy.elements().removeClass("faded hl");
    apply3DFilter();
  }

  function applyTagFilter(tag) {
    cy.elements().addClass("faded");
    var keep = cy.nodes().filter(function (n) {
      return ("," + (n.data("tags") || "").replace(/\s/g, "") + ",").indexOf("," + tag + ",") !== -1;
    });
    keep.removeClass("faded").addClass("hl");
    keep.connectedEdges().forEach(function (e) {
      if (!e.source().hasClass("faded") && !e.target().hasClass("faded")) e.removeClass("faded");
    });
  }

  function renderPanelHtml(info) {
    if (!panel) return;
    var rows = info.edges.map(function (e) {
      return '<li><a href="' + root + e.url + '">' +
        escapeHtml(e.label) + "</a>" +
        (e.reason ? '<span class="graph-reason">' + escapeHtml(e.reason) + "</span>" : "") +
        "</li>";
    }).join("");
    panel.innerHTML =
      '<button type="button" class="graph-panel-close" aria-label="Đóng">×</button>' +
      "<h2>" + escapeHtml(info.label) + "</h2>" +
      (info.tags ? '<p class="graph-panel-tags">' + escapeHtml(info.tags) + "</p>" : "") +
      '<a class="graph-open" href="' + root + info.url + '">Mở bài viết →</a>' +
      "<p class=\"graph-panel-label\">" + info.edges.length + " liên kết</p>" +
      '<ul class="graph-links">' + rows + "</ul>";
    panel.hidden = false;
    var close = panel.querySelector(".graph-panel-close");
    if (close) close.addEventListener("click", function () {
      if (cy) cy.$(":selected").unselect();
      clearFocus();
      hidePanel();
    });
  }

  function showPanel(node) {
    if (!panel) return;
    var edges = node.connectedEdges();
    var info = {
      label: node.data("label"),
      tags: node.data("tags"),
      url: node.data("url"),
      edges: edges.map(function (e) {
        var other = e.source().id() === node.id() ? e.target() : e.source();
        return {
          label: other.data("label"),
          url: other.data("url"),
          reason: e.data("reason"),
        };
      }),
    };
    renderPanelHtml(info);
  }

  function hidePanel() {
    if (panel) { panel.hidden = true; panel.innerHTML = ""; }
  }

  function setDirOn(on) {
    dirOn = !!on;
    try { localStorage.setItem(KB_DIR_KEY, dirOn ? "1" : "0"); } catch (e) {}
    if (cy) {
      if (dirOn) {
        cy.edges().forEach(function (e) {
          e.addClass("dir");
          if (e.data("bidi")) e.addClass("bidi");
        });
        startDashAnim();
      } else {
        stopDashAnim();
        cy.edges().removeClass("dir bidi");
      }
    }
    apply3DDirection();
  }

  function startDashAnim() {
    if (dashTimer) return;
    dashTimer = setInterval(function () {
      if (!cy) return;
      dashOffset = (dashOffset + 1) % 1000;
      cy.startBatch();
      cy.edges(".dir").style("line-dash-offset", -dashOffset);
      cy.endBatch();
    }, 80);
  }

  function stopDashAnim() {
    if (dashTimer) { clearInterval(dashTimer); dashTimer = 0; }
  }

  function apply3DDirection() {
    if (!fg3d) return;
    var edgeCol = theme3DColors().edge;
    var accent = cssVar("--accent") || "#2f6e4a";
    fg3d
      .linkColor(function (l) {
        return dirOn && l.bidirectional ? accent : edgeCol;
      })
      .linkDirectionalArrowLength(function (l) {
        return dirOn ? 4 : 0;
      })
      .linkDirectionalArrowRelPos(0.95)
      .linkDirectionalParticles(function (l) {
        if (!dirOn) return 0;
        return l.bidirectional ? 3 : 1;
      })
      .linkDirectionalParticleSpeed(0.005)
      .linkDirectionalParticleWidth(1.5);
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  // ---------------- 3D view ----------------

  function loadScript(src) {
    return new Promise(function (resolve, reject) {
      if (!src) { reject(new Error("loadScript: src rỗng")); return; }
      var existing = document.querySelector('script[data-kb3d="' + src + '"]');
      if (existing) {
        if (existing.dataset.loaded === "1") { resolve(); return; }
        existing.addEventListener("load", function () { resolve(); });
        existing.addEventListener("error", function () { reject(new Error("Không tải được " + src)); });
        return;
      }
      var s = document.createElement("script");
      s.src = src;
      s.async = false;
      s.setAttribute("data-kb3d", src);
      s.onload = function () { s.dataset.loaded = "1"; resolve(); };
      s.onerror = function () { reject(new Error("Không tải được " + src)); };
      document.head.appendChild(s);
    });
  }

  function ensureLibs3D() {
    if (libs3dLoaded) return Promise.resolve();
    return loadScript(LIB_THREE)
      .then(function () { return loadScript(LIB_SPRITETEXT); })
      .then(function () { return loadScript(LIB_FG3D); })
      .then(function () { libs3dLoaded = true; });
  }

  function enter3D() {
    if (!dataCache) return Promise.reject(new Error("Không có dữ liệu"));
    el3d = document.getElementById("kb-graph-3d");
    if (!el3d) return Promise.reject(new Error("Thiếu container #kb-graph-3d"));
    el3d.style.position = "absolute";
    el3d.style.inset = "0";
    el3d.style.width = "100%";
    el3d.style.height = "100%";
    el3d.style.zIndex = "1";
    return ensureLibs3D().then(function () {
      el.style.display = "none";
      if (field) field.style.display = "none";
      el3d.hidden = false;
      if (!fg3d) initFg3d();
      sync3DSize();
      is3D = true;
      apply3DFilter();
      apply3DDirection();
      try { localStorage.setItem(KB_3D_KEY, "1"); } catch (e) {}
    });
  }

  function sync3DSize() {
    if (!fg3d || !el3d) return;
    var w = el3d.clientWidth || el3d.offsetWidth || window.innerWidth;
    var h = el3d.clientHeight || el3d.offsetHeight || window.innerHeight;
    fg3d.width(w).height(h);
  }

  function exit3D() {
    el.style.display = "";
    if (field && fieldOn) field.style.display = "";
    if (el3d) el3d.hidden = true;
    is3D = false;
    try { localStorage.setItem(KB_3D_KEY, "0"); } catch (e) {}
  }

  function theme3DColors() {
    return {
      bg: cssVar("--bg-elevated") || "#ffffff",
      text: cssVar("--text") || "#1b1f24",
      edge: cssVar("--border") || "#cccccc",
    };
  }

  function makeSprite(name) {
    var c = theme3DColors();
    var s = new window.SpriteText(name);
    s.color = c.text;
    s.backgroundColor = "rgba(0,0,0,0)";
    s.textHeight = 4;
    s.fontFace = "system-ui, sans-serif";
    s.position.set(0, 8, 0);
    return s;
  }

  function initFg3d() {
    var ForceGraph3D = window.ForceGraph3D;
    var c = theme3DColors();

    var nodes3d = dataCache.nodes.map(function (n) {
      var cols = tagColors(n.tags);
      return {
        id: n.id,
        name: n.title,
        url: n.url,
        tags: n.tags || [],
        degree: n.degree,
        color: cols[0],
      };
    });
    node3dById = {};
    adj3d = {};
    nodes3d.forEach(function (n) { node3dById[n.id] = n; adj3d[n.id] = []; });

    var links3d = dataCache.edges.map(function (e) {
      var reason = (e.labels || []).join(" · ");
      adj3d[e.source].push({ other: e.target, reason: reason });
      adj3d[e.target].push({ other: e.source, reason: reason });
      return {
        source: e.source,
        target: e.target,
        reason: reason,
        bidirectional: !!e.bidirectional,
      };
    });

    fg3d = ForceGraph3D()(el3d)
      .graphData({ nodes: nodes3d, links: links3d })
      .backgroundColor(c.bg)
      .nodeRelSize(4)
      .nodeVal(function (n) { return 2 + Math.sqrt(n.degree || 1); })
      .nodeColor(function (n) { return n.color; })
      .nodeOpacity(0.95)
      .linkColor(function () { return theme3DColors().edge; })
      .linkOpacity(0.35)
      .linkLabel(function (l) { return l.reason || ""; })
      .nodeLabel(function (n) { return ""; })
      .nodeThreeObjectExtend(true)
      .nodeThreeObject(function (n) { return makeSprite(n.name); })
      .onNodeClick(function (n) {
        var info = {
          label: n.name,
          tags: (n.tags || []).join(", "),
          url: n.url,
          edges: (adj3d[n.id] || []).map(function (e) {
            var other = node3dById[e.other];
            return { label: other.name, url: other.url, reason: e.reason };
          }),
        };
        renderPanelHtml(info);
        var dist = 120;
        var dx = n.x || 0, dy = n.y || 0, dz = n.z || 0;
        var distRatio = 1 + dist / Math.hypot(dx, dy, dz || 1);
        fg3d.cameraPosition(
          { x: dx * distRatio, y: dy * distRatio, z: dz * distRatio },
          n,
          800
        );
      })
      .onBackgroundClick(function () { hidePanel(); });

    var mo = new MutationObserver(function () {
      if (!fg3d) return;
      var cc = theme3DColors();
      fg3d
        .backgroundColor(cc.bg)
        .linkColor(function () { return cc.edge; })
        .nodeThreeObject(function (n) { return makeSprite(n.name); })
        .refresh();
    });
    mo.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

    window.addEventListener("resize", function () {
      if (is3D) sync3DSize();
    });
  }

  function apply3DFilter() {
    if (!fg3d) return;
    var tag = activeLegendTag;
    if (!tag) {
      fg3d.nodeVisibility(function () { return true; });
      fg3d.linkVisibility(function () { return true; });
      return;
    }
    function matches(id) {
      var n = node3dById[id];
      return !!n && (n.tags || []).indexOf(tag) !== -1;
    }
    fg3d.nodeVisibility(function (n) { return matches(n.id); });
    fg3d.linkVisibility(function (l) {
      var sid = typeof l.source === "object" ? l.source.id : l.source;
      var tid = typeof l.target === "object" ? l.target.id : l.target;
      return matches(sid) && matches(tid);
    });
  }
})();
