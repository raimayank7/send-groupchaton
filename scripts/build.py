"""Builds send.groupchaton.com into docs/ (GitHub Pages serves main /docs).
   python -X utf8 scripts/build.py
   Source: src/assets/*, src/sw.js, static/brand/* and the page texts below. Designed & Developed by: Nivesh Sahayak."""
import os, json, shutil, hashlib, html, datetime

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(HERE, 'docs')
SITE = 'https://send.groupchaton.com'
NAME = 'Send by GroupChatOn'
AD_CLIENT = 'ca-pub-5935207738848708'
YEAR = datetime.date.today().year
PEERJS = ('https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js', 'sha384-nlUQ8ZqCbvStErob+biJNzSgltf6urV3VGqhfIfzhmg9RXmpeRm76ELw0pYnKlTR')
QRCODE = ('https://cdnjs.cloudflare.com/ajax/libs/qrcode-generator/1.4.4/qrcode.min.js', 'sha384-mZT2gIty7ZDdOGkxfP6joZcYdMW1Jvj9dRlfpTmaJAKKXTqzygtB22k7FLe+KZC1')
FONTS = 'https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Outfit:wght@500;600;700&family=Red+Hat+Mono:wght@500;600&display=swap'
# the transfer page only runs its own files, the two libraries above and the credit; no ads there (they would run inside the page)
CSP = ("default-src 'self'; script-src 'self' https://unpkg.com https://cdnjs.cloudflare.com https://assets.niveshsahayak.in; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
       "img-src 'self' data: blob: https://assets.niveshsahayak.in; connect-src 'self' https://0.peerjs.com wss://0.peerjs.com; "
       "media-src 'self' blob:; worker-src 'self'; manifest-src 'self'; frame-src 'none'; object-src 'none'; base-uri 'none'; form-action 'self'")

esc = lambda s: html.escape(s, quote=True)
def rd(p): return open(os.path.join(HERE, p), encoding='utf-8').read()
def ver(p): return hashlib.sha1(open(os.path.join(HERE, 'src', p), 'rb').read()).hexdigest()[:8]
def wr(rel, text):
    p = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, 'w', encoding='utf-8', newline='\n').write(text)

NAV = [('How it works', '/how-it-works/'), ('Security', '/security/'), ('FAQ', '/faq/')]
CRIT = ("body{margin:0;background:#fbf8f5;color:#1c1917}html[data-theme='dark'] body{background:#0f0d0c;color:#f5f0eb}"
        ".hdr{height:62px}.sd{min-height:340px}")

def page(path, title, desc, main, ld=None, crumbs=None, ads=False, tool=False, noindex=False):
    canon = SITE + path
    nav = ''.join("<a href='%s'%s>%s</a>" % (u, " aria-current='page'" if u == path else '', n) for n, u in NAV)
    graph = [{'@type': 'WebSite', '@id': SITE + '/#site', 'name': NAME, 'url': SITE + '/', 'inLanguage': 'en',
              'publisher': {'@type': 'Organization', 'name': 'GroupChatOn', 'url': 'https://www.groupchaton.com/',
                            'logo': SITE + '/brand/favicon-512.png'}},
             {'@type': 'WebPage', 'url': canon, 'name': title, 'description': desc, 'isPartOf': {'@id': SITE + '/#site'}}]
    if crumbs:
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate([('Home', '/')] + crumbs)]})
    graph += ld or []
    ldj = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('</', '<\\/')
    bc = ''
    if crumbs:
        bc = "<nav class='crumbs' aria-label='Breadcrumb'><a href='/'>Home</a> <span aria-hidden='true'>›</span> <span aria-current='page'>%s</span></nav>" % esc(crumbs[-1][0])
    head_extra = ''
    if tool:
        head_extra = "<meta http-equiv='Content-Security-Policy' content=\"%s\">\n<meta name='referrer' content='no-referrer'>\n" % CSP
    adsense = ("<script async src='https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=%s' crossorigin='anonymous'></script>" % AD_CLIENT) if ads else ''
    scripts = ''
    if tool:
        scripts = ("<script src='%s' integrity='%s' crossorigin='anonymous'></script>\n<script src='%s' integrity='%s' crossorigin='anonymous'></script>\n"
                   "<script src='/assets/send.js?v=%s'></script>\n") % (PEERJS[0], PEERJS[1], QRCODE[0], QRCODE[1], ver('assets/send.js'))
    return f"""<!doctype html>
<html lang='en' data-theme='light'>
<head>
<meta charset='utf-8'>
<meta name='viewport' content='width=device-width, initial-scale=1, viewport-fit=cover'>
{head_extra}<title>{esc(title)}</title>
<meta name='description' content='{esc(desc)}'>
<link rel='canonical' href='{canon}'>
<meta name='robots' content='{"noindex, follow" if noindex else "index, follow, max-image-preview:large"}'>
<meta property='og:type' content='website'><meta property='og:site_name' content='{NAME}'>
<meta property='og:title' content='{esc(title)}'><meta property='og:description' content='{esc(desc)}'><meta property='og:url' content='{canon}'>
<meta property='og:image' content='{SITE}/brand/favicon-512.png'><meta name='twitter:card' content='summary'>
<meta name='twitter:title' content='{esc(title)}'><meta name='twitter:description' content='{esc(desc)}'>
<meta name='theme-color' content='#EA580C'>
<link rel='icon' href='/brand/favicon.ico' sizes='any'><link rel='icon' type='image/png' sizes='32x32' href='/brand/favicon-32.png'>
<link rel='apple-touch-icon' href='/brand/apple-touch-icon.png'><link rel='manifest' href='/manifest.webmanifest'>
<style>{CRIT}</style>
<script src='/assets/theme.js?v={ver('assets/theme.js')}'></script>
<link rel='preconnect' href='https://fonts.googleapis.com'><link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>
<link rel='stylesheet' href='{FONTS}'>
<link rel='stylesheet' href='/assets/send.css?v={ver('assets/send.css')}'>
<script type='application/ld+json'>{ldj}</script>
{adsense}
</head>
<body data-ads='{1 if ads else 0}'>
<a class='skip' href='#main'>Skip to content</a>
<header class='hdr'>
  <div class='wrap hdr-in'>
    <a class='brand' href='/' aria-label='{NAME}: home'><img class='logo-l' src='/brand/logo-light.png' width='218' height='50' alt='GroupChatOn'><img class='logo-d' src='/brand/logo-dark.png' width='218' height='50' alt='GroupChatOn'><span class='brand-t'>Send</span></a>
    <nav class='nav' id='nav' aria-label='Site'>{nav}</nav>
    <div class='hdr-act'>
      <button class='ibtn' type='button' data-theme-toggle aria-label='Switch light or dark mode' title='Light / dark'><svg viewBox='0 0 24 24' aria-hidden='true'><path d='M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z'/></svg></button>
      <button class='ibtn' type='button' data-install hidden aria-label='Install Send as an app' title='Install app'><svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 3v12M7 10l5 5 5-5M5 21h14'/></svg></button>
      <button class='ibtn menu-btn' type='button' aria-controls='nav' aria-expanded='false' aria-label='Menu'><svg viewBox='0 0 24 24' aria-hidden='true'><path d='M4 7h16M4 12h16M4 17h16'/></svg></button>
    </div>
  </div>
</header>
<main id='main' class='wrap'>
{bc}
{main}
</main>
<footer class='ftr'>
  <div class='wrap ftr-in'>
    <div class='ftr-brand'><img src='/brand/mark.svg' width='40' height='40' alt=''><div><b>{NAME}</b><br><span>Send files and notes straight from one device to another. Encrypted, no upload, no sign-up.</span></div></div>
    <nav class='ftr-nav' aria-label='About Send'><b>Send</b><a href='/how-it-works/'>How it works</a><a href='/security/'>Security</a><a href='/faq/'>FAQ</a><a href='/about/'>About</a><a href='/contact/'>Contact</a><a href='/privacy-policy/'>Privacy policy</a><a href='/terms-of-use/'>Terms of use</a><a href='/disclaimer/'>Disclaimer</a></nav>
    <nav class='ftr-nav' aria-label='GroupChatOn'><b>GroupChatOn</b><a href='https://www.groupchaton.com/'>Novels ↗</a><a href='https://infinity.groupchaton.com/'>Infinity free tools ↗</a><a href='https://toolkit.groupchaton.com/'>Toolkit ↗</a><a href='https://share.groupchaton.com/'>Share ↗</a><a href='https://help.groupchaton.com/'>Help ↗</a></nav>
  </div>
  <div class='wrap ftr-base'>
    <p>© {YEAR} GroupChatOn. All rights reserved.</p>
    <p><span data-ns-credit>Designed &amp; Developed by: <a href='https://www.niveshsahayak.in/'>Nivesh Sahayak</a></span></p>
  </div>
</footer>
<script defer src='/assets/site.js?v={ver('assets/site.js')}'></script>
{scripts}<script async src='https://assets.niveshsahayak.in/assets/credit.js'></script>
</body>
</html>
"""

def faq_html(items):
    return "<div class='faq'>" + ''.join("<details><summary>%s</summary><p>%s</p></details>" % (q, a) for q, a in items) + "</div>"
def faq_ld(items):
    import re
    strip = lambda s: re.sub(r'<[^>]+>', '', s)
    return {'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': strip(q), 'acceptedAnswer': {'@type': 'Answer', 'text': strip(a)}} for q, a in items]}

# ------------------------------------------------------------------ home: the app
APP = """
<section class='hero'>
  <h1>Send files to any device, directly</h1>
  <p class='lead'>Pair two devices with a one-time code and send photos, videos, documents and notes straight across: phone to computer, office to home, India to America. Nothing is uploaded and nothing is stored.</p>
  <ul class='pills'><li>🔒 End-to-end encrypted</li><li>☁️ No upload, no storage</li><li>📏 No size limit</li><li>👤 No sign-up</li></ul>
  <div class='sd' id='send-app' data-view='pair' aria-live='polite'>
    <p class='sd-status' data-status role='status'>Loading…</p>

    <div class='sd-view v-pair'>
      <div class='sd-grid'>
        <div class='sd-box'>
          <h2>This device's code</h2>
          <p class='hint'>Enter it on the other device, open the link there, or scan the QR code.</p>
          <div class='sd-code' data-code>····-····</div>
          <div class='sd-qr-row'>
            <div class='sd-qr' data-qr></div>
            <div class='sd-links'>
              <label class='sd-small' for='sd-link' style='margin:0'>Link for the other device</label>
              <input id='sd-link' data-link readonly>
              <button class='sd-btn' type='button' data-copy-link>Copy link</button>
              <button class='sd-btn' type='button' data-share-link hidden>Share link</button>
              <button class='sd-btn is-quiet' type='button' data-new-code>New code</button>
            </div>
          </div>
        </div>
        <form class='sd-box sd-join' data-join-form autocomplete='off'>
          <h2>Have a code?</h2>
          <p class='hint'>Type the code shown on the other device.</p>
          <label class='sr' for='sd-join' hidden>Code from the other device</label>
          <input id='sd-join' data-join-code inputmode='text' autocapitalize='characters' spellcheck='false' maxlength='9' placeholder='K7Q2-M9XP' aria-label='Code from the other device'>
          <button class='sd-btn is-main' type='submit'>Connect</button>
          <p class='sd-small'>Each code works for one connection only. Once two devices pair, nobody else can join.</p>
        </form>
      </div>
    </div>

    <div class='sd-view v-live'>
      <div class='sd-head'>
        <div class='sd-peer'>Connected to <span data-peer-name>the other device</span><small data-route>Encrypted</small></div>
        <div class='sd-safety' title='Both screens should show the same pictures'><b data-safety>…</b><span>Safety code: check the other screen shows the same</span></div>
        <button class='sd-btn is-quiet' type='button' data-hangup>Disconnect</button>
      </div>
      <label class='sd-drop' data-drop>
        <svg viewBox='0 0 24 24' aria-hidden='true'><path d='M12 16V4M7 9l5-5 5 5M4 16v3a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-3'/></svg>
        <b>Drop files here or tap to choose</b>
        <span>Any type, any size. The other device decides whether to accept each one.</span>
        <input type='file' multiple data-pick>
      </label>
      <form class='sd-note-form' data-note-form>
        <textarea data-note rows='1' maxlength='20000' placeholder='Or send a note, a link or a password…' aria-label='Note to send'></textarea>
        <button class='sd-btn is-main' type='submit'>Send note</button>
      </form>
      <p class='sd-empty' data-empty>Files and notes you send or receive appear here.</p>
      <ul class='sd-list' data-list aria-label='Transfers'></ul>
    </div>

    <div class='sd-view v-ended'>
      <p data-ended>Disconnected.</p>
      <button class='sd-btn is-main' type='button' data-again>Get a new code</button>
    </div>
  </div>
</section>
"""

HOME_FAQ = [
    ('Is Send really free?', 'Yes. There is no sign-up, no plan and no limit on the number of files. Send costs almost nothing to run because your files never touch our servers.'),
    ('Is there a file size limit?', 'No limit is set by Send. Very large files (several GB) work best in Chrome or Edge on a computer, which save them straight to disk. Phones keep a received file in memory until you tap Save, so a phone may struggle with files bigger than 1 to 2 GB.'),
    ('Do both devices need to be online at the same time?', 'Yes. Send moves the file live from one device to the other, so both keep the page open until the transfer ends. Nothing is kept for later.'),
    ('Can someone else join with my code?', 'A code works for one connection only and is random (about a trillion possibilities). The moment two devices pair, both leave the pairing service, so the code stops working. Even then, nothing reaches you until you tap Accept.'),
    ('What is the safety code?', 'Four small pictures made from the encryption keys of this connection. If both screens show the same four, the two devices are talking straight to each other with nobody in the middle.'),
    ('Does it work between a phone and a computer, or across countries?', 'Yes. Any two devices with an up-to-date browser and internet work: Android, iPhone, Windows, Mac, Linux, Chromebook. Distance doesn\'t matter.'),
]

HOME = APP + """
<div class='content'>
  <h2>How to send a file in three steps</h2>
  <ol class='steps'>
    <li><b>Open Send on both devices.</b> Each one shows its own code.</li>
    <li><b>Pair them.</b> On one device, type the other's code, open its link or scan its QR code.</li>
    <li><b>Drop your files.</b> The other device taps Accept, and the file arrives directly.</li>
  </ol>
  <h2>Why people use Send</h2>
  <div class='cards'>
    <div><h3>No cloud in between</h3><p>Email, Drive and chat apps upload your file first and keep a copy. Send moves it straight across, so there is no copy anywhere else.</p></div>
    <div><h3>Full quality</h3><p>Photos and videos arrive exactly as they left: no compression, no resizing, the same bytes.</p></div>
    <div><h3>Any device, no app</h3><p>It runs in the browser you already have. Install it as an app if you like: it opens like one and keeps working offline for pairing on your Wi-Fi.</p></div>
    <div><h3>Private by design</h3><p>No account, no tracking of what you send, no ads on the transfer screen. <a href='/security/'>See how Send keeps files safe</a>.</p></div>
  </div>
  <h2>Questions</h2>
  """ + faq_html(HOME_FAQ) + """
  <p><a href='/faq/'>More questions and answers →</a></p>
</div>
"""

# ------------------------------------------------------------------ info pages
HOW = """
<div class='content'>
<h1>How Send works</h1>
<p>Send moves a file from one browser to another using <b>WebRTC</b>, the same technology video-call websites use to send your camera picture directly to the person you are talking to. Instead of video, Send sends the pieces of your file.</p>
<h2>1. Two devices meet</h2>
<p>When you open Send, your browser makes a random 8-character code and tells a small public pairing service (PeerJS) "a device with this code is waiting". When the other device enters the code, the pairing service passes a short introduction between them: which network addresses each one can be reached at, and the encryption key fingerprints. That is all it ever sees. It never sees file names, notes or files.</p>
<h2>2. A direct, encrypted line opens</h2>
<p>With that introduction, the two browsers connect to each other directly, through home routers and mobile networks, using a technique called ICE. Every WebRTC connection is encrypted with DTLS, the same family of encryption as the padlock in your address bar. Browsers do not allow an unencrypted WebRTC connection, so this can't be switched off, by us or anyone else.</p>
<p>As soon as the line is open, both devices disconnect from the pairing service. From then on the code is useless: nobody can use it to join.</p>
<h2>3. You choose what to accept</h2>
<p>When one side drops a file, the other side first receives only its name, type and size, and taps <b>Accept</b> or <b>Decline</b>. Only after Accept does the file start to move, in small pieces, with a progress bar, speed and time left on both screens. Files that can run programs (like .exe, .apk or .bat) carry a warning.</p>
<h2>4. The file is saved on the receiving device</h2>
<p>On phones and most browsers, the received file is kept in the page until you tap <b>Save</b>; then it goes to your Downloads like any other download. In Chrome and Edge on a computer, files larger than 200 MB are written straight to the place you choose, so even very large files don't fill memory.</p>
<h2>What if the devices can't connect?</h2>
<p>Most home Wi-Fi and mobile networks allow direct connections. A few strict office, school or public networks block them. If that happens, Send says so after a short wait: switch one device to mobile data or another Wi-Fi and get a new code.</p>
<h2>What Send does not do</h2>
<ul><li>It does not store files, for later or at all. Close the page and nothing is left.</li><li>It does not need an account, email or phone number.</li><li>It does not compress or change your files.</li></ul>
<p class='note'>Want the safety details? Read <a href='/security/'>how Send keeps your files private</a>.</p>
</div>
"""

SEC = """
<div class='content'>
<h1>Security: how Send keeps your files private</h1>
<p>Send was built so that the people running it can't see what you send, even if they wanted to. Here is exactly what protects you, and the limits you should know.</p>
<h2>What protects you</h2>
<table>
<tr><th>Protection</th><th>What it means for you</th></tr>
<tr><td>End-to-end encryption (WebRTC DTLS)</td><td>Files and notes are encrypted on your device and decrypted only on the other device. Browsers make this compulsory.</td></tr>
<tr><td>No upload, no storage</td><td>There is no server that holds your file. Nothing can leak from a server that never had it.</td></tr>
<tr><td>One-time codes</td><td>Codes are 8 random characters from a 32-character alphabet (over a trillion combinations), made by your browser's secure random generator. After pairing, both devices leave the pairing service and the code dies.</td></tr>
<tr><td>Accept before anything arrives</td><td>The receiver sees the name, type and size of each file and must tap Accept. Nothing downloads or opens by itself.</td></tr>
<tr><td>Safety code</td><td>Both screens show four pictures computed from the encryption keys of this connection. Same pictures on both = nobody in the middle.</td></tr>
<tr><td>Risky-file warning</td><td>Programs and scripts (.exe, .msi, .apk, .bat, .ps1, .js, macro documents and more) get a clear warning before you accept.</td></tr>
<tr><td>Locked-down page</td><td>The transfer page may only run its own code plus two pinned libraries (PeerJS and a QR-code drawer, each checked against a fixed fingerprint so a changed copy is refused). It shows no ads and loads no trackers.</td></tr>
<tr><td>Code kept out of addresses sent to servers</td><td>Pairing links put the code after a # sign. Browsers never send that part to any website.</td></tr>
</table>
<h2>Honest limits</h2>
<ul>
<li><b>The other device sees your internet address.</b> Every direct connection works this way (video calls too). It shows roughly which city or network you are on, not who you are.</li>
<li><b>Only accept files from people you know.</b> Encryption protects a file on its way; it can't make a harmful file safe. Never run a program someone unexpected sent you.</li>
<li><b>The pairing service is a public one (PeerJS).</b> It sees that two devices connected, and their network addresses, for the moment it introduces them. It never sees files or notes, and the safety code lets you confirm it didn't place itself in the middle.</li>
<li><b>A device that is already infected</b> (malware, a screen-recording app) can see whatever you see. Send can't protect a compromised device.</li>
</ul>
<h2>Good habits</h2>
<ol><li>Read the code out loud or scan the QR code rather than posting it publicly.</li><li>For something sensitive, compare the safety code on both screens before sending.</li><li>Tap Disconnect when you are done.</li></ol>
<p>Found a security problem? Please tell us through the <a href='/contact/'>contact page</a>.</p>
</div>
"""

FAQ = HOME_FAQ + [
    ('Does Send keep a copy of my files?', 'No. Files go from one device to the other and are never uploaded. There is nowhere for a copy to be.'),
    ('Why didn\'t the devices connect?', 'Some office, school and public networks block direct connections. Send tells you after about 25 seconds. Switch one of the devices to mobile data or to a different Wi-Fi, tap New code, and try again.'),
    ('I accepted a file but it says "not saved yet". Where is it?', 'It is ready inside the page. Tap <b>Save</b> next to it and your browser saves it to Downloads (on iPhone, choose where to save in the box that opens).'),
    ('Can I send to several people at once?', 'Not yet. One code pairs exactly two devices. To send to another person, finish, then pair again with a new code.'),
    ('Can I send folders?', 'Choose all the files inside the folder (or zip the folder first). Several files can be sent in one go; they move one after another.'),
    ('Does it use my mobile data?', 'Yes, if you are on mobile data: the file travels over the internet like any download. On the same Wi-Fi, many routers send it locally, which is faster.'),
    ('Which browsers work?', 'Current versions of Chrome, Edge, Firefox, Safari, Samsung Internet and Opera, on phones and computers.'),
    ('Can I install it?', 'Yes. Use the install button in the header (or Share → Add to Home Screen on iPhone). It opens in its own window like an app.'),
    ('Is there a limit on notes?', 'A note can be up to 20,000 characters, enough for long messages, links or a list of passwords you don\'t want to put in a chat app.'),
    ('Who makes Send?', 'Send is part of GroupChatOn, alongside the Infinity free tools, the Toolkit and the novel reader. <a href=\'/about/\'>About Send</a>.'),
]
FAQ_PAGE = "<div class='content'><h1>Send: questions and answers</h1><p>Everything people ask about sending files directly between devices with Send.</p>" + faq_html(FAQ) + "</div>"

ABOUT = """
<div class='content'>
<h1>About Send</h1>
<p>Send by GroupChatOn is a free tool for moving files and notes directly between two devices, from a phone to a laptop in the same room or from an office PC in India to a family computer in America.</p>
<p>We built it because the usual ways to move a file are clumsy or nosy: emailing yourself hits size limits, chat apps compress photos, and cloud drives keep copies of everything. Send skips all of that: two devices, one code, a direct encrypted line.</p>
<h2>Our promises</h2>
<ul><li>Free to use, with no account.</li><li>Your files are never uploaded or stored.</li><li>No ads or trackers on the transfer screen.</li><li>Plain explanations of how it works and what its limits are.</li></ul>
<h2>Part of GroupChatOn</h2>
<p>Send sits next to <a href='https://infinity.groupchaton.com/'>Infinity</a> (600+ free browser tools), the <a href='https://toolkit.groupchaton.com/'>Toolkit</a> (office templates), <a href='https://share.groupchaton.com/'>Share</a> (group listings) and <a href='https://www.groupchaton.com/'>GroupChatOn novels</a>.</p>
</div>
"""

CONTACT = """
<div class='content'>
<h1>Contact Send</h1>
<p>Questions, ideas, a problem with a transfer, or a security concern: we read every message.</p>
<p><a class='sd-btn is-main' href='https://www.groupchaton.com/p/contact-us.html'>Open the GroupChatOn contact form</a></p>
<p>Please mention <b>Send</b> in your message. For a transfer problem, tell us the two devices and browsers (for example "Android Chrome to Windows Edge") and what the screen said. Never send us the files themselves or your codes; we don't need them.</p>
<p>Many answers are already in the <a href='/faq/'>FAQ</a>.</p>
</div>
"""

PRIVACY = """
<div class='content'>
<h1>Privacy policy</h1>
<p>Last updated: {date}. This policy covers send.groupchaton.com ("Send"), run by GroupChatOn.</p>
<h2>Files and notes</h2>
<p>Files and notes you send travel directly between the two devices over an encrypted WebRTC connection. They are never uploaded to, stored on or readable by our servers or the pairing service. We cannot see, recover or delete them, because we never have them.</p>
<h2>The pairing service</h2>
<p>To introduce two devices, Send uses the public PeerJS service (0.peerjs.com). During pairing it handles a random device identifier made from your code, and the network addresses your devices offer to connect on. It does not receive file names, files or notes. Its operators' own terms apply to that service.</p>
<h2>What stays on your device</h2>
<p>Send saves only your light/dark choice in your browser's local storage, and keeps the app's own files (not your transfers) in the browser cache so it opens quickly. You can clear both in your browser settings.</p>
<h2>Fonts and libraries</h2>
<p>Pages load fonts from Google Fonts and two libraries from unpkg.com and cdnjs.cloudflare.com. These services see a normal web request from your browser (including your IP address), as with any website.</p>
<h2>Advertising</h2>
<p>The transfer page shows no ads. Information pages (such as How it works and FAQ) may show ads from Google AdSense. Google may use cookies to show ads based on your visits to this and other websites; you can control this at <a href='https://adssettings.google.com/'>Google Ads Settings</a> and read more at <a href='https://policies.google.com/technologies/ads'>how Google uses information from sites that use its services</a>.</p>
<h2>Children</h2>
<p>Send is not directed at children under 13 and collects no personal information from anyone.</p>
<h2>Changes and contact</h2>
<p>We will update this page if anything changes. Questions: <a href='/contact/'>contact us</a>.</p>
</div>
"""

TERMS = """
<div class='content'>
<h1>Terms of use</h1>
<p>Last updated: {date}. By using send.groupchaton.com ("Send") you agree to these terms.</p>
<h2>Using Send</h2>
<ul><li>Send is free, provided as is, for moving your own files and notes between devices.</li>
<li>You are responsible for what you send and receive, and must have the right to share it.</li>
<li>Do not use Send to share illegal content, malware, or material that infringes anyone's rights, or to harass anyone.</li>
<li>Do not try to disrupt, overload or attack Send or the pairing service.</li></ul>
<h2>No storage, no recovery</h2>
<p>Send never stores files. If a transfer fails or a page is closed, the file can't be recovered from us; send it again.</p>
<h2>Availability</h2>
<p>Send depends on browsers, networks and a third-party pairing service. We don't guarantee it will always be available or that every pair of networks can connect.</p>
<h2>Liability</h2>
<p>To the extent the law allows, GroupChatOn is not liable for any loss or damage from using Send, including lost files, harmful files you choose to accept, or interrupted transfers.</p>
<h2>Changes</h2>
<p>We may update these terms; the date above shows the latest version. Questions: <a href='/contact/'>contact us</a>.</p>
</div>
"""

DISCLAIMER = """
<div class='content'>
<h1>Disclaimer</h1>
<p>Send by GroupChatOn is a free tool provided as is, without any warranty. We do our best to keep it working and secure, but networks, browsers and devices differ and we can't promise every transfer will succeed.</p>
<p>Send has no control over the files people share. Accept files only from people you know and trust, and scan downloaded programs with security software before opening them.</p>
<p>Encryption protects files while they travel between devices. It doesn't protect a device that is already compromised, and it doesn't hide the fact that two devices connected.</p>
<p>Links to other websites are provided for convenience; we are not responsible for their content.</p>
</div>
"""

NOTFOUND = """
<div class='content' style='text-align:center'>
<h1>Page not found</h1>
<p>That address doesn't exist on Send. If you opened a pairing link, it may be incomplete: ask for the link again, or type the code instead.</p>
<p><a class='sd-btn is-main' href='/'>Open Send</a></p>
</div>
"""

def build():
    # files are replaced in place, not folders deleted: OneDrive holds a lock on folders it is syncing
    for d, _, files in os.walk(OUT):
        for f in files: os.remove(os.path.join(d, f))
    os.makedirs(OUT, exist_ok=True)
    shutil.copytree(os.path.join(HERE, 'src', 'assets'), os.path.join(OUT, 'assets'), dirs_exist_ok=True)
    shutil.copytree(os.path.join(HERE, 'static', 'brand'), os.path.join(OUT, 'brand'), dirs_exist_ok=True)
    today = datetime.date.today()
    date = today.strftime('%d %B %Y').lstrip('0')
    app_ld = {'@type': 'WebApplication', 'name': NAME, 'url': SITE + '/', 'applicationCategory': 'UtilitiesApplication',
              'operatingSystem': 'Any (runs in the browser)', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
              'description': 'Send files and notes directly between two devices with a one-time code. End-to-end encrypted, no upload, no size limit, no sign-up.'}
    pages = [
        ('/', 'Send files to any device directly, free and encrypted | Send', 'Send photos, videos and documents straight from one device to another with a one-time code. End-to-end encrypted, no upload, no size limit, no sign-up.', HOME, [app_ld, faq_ld(HOME_FAQ)], None, False, True),
        ('/how-it-works/', 'How Send works: direct, encrypted file transfer between devices', 'A plain explanation of how Send pairs two devices with a code and moves files directly over an encrypted WebRTC connection, with nothing uploaded.', HOW, None, [('How it works', '/how-it-works/')], True, False),
        ('/security/', 'Is Send secure? Encryption, one-time codes and honest limits', 'What protects your files on Send: compulsory end-to-end encryption, no storage, one-time codes, accept-first downloads, a safety code, and the limits to know.', SEC, None, [('Security', '/security/')], True, False),
        ('/faq/', 'Send FAQ: file size, browsers, safety and more', 'Answers about Send: size limits, browsers, why devices may not connect, saving received files, safety codes, mobile data and installing the app.', FAQ_PAGE, [faq_ld(FAQ)], [('FAQ', '/faq/')], True, False),
        ('/about/', 'About Send by GroupChatOn', 'Why Send exists: a free, private way to move files and notes directly between devices without email limits, compression or cloud copies.', ABOUT, None, [('About', '/about/')], True, False),
        ('/contact/', 'Contact Send by GroupChatOn', 'How to reach the Send team with a question, an idea, a transfer problem or a security report.', CONTACT, None, [('Contact', '/contact/')], False, False),
        ('/privacy-policy/', 'Privacy policy | Send by GroupChatOn', 'How Send handles data: files go device to device and are never stored; what the pairing service sees; local settings; fonts; ads on info pages.', PRIVACY.replace('{date}', date), None, [('Privacy policy', '/privacy-policy/')], False, False),
        ('/terms-of-use/', 'Terms of use | Send by GroupChatOn', 'The rules for using Send: your responsibility for what you share, no storage or recovery, availability and liability.', TERMS.replace('{date}', date), None, [('Terms of use', '/terms-of-use/')], False, False),
        ('/disclaimer/', 'Disclaimer | Send by GroupChatOn', 'Send is provided as is: accept files only from people you trust; encryption protects files in transit, not compromised devices.', DISCLAIMER, None, [('Disclaimer', '/disclaimer/')], False, False),
    ]
    for path, title, desc, main, ld, crumbs, ads, tool in pages:
        wr((path.strip('/') + '/index.html') if path != '/' else 'index.html', page(path, title, desc, main, ld, crumbs, ads, tool))
    wr('404.html', page('/404.html', 'Page not found | Send', 'This page does not exist on Send by GroupChatOn.', NOTFOUND, noindex=True))

    wr('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
       ''.join('<url><loc>%s%s</loc><lastmod>%s</lastmod></url>\n' % (SITE, p[0], today.isoformat()) for p in pages) + '</urlset>\n')
    wr('robots.txt', 'User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n' % SITE)
    wr('ads.txt', 'google.com, pub-5935207738848708, DIRECT, f08c47fec0942fa0\n')
    wr('CNAME', 'send.groupchaton.com')
    wr('.nojekyll', '')
    icons = [{'src': '/brand/favicon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
             {'src': '/brand/favicon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any'},
             {'src': '/brand/maskable-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}]
    wr('manifest.webmanifest', json.dumps({'name': NAME, 'short_name': 'Send', 'id': '/', 'start_url': '/?source=pwa', 'scope': '/',
        'display': 'standalone', 'background_color': '#0F0D0C', 'theme_color': '#EA580C', 'lang': 'en', 'icons': icons,
        'categories': ['utilities', 'productivity'],
        'description': 'Send files and notes directly between two devices. End-to-end encrypted, no upload, no sign-up.'}, indent=1, ensure_ascii=False))
    files = ['/', '/manifest.webmanifest', '/brand/favicon-192.png', '/brand/favicon-512.png', '/brand/logo-light.png', '/brand/logo-dark.png',
             '/brand/mark.svg'] + ['/assets/%s?v=%s' % (n, ver('assets/' + n)) for n in ('send.css', 'send.js', 'site.js', 'theme.js')]
    version = hashlib.sha1(''.join(files).encode()).hexdigest()[:10]
    wr('sw.js', rd('src/sw.js').replace('{{VERSION}}', version).replace('{{FILES}}', json.dumps(files)))
    print('built %d pages into %s (sw %s)' % (len(pages) + 1, OUT, version))

if __name__ == '__main__':
    build()
