import requests, time, re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from analyzer.config import MAX_PAGES, DELAY, HEADERS


def detect_tracking(soup):
    scripts = ' '.join(str(s) for s in soup.find_all('script'))
    return {
        'gtm_present':      'googletagmanager.com/gtm.js' in scripts,
        'gtm_ids':          list(set(re.findall(r'GTM-[A-Z0-9]+', scripts))),
        'ga4_present':      bool(re.search(r'G-[A-Z0-9]+', scripts)),
        'ga4_ids':          list(set(re.findall(r'G-[A-Z0-9]+', scripts))),
        'meta_pixel':       'connect.facebook.net' in scripts,
        'datalayer_init':   'dataLayer' in scripts,
        'datalayer_pushes': scripts.count('dataLayer.push'),
    }


def analyze_forms(soup, page_url):
    forms = []
    for form in soup.find_all('form'):
        fields = []
        for el in form.find_all(['input', 'select', 'textarea']):
            field_type = el.get('type', 'text')
            if field_type in ('hidden', 'submit', 'button', 'reset'):
                continue
            fields.append({
                'tag':         el.name,
                'type':        field_type,
                'name':        el.get('name') or el.get('id', ''),
                'placeholder': el.get('placeholder', ''),
                'required':    el.has_attr('required'),
            })
        if fields:
            forms.append({
                'page_url':    page_url,
                'form_id':     form.get('id', ''),
                'form_action': form.get('action', ''),
                'form_method': form.get('method', 'get').upper(),
                'field_count': len(fields),
                'fields':      fields,
            })
    return forms


def analyze_ctas(soup):
    ctas = []
    kw = re.compile(r'btn|cta|button|call|action|inscri|admisi|contacto|registro|solicita', re.I)
    for tag in ['a', 'button']:
        for el in soup.find_all(tag):
            classes = ' '.join(el.get('class', []))
            text    = el.get_text(strip=True)
            if kw.search(classes) or kw.search(text):
                ctas.append({
                    'tag':     tag,
                    'text':    text[:80],
                    'href':    el.get('href', ''),
                    'classes': classes[:100],
                    'id':      el.get('id', ''),
                })
    return ctas[:20]


def crawl_site(start_url, max_pages=MAX_PAGES):
    domain    = urlparse(start_url).netloc
    visited   = set()
    queue     = [start_url]
    results   = []
    all_forms = []

    print(f"\n{'─'*55}")
    print(f"  Crawleando: {start_url}")
    print(f"  Límite: {max_pages} páginas | Delay: {DELAY}s")
    print(f"{'─'*55}\n")

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            r        = requests.get(url, headers=HEADERS, timeout=10)
            soup     = BeautifulSoup(r.text, 'html.parser')
            title    = soup.title.string.strip() if soup.title else ''
            tracking = detect_tracking(soup)
            forms    = analyze_forms(soup, url)
            ctas     = analyze_ctas(soup)
            all_forms.extend(forms)

            results.append({
                'url':        url,
                'title':      title,
                'status':     r.status_code,
                'tracking':   tracking,
                'forms':      forms,
                'form_count': len(forms),
                'ctas':       ctas,
                'cta_count':  len(ctas),
            })

            for a in soup.find_all('a', href=True):
                href = urljoin(url, a['href']).split('#')[0].split('?')[0]
                if (urlparse(href).netloc == domain
                        and href not in visited
                        and href not in queue
                        and not href.endswith(('.pdf', '.jpg', '.png', '.zip'))):
                    queue.append(href)

            gtm_label = f"GTM: {','.join(tracking['gtm_ids'])}" if tracking['gtm_ids'] else "GTM: ✗"
            ga4_label = f"GA4: {','.join(tracking['ga4_ids'])}" if tracking['ga4_ids'] else "GA4: ✗"
            print(f"  [{len(visited):02}/{max_pages}] {gtm_label} | {ga4_label} | Forms: {len(forms)} | {url[:60]}")
            time.sleep(DELAY)

        except Exception as e:
            print(f"  [ERROR] {url[:60]} → {e}")

    print(f"\nCrawleo completado: {len(results)} páginas analizadas\n")
    return results, all_forms
