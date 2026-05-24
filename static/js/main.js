// CivicFix — Main JS
console.log('CivicFix loaded ✅');

// Animate numbers on homepage
document.querySelectorAll('.stat-num').forEach(el => {
  const target = parseInt(el.textContent);
  if (isNaN(target)) return;
  let current = 0;
  const step = Math.max(1, Math.floor(target / 40));
  const timer = setInterval(() => {
    current = Math.min(current + step, target);
    el.textContent = current;
    if (current >= target) clearInterval(timer);
  }, 30);
});
