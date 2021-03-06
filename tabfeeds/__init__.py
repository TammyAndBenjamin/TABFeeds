import base64
import hashlib
import hmac
import json
import os
from functools import wraps

import requests
from flask import Flask, Response, current_app, request, abort


LANGUAGES = {
    'ly133': 'en',
    'ly132': 'fr',
}


app = Flask(__name__)


def _hmac_is_valid(data, secret, hmac_to_verify):
    hash_ = hmac.new(secret, msg=data, digestmod=hashlib.sha256)
    hmac_calculated = base64.b64encode(hash_.digest())
    return hmac.compare_digest(hmac_calculated, hmac_to_verify)


@app.route('/products.xml')
def products():
    xml = '''<?xml version="1.0"?>
	<rss xmlns:g="http://base.google.com/ns/1.0" version="2.0">
	  <channel>
	    <title>TAMMY &amp; BENJAMIN</title>
	    <link>https://www.tammyandbenjamin.com</link>
	    <description>Leather goods</description>

	    <item>
	      <g:id>6747611905</g:id>
	      <g:title>ALEXIA - Figue</g:title>
	      <g:description>Le ladybag par excellence</g:description>
	      <g:link>https://www.tammyandbenjamin.com/products/alexia-figue</g:link>
	      <g:image_link>https://cdn.shopify.com/s/files/1/0343/0553/products/ALEXIA_Fig_01_1200x630.jpg</g:image_link>
	      <g:condition>new</g:condition>
	      <g:availability>in stock</g:availability>
	      <g:price>500.00 EUR</g:price>
	      <g:brand>TAB</g:brand>
	    </item>

	    <item>
	      <g:id>6747643585</g:id>
	      <g:title>ALEXIA - Noir ébène</g:title>
	      <g:description>Le ladybag par excellence</g:description>
	      <g:link>https://www.tammyandbenjamin.com/products/alexia-noir-ebene</g:link>
	      <g:image_link>https://cdn.shopify.com/s/files/1/0343/0553/products/ALEXIA_Black_01_1200x630.jpg</g:image_link>
	      <g:condition>new</g:condition>
	      <g:availability>in stock</g:availability>
	      <g:price>500.00 EUR</g:price>
	      <g:brand>TAB</g:brand>
	    </item>

	  </channel>
	</rss>
    '''
    return Response(xml, mimetype='text/xml')


@app.route('/order_hook', methods=['POST'])
def order_hook():
    try:
        topic = request.headers['X-Shopify-Topic']
        webhook_hmac = request.headers['X-Shopify-Hmac-Sha256'].encode()
        json.loads(request.get_data().decode())
    except Exception as e:
        current_app.logger.error(e)
        return abort(400)
    if not _hmac_is_valid(request.get_data(), os.environ['SHOPIFY_SECRET'].encode(), webhook_hmac):
        current_app.logger.error('HMAC not valid for webhook')
        return abort(403)

    mc_api_version = os.environ['MC_API_VERSION']
    mc_api_key = os.environ['MC_API_KEY']
    _, mc_zone = mc_api_key.split('-')
    mc_auth = ('tabfeeds', mc_api_key)
    mc_base_url = 'https://{}.api.mailchimp.com/{}/'.format(mc_zone, mc_api_version)

    data = request.get_json()
    customer_email = data['customer']['email']
    customer_lang = None
    for attr in data['note_attributes']:
        if attr['name'] == 'language':
            customer_lang = attr['value']
    customer_lang = LANGUAGES.get(customer_lang, 'fr')

    search_path = 'search-members'
    payload = {
        'query': customer_email,
    }
    response = requests.get(mc_base_url + search_path, params=payload, auth=mc_auth)
    data = response.json()

    matches = data['exact_matches']
    if matches['total_items'] == 0:
        current_app.logger.warning('No member found for email {}', customer_email)
        return 'ok'
    member_urls = {'{}/lists/{}/members/{}'.format(mc_base_url, member['list_id'], member['id']) for member in matches['members']}
    for member_url in member_urls:
        payload = {
            'language': customer_lang,
        }
        response = requests.patch(member_url, params=payload, auth=mc_auth)
    return 'ok'
