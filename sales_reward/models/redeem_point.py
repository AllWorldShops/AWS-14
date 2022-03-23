from odoo import  fields, models, api, _

class redeem_point_wizard(models.TransientModel):
    _name = "redeem.point"

    point_to_use = fields.Integer()

    def get_points_to_redeem(self):

        sorder = self.env.context.get('active_id')
        sale_id = self.env['sale.order'].search([('id', '=', sorder)])
        point_to_use_sale = self.point_to_use
        sale_id.point_to_use = point_to_use_sale

        sale_id.so_redeem()


