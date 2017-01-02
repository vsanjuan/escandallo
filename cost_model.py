# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class CostHeader(models.Model):
	_name = 'cost.header' 

	name = fields.Char("Code")
	cost_ids = fields.One2many('cost.lines','cost_line_id','BOM')
	material_cost = fields.Float(compute='cost_materials',string='Material Cost')


	# Actualiza el valor del coste de los materiales cuando se modifican la líneas
	@api.one 
	@api.onchange('cost_ids','cost_ids.component_ids')
	@api.depends('cost_ids.price_total')
	def cost_materials(self):

		total = 0

		for i in self.cost_ids:
			total += i.qty_ldm * i.price_unit * ( 1- i.discount /100 )

		self.material_cost = total


							
class CostLines(models.Model):
	_name= 'cost.lines'

	cost_line_id = fields.Many2one('cost.header','Cost header')
	product_id = fields.Many2one('product.product',string="Product")
	component_name = fields.Char('Component')
	unidades = fields.Many2one('product.uom', string='Unidades',readonly=True)
	qty_ldm = fields.Float(string='Cantidad', default=0)
	price_unit = fields.Float(string='Precio Unitario',default=0)
	discount = fields.Float(string='Descuento', default=0)
	price_unit_net = fields.Float(compute='unit_net_price',
								  string='Precio neto',
								  readonly=True,
								  default=0)
	price_total = fields.Float(compute='onchange_qty_price',
                               string=_('Precio Total'),
                               readonly=True,
                               #store=True,
                               default=0)

	# Link cost lines to component
	component_ids = fields.One2many('component.header','cost_line_id','Component')


	# Actualiza los campos Unidad de medida y precio al cambiar el producto
	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.unidades = self.product_id.uom_id
			self.price_unit = self.product_id.standard_price

	# Actualizar el valor neto unitario al cambiar el precio unitario
	@api.one
	@api.onchange('price_unit','discount')
	def unit_net_price(self):
		self.price_unit_net = self.price_unit * (1 - self.discount/100)


	# Actualiza el campo price_total cuando varía el precio o la cantidad
	@api.one
	@api.onchange('qty_ldm','price_unit','discount')
	def onchange_qty_price(self):
		if self.qty_ldm and self.price_unit:
			self.price_total = self.qty_ldm * self.price_unit * (1 - self.discount/100)


	# Open a window with the components
	@api.multi
	def open_component(self):
		component_model = self.env['component.header']
		component = component_model.search([('cost_line_id','=',self.id)])
		return {
				'name': self.component_name,
				'view_type':'form',
				'view_mode':'form',
				'res_model':'component.header',
				'res_id': component.id or False,
				'view_id': False,
				'type':'ir.actions.act_window',
				'target':'new',
		}


class ComponentHeader(models.Model):
	_name = 'component.header'

	name = fields.Char("Code")
	cost_ids = fields.One2many('component.lines','cost_line_id','BOM')
	cost_line_id = fields.Many2one('cost.lines')
	#price_total = fields.Float(compute='on_change_lines', )

	@api.multi
	def save_component(self):

		# Calculates the cost of the component
		total = 0
		for i in self.cost_ids:
			total += i.qty_ldm * i.price_unit


		# Saves the value on the price unit line on the BOM

		# Warning! Don't know how but prevents getting several lines
		self.cost_line_id = self._context.get('active_ids')[0] 
		self.cost_line_id.price_unit = total 


class CostLines(models.Model):
	_name= 'component.lines'

	cost_line_id = fields.Many2one('component.header','Component header')
	product_id = fields.Many2one('product.product',string="Product")
	unidades = fields.Many2one('product.uom', string='Unidades',readonly=True)
	qty_ldm = fields.Float(string='Cantidad', default=0)
	price_unit = fields.Float(string='Precio Unitario')
	price_total = fields.Float(compute='onchange_qty_price',
                               string=_('Precio Total'),
                               readonly=True,
                               default=0)


	# Actualiza los campos Unidad de medida y precio al cambiar el producto
	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.unidades = self.product_id.uom_id
			self.price_unit = self.product_id.standard_price


	# Actualiza el campo price_total cuando varía el precio o la cantidad
	@api.one
	@api.depends('qty_ldm','price_unit')
	@api.onchange('qty_ldm','price_unit')
	def onchange_qty_price(self):
		if self.qty_ldm and self.price_unit:
			self.price_total = self.qty_ldm * self.price_unit






