/* ── Cookie / Storage Consent Banner ─────────────────────────────────── */
(function () {
  'use strict';

  var STORAGE_KEY = 'rh_cookie_consent';
  var CONSENT_VERSION = '1';

  /* Already answered? */
  try {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      var d = JSON.parse(saved);
      if (d && d.v === CONSENT_VERSION) return;
    }
  } catch (e) {}

  /* ── Styles ── */
  var css = [
    '#rh-cookie{',
    '  position:fixed;bottom:0;left:0;right:0;z-index:9999;',
    '  background:#F2EDE5;border-top:1px solid #E0D8CF;',
    '  padding:20px 24px;',
    '  display:flex;align-items:flex-start;gap:20px;flex-wrap:wrap;',
    '  box-shadow:0 -4px 24px rgba(44,44,44,.08);',
    '  font-family:"Jost",sans-serif;font-size:.82rem;font-weight:300;',
    '  color:#2C2C2C;line-height:1.65;',
    '}',
    '#rh-cookie .rh-c-text{flex:1;min-width:200px;}',
    '#rh-cookie .rh-c-text strong{font-weight:400;}',
    '#rh-cookie .rh-c-text a{color:#5C7A62;text-decoration:underline;text-underline-offset:2px;}',
    '#rh-cookie .rh-c-text a:hover{color:#B89A5E;}',
    '#rh-cookie .rh-c-btns{display:flex;align-items:center;gap:12px;flex-wrap:wrap;flex-shrink:0;}',
    '#rh-cookie .rh-c-accept{',
    '  background:#B89A5E;color:#fff;border:none;cursor:pointer;',
    '  padding:10px 22px;font-family:"Jost",sans-serif;font-size:.78rem;',
    '  font-weight:400;letter-spacing:.08em;text-transform:uppercase;',
    '  transition:background .2s;white-space:nowrap;',
    '}',
    '#rh-cookie .rh-c-accept:hover{background:#a38750;}',
    '#rh-cookie .rh-c-reject{',
    '  background:none;border:1px solid #E0D8CF;color:#6B6560;cursor:pointer;',
    '  padding:9px 18px;font-family:"Jost",sans-serif;font-size:.78rem;',
    '  font-weight:300;letter-spacing:.06em;',
    '  transition:border-color .2s,color .2s;white-space:nowrap;',
    '}',
    '#rh-cookie .rh-c-reject:hover{border-color:#B89A5E;color:#2C2C2C;}',
    '#rh-cookie .rh-c-details{',
    '  width:100%;font-size:.77rem;color:#6B6560;',
    '  border-top:1px solid #E0D8CF;padding-top:12px;margin-top:4px;',
    '  display:none;',
    '}',
    '#rh-cookie .rh-c-details ul{padding-left:16px;margin:6px 0 0;}',
    '#rh-cookie .rh-c-details li{margin-bottom:4px;}',
    '#rh-cookie .rh-c-toggle{',
    '  background:none;border:none;color:#5C7A62;cursor:pointer;',
    '  font-family:"Jost",sans-serif;font-size:.78rem;font-weight:300;',
    '  text-decoration:underline;text-underline-offset:2px;padding:0;',
    '  letter-spacing:.03em;',
    '}',
    '@media(max-width:600px){',
    '  #rh-cookie{flex-direction:column;gap:14px;}',
    '  #rh-cookie .rh-c-btns{width:100%;}',
    '  #rh-cookie .rh-c-accept,#rh-cookie .rh-c-reject{flex:1;text-align:center;}',
    '}',
  ].join('');

  var style = document.createElement('style');
  style.textContent = css;
  document.head.appendChild(style);

  /* ── HTML ── */
  var privacyUrl = (function () {
    var base = window.location.pathname.indexOf('/blog/') !== -1 ? '../' : '';
    return base + 'polityka-prywatnosci.html';
  })();

  var el = document.createElement('div');
  el.id = 'rh-cookie';
  el.setAttribute('role', 'dialog');
  el.setAttribute('aria-label', 'Informacja o plikach cookie');
  el.innerHTML = [
    '<div class="rh-c-text">',
    '  <strong>Ta strona używa plików cookie i pamięci przeglądarki.</strong> ',
    '  Niezbędne pliki zapewniają działanie strony (np. zapamiętanie języka i danych rezerwacji). ',
    '  Korzystamy też z Google Fonts i EmailJS — zewnętrznych usług, które mogą zapisywać Twój adres IP. ',
    '  Więcej w <a href="' + privacyUrl + '">Polityce prywatności</a>.',
    '  <div class="rh-c-details" id="rh-c-details">',
    '    <ul>',
    '      <li><strong>Niezbędne:</strong> localStorage (język interfejsu), sessionStorage (dane rezerwacji — kasowane po powrocie z płatności)</li>',
    '      <li><strong>Zewnętrzne funkcjonalne:</strong> Google Fonts (fonts.googleapis.com) — czcionki; EmailJS (cdn.jsdelivr.net) — wysyłka potwierdzeń rezerwacji</li>',
    '      <li><strong>Płatności:</strong> Przelewy24 — własne pliki cookie podczas procesu płatności (operator: PayPro S.A.)</li>',
    '      <li><strong>Analityczne/marketingowe:</strong> brak</li>',
    '    </ul>',
    '  </div>',
    '  <button class="rh-c-toggle" id="rh-c-toggle" aria-expanded="false">Szczegóły ▾</button>',
    '</div>',
    '<div class="rh-c-btns">',
    '  <button class="rh-c-reject" id="rh-c-reject">Tylko niezbędne</button>',
    '  <button class="rh-c-accept" id="rh-c-accept">Rozumiem i akceptuję</button>',
    '</div>',
  ].join('');

  document.body.appendChild(el);

  /* ── Logic ── */
  function saveConsent(type) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({
        v: CONSENT_VERSION,
        type: type,
        ts: Date.now()
      }));
    } catch (e) {}
    el.style.transition = 'transform .3s ease, opacity .3s ease';
    el.style.transform = 'translateY(100%)';
    el.style.opacity = '0';
    setTimeout(function () {
      if (el.parentNode) el.parentNode.removeChild(el);
    }, 350);
  }

  document.getElementById('rh-c-accept').addEventListener('click', function () {
    saveConsent('all');
  });

  document.getElementById('rh-c-reject').addEventListener('click', function () {
    saveConsent('necessary');
  });

  document.getElementById('rh-c-toggle').addEventListener('click', function () {
    var details = document.getElementById('rh-c-details');
    var expanded = this.getAttribute('aria-expanded') === 'true';
    details.style.display = expanded ? 'none' : 'block';
    this.setAttribute('aria-expanded', String(!expanded));
    this.textContent = expanded ? 'Szczegóły ▾' : 'Ukryj szczegóły ▴';
  });
})();
