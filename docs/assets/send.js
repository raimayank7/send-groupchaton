/* Send by GroupChatOn: files go straight from one browser to another (WebRTC data channel, always encrypted).
   Our meeting point (a PeerJS-compatible Cloudflare Worker) only introduces the two devices; files and notes never pass
   through it. On networks that block direct links, Cloudflare's relay may carry the already-encrypted data.
   Pairing: one device shows a one-time code; the other enters it (or opens the link / scans the QR).
   After pairing both leave the meeting point, so the code can't be used again. Nothing is received until the user accepts it.
   Designed & Developed by: Nivesh Sahayak. */
(function () {
  'use strict';
  var app = document.getElementById('send-app');
  if (!app) return;

  var ALPHA = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ';   // no 0/1/I/O: easy to read out loud
  var PREFIX = 'gcosend-v1-';
  // our own meeting point (Cloudflare Worker, folder send-meet); /ice adds a relay pass when Cloudflare TURN is on
  var MEET = { host: 'send-meet.send-meet.workers.dev', port: 443, path: '/', key: 'gcosend', secure: true, debug: 0 };
  var ICE = { iceServers: [{ urls: 'stun:stun.cloudflare.com:3478' }, { urls: 'stun:stun.l.google.com:19302' }] }, iceAt = 0;
  function opts() { var o = {}; for (var k in MEET) o[k] = MEET[k]; o.config = ICE; return o; }
  function withIce(go) {                                  // fresh connection details at most once an hour; never wait more than 4 s
    if (Date.now() - iceAt < 36e5) return go();
    var done = false, finish = function () { if (!done) { done = true; go(); } };
    setTimeout(finish, 4000);
    fetch('https://' + MEET.host + '/ice', { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (j) {
      if (j && j.iceServers && j.iceServers.length) { ICE = { iceServers: j.iceServers }; iceAt = Date.now(); }
    }).catch(function () {}).then(finish);
  }
  var RISKY = /\.(exe|msi|bat|cmd|com|scr|pif|vbs|vbe|js|jse|wsf|wsh|ps1|psm1|reg|lnk|hta|cpl|jar|apk|xapk|dmg|pkg|app|sh|run|bin|iso|img|docm|xlsm|pptm)$/i;
  var EMOJI = ['🍎','🍌','🍇','🍉','🍒','🍋','🥕','🌽','🍄','🌵','🌻','🌲','🍀','🌙','⭐','☀️','⚡','🔥','💧','❄️','🌈','☂️','🎈','🎁',
               '🎵','🎲','🧩','🪁','⚽','🏀','🎯','🚲','🚗','🚀','⛵','✈️','🏠','⏰','📚','✏️','🔑','🔔','💡','🧭','🧲','🧸','🐶','🐱',
               '🐭','🐰','🦊','🐻','🐼','🐨','🐯','🦁','🐮','🐷','🐸','🐵','🐔','🐧','🐢','🐙'];

  var $ = function (s, r) { return (r || app).querySelector(s); };
  var peer = null, conn = null, myCode = '', role = '', outQueue = [], sending = null, incoming = {}, current = null, wake = null;
  var chunkSize = 16384, retries = 0, turn = 0;

  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e; }
  function size(n) { var u = ['B', 'KB', 'MB', 'GB', 'TB'], i = 0; while (n >= 1024 && i < 4) { n /= 1024; i++; } return (i ? n.toFixed(n < 10 ? 1 : 0) : n) + ' ' + u[i]; }
  function time(s) { s = Math.round(s); return s < 60 ? s + ' s' : Math.floor(s / 60) + ' min ' + (s % 60) + ' s'; }
  function newCode() { var a = new Uint8Array(8), s = ''; crypto.getRandomValues(a); for (var i = 0; i < 8; i++) s += ALPHA[a[i] % 32]; return s; }
  function pretty(c) { return c.slice(0, 4) + '-' + c.slice(4); }
  function clean(c) { return String(c || '').toUpperCase().replace(/[^0-9A-Z]/g, ''); }
  function valid(c) { return c.length === 8 && c.split('').every(function (ch) { return ALPHA.indexOf(ch) >= 0; }); }
  function device() {
    var u = navigator.userAgent, os = /Android/.test(u) ? 'Android' : /iPhone|iPod/.test(u) ? 'iPhone' : /iPad|Macintosh/.test(u) && navigator.maxTouchPoints > 1 ? 'iPad' :
      /Windows/.test(u) ? 'Windows PC' : /Mac/.test(u) ? 'Mac' : /CrOS/.test(u) ? 'Chromebook' : /Linux/.test(u) ? 'Linux PC' : 'Device';
    var br = /Edg\//.test(u) ? 'Edge' : /OPR\//.test(u) ? 'Opera' : /SamsungBrowser/.test(u) ? 'Samsung Internet' : /Firefox|FxiOS/.test(u) ? 'Firefox' :
      /Chrome|CriOS/.test(u) ? 'Chrome' : /Safari/.test(u) ? 'Safari' : 'browser';
    return os + ' · ' + br;
  }
  function status(t, kind) { var s = $('[data-status]'); s.textContent = t; s.className = 'sd-status' + (kind ? ' is-' + kind : ''); }
  function show(view) { app.setAttribute('data-view', view); }

  /* ---------- waiting for a partner ---------- */
  function start() {
    if (!window.Peer) { status('Could not load the connection library. Check your internet and reload the page.', 'bad'); return; }
    stop();
    myCode = newCode(); role = '';
    $('[data-code]').textContent = pretty(myCode);
    var link = location.origin + '/#' + myCode;
    $('[data-link]').value = link;
    drawQR(link);
    show('pair');
    status('Getting your code ready…');
    var t = turn;
    withIce(function () { if (t === turn) host(); });    // a later start/join cancels this one
  }
  function host() {
    peer = new Peer(PREFIX + myCode.toLowerCase(), opts());
    peer.on('open', function () { retries = 0; status('Waiting for the other device. Your code works once.', 'wait'); });
    peer.on('connection', function (c) {
      if (conn) { c.on('open', function () { c.close(); }); return; }       // one partner per code
      role = 'host'; attach(c);
    });
    peer.on('error', onPeerError);
  }

  function join(code) {
    code = clean(code);
    if (!valid(code)) { status('That code doesn\'t look right: it has 8 letters and numbers, like K7Q2-M9XP.', 'bad'); return; }
    if (code === myCode) { status('That\'s this device\'s own code. Enter the code shown on the OTHER device.', 'bad'); return; }
    if (!window.Peer) { status('Could not load the connection library. Check your internet and reload the page.', 'bad'); return; }
    stop(); role = 'guest';
    status('Connecting to ' + pretty(code) + '…');
    var t = turn;
    withIce(function () { if (t === turn) guest(code); });
  }
  function guest(code) {
    peer = new Peer(undefined, opts());
    peer.on('open', function () { attach(peer.connect(PREFIX + code.toLowerCase(), { reliable: true, serialization: 'raw' })); });
    peer.on('error', onPeerError);
  }

  function onPeerError(e) {
    var t = e && e.type;
    if (conn && conn.open) return;                       // the server going away after pairing doesn't matter
    if (t === 'peer-unavailable') status('No device is waiting with that code. Check it, or ask for a fresh code (a code works only once).', 'bad');
    else if (t === 'unavailable-id') { start(); return; }  // that code is taken: make another
    else if (t === 'network' || t === 'server-error' || t === 'socket-error' || t === 'socket-closed') {
      if (role !== 'guest' && retries < 3) { retries++; status('Reconnecting to the pairing service…'); setTimeout(start, 2000 * retries); return; }   // a blip, e.g. Wi-Fi changing
      status('Can\'t reach the pairing service. Check your internet connection, then tap New code.', 'bad');
    }
    else if (t === 'browser-incompatible') status('This browser can\'t make direct connections. Try an up-to-date Chrome, Edge, Firefox or Safari.', 'bad');
    else status('Something went wrong (' + (t || 'unknown') + '). Try again.', 'bad');
    if (role === 'guest') { role = ''; setTimeout(start, 0); }
  }

  /* ---------- connected ---------- */
  function attach(c) {
    conn = c;
    var opened = false;
    var timer = setTimeout(function () {
      if (!opened) { status('The two devices couldn\'t reach each other directly. Some office and mobile networks block this: try Wi-Fi on one device or mobile data on the other.', 'bad'); hangup(true); }
    }, 25000);
    c.on('open', function () {
      opened = true; clearTimeout(timer);
      try { peer.disconnect(); } catch (e) {}           // leave the pairing server: the code is now dead
      var dc = c.dataChannel; dc.binaryType = 'arraybuffer'; dc.bufferedAmountLowThreshold = 1 << 20;
      var pc = c.peerConnection, max = pc && pc.sctp && pc.sctp.maxMessageSize;
      chunkSize = max ? Math.max(16384, Math.min(65536, max)) : 16384;
      send({ t: 'hello', name: device(), v: 1 });
      show('live'); $('[data-peer-name]').textContent = 'the other device';
      status('Connected. Drop files or write a note.', 'ok');
      safety(pc); route(pc);
      history.replaceState(null, '', location.pathname);
    });
    c.on('data', function (d) {
      if (typeof d === 'string') { try { onMsg(JSON.parse(d)); } catch (e) {} }
      else if (d instanceof ArrayBuffer) onChunk(d);
      else if (d && d.arrayBuffer) d.arrayBuffer().then(onChunk);
    });
    c.on('close', function () { if (app.getAttribute('data-view') === 'live') ended('The other device left.'); });
    c.on('error', function () { if (app.getAttribute('data-view') === 'live') ended('The connection dropped.'); });
  }
  function send(o) { if (conn && conn.open) conn.send(JSON.stringify(o)); }

  function hangup(silent) {
    try { conn && conn.close(); } catch (e) {}
    conn = null;
    if (!silent) ended('You disconnected.');
  }
  function stop() { turn++; try { conn && conn.close(); } catch (e) {} try { peer && peer.destroy(); } catch (e) {} conn = null; peer = null; }
  function ended(why) {
    Object.keys(incoming).forEach(function (id) { var f = incoming[id]; if (f.state !== 'done') mark(f, 'Stopped'); if (f.writer) f.writer.abort().catch(function () {}); });
    if (sending) mark(sending, 'Stopped');
    outQueue.forEach(function (f) { mark(f, 'Not sent'); });
    outQueue = []; sending = null; current = null; release();
    stop(); show('ended'); $('[data-ended]').textContent = why;
  }

  /* the safety code: both screens show the same 4 pictures only if nobody sits between the two devices */
  function safety(pc) {
    function fp(sdp) { var m = /a=fingerprint:\S+ ([0-9A-F:]+)/i.exec(sdp || ''); return m ? m[1].toUpperCase() : ''; }
    var a = fp(pc.currentLocalDescription && pc.currentLocalDescription.sdp), b = fp(pc.currentRemoteDescription && pc.currentRemoteDescription.sdp);
    var box = $('[data-safety]');
    if (!a || !b || !crypto.subtle) { box.textContent = '—'; return; }
    crypto.subtle.digest('SHA-256', new TextEncoder().encode([a, b].sort().join('|'))).then(function (h) {
      var v = new Uint8Array(h), out = [];
      for (var i = 0; i < 4; i++) out.push(EMOJI[v[i] % 64]);
      box.textContent = out.join(' ');
      box.setAttribute('aria-label', 'Safety code ' + out.join(' '));
    });
  }
  /* direct or through a relay (only shown, never changes anything) */
  function route(pc) {
    if (!pc.getStats) return;
    setTimeout(function () {
      pc.getStats().then(function (st) {
        var pair, local = {};
        st.forEach(function (r) {
          if (r.type === 'transport' && r.selectedCandidatePairId) pair = st.get(r.selectedCandidatePairId);
          if (r.type === 'local-candidate') local[r.id] = r;
        });
        if (!pair) st.forEach(function (r) { if (r.type === 'candidate-pair' && r.state === 'succeeded' && (r.nominated || r.selected)) pair = r; });
        var lc = pair && local[pair.localCandidateId];
        var same = lc && (lc.candidateType === 'host');
        $('[data-route]').textContent = !lc ? 'Encrypted' : lc.candidateType === 'relay' ? 'Encrypted · relayed' : same ? 'Encrypted · same network' : 'Encrypted · direct';
      }).catch(function () {});
    }, 1200);
  }

  /* ---------- the list of transfers ---------- */
  function row(f, dir) {
    var li = el('li', 'sd-item is-' + dir);
    var top = el('div', 'sd-item-top');
    var name = el('span', 'sd-name', f.name);
    var meta = el('span', 'sd-meta', size(f.size) + (dir === 'in' ? ' · from the other device' : ' · to the other device'));
    top.appendChild(name); top.appendChild(meta);
    li.appendChild(top);
    if (dir === 'in' && RISKY.test(f.name)) li.appendChild(el('p', 'sd-warn', 'Careful: this kind of file can run programs on your device. Accept it only if you know the sender and expected it.'));
    var bar = el('div', 'sd-bar'); bar.appendChild(el('i')); li.appendChild(bar);
    var foot = el('div', 'sd-item-foot');
    f.stateEl = el('span', 'sd-state', dir === 'in' ? 'Waiting for you' : 'Waiting for the other device to accept');
    f.actions = el('span', 'sd-acts');
    foot.appendChild(f.stateEl); foot.appendChild(f.actions); li.appendChild(foot);
    f.li = li; f.bar = bar.firstChild;
    $('[data-list]').prepend(li);
    $('[data-empty]').hidden = true;
    return li;
  }
  function button(f, label, cls, fn) { var b = el('button', 'sd-btn ' + (cls || ''), label); b.type = 'button'; b.addEventListener('click', fn); f.actions.appendChild(b); return b; }
  function mark(f, t, cls) { f.state = cls || f.state; if (f.stateEl) f.stateEl.textContent = t; }
  function clearActs(f) { f.actions.textContent = ''; }

  /* sending */
  function addFiles(list) {
    if (!conn || !conn.open) return;
    Array.prototype.forEach.call(list, function (file) {
      var f = { id: Math.random().toString(36).slice(2) + Date.now().toString(36), name: file.name || 'file', size: file.size, type: file.type || '', file: file, state: 'offered' };
      row(f, 'out');
      button(f, 'Cancel', 'is-quiet', function () { cancelOut(f); });
      outQueue.push(f);
      send({ t: 'offer', id: f.id, name: f.name, size: f.size, type: f.type });
    });
  }
  function cancelOut(f) {
    send({ t: 'cancel', id: f.id });
    f.cancelled = true; mark(f, 'Cancelled', 'cancelled'); clearActs(f);
    outQueue = outQueue.filter(function (x) { return x !== f; });
  }
  function pump() {
    if (sending || !conn || !conn.open) return;
    var f = outQueue.find(function (x) { return x.state === 'accepted'; });
    if (!f) return;
    outQueue = outQueue.filter(function (x) { return x !== f; });
    sending = f; hold();
    send({ t: 'start', id: f.id });
    var dc = conn.dataChannel, off = 0, t0 = performance.now();
    mark(f, 'Sending…', 'sending');
    (function next() {
      if (f.cancelled || !conn || !conn.open) { sending = null; release(); pump(); return; }
      if (dc.bufferedAmount > 8 * chunkSize * 32) { dc.onbufferedamountlow = function () { dc.onbufferedamountlow = null; next(); }; return; }
      if (off >= f.size) {
        send({ t: 'done', id: f.id });
        mark(f, 'Sent ✓', 'done'); clearActs(f); f.bar.style.width = '100%';
        sending = null; release(); pump(); return;
      }
      f.file.slice(off, off + chunkSize).arrayBuffer().then(function (buf) {
        try { conn.send(buf); } catch (e) { ended('The connection dropped while sending.'); return; }
        off += buf.byteLength;
        progress(f, off, t0);
        next();
      });
    })();
  }
  function progress(f, done, t0) {
    var pct = f.size ? done / f.size * 100 : 100, sec = (performance.now() - t0) / 1000, rate = done / Math.max(sec, 0.001);
    f.bar.style.width = pct.toFixed(1) + '%';
    if (!f.tick || performance.now() - f.tick > 300) {
      f.tick = performance.now();
      mark(f, Math.floor(pct) + '% · ' + size(rate) + '/s' + (rate > 0 && done < f.size ? ' · ' + time((f.size - done) / rate) + ' left' : ''));
    }
  }

  /* receiving */
  function onMsg(m) {
    if (m.t === 'hello') { $('[data-peer-name]').textContent = String(m.name || 'the other device').slice(0, 60); return; }
    if (m.t === 'note') { note(String(m.text || '').slice(0, 20000), 'in'); return; }
    if (m.t === 'offer') {
      var f = { id: String(m.id), name: String(m.name || 'file').replace(/[\\/:*?"<>|\u0000-\u001f]/g, '_').slice(0, 200), size: +m.size || 0, type: String(m.type || ''), state: 'offered', got: 0, parts: [] };
      incoming[f.id] = f; row(f, 'in');
      button(f, 'Accept', 'is-main', function () { accept(f); });
      button(f, 'Decline', 'is-quiet', function () { send({ t: 'decline', id: f.id }); mark(f, 'Declined', 'declined'); clearActs(f); });
      try { if (navigator.vibrate && (!navigator.userActivation || navigator.userActivation.hasBeenActive)) navigator.vibrate(80); } catch (e) {}
      return;
    }
    var o = outQueue.concat(sending ? [sending] : []).find(function (x) { return x.id === m.id; });
    if (m.t === 'accept' && o && o.state === 'offered') { o.state = 'accepted'; mark(o, 'Accepted, starting…'); pump(); }
    else if (m.t === 'decline' && o) { mark(o, 'The other device declined it', 'declined'); clearActs(o); outQueue = outQueue.filter(function (x) { return x !== o; }); }
    else if (m.t === 'cancel' && incoming[m.id]) { var g = incoming[m.id]; mark(g, 'The sender cancelled it', 'cancelled'); clearActs(g); g.parts = []; if (g.writer) g.writer.abort().catch(function () {}); if (current === g) current = null; }
    else if (m.t === 'start' && incoming[m.id]) { current = incoming[m.id]; current.t0 = performance.now(); mark(current, 'Receiving…', 'receiving'); hold(); }
    else if (m.t === 'done' && incoming[m.id]) finish(incoming[m.id]);
  }
  function accept(f) {
    clearActs(f); mark(f, 'Accepted, waiting for it to start…', 'accepted');
    var big = f.size > 200 * 1048576;
    if (big && window.showSaveFilePicker) {     // big files go straight to disk (Chrome/Edge on computers)
      window.showSaveFilePicker({ suggestedName: f.name }).then(function (h) { return h.createWritable(); })
        .then(function (w) { f.writer = w; send({ t: 'accept', id: f.id }); })
        .catch(function () { mark(f, 'Choose where to save it to accept', 'offered'); button(f, 'Accept', 'is-main', function () { accept(f); }); });
      return;
    }
    if (big && f.size > 1.5 * 1073741824) mark(f, 'Large file: this browser keeps it in memory until it is saved. Close other tabs if it stops.', 'accepted');
    send({ t: 'accept', id: f.id });
  }
  function onChunk(buf) {
    var f = current;
    if (!f || f.state === 'cancelled') return;
    if (f.writer) f.writer.write(buf); else f.parts.push(buf);
    f.got += buf.byteLength;
    progress(f, f.got, f.t0);
  }
  function finish(f) {
    current = null; release();
    f.bar.style.width = '100%';
    if (f.writer) { f.writer.close().then(function () { mark(f, 'Saved ✓', 'done'); }); return; }
    var blob = new Blob(f.parts, { type: f.type || 'application/octet-stream' }); f.parts = [];
    var url = URL.createObjectURL(blob);
    mark(f, 'Received ✓ · not saved yet', 'done'); clearActs(f);
    var a = el('a', 'sd-btn is-main', 'Save'); a.href = url; a.download = f.name; a.rel = 'noopener';
    a.addEventListener('click', function () { setTimeout(function () { mark(f, 'Saved to your downloads ✓', 'done'); }, 400); });
    f.actions.appendChild(a);
    if (/^image\//.test(blob.type) && blob.size < 30 * 1048576 && !/svg/.test(blob.type)) {
      var img = el('img', 'sd-thumb'); img.src = url; img.alt = ''; f.li.insertBefore(img, f.li.children[1]);
    }
  }

  /* notes */
  function note(text, dir) {
    if (!text) return;
    var li = el('li', 'sd-item sd-note is-' + dir);
    li.appendChild(el('span', 'sd-meta', dir === 'in' ? 'Note from the other device' : 'Your note'));
    li.appendChild(el('p', 'sd-note-text', text));
    var b = el('button', 'sd-btn is-quiet', 'Copy'); b.type = 'button';
    b.addEventListener('click', function () { copy(text, b); });
    li.appendChild(b);
    $('[data-list]').prepend(li); $('[data-empty]').hidden = true;
  }
  function copy(text, b) {
    var done = function () { var t = b.textContent; b.textContent = 'Copied ✓'; setTimeout(function () { b.textContent = t; }, 1500); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, fallback); else fallback();
    function fallback() { var t = el('textarea'); t.value = text; t.setAttribute('readonly', ''); t.style.position = 'fixed'; t.style.opacity = '0'; document.body.appendChild(t); t.select(); try { document.execCommand('copy'); done(); } catch (e) {} t.remove(); }
  }

  /* keep the screen on while something is moving */
  function hold() { if (!wake && navigator.wakeLock) navigator.wakeLock.request('screen').then(function (w) { wake = w; }, function () {}); }
  function release() { if (wake && !sending && !current) { wake.release().catch(function () {}); wake = null; } }

  function drawQR(text) {
    var box = $('[data-qr]');
    box.textContent = '';
    if (!window.qrcode) return;
    var q = window.qrcode(0, 'M'); q.addData(text); q.make();
    box.innerHTML = q.createSvgTag({ cellSize: 4, margin: 2, scalable: true });
    var svg = box.querySelector('svg'); if (svg) { svg.setAttribute('role', 'img'); svg.setAttribute('aria-label', 'QR code: scan it with the other device to connect'); }
  }

  /* ---------- wiring ---------- */
  $('[data-copy-link]').addEventListener('click', function () { copy($('[data-link]').value, this); });
  $('[data-share-link]').hidden = !navigator.share;
  $('[data-share-link]').addEventListener('click', function () { navigator.share({ title: 'Send files to me', text: 'Open this to send files to my device. Code: ' + pretty(myCode), url: $('[data-link]').value }).catch(function () {}); });
  $('[data-join-form]').addEventListener('submit', function (e) { e.preventDefault(); join($('[data-join-code]').value); });
  $('[data-join-code]').addEventListener('input', function () {
    var c = clean(this.value).slice(0, 8); var v = c.length > 4 ? c.slice(0, 4) + '-' + c.slice(4) : c;
    if (v !== this.value) this.value = v;
  });
  $('[data-new-code]').addEventListener('click', start);
  $('[data-again]').addEventListener('click', start);
  $('[data-hangup]').addEventListener('click', function () { if (!(sending || current) || confirm('A file is still moving. Disconnect anyway?')) hangup(); });
  var pick = $('[data-pick]');
  pick.addEventListener('change', function () { addFiles(pick.files); pick.value = ''; });
  var drop = $('[data-drop]');
  ['dragenter', 'dragover'].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.add('is-over'); }); });
  ['dragleave', 'drop'].forEach(function (t) { drop.addEventListener(t, function (e) { e.preventDefault(); drop.classList.remove('is-over'); }); });
  drop.addEventListener('drop', function (e) { if (e.dataTransfer && e.dataTransfer.files.length) addFiles(e.dataTransfer.files); });
  document.addEventListener('paste', function (e) {
    if (app.getAttribute('data-view') !== 'live' || /INPUT|TEXTAREA/.test((e.target || {}).tagName)) return;
    var fs = e.clipboardData && e.clipboardData.files; if (fs && fs.length) addFiles(fs);
  });
  $('[data-note-form]').addEventListener('submit', function (e) {
    e.preventDefault(); var t = $('[data-note]'), v = t.value.trim(); if (!v || !conn || !conn.open) return;
    send({ t: 'note', text: v.slice(0, 20000) }); note(v, 'out'); t.value = '';
  });
  window.addEventListener('beforeunload', function (e) { if (sending || current) { e.preventDefault(); e.returnValue = ''; } });
  window.addEventListener('pagehide', function () { stop(); });

  // opened from a link or QR code (send.groupchaton.com/#K7Q2M9XP): the code stays in the # part, which never reaches any server
  var fromLink = clean(location.hash.slice(1));
  start();
  if (valid(fromLink)) { $('[data-join-code]').value = pretty(fromLink); join(fromLink); }
  app.classList.add('is-ready');
})();
