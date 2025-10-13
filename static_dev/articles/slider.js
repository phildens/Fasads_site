(function () {
  const root = document.getElementById("articlesSlider");
  if (!root) return;
  const rail = root.querySelector(".rail");
  let autoplay = root.dataset.autoplay === "true";
  const interval = parseInt(root.dataset.interval || "4000", 10);

  // автоскролл
  let timer = null;
  const start = () => {
    if (!autoplay || timer) return;
    timer = setInterval(() => {
      const w = rail.clientWidth;
      const current = rail.scrollLeft;
      const max = rail.scrollWidth - w;
      const step = Math.max(320, w * 0.6);
      const next = current + step;
      rail.scrollTo({ left: next >= max ? 0 : next, behavior: "smooth" });
    }, interval);
  };
  const stop = () => { if (timer) { clearInterval(timer); timer = null; }};

  // пауза при взаимодействии
  ["mouseenter", "touchstart", "focusin"].forEach(e => rail.addEventListener(e, stop, {passive:true}));
  ["mouseleave", "touchend", "focusout"].forEach(e => rail.addEventListener(e, start, {passive:true}));

  // позволяем «тащить» мышью на десктопе
  let isDown = false, startX = 0, scrollLeft = 0;
  rail.addEventListener("mousedown", (e) => { isDown = true; startX = e.pageX - rail.offsetLeft; scrollLeft = rail.scrollLeft; stop(); });
  window.addEventListener("mouseup", () => { isDown = false; start(); });
  rail.addEventListener("mouseleave", () => { isDown = false; start(); });
  rail.addEventListener("mousemove", (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - rail.offsetLeft;
    const walk = (x - startX) * 1.2;
    rail.scrollLeft = scrollLeft - walk;
  });

  start();
})();
