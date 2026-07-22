(function() {
  if (window.__GTM_AUDIT_ACTIVE__) {
    const total = JSON.parse(localStorage.getItem('gtm_audit_log') || '[]').length;
    console.log('%c[GTM-AUDIT] Ya activo. Eventos acumulados: ' + total, 'color:#1D9E75;font-weight:bold');
    return;
  }
  window.__GTM_AUDIT_ACTIVE__ = true;

  const STORAGE_KEY = 'gtm_audit_log';
  const SESSION_ID  = 'sess_' + Date.now();
  let log = [];

  try {
    const prev = localStorage.getItem(STORAGE_KEY);
    if (prev) log = JSON.parse(prev);
  } catch(e) {}

  const badge = document.createElement('div');
  badge.id = 'gtm-audit-badge';
  badge.style.cssText = [
    'position:fixed', 'bottom:16px', 'right:16px', 'z-index:2147483647',
    'background:#1a1a2e', 'color:#fff', 'font-family:monospace',
    'font-size:12px', 'border-radius:10px', 'padding:10px 14px',
    'box-shadow:0 4px 16px rgba(0,0,0,0.5)', 'min-width:190px',
    'display:flex', 'flex-direction:column', 'gap:6px'
  ].join(';');

  badge.innerHTML = [
    '<div style="display:flex;align-items:center;gap:8px">',
    '  <span style="width:8px;height:8px;border-radius:50%;background:#1D9E75;display:inline-block"></span>',
    '  <span style="font-weight:bold;color:#1D9E75">GTM AUDIT</span>',
    '</div>',
    '<div id="gtm-audit-count" style="color:#aaa">Eventos: 0</div>',
    '<div id="gtm-audit-page" style="color:#aaa;font-size:11px;max-width:170px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"></div>',
    '<div style="display:flex;gap:6px;margin-top:2px">',
    '  <button id="gtm-btn-export" style="flex:1;background:#1D9E75;color:#fff;border:none;border-radius:6px;padding:5px 0;font-size:11px;cursor:pointer">Exportar JSON</button>',
    '  <button id="gtm-btn-summary" style="flex:1;background:#2a2a3e;color:#fff;border:none;border-radius:6px;padding:5px 0;font-size:11px;cursor:pointer">Resumen</button>',
    '</div>',
    '<button id="gtm-btn-clear" style="background:transparent;color:#555;border:none;font-size:10px;cursor:pointer;text-align:left;padding:0">✕ Limpiar log</button>'
  ].join('');

  document.body.appendChild(badge);

  document.getElementById('gtm-btn-export').onclick  = () => GTMAudit.exportJSON();
  document.getElementById('gtm-btn-summary').onclick = () => GTMAudit.summary();
  document.getElementById('gtm-btn-clear').onclick   = () => GTMAudit.clear();

  function updateBadge() {
    const total = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]').length;
    document.getElementById('gtm-audit-count').textContent = 'Eventos: ' + total;
    document.getElementById('gtm-audit-page').textContent = document.title;
  }

  function save(entry) {
    entry.session = SESSION_ID;
    entry.ts = new Date().toISOString();
    entry.url = location.href;
    entry.page = document.title;
    log.push(entry);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(log));
    } catch(e) {}
    updateBadge();
    console.log('%c[GTM-AUDIT]', 'color:#1D9E75;font-weight:bold', entry.type, '->', entry);
  }

  window.dataLayer = window.dataLayer || [];
  const _orig = window.dataLayer.push.bind(window.dataLayer);

  window.dataLayer.push = function(...args) {
    args.forEach(obj => save({
      type: 'dataLayer_push',
      event: obj.event || '(sin evento)',
      data: JSON.parse(JSON.stringify(obj))
    }));
    return _orig(...args);
  };

  (window.dataLayer || []).forEach(obj =>
    save({
      type: 'dataLayer_initial',
      event: obj.event || '(inicial)',
      data: obj
    })
  );

  document.addEventListener('click', function(e) {
    const el = e.target.closest('a,button,[role="button"],input[type="submit"],label');
    if (!el || el.closest('#gtm-audit-badge')) return;

    save({
      type: 'click',
      tag: el.tagName.toLowerCase(),
      text: (el.innerText || el.value || '').trim().slice(0, 80),
      id: el.id || null,
      classes: el.className || null,
      href: el.href || null,
      dataAttrs: Object.fromEntries(
        [...el.attributes]
          .filter(a => a.name.startsWith('data-'))
          .map(a => [a.name, a.value])
      )
    });
  }, true);

  document.addEventListener('submit', function(e) {
    const form = e.target;

    save({
      type: 'form_submit',
      formId: form.id || null,
      action: form.action || null,
      method: form.method || 'get',
      fields: [...form.elements].map(f => ({
        name: f.name || f.id,
        type: f.type,
        value: f.type === 'password' ? '[REDACTED]' : f.value
      })).filter(f => f.name)
    });
  }, true);

  ['pushState', 'replaceState'].forEach(method => {
    const orig = history[method];

    history[method] = function(...a) {
      orig.apply(this, a);
      save({
        type: 'navigation',
        method,
        newUrl: a[2]
      });
    };
  });

  window.addEventListener('popstate', () =>
    save({
      type: 'navigation',
      method: 'popstate',
      newUrl: location.href
    })
  );

  const SELECTORS = [
    '[data-track]',
    '.cta',
    'form',
    '[class*="precio"]',
    '[class*="price"]',
    '[class*="banner"]',
    '[class*="formulario"]'
  ];

  const io = new IntersectionObserver(entries => {
    entries.filter(e => e.isIntersecting).forEach(e => {
      save({
        type: 'element_visible',
        tag: e.target.tagName.toLowerCase(),
        id: e.target.id || null,
        classes: e.target.className || '',
        text: (e.target.innerText || '').trim().slice(0, 60)
      });
      io.unobserve(e.target);
    });
  }, {
    threshold: 0.5
  });

  document.querySelectorAll(SELECTORS.join(', ')).forEach(el => io.observe(el));

  window.GTMAudit = {
    exportJSON: function() {
      const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
      const blob = new Blob([JSON.stringify(data, null, 2)], {
        type: 'application/json'
      });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `gtm_audit_${new Date().toISOString().slice(0,10)}.json`;
      a.click();
      console.log('[GTM-AUDIT] Exportados', data.length, 'eventos');
    },

    summary: function() {
      const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');

      const byType = data.reduce((acc, e) => {
        acc[e.type] = (acc[e.type] || 0) + 1;
        return acc;
      }, {});

      console.log('%c[GTM-AUDIT] Resumen por tipo', 'color:#7f77dd;font-weight:bold');
      console.table(byType);

      const dlEvents = data
        .filter(e => e.type === 'dataLayer_push')
        .reduce((acc, e) => {
          const name = e.data?.event || 'unknown';
          acc[name] = (acc[name] || 0) + 1;
          return acc;
        }, {});

      console.log('%c[GTM-AUDIT] Eventos dataLayer', 'color:#185fa5;font-weight:bold');
      console.table(dlEvents);
    },

    clear: function() {
      localStorage.removeItem(STORAGE_KEY);
      log = [];
      updateBadge();
      console.log('[GTM-AUDIT] Log limpiado');
    }
  };

  updateBadge();

  console.log('%c[GTM-AUDIT] Snippet activo', 'color:#1D9E75;font-weight:bold;font-size:14px');
  console.log('Comandos disponibles: GTMAudit.exportJSON() · GTMAudit.summary() · GTMAudit.clear()');
})();