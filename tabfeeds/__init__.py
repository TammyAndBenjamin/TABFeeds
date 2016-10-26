import hashlib, base64, hmac, json
from functools import wraps

import requests
from flask import Flask, Response, current_app, request, abort


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
        request.headers['X-Shopify-Topic']
        webhook_hmac = request.headers['X-Shopify-Hmac-Sha256'].encode()
        json.loads(request.get_data().decode())
    except Exception as e:
        current_app.logger.error(e)
        return abort(400)
    if not _hmac_is_valid(request.get_data(), '4b543c40d4156b4a97948f4aea67ede2'.encode(), webhook_hmac):
        current_app.logger.error('HMAC not valid for webhook')
        return abort(403)
    data = request.get_json()
    customer_email = data['customer']['email']
    customer_lang = None
    for attr in data['note_attributes']:
        if attr['name'] == 'language':
            customer_lang = attr['value']
    current_app.logger.info(customer_email)
    current_app.logger.info(customer_lang)
    return 'ok'
