import json
from collections import defaultdict


def analyze_js_log(json_path):
    if not json_path:
        return None
    try:
        with open(json_path) as f:
            events = json.load(f)
    except FileNotFoundError:
        print(f"JSON no encontrado: {json_path} — se omite esta sección.")
        return None

    summary = defaultdict(list)
    for ev in events:
        summary[ev['type']].append(ev)

    dl_events = {}
    for ev in summary.get('dataLayer_push', []):
        name = ev.get('data', {}).get('event', 'unknown')
        if name not in dl_events:
            dl_events[name] = {'count': 0, 'params': set(), 'pages': set()}
        dl_events[name]['count'] += 1
        dl_events[name]['params'].update(ev.get('data', {}).keys())
        dl_events[name]['pages'].add(ev.get('url', ''))

    return {
        'total_events':     len(events),
        'by_type':          {k: len(v) for k, v in summary.items()},
        'datalayer_events': dl_events,
        'forms_captured':   summary.get('form_submit', []),
        'navigations':      [e.get('newUrl', '') for e in summary.get('navigation', [])],
        'raw':              events,
    }
