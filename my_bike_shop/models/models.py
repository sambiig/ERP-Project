from odoo import models, fields, api
from datetime import timedelta

# -------------------------------------------------------------------
#  PRODUITS DU MAGASIN DE VÉLOS (héritage de product.template)
# -------------------------------------------------------------------

class BikeProduct(models.Model):
    _inherit = 'product.template'

    # Marqueur pour distinguer les produits de ton module
    is_bike_shop_item = fields.Boolean(
        string="Article du Bike Shop",
        default=True
    )

    product_type = fields.Selection([
        ('bike', 'Vélo'),
        ('part', 'Pièce détachée'),
        ('accessory', 'Accessoire'),
    ], string='Type de produit', required=True, default='bike')

    brand = fields.Char(string='Marque')
    model_name = fields.Char(string='Modèle')
    size = fields.Selection([
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
    ], string='Taille')
    color = fields.Char(string='Couleur')

    rental_price_hour = fields.Float(string='Prix location/heure')
    rental_price_day = fields.Float(string='Prix location/jour')
    rental_price_week = fields.Float(string='Prix location/semaine')

    is_available = fields.Boolean(string='Disponible', default=True)

    rental_ids = fields.One2many(
        'bike.shop.rental',
        'bike_id',
        string='Locations'
    )

    stock_status = fields.Selection([
        ('in_stock', 'En stock'),
        ('low_stock', 'Stock faible'),
        ('out_of_stock', 'Rupture de stock'),
    ], string='Statut du stock', compute='_compute_stock_status', store=True)

    @api.depends('qty_available')
    def _compute_stock_status(self):
        for record in self:
            if record.qty_available <= 0:
                record.stock_status = 'out_of_stock'
            elif record.qty_available <= 1:
                record.stock_status = 'low_stock'
            else:
                record.stock_status = 'in_stock'


# -------------------------------------------------------------------
#  LOCATION DE VÉLOS
# -------------------------------------------------------------------

class BikeRental(models.Model):
    _name = 'bike.shop.rental'
    _description = 'Location de vélo'
    _order = 'start_date desc'

    name = fields.Char(string='Référence', readonly=True)

    bike_id = fields.Many2one(
        'product.template',
        string='Vélo',
        required=True,
        domain="[('is_bike_shop_item','=',True), ('product_type','=','bike')]"
    )

    customer_id = fields.Many2one(
        'res.partner', string='Client', required=True
    )

    start_date = fields.Datetime(
        string='Date de début', 
        required=True, 
        default=fields.Datetime.now
    )
    end_date = fields.Datetime(
        string='Date de fin', 
        required=True
    )

    rental_duration = fields.Integer(
        string='Durée (jours)',
        compute='_compute_duration',
        store=True
    )

    rental_type = fields.Selection([
        ('hour', 'À l\'heure'),
        ('day', 'À la journée'),
        ('week', 'À la semaine'),
    ], string='Type de location', required=True, default='day')

    unit_price = fields.Float(string='Prix unitaire')
    total_price = fields.Float(string='Prix total', compute='_compute_total_price', store=True)

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('in_progress', 'En cours'),
        ('returned', 'Retourné'),
        ('cancelled', 'Annulée'),
    ], default='draft')

    notes = fields.Text(string='Notes')

    # -------------------------------------------------------------
    #  CALCUL DE LA DURÉE
    # -------------------------------------------------------------
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                duration = (rec.end_date - rec.start_date).days
                rec.rental_duration = duration if duration > 0 else 1
            else:
                rec.rental_duration = 0

    # -------------------------------------------------------------
    #  CALCUL DU MONTANT TOTAL
    # -------------------------------------------------------------
    @api.depends('rental_duration', 'unit_price', 'rental_type')
    def _compute_total_price(self):
        for rec in self:
            if rec.rental_type == 'hour':
                rec.total_price = rec.unit_price * (rec.rental_duration * 24)
            elif rec.rental_type == 'week':
                weeks = rec.rental_duration / 7
                rec.total_price = rec.unit_price * (weeks if weeks > 1 else 1)
            else:
                rec.total_price = rec.unit_price * rec.rental_duration

    # -------------------------------------------------------------
    #  ONCHANGE : mettre le bon tarif automatiquement
    # -------------------------------------------------------------
    @api.onchange('bike_id', 'rental_type')
    def _onchange_bike_rental_type(self):
        if self.bike_id:
            if self.rental_type == 'hour':
                self.unit_price = self.bike_id.rental_price_hour
            elif self.rental_type == 'day':
                self.unit_price = self.bike_id.rental_price_day
            elif self.rental_type == 'week':
                self.unit_price = self.bike_id.rental_price_week

    # -------------------------------------------------------------
    #  GÉNÉRATION AUTOMATIQUE DE LA RÉFÉRENCE
    # -------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        """Génère automatiquement la référence (name) pour chaque location."""
        for vals in vals_list:
            if vals.get('name', '/') in (False, '/', 'Nouvelle Location'):
                vals['name'] = self.env['ir.sequence'].next_by_code('bike.shop.rental') or '/'
        return super().create(vals_list)

    # === HELPER POUR LES LOCATIONS DE STOCK ===
    def _get_stock_locations(self):
        """Retourne (stock_location, customer_location, picking_type_out, picking_type_in)."""
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        if not warehouse:
            raise UserError("Aucun entrepôt trouvé pour gérer le stock des locations.")

        stock_location = warehouse.lot_stock_id  # emplacement stock interne
        customer_location = self.env.ref('stock.stock_location_customers')

        picking_type_out = warehouse.out_type_id     # livraison client
        picking_type_in = warehouse.in_type_id       # retour / réception

        return stock_location, customer_location, picking_type_out, picking_type_in


    def action_confirm(self):
        self.write({'state': 'confirmed'})

    # === ACTION DÉMARRER : SORTIE DU VÉLO DU STOCK ===
    def action_start(self):
        stock_location, customer_location, picking_type_out, _ = self._get_stock_locations()

        for rec in self:
            if rec.bike_id.qty_available <= 0:
                raise UserError(
                    f"Pas de stock disponible pour le vélo '{rec.bike_id.name}'."
                )

            product = rec.bike_id.product_variant_id

            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type_out.id,
                'location_id': stock_location.id,
                'location_dest_id': customer_location.id,
                'origin': rec.name,
            })

            move = self.env['stock.move'].create({
                'name': rec.name,
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'product_uom_qty': 1.0,
                'location_id': stock_location.id,
                'location_dest_id': customer_location.id,
                'picking_id': picking.id,
            })

            move._action_confirm()
            move._action_assign()
            move._action_done()

        self.write({'state': 'in_progress'})

    # === ACTION RETOUR : RETOUR DU VÉLO AU STOCK ===
    def action_return(self):
        stock_location, customer_location, _, picking_type_in = self._get_stock_locations()

        for rec in self:
            product = rec.bike_id.product_variant_id

            picking = self.env['stock.picking'].create({
                'picking_type_id': picking_type_in.id,
                'location_id': customer_location.id,
                'location_dest_id': stock_location.id,
                'origin': rec.name + " retour",
            })

            move = self.env['stock.move'].create({
                'name': rec.name + " retour",
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'product_uom_qty': 1.0,
                'location_id': customer_location.id,
                'location_dest_id': stock_location.id,
                'picking_id': picking.id,
            })

            move._action_confirm()
            move._action_assign()
            move._action_done()

        self.write({'state': 'returned'})


    # -------------------------------------------------------------
    #  FACTURATION AUTOMATIQUE
    # -------------------------------------------------------------
    def action_invoice(self):
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_line_ids': [(0, 0, {
                'name': f'Location {self.bike_id.name}',
                'quantity': 1,
                'price_unit': self.total_price,
                'product_id': self.bike_id.product_variant_id.id,
            })]
        })
        return invoice
    def action_invoice(self):
        """Créer la facture (même un stub vide pour l'instant)."""
        # pour l'instant tu peux juste mettre un placeholder :
        return True

    def action_cancel(self):
        """Annuler la location."""
        self.write({'state': 'cancelled'})
