// bpclaude: aşamalı geliştirme. Betik çalışmazsa bütün içerik ve bağlantılar yine kullanılabilir.
(function () {
  "use strict";

  // Betik çalışıyor: betik gerektiren araçlar (arama ve süzgeç formları) görünür olur. Betik yüklenemezse gizli kalırlar.
  document.documentElement.classList.add("js");

  // Yatay kayan bir kutunun konumunu bildirir (bas, orta, son); taşma yoksa özniteliği kaldırır. Stil, devamı olan kenarı soldurur.
  function edgeOf(box) {
    var max = box.scrollWidth - box.clientWidth;
    if (max <= 1) box.removeAttribute("data-kenar");
    else box.setAttribute("data-kenar", box.scrollLeft <= 1 ? "bas" : box.scrollLeft >= max - 1 ? "son" : "orta");
  }

  // Bir öğeyi kayan kutunun görünen kısmına, solma bölgelerinin dışına getirir (bölgeler kutunun scroll-padding değeridir).
  function reveal(box, a) {
    var cs = getComputedStyle(box);
    var left = a.offsetLeft - box.offsetLeft;
    var min = left - (parseFloat(cs.scrollPaddingLeft) || 0);
    var max = left + a.offsetWidth - box.clientWidth + (parseFloat(cs.scrollPaddingRight) || 0);
    if (box.scrollLeft > min) box.scrollLeft = Math.max(0, min);
    else if (box.scrollLeft < max) box.scrollLeft = max;
  }

  // Gezinme şeridi her zaman görünür; betik geçerli sayfanın bağlantısını görünen kısma getirir ve şeridin konumunu bildirir.
  var strip = document.getElementById("site-nav-list");
  if (strip) {
    var current = strip.querySelector("[aria-current]");
    // Geçerli bağlantı görünmüyorsa ortalanır. Şeridin genişliği değiştikçe (yön değişimi, geç gelen yerleşim) yinelenir.
    var center = function () {
      if (!current || strip.scrollWidth <= strip.clientWidth) return;
      var left = current.offsetLeft - strip.offsetLeft;
      if (left < strip.scrollLeft || left + current.offsetWidth > strip.scrollLeft + strip.clientWidth) {
        strip.scrollLeft = Math.max(0, left - (strip.clientWidth - current.offsetWidth) / 2);
      }
    };
    var edge = function () { edgeOf(strip); };
    // Yalnız genişlik gerçekten değiştiyse yeniden ortalanır: kullanıcının kaydırdığı şerit yerinden oynatılmaz.
    var width = strip.clientWidth;
    var sync = function () {
      if (strip.clientWidth !== width) { width = strip.clientWidth; center(); }
      edge();
    };
    center();
    edge();
    strip.addEventListener("scroll", edge, { passive: true });
    if ("ResizeObserver" in window) new ResizeObserver(sync).observe(strip);
    else window.addEventListener("resize", sync);
  }

  // Kayan şeritlerde klavyeyle gelinen bağlantı tam görünür olur: bazı tarayıcılar yarısı görünen öğeyi kaydırmaz.
  // Yalnız klavye odağında çalışır: fare ya da dokunmayla odaklanan bağlantı işaretçinin altından kaydırılırsa tıklama boşa gider.
  var toc = document.querySelector(".toc__list");
  [strip, toc].forEach(function (box) {
    if (!box) return;
    box.addEventListener("focusin", function (ev) {
      var a = ev.target;
      if (a === box) return;
      try { if (!a.matches(":focus-visible")) return; } catch (err) { return; }
      reveal(box, a);
    });
  });

  // Bölüm gezintisi: sayfa kaydıkça bulunulan bölümün bağlantısı işaretlenir ve şeritte görünür tutulur.
  if (toc) {
    var secs = [];
    Array.prototype.forEach.call(toc.querySelectorAll("a"), function (a) {
      var el = document.getElementById(a.getAttribute("href").slice(1));
      if (el) secs.push({ a: a, el: el });
    });
    var here = null, waiting = false;
    var mark = function () {
      waiting = false;
      // Eşik, çapa hedefinin geldiği konumla aynı kaynaktan (kökün scroll-padding-top değeri) okunur; başlık ekranın üst üçte birine
      // girince de bölüm değişir. Sayfanın sonuna gelindiyse son bölüm işaretlenir (kısa son bölüm eşiğe hiç ulaşamaz).
      var root = document.documentElement;
      var line = Math.max((parseFloat(getComputedStyle(root).scrollPaddingTop) || 0) + 2, window.innerHeight / 3), now = null;
      secs.forEach(function (x) { if (x.el.getBoundingClientRect().top <= line) now = x.a; });
      if (now && secs.length && window.innerHeight + window.pageYOffset >= root.scrollHeight - 2) now = secs[secs.length - 1].a;
      if (now === here) return;
      if (here) here.removeAttribute("aria-current");
      if (now) { now.setAttribute("aria-current", "location"); reveal(toc, now); }
      here = now;
    };
    window.addEventListener("scroll", function () {
      if (!waiting) { waiting = true; requestAnimationFrame(mark); }
    }, { passive: true });
    mark();
  }

  // Kaydırma bölgeleri (tablo, şekil): içerik taşıyorsa klavye durağı olur, ok tuşlarıyla kayar ve sağ kenarı solar; taşmıyorsa durak değildir.
  var regions = Array.prototype.slice.call(document.querySelectorAll(".table-wrap, .figure__scroll"));
  function syncRegions() {
    regions.forEach(function (r) {
      if (r.scrollWidth > r.clientWidth) r.setAttribute("tabindex", "0");
      else if (document.activeElement !== r) r.removeAttribute("tabindex");
      edgeOf(r);
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
      r.addEventListener("scroll", function () { edgeOf(r); }, { passive: true });
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
  function lower(s) { return s.toLocaleLowerCase("tr"); }

  // Proje sözlüğü: arama ve tür süzgeci. Sayı, açılır bölümün başlığında görünür; canlı bölge gecikmeyle duyurur.
  var sozluk = document.getElementById("sozluk-arac");
  if (sozluk) {
    var items = Array.prototype.slice.call(document.querySelectorAll("#sozluk-liste .glossary > li"));
    var groups = Array.prototype.slice.call(document.querySelectorAll("#sozluk-liste .glossary__group"));
    var sq = document.getElementById("sq");
    var sonuc = document.getElementById("sozluk-sonuc");
    var bos = document.getElementById("sozluk-bos");
    var sozet = document.getElementById("sozluk-ozet");
    var gs = { q: "", grup: "" };
    var shownG = items.length;
    var announceG = debounce(function () { if (sonuc) sonuc.textContent = shownG + " proje"; }, 300);
    var filterGlossary = function () {
      var n = 0;
      items.forEach(function (li) {
        var ok = (!gs.grup || li.dataset.grup === gs.grup) && (!gs.q || li.dataset.text.indexOf(gs.q) !== -1);
        li.hidden = !ok;
        if (ok) n += 1;
      });
      groups.forEach(function (g) { g.hidden = !g.querySelector(".glossary > li:not([hidden])"); });
      if (bos) bos.hidden = n !== 0;
      if (sozet) sozet.textContent = n + " proje · " + (gs.grup ? lower(gs.grup) : "tümü");
      shownG = n;
      announceG();
    };
    sozluk.addEventListener("submit", function (ev) { ev.preventDefault(); });
    sozluk.addEventListener("click", function (ev) {
      var btn = ev.target.closest(".chip");
      if (!btn) return;
      gs.grup = btn.dataset.gfilter || "";
      Array.prototype.forEach.call(sozluk.querySelectorAll(".chip"), function (c) { c.setAttribute("aria-pressed", String(c === btn)); });
      filterGlossary();
    });
    if (sq) {
      sq.addEventListener("input", function () { gs.q = fold(sq.value.trim()); filterGlossary(); });
      gs.q = fold(sq.value.trim());
      if (gs.q) filterGlossary();
    }
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
  var distButtons = [];

  function chipsOf(kind) {
    return form ? Array.prototype.slice.call(form.querySelectorAll(kind === "sort" ? ".chip[data-sort]" : '.chip[data-filter="' + kind + '"]')) : [];
  }

  function syncChips() {
    FILTERS.forEach(function (k) {
      chipsOf(k).forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.value === state[k])); });
    });
    chipsOf("sort").forEach(function (c) { c.setAttribute("aria-pressed", String(c.dataset.sort === state.sort)); });
    distButtons.forEach(function (b) { b.setAttribute("aria-pressed", String(b.dataset.karar === state.karar)); });
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
    var sorted = rows.slice().sort(function (a, b) {
      return dir[key] * (parseFloat(a.dataset[key]) - parseFloat(b.dataset[key])) || (parseFloat(a.dataset.yatirim) - parseFloat(b.dataset.yatirim));
    });
    // Sıra değişmediyse satırlar yerinden oynatılmaz.
    if (sorted.some(function (r, i) { return list.children[i] !== r; })) sorted.forEach(function (r) { list.appendChild(r); });
    if (count) {
      if (immediate) count.textContent = shown + " seçenek gösteriliyor";
      else announceCount();
    }
    if (empty) empty.hidden = shown !== 0;
    if (ozet && form) {
      var parts = [shown + " seçenek"];
      Array.prototype.forEach.call(form.querySelectorAll('.chip[data-filter][aria-pressed="true"]'), function (c) {
        if (c.dataset.value) parts.push(lower(c.textContent));
      });
      var sorted1 = form.querySelector('.chip[data-sort][aria-pressed="true"]');
      if (sorted1) parts.push(lower(sorted1.textContent));
      ozet.textContent = parts.join(" · ");
    }
    writeUrl();
  }

  if (form) {
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

  // Karar dağılımı hücreleri, betik varken hızlı süzgeç düğmelerine dönüşür.
  var dagilim = document.getElementById("dagilim");
  if (dagilim) {
    dagilim.setAttribute("aria-label", "Karara göre süz");
    Array.prototype.forEach.call(dagilim.children, function (li) {
      var btn = document.createElement("button");
      btn.type = "button";
      btn.dataset.karar = li.dataset.karar;
      btn.setAttribute("aria-pressed", "false");
      while (li.firstChild) btn.appendChild(li.firstChild);
      li.appendChild(btn);
      distButtons.push(btn);
      btn.addEventListener("click", function () {
        state.karar = state.karar === btn.dataset.karar ? "" : btn.dataset.karar;
        syncChips();
        apply(true);
      });
    });
  }

  readUrl();
  if (q) state.q = fold(q.value.trim());
  // Süzgeç paneli kapalı başlar (liste ilk ekranda görünsün); adreste seçim varsa açılır.
  if (panel && (FILTERS.some(function (k) { return state[k]; }) || state.sort !== "yatirim")) panel.open = true;
  syncChips();
  apply(true);
})();
