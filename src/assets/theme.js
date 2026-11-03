/* before the first paint: the saved or device light/dark choice (a file, not inline, so the strict page rules allow it) */
(function () {
  var t = null;
  try { t = localStorage.getItem('gco-send-theme'); } catch (e) {}
  if (t !== 'light' && t !== 'dark') t = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', t);
})();
