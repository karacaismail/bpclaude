// bpclaude: aşamalı geliştirme. Betik çalışmazsa bütün içerik ve bağlantılar yine kullanılabilir.
(function () {
  "use strict";

  var root = document.documentElement;
  var WIDE = (getComputedStyle(root).getPropertyValue("--bp-wide") || "").trim() || "60rem";

  // Dar ekran menüsü. Betiksiz durumda "Menü" bir bağlantıdır ve listeyi :target ile açar.
  // Betik çalışınca aynı yerde gerçek bir düğmeye dönüşür; sayfa düzeni kaymaz.
  var nav = document.querySelector(".site-nav");
  var link = document.querySelector("a.nav-toggle");
  if (nav && link) {
    var toggle = document.createElement("button");
    toggle.type = "button";
    toggle.className = link.className;
    toggle.textContent = link.textContent;
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-controls", "site-nav-list");
    link.parentNode.replaceChild(toggle, link);
    var setOpen = function (open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
    };
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key !== "Escape" || toggle.getAttribute("aria-expanded") !== "true") return;
      var a = document.activeElement;
      if (a !== toggle && !nav.contains(a)) return;
      setOpen(false);
      toggle.focus();
    });
  }

  // Kaydırma bölgeleri: içerik taşıyorsa klavye durağı olur ve ok tuşlarıyla kayar; taşmıyorsa durak değildir.
  var regions = Array.prototype.slice.call(document.querySelectorAll(".table-wrap, .figure__scroll"));
  function syncRegions() {
    regions.forEach(function (r) {
      if (r.scrollWidth > r.clientWidth) r.setAttribute("tabindex", "0");
      else if (document.activeElement !== r) r.removeAttribute("tabindex");
    });
  }
  if (regions.length) {
    syncRegions();
    window.addEventListener("resize", syncRegions);
    window.addEventListener("load", syncRegions);
    document.addEventListener("toggle", syncRegions, true);
    if ("ResizeObserver" in window) {
      var ro = new ResizeObserver(syncRegions);
      regions.forEach(function (r) {
        ro.observe(r);
        if (r.firstElementChild) ro.observe(r.firstElementChild);
      });
    }
    regions.forEach(function (r) {
      r.addEventListener("keydown", function (ev) {
        if (ev.target !== r || ev.altKey || ev.ctrlKey || ev.metaKey) return;
        var step = ev.key === "ArrowRight" ? 48 : ev.key === "ArrowLeft" ? -48 : 0;
        if (!step) return;
        ev.preventDefault();
        r.scrollLeft += step;
      });
    });
  }

  // Türkçe harfleri sadeleştirir: "İK", "ik" ve "IK" aynı sonucu verir. tools/sitelib.py içindeki fold() ile aynıdır.
  var FOLD = { "İ": "i", "I": "i", "ı": "i", "Ş": "s", "ş": "s", "Ğ": "g", "ğ": "g", "Ü": "u", "ü": "u", "Ö": "o", "ö": "o", "Ç": "c", "ç": "c", "Â": "a", "â": "a", "Î": "i", "î": "i", "Û": "u", "û": "u" };
  function fold(s) {
    return s.normalize("NFC").replace(/[İIıŞşĞğÜüÖöÇçÂâÎîÛû]/g, function (c) { return FOLD[c]; }).toLowerCase();
  }
  function debounce(fn, ms) {
    var t;
    return function () { clearTimeout(t); t = setTimeout(fn, ms); };
  }

  // Proje sözlüğü: arama ve tür süzgeci.
  var sozluk = document.getElementById("sozluk-arac");
  if (sozluk) {
    var items = Array.prototype.slice.call(document.querySelectorAll("#sozluk-liste .glossary > li"));
    var groups = Array.prototype.slice.call(document.querySelectorAll("#sozluk-liste .glossary__group"));
    var sq = document.getElementById("sq");
    var sonuc = document.getElementById("sozluk-sonuc");
    var bos = document.getElementById("sozluk-bos");
    var gs = { q: "", grup: "" };
    var filterGlossary = function () {
      var n = 0;
      items.forEach(function (li) {
        var ok = (!gs.grup || li.dataset.grup === gs.grup) && (!gs.q || li.dataset.text.indexOf(gs.q) !== -1);
        li.hidden = !ok;
        if (ok) n += 1;
      });
      groups.forEach(function (g) { g.hidden = !g.querySelector(".glossary > li:not([hidden])"); });
      if (bos) bos.hidden = n !== 0;
      var shown = n;
      clearTimeout(filterGlossary.t);
      filterGlossary.t = setTimeout(function () { if (sonuc) sonuc.textContent = shown + " proje"; }, 300);
    };
    sozluk.hidden = false;
    var spanel = document.getElementById("sozluk-panel");
    var sozet = document.getElementById("sozluk-ozet");
    if (spanel && window.matchMedia("(min-width: " + WIDE + ")").matches) spanel.open = true;
    sozluk.addEventListener("submit", function (ev) { ev.preventDefault(); });
    sozluk.addEventListener("click", function (ev) {
      var btn = ev.target.closest(".chip");
      if (!btn) return;
      gs.grup = btn.dataset.gfilter || "";
      Array.prototype.forEach.call(sozluk.querySelectorAll(".chip"), function (c) { c.setAttribute("aria-pressed", String(c === btn)); });
      if (sozet) sozet.textContent = gs.grup ? gs.grup.toLocaleLowerCase("tr") : "tümü";
      filterGlossary();
    });
    if (sq) sq.addEventListener("input", function () { gs.q = fold(sq.value.trim()); filterGlossary(); });
  }

  // Sıralama sayfası: süzme, arama ve sıralama.
  var list = document.getElementById("liste");
  if (!list) return;
  var form = document.getElementById("suzgec");
  var panel = document.getElementById("suzgec-panel");
  var ozet = document.getElementById("suzgec-ozet");
  var count = document.getElementById("sonuc");
  var empty = document.getElementById("bos");
  var reset = document.getElementById("temizle");
  var q = document.getElementById("q");
  var rows = Array.prototype.slice.call(list.children);
  var dir = { yatirim: 1, puan: -1, nakit: -1, sure: 1, ogrenme: 1, stratejik: -1 };
  var FILTERS = ["karar", "nsinif", "tur"];
  var PARAM = { karar: "karar", nsinif: "nakit", tur: "tur" };
  var state = { karar: "", nsinif: "", tur: "", sort: "yatirim", q: "" };
  var lastUrl = location.search;

  function chipsOf(kind) {
    return form ? Array.prototype.slice.call(form.querySelectorAll(kind === "sort" ? ".chip[data-sort]" : '.chip[data-filter="' + kind + '"]')) : [];
  }

  function syncChips() {
    FILTERS.forEach(function (k) {
      chipsOf(k).forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.value === state[k])); });
    });
    chipsOf("sort").forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.sort === state.sort)); });
  }

  // Adres çubuğuna yalnız düğme seçimleri yazılır ve yalnız değiştiğinde; arama metni adrese konmaz.
  function writeUrl() {
    if (!window.history || !history.replaceState) return;
    var p = new URLSearchParams();
    FILTERS.forEach(function (k) { if (state[k]) p.set(PARAM[k], state[k]); });
    if (state.sort !== "yatirim") p.set("sirala", state.sort);
    var s = p.toString() ? "?" + p.toString() : "";
    if (s === lastUrl) return;
    lastUrl = s;
    try { history.replaceState(null, "", location.pathname + s + location.hash); } catch (err) { /* dosyadan açıldıysa adres değişmez */ }
  }

  function readUrl() {
    var p;
    try { p = new URLSearchParams(location.search); } catch (err) { return; }
    var has = function (kind, v) { return chipsOf(kind).some(function (c) { return (kind === "sort" ? c.dataset.sort : c.dataset.value) === v; }); };
    FILTERS.forEach(function (k) {
      var v = p.get(PARAM[k]);
      if (v && has(k, v)) state[k] = v;
    });
    if (p.get("sirala") && has("sort", p.get("sirala"))) state.sort = p.get("sirala");
  }

  var announceCount = debounce(function () {
    if (count) count.textContent = rows.filter(function (r) { return !r.hidden; }).length + " seçenek gösteriliyor";
  }, 300);

  function apply(immediate) {
    var shown = 0;
    rows.forEach(function (r) {
      var ok = FILTERS.every(function (k) { return !state[k] || r.dataset[k] === state[k]; }) &&
        (!state.q || r.dataset.text.indexOf(state.q) !== -1);
      r.hidden = !ok;
      if (ok) shown += 1;
    });
    var key = state.sort;
    rows.slice().sort(function (a, b) {
      return dir[key] * (parseFloat(a.dataset[key]) - parseFloat(b.dataset[key])) || (parseFloat(a.dataset.yatirim) - parseFloat(b.dataset.yatirim));
    }).forEach(function (r) { list.appendChild(r); });
    if (count) {
      if (immediate) count.textContent = shown + " seçenek gösteriliyor";
      else announceCount();
    }
    if (empty) empty.hidden = shown !== 0;
    if (ozet && form) {
      var parts = [];
      Array.prototype.forEach.call(form.querySelectorAll('.chip[data-filter][aria-pressed="true"]'), function (c) {
        if (c.dataset.value) parts.push(c.textContent.toLocaleLowerCase("tr"));
      });
      if (!parts.length) parts.push("tümü");
      var sorted = form.querySelector('.chip[data-sort][aria-pressed="true"]');
      if (sorted) parts.push(sorted.textContent.toLocaleLowerCase("tr"));
      ozet.textContent = parts.join(" · ");
    }
    writeUrl();
  }

  if (form) {
    form.hidden = false;
    form.addEventListener("submit", function (ev) { ev.preventDefault(); });
    form.addEventListener("click", function (ev) {
      var btn = ev.target.closest(".chip");
      if (!btn) return;
      if (btn.dataset.filter) state[btn.dataset.filter] = btn.dataset.value;
      if (btn.dataset.sort) state.sort = btn.dataset.sort;
      syncChips();
      apply(true);
    });
  }
  if (q) {
    q.addEventListener("input", function () {
      state.q = fold(q.value.trim());
      apply(false);
    });
  }
  if (reset) {
    reset.addEventListener("click", function () {
      FILTERS.forEach(function (k) { state[k] = ""; });
      state.q = "";
      if (q) q.value = "";
      syncChips();
      apply(true);
      if (q) q.focus();
    });
  }

  readUrl();
  var filtered = FILTERS.some(function (k) { return state[k]; }) || state.sort !== "yatirim";
  if (panel && (window.matchMedia("(min-width: " + WIDE + ")").matches || filtered)) panel.open = true;
  syncChips();
  apply(true);
})();
