/* Send by GroupChatOn: light/dark, phone menu, install as an app, offline shell. Designed & Developed by: Nivesh Sahayak. */
(function () {
  'use strict';
  var d = document.documentElement;
  document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
    b.addEventListener('click', function () {
      var t = d.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
      d.setAttribute('data-theme', t);
      try { localStorage.setItem('gco-send-theme', t); } catch (e) {}
    });
  });

  var menu = document.querySelector('.menu-btn'), nav = document.getElementById('nav');
  if (menu && nav) {
    menu.addEventListener('click', function () { var o = nav.classList.toggle('is-open'); menu.setAttribute('aria-expanded', o ? 'true' : 'false'); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') { nav.classList.remove('is-open'); menu.setAttribute('aria-expanded', 'false'); } });
  }

  // install: the browser's own prompt where there is one; iPhone/iPad get the Share-menu steps
  var prompt = null, btns = document.querySelectorAll('[data-install]');
  var standalone = matchMedia('(display-mode: standalone)').matches || navigator.standalone;
  var ios = /iPhone|iPad|iPod/.test(navigator.userAgent) || (/Macintosh/.test(navigator.userAgent) && navigator.maxTouchPoints > 1);
  function showBtns(on) { btns.forEach(function (b) { b.hidden = !on; }); }
  window.addEventListener('beforeinstallprompt', function (e) { e.preventDefault(); prompt = e; showBtns(true); });
  window.addEventListener('appinstalled', function () { prompt = null; showBtns(false); });
  if (ios && !standalone) showBtns(true);
  btns.forEach(function (b) {
    b.addEventListener('click', function () {
      if (prompt) { prompt.prompt(); prompt.userChoice.finally(function () { prompt = null; showBtns(false); }); return; }
      if (ios) alert('To install Send on your iPhone or iPad: tap the Share button (the square with an arrow), then "Add to Home Screen".');
    });
  });

  if ('serviceWorker' in navigator && location.protocol === 'https:') {
    window.addEventListener('load', function () { navigator.serviceWorker.register('/sw.js').catch(function () {}); });
  }
})();
