# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

class CostHeader(models.Model):
	_name = 'cost.header' 

	# General Fields

	name = fields.Char("Code")
	customer_id = fields.Many2one('res.partner',string=_('Customer'),domain=[('customer','=',True)])
	version = fields.Char(string=_("Version"))
	description = fields.Text(string=_('Description'))
	start_date = fields.Date(string=_("Start Date"))
	end_date = fields.Date(string=_('End Date'))

	stage = fields.Selection([('pending','Pending'),('doing','In Process'),('done','Done')])


	units = fields.Integer('Units',default=1)

	# Cost Fields

	cost_ids = fields.One2many('cost.lines','cost_line_id','BOM')
	work_ids = fields.One2many('work.lines','cost_line_id','Work')
	material_cost = fields.Float(compute='cost_materials',string= _('Unit Material Cost'))
	work_cost = fields.Float(compute='cost_work',string=_('Unit Work cost'))
	material_markup = fields.Float(string=_('% Markup')) 
	material_cost_markup = fields.Float(compute='_markup',string=_('Total Unit Price')) # Material cost including markup
	unit_margin = fields.Float(string=_('Unit margin'))
	project_margin = fields.Float(string=_('Project margin'))
	unit_price = fields.Float(compute='_unit_price',string=_('Unit price'))
	total_price = fields.Float(string=_('Total Price'))


	# Actualiza el valor del coste de los materiales cuando se modifican la líneas
	@api.one 
	@api.onchange('cost_ids')
	@api.depends('cost_ids.price_total')
	def cost_materials(self):

		total = 0

		for i in self.cost_ids:
			total += i.qty_ldm * i.price_unit * ( 1- i.discount /100 )

		self.material_cost = total

	# Actualiza el valor del coste del trabajo cuando se modifican la líneas
	@api.one 
	@api.onchange('work_ids')
	def cost_work(self):

		total = 0

		for i in self.work_ids:
			total += i.qty_ldm * i.price_unit * ( 1- i.discount /100 )

		self.work_cost = total

	# Calcula el valor de los materiales con el markup
	@api.one
	@api.onchange('material_cost','material_markup','units')
	def _markup(self):
		self.material_cost_markup = self.material_cost * (1 + self.material_markup/100)
		self.project_margin = self.material_cost * self.units * self.material_markup / 100
		self.unit_margin = self.material_cost * self.material_markup / 100

	# Calcula el precio de venta unitario
	@api.one
	@api.onchange('material_cost_markup','work_cost','units')
	def _unit_price(self):
		self.unit_price = self.material_cost_markup + self.work_cost
		self.total_price = self.units * ( self.material_cost_markup + self.work_cost)

							
class CostLines(models.Model):
	_name= 'cost.lines'

	cost_line_id = fields.Many2one('cost.header','Cost header')
	product_id = fields.Many2one('product.product',string=_('Product'))
	component_name = fields.Char(string=_('Component'))
	unidades = fields.Many2one('product.uom', string=_('Units'),readonly=True)
	qty_ldm = fields.Float(string=_('Amount'), default=1)
	price_unit = fields.Float(string=_('Unit price'),default=0)
	discount = fields.Float(string=_('Discount'), default=0)
	price_unit_net = fields.Float(compute='unit_net_price',
								  string=_('Net price'),
								  readonly=True,
								  default=0)
	price_total = fields.Float(compute='onchange_qty_price',
                               string=_('Total Value'),
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

	# Actualizar el precio cuando seleccciona componente
	# @api.one
	# @api.onchange('component_ids')
	# def _unit_price(self):
	# 	total = 0
	# 	for i in self.component_ids:
	# 		total = i.cost_ids.qty_ldm * i.cost_ids.price_unit

	# 	self.price_unit = total



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
		return True 


class ComponentLines(models.Model):
	_name= 'component.lines'

	cost_line_id = fields.Many2one('component.header','Component header')
	product_id = fields.Many2one('product.product',string=_('Product'))
	unidades = fields.Many2one('product.uom', string=_('Units'),readonly=True)
	qty_ldm = fields.Float(string=_('Amount'), default=0)
	price_unit = fields.Float(string=_('Unit Price'))
	price_total = fields.Float(compute='onchange_qty_price',
                               string=_('Total Value'),
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
	@api.onchange('qty_ldm','price_unit')
	def onchange_qty_price(self):
		if self.qty_ldm and self.price_unit:
			self.price_total = self.qty_ldm * self.price_unit


class WorkLines(CostLines):
	_name= 'work.lines'

	cost_line_id = fields.Many2one('cost.header','Headlines')



	

