import requests
import urllib
import base64


import xmlrpc.client
import requests
import base64
import urllib
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format("https://allworldshops-aws-14-stage-1906388.dev.odoo.com"))
 
print(common.version())
 
url = "https://allworldshops-aws-14-stage-1906388.dev.odoo.com"
db = "allworldshops-aws-14-stage-1906388"
username = "admin"
password = "admin"
uid = common.authenticate(db, username, password, {})
print(uid)
 
 
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
 
 
product_ids = models.execute_kw(db, uid, password,
    'product.template', 'search',
    [[['image_url', '!=', False],['image_1920', '=', False]]])
 
print(len(product_ids))
 
 
product_ids = models.execute_kw(db, uid, password,
    'product.template', 'read',
    [product_ids], {'fields': ['name', 'image_url','image_image_url']})
 
 
print(product_ids[0])
 
for product_id in product_ids:
     
    try:
                  
        image_medium = base64.encodestring(urllib.request.urlopen(product_id['image_url'].replace(" ", "%20")).read())
        if image_medium:
            models.execute_kw(db, uid, password, 'product.template', 'write', [[product_id['id']], {
            'image_image_url': image_medium}])
 
    except Exception:
        print(product_id['image_url'])
        pass


