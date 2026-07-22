import pandas as pd
from datetime import datetime


def export_report(crawl_results, all_forms, js_analysis=None):
    ts   = datetime.now().strftime("%Y%m%d_%H%M")
    path = f"gtm_audit_report_{ts}.xlsx"

    with pd.ExcelWriter(path, engine='openpyxl') as writer:

        gtm_ids_found = list(set(
            gid for r in crawl_results for gid in r['tracking']['gtm_ids']
        ))
        ga4_ids_found = list(set(
            gid for r in crawl_results for gid in r['tracking']['ga4_ids']
        ))
        pages_with_gtm   = sum(1 for r in crawl_results if r['tracking']['gtm_present'])
        pages_with_ga4   = sum(1 for r in crawl_results if r['tracking']['ga4_present'])
        pages_with_pixel = sum(1 for r in crawl_results if r['tracking']['meta_pixel'])
        pages_with_forms = sum(1 for r in crawl_results if r['form_count'] > 0)
        multiple_gtm     = sum(1 for r in crawl_results if len(r['tracking']['gtm_ids']) > 1)

        resumen_rows = [
            ('CRAWLEO ESTÁTICO', ''),
            ('Páginas analizadas',            len(crawl_results)),
            ('Páginas con GTM',               f"{pages_with_gtm} / {len(crawl_results)}"),
            ('Páginas con GA4',               f"{pages_with_ga4} / {len(crawl_results)}"),
            ('Páginas con Meta Pixel',        f"{pages_with_pixel} / {len(crawl_results)}"),
            ('Páginas con formularios',       f"{pages_with_forms} / {len(crawl_results)}"),
            ('Páginas con +1 contenedor GTM', multiple_gtm),
            ('Contenedores GTM encontrados',  ', '.join(gtm_ids_found) or 'Ninguno'),
            ('IDs GA4 encontrados',           ', '.join(ga4_ids_found) or 'Ninguno'),
            ('Total formularios detectados',  len(all_forms)),
            ('', ''),
        ]

        if js_analysis:
            resumen_rows += [
                ('NAVEGACIÓN EN VIVO (snippet JS)', ''),
                ('Total eventos capturados',        js_analysis['total_events']),
                ('Eventos dataLayer únicos',        len(js_analysis['datalayer_events'])),
                ('Formularios enviados',            len(js_analysis['forms_captured'])),
                ('Navegaciones SPA',                len(js_analysis['navigations'])),
            ]
        else:
            resumen_rows.append(('NAVEGACIÓN EN VIVO', 'No se proporcionó JSON del snippet'))

        pd.DataFrame(resumen_rows, columns=['Métrica', 'Valor']) \
          .to_excel(writer, sheet_name='Resumen', index=False)

        pages_df = pd.DataFrame([{
            'URL':                  r['url'],
            'Título':               r['title'],
            'Status HTTP':          r['status'],
            'GTM instalado':        r['tracking']['gtm_present'],
            'GTM IDs':              ', '.join(r['tracking']['gtm_ids']),
            'Contenedores GTM':     len(r['tracking']['gtm_ids']),
            'GA4 instalado':        r['tracking']['ga4_present'],
            'GA4 IDs':              ', '.join(r['tracking']['ga4_ids']),
            'Meta Pixel':           r['tracking']['meta_pixel'],
            'dataLayer presente':   r['tracking']['datalayer_init'],
            'dataLayer.push count': r['tracking']['datalayer_pushes'],
            'Formularios':          r['form_count'],
            'CTAs detectados':      r['cta_count'],
        } for r in crawl_results])
        pages_df.to_excel(writer, sheet_name='Páginas', index=False)

        form_rows = []
        for form in all_forms:
            for field in form['fields']:
                form_rows.append({
                    'Página':      form['page_url'],
                    'Form ID':     form['form_id'],
                    'Action':      form['form_action'],
                    'Método':      form['form_method'],
                    'Campo':       field['name'],
                    'Tipo':        field['type'],
                    'Placeholder': field['placeholder'],
                    'Requerido':   field['required'],
                })
        if form_rows:
            pd.DataFrame(form_rows).to_excel(writer, sheet_name='Formularios (estático)', index=False)

        cta_rows = []
        for r in crawl_results:
            for cta in r['ctas']:
                cta_rows.append({'Página': r['url'], **cta})
        if cta_rows:
            pd.DataFrame(cta_rows).to_excel(writer, sheet_name='CTAs', index=False)

        if js_analysis:
            dl_rows = [{
                'Evento':     name,
                'Disparos':   info['count'],
                'Parámetros': ', '.join(sorted(info['params'])),
                'Páginas':    ', '.join(info['pages']),
            } for name, info in js_analysis['datalayer_events'].items()]
            if dl_rows:
                pd.DataFrame(dl_rows).to_excel(writer, sheet_name='DataLayer (vivo)', index=False)

            live_form_rows = []
            for ev in js_analysis['forms_captured']:
                for field in ev.get('fields', []):
                    live_form_rows.append({
                        'Página':  ev.get('url', ''),
                        'Form ID': ev.get('formId', ''),
                        'Action':  ev.get('action', ''),
                        'Campo':   field.get('name', ''),
                        'Tipo':    field.get('type', ''),
                        'Valor':   field.get('value', ''),
                    })
            if live_form_rows:
                pd.DataFrame(live_form_rows).to_excel(writer, sheet_name='Formularios (vivo)', index=False)

    print(f"Reporte generado: {path}\n")
    return path
