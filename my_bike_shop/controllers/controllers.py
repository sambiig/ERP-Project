from odoo import http

class MyBikeShop(http.Controller):
    
    @http.route('/bike_shop/velos', auth='public', website=True)
    def list_bikes(self, **kw):
        bikes = http.request.env['bike.shop.product'].search([('product_type', '=', 'bike')])
        return http.request.render('my_bike_shop.bike_listing', {
            'bikes': bikes,
        })