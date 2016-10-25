from flask import Flask


app = Flask(__name__)


@app.route('/products.xml')
def products():
    xml = '''
	<?xml version="1.0"?>
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
	      <g:image_link>https://cdn.shopify.com/s/files/1/0343/0553/products/ALEXIA_Fig_01_600x600.jpg</g:image_link>
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
	      <g:image_link>https://cdn.shopify.com/s/files/1/0343/0553/products/ALEXIA_Black_01_600x600.jpg</g:image_link>
	      <g:condition>new</g:condition>
	      <g:availability>in stock</g:availability>
	      <g:price>500.00 EUR</g:price>
	      <g:brand>TAB</g:brand>
	    </item>

	  </channel>
	</rss>
    '''
    return Response(xml, mimetype='text/xml')
