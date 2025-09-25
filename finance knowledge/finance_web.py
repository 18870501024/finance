# -*- coding: utf-8 -*-
from flask import Flask, abort, jsonify, render_template_string

from finance_content import (
    CATEGORIES,
    CARDS,
    CARD_DETAILS,
    MODELS,
    ETFS,
    ETF_CARDS,
    TEMPLATE,
)
import finance_etf

app = Flask(__name__)


@app.route('/card/<slug>')
def card_detail(slug: str):
    payload = CARD_DETAILS.get(slug)
    if not payload:
        abort(404)

    card = payload['card']
    related = [
        item for item in CARDS
        if item.get('category') == card.get('category') and item.get('slug') != slug
    ][:3]

    return render_template_string(
        TEMPLATE,
        categories=CATEGORIES,
        cards=CARDS,
        models=MODELS,
        etfs=ETFS,
        etf_cards=ETF_CARDS,
        card_detail=payload,
        related_cards=related,
        page_type='card_detail',
    )


@app.route('/api/etf/<ticker>')
def etf_timeseries(ticker: str):
    normalized = (ticker or '').upper()
    if not normalized:
        return jsonify({'dates': [], 'navs': [], 'returns': []}), 400

    if not finance_etf.ensure_etf_cache():
        return jsonify({'dates': [], 'navs': [], 'returns': []}), 502

    series = finance_etf.ETF_CACHE.get(normalized)
    if not series:
        if not finance_etf.ensure_etf_cache(force_refresh=True):
            return jsonify({'dates': [], 'navs': [], 'returns': []}), 502
        series = finance_etf.ETF_CACHE.get(normalized, [])
    if not series:
        return jsonify({'dates': [], 'navs': [], 'returns': []}), 404

    return jsonify({
        'dates': [point['date'] for point in series],
        'navs': [point['nav'] for point in series],
        'returns': [point['return_pct'] for point in series],
    })


@app.route('/')
def index():
    return render_template_string(
        TEMPLATE,
        categories=CATEGORIES,
        cards=CARDS,
        models=MODELS,
        etfs=ETFS,
        etf_cards=ETF_CARDS,
        page_type='home',
    )


if __name__ == '__main__':
    if not finance_etf.EXCEL_PATH.exists():
        finance_etf.ensure_etf_cache(force_refresh=True)
    else:
        finance_etf.ensure_etf_cache()
    app.run(debug=True)


