// flugelserver panel — kart animasyonlari (sistem-bakim)
(() => {
  // kartlara sira numarasi ver (sirayla belirme) — kartlar sonradan yuklendigi icin izle
  const numarala = () => document.querySelectorAll(".service").forEach((el, i) => el.style.setProperty("--i", i));
  new MutationObserver(numarala).observe(document.documentElement, { childList: true, subtree: true });
  numarala();
  // fareyi takip eden parilti
  document.addEventListener("pointermove", (e) => {
    const kart = e.target.closest && e.target.closest(".service-card");
    if (!kart) return;
    const r = kart.getBoundingClientRect();
    kart.style.setProperty("--mx", `${e.clientX - r.left}px`);
    kart.style.setProperty("--my", `${e.clientY - r.top}px`);
  }, { passive: true });
})();
