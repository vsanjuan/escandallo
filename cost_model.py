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
	## TODO : Add component OnetoMany.
	component_ids = One2many('component.set','component_set_id',"Componentes") 
	unidades = fields.Many2one('product.uom', string='Unidades',readonly=True)
	qty_ldm = fields.Float(string='Cantidad', default=0)
	price_unit = fields.Float(string='Precio Unitario')
	price_total = fields.Float(compute='onchange_qty_price',
                               string=_('Precio Total'),
                               readonly=True,
                               default=0)
	is_set = fields.Boolean('Conjunto')
	


	# Updates Unit of Measure and price when the product_id changes
	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.unidades = self.product_id.uom_id
			self.price_unit = self.product_id.standard_price

	## TODO: Function to calculate component price adding component BOM and prices

	@api.one
	@api.depends('qty_ldm','price_unit')
	@api.onchange('qty_ldm','price_unit')
	def onchange_qty_price(self):
		if self.qty_ldm and self.price_unit:
			self.price_total = self.qty_ldm * self.price_unit


	@api.multi
    def open_component(self):

        components = self.env['component.set']
        component_id = components.search(
            [('component_id', '=', self.id)])
        return {
        		## TODO: Load the component name on the form
                'name': 'Component',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'component.set',
                'res_id': component_id.id or False,
                'view_id': False,
                'type': 'ir.actions.act_window',
                'target': 'new',
                }


class Component(models.Model):
	_name = "component.set"

	name = fields.Char('Component')
	component_set_id = fields.Many2one('cost.lines','Component')
	component_ids = fields.One2many('component.set.line','component_id')


class ComponentLines(models.Model):
	_name = 'component.set.line'

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




