# -*- coding: utf-8 -*-

from openerp import models, fields, api,_

class CostHeader(models.Model):
	_name = 'cost.header' 

	name = fields.Char("Code")
	cost_ids = fields.One2many('cost.lines','cost_line_id','BOM')


class CostLines(models.Model):
	_name= 'cost.lines'

	cost_line_id = fields.Many2one('cost.header','Cost header')
	product_id = fields.Many2one('product.product',string="Product")
	unidades = fields.Many2one('product.uom', string='Unidades',readonly=True)
	qty_ldm = fields.Float(string='Cantidad', default=0)
	price_unit = fields.Float(string='Precio Unitario')
	price_total = fields.Float(compute='onchange_qty_price',
                               string=_('Precio Total'),
                               readonly=True,
                               default=0)
	is_set = fields.Boolean('Conjunto')
	component_ids = One2many('set.components','component_id',"Componentes")



	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.unidades = self.product_id.uom_id
			self.price_unit = self.product_id.standard_price

	@api.one
	@api.depends('qty_ldm','price_unit')
	@api.onchange('qty_ldm','price_unit')
	def onchange_qty_price(self):
		if self.qty_ldm and self.price_unit:
			self.price_total = self.qty_ldm * self.price_unit


	@api.multi
    def open_set(self):

        components = self.env['cost.lines']
        cost_line_id = components.search(
            [('mrp_bom_escandall_id', '=', self.id)])
        return {
                'name': self.product_id.name,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'mrp.bom.line.escandallo',
                'res_id': calculo_id.id or False,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                }


class PieceSet(models.Model):
	_name = 'set.components'

	component_id = fields.Many2one('cost.lines','Component')

	product_id = fields.Many2one('product.product',string="Product")
	unidades = fields.Many2one('product.uom', string='Unidades',readonly=True)
	qty_ldm = fields.Float(string='Cantidad', default=0)
	price_unit = fields.Float(string='Precio Unitario')
	price_total = fields.Float(compute='onchange_qty_price',
                               string=_('Precio Total'),
                               readonly=True,
                               default=0)


	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.unidades = self.product_id.uom_id
			self.price_unit = self.product_id.standard_price

	@api.one
	@api.depends('qty_ldm','price_unit')
	@api.onchange('qty_ldm','price_unit')
	def onchange_qty_price(self):
		if self.qty_ldm and self.price_unit:
			self.price_total = self.qty_ldm * self.price_unit




