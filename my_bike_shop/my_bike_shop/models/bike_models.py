from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
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

    # Nouveau : nombre de locations actives
    active_rental_count = fields.Integer(
        string='Locations actives',
        compute='_compute_active_rental_count'
    )

    # Nouveau : revenus total des locations
    total_rental_revenue = fields.Float(
        string='Revenus locations',
        compute='_compute_total_rental_revenue'
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

    @api.depends('rental_ids', 'rental_ids.state')
    def _compute_active_rental_count(self):
        """Calcule le nombre de locations en cours"""
        for record in self:
            record.active_rental_count = len(
                record.rental_ids.filtered(lambda r: r.state == 'in_progress')
            )

    @api.depends('rental_ids', 'rental_ids.total_price', 'rental_ids.state')
    def _compute_total_rental_revenue(self):
        """Calcule les revenus totaux des locations terminées"""
        for record in self:
            completed_rentals = record.rental_ids.filtered(
                lambda r: r.state == 'returned'
            )
            record.total_rental_revenue = sum(completed_rentals.mapped('total_price'))

    # Contraintes de validation
    @api.constrains('rental_price_hour', 'rental_price_day', 'rental_price_week')
    def _check_rental_prices(self):
        """Vérifie que les prix de location sont positifs"""
        for record in self:
            if record.product_type == 'bike':
                if record.rental_price_hour < 0 or record.rental_price_day < 0 or record.rental_price_week < 0:
                    raise ValidationError("Les prix de location doivent être positifs.")


# -------------------------------------------------------------------
#  LOCATION DE VÉLOS
# -------------------------------------------------------------------

class BikeRental(models.Model):
    _name = 'bike.shop.rental'
    _description = 'Location de vélo'
    _order = 'start_date desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Pour le suivi des activités

    name = fields.Char(string='Référence', readonly=True, tracking=True)

    bike_id = fields.Many2one(
        'product.template',
        string='Vélo',
        required=True,
        domain="[('is_bike_shop_item','=',True), ('product_type','=','bike')]",
        tracking=True
    )

    customer_id = fields.Many2one(
        'res.partner', 
        string='Client', 
        required=True,
        tracking=True
    )

    start_date = fields.Datetime(
        string='Date de début', 
        required=True, 
        default=fields.Datetime.now,
        tracking=True
    )
    end_date = fields.Datetime(
        string='Date de fin', 
        required=True,
        tracking=True
    )

    rental_duration = fields.Float(
        string='Durée',
        compute='_compute_duration',
        store=True
    )

    rental_duration_display = fields.Char(
        string='Durée formatée',
        compute='_compute_duration_display'
    )

    rental_type = fields.Selection([
        ('hour', 'À l\'heure'),
        ('day', 'À la journée'),
        ('week', 'À la semaine'),
    ], string='Type de location', required=True, default='day', tracking=True)

    unit_price = fields.Float(string='Prix unitaire', tracking=True)
    total_price = fields.Float(
        string='Prix total', 
        compute='_compute_total_price', 
        store=True,
        tracking=True
    )

    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirmed', 'Confirmée'),
        ('in_progress', 'En cours'),
        ('returned', 'Retourné'),
        ('cancelled', 'Annulée'),
    ], default='draft', tracking=True)

    notes = fields.Text(string='Notes')

    # Nouveau : référence à la facture créée
    invoice_id = fields.Many2one('account.move', string='Facture', readonly=True)
    invoice_state = fields.Selection(related='invoice_id.state', string='État facture')

    # Nouveau : champ pour les pénalités de retard
    late_fee = fields.Float(string='Frais de retard', default=0.0)
    is_late = fields.Boolean(string='En retard', compute='_compute_is_late', store=True)

    # -------------------------------------------------------------
    #  CALCUL DE LA DURÉE (CORRIGÉ)
    # -------------------------------------------------------------
    @api.depends('start_date', 'end_date')
    def _compute_duration(self):
        for rec in self:
            if rec.start_date and rec.end_date:
                delta = rec.end_date - rec.start_date
                
                if rec.rental_type == 'hour':
                    # Durée en heures (avec décimales)
                    rec.rental_duration = delta.total_seconds() / 3600
                elif rec.rental_type == 'week':
                    # Durée en semaines
                    rec.rental_duration = delta.days / 7
                else:  # day
                    # Durée en jours
                    rec.rental_duration = delta.days if delta.days > 0 else 1
            else:
                rec.rental_duration = 0

    @api.depends('rental_duration', 'rental_type')
    def _compute_duration_display(self):
        """Affichage formaté de la durée"""
        for rec in self:
            if rec.rental_type == 'hour':
                rec.rental_duration_display = f"{rec.rental_duration:.1f} heure(s)"
            elif rec.rental_type == 'week':
                rec.rental_duration_display = f"{rec.rental_duration:.2f} semaine(s)"
            else:
                rec.rental_duration_display = f"{int(rec.rental_duration)} jour(s)"

    # -------------------------------------------------------------
    #  CALCUL DU MONTANT TOTAL (CORRIGÉ)
    # -------------------------------------------------------------
    @api.depends('rental_duration', 'unit_price', 'rental_type', 'late_fee')
    def _compute_total_price(self):
        for rec in self:
            base_price = 0
            
            if rec.rental_type == 'hour':
                # Prix par heure × nombre d'heures
                base_price = rec.unit_price * rec.rental_duration
            elif rec.rental_type == 'week':
                # Prix par semaine × nombre de semaines
                weeks = max(rec.rental_duration, 1)
                base_price = rec.unit_price * weeks
            else:  # day
                # Prix par jour × nombre de jours
                days = max(rec.rental_duration, 1)
                base_price = rec.unit_price * days
            
            rec.total_price = base_price + rec.late_fee

    @api.depends('end_date', 'state')
    def _compute_is_late(self):
        """Vérifie si la location est en retard"""
        now = fields.Datetime.now()
        for rec in self:
            rec.is_late = (
                rec.state == 'in_progress' and 
                rec.end_date and 
                rec.end_date < now
            )
   

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
    #  CONTRAINTES DE VALIDATION
    # -------------------------------------------------------------
    @api.constrains('start_date', 'end_date')
    def _check_dates(self):
        """Vérifie que la date de fin est après la date de début"""
        for rec in self:
            if rec.start_date and rec.end_date and rec.end_date <= rec.start_date:
                raise ValidationError(
                    "La date de fin doit être postérieure à la date de début."
                )

    
    @api.constrains('bike_id', 'start_date', 'end_date', 'state')
    def _check_bike_availability(self):
        """Vérifie qu'il y a assez de stock pour la période"""
        for rec in self:
            if rec.state in ['cancelled', 'returned']:
                continue
            
            # Compter les locations actives sur cette période pour ce vélo
            overlapping_count = self.env['bike.shop.rental'].search_count([
                ('bike_id', '=', rec.bike_id.id),
                ('id', '!=', rec.id),
                ('state', 'in', ['confirmed', 'in_progress']),
                ('start_date', '<', rec.end_date),
                ('end_date', '>', rec.start_date),
            ])
            
            # Vérifier qu'il reste du stock
            available_qty = rec.bike_id.qty_available
            
            if overlapping_count >= available_qty:
                raise ValidationError(
                    f"Plus de stock disponible pour '{rec.bike_id.name}' sur cette période. "
                    f"Stock total : {rec.bike_id.qty_available}, "
                    f"Locations actives : {overlapping_count}"
                )
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

    # -------------------------------------------------------------
    #  ACTIONS DE WORKFLOW
    # -------------------------------------------------------------
    def action_confirm(self):
        """Confirme la location"""
        for rec in self:
            if rec.state != 'draft':
                raise UserError("Seules les locations en brouillon peuvent être confirmées.")
        
        self.write({'state': 'confirmed'})
        
        # Notification par email (optionnel)
        for rec in self:
            rec.message_post(
                body=f"Location confirmée pour {rec.bike_id.name}",
                subject="Confirmation de location"
            )

    def action_start(self):
        """Démarre la location et sort le vélo du stock"""
        for rec in self:
            if rec.state != 'confirmed':
                raise UserError("Seules les locations confirmées peuvent être démarrées.")
            
            product = rec.bike_id.product_variant_id
            
            # Vérifier le stock
            if product.qty_available <= 0:
                raise UserError(f"Pas de stock disponible pour {rec.bike_id.name}")
            
            # Emplacements
            stock_location = self.env.ref('stock.stock_location_stock')
            customer_location = self.env.ref('stock.stock_location_customers')
            
            # Créer le mouvement de stock
            move = self.env['stock.move'].create({
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'product_uom_qty': 1.0,
                'location_id': stock_location.id,
                'location_dest_id': customer_location.id,
            })
            
            # Confirmer et valider le mouvement
            move._action_confirm()
            move._action_assign()
            move.quantity = 1.0  # ← Utiliser 'quantity' au lieu de 'quantity_done'
            move._action_done()
            
            rec.state = 'in_progress'
        
        return True


    def action_return(self):
        """Retourne le vélo au stock"""
        for rec in self:
            if rec.state != 'in_progress':
                raise UserError("Seules les locations en cours peuvent être retournées.")
            
            product = rec.bike_id.product_variant_id
            
            # Calculer les frais de retard
            if rec.is_late and rec.late_fee == 0:
                days_late = (fields.Datetime.now() - rec.end_date).days
                rec.late_fee = days_late * 10.0
            
            # Emplacements
            stock_location = self.env.ref('stock.stock_location_stock')
            customer_location = self.env.ref('stock.stock_location_customers')
            
            # Créer le mouvement de retour
            move = self.env['stock.move'].create({
                'product_id': product.id,
                'product_uom': product.uom_id.id,
                'product_uom_qty': 1.0,
                'location_id': customer_location.id,
                'location_dest_id': stock_location.id,
            })
            
            # Confirmer et valider
            move._action_confirm()
            move._action_assign()
            move.quantity = 1.0  # ← Utiliser 'quantity'
            move._action_done()
            
            rec.state = 'returned'
            rec.actual_return_date = fields.Datetime.now()
        
        return True
    # -------------------------------------------------------------
    #  FACTURATION AUTOMATIQUE (CORRIGÉ - PLUS DE DOUBLON)
    # -------------------------------------------------------------
    def action_invoice(self):
        """Créer une facture pour la location"""
        self.ensure_one()
        
        if self.state not in ['returned', 'in_progress']:
            raise UserError("Vous ne pouvez facturer qu'une location retournée ou en cours.")
        
        if self.invoice_id:
            raise UserError("Cette location a déjà été facturée.")

        # Création de la facture
        invoice_lines = [(0, 0, {
            'name': f'Location {self.bike_id.name} - {self.rental_duration_display}',
            'quantity': 1,
            'price_unit': self.total_price,
            'product_id': self.bike_id.product_variant_id.id,
        })]

        # Ajouter une ligne pour les frais de retard si applicable
        if self.late_fee > 0:
            invoice_lines.append((0, 0, {
                'name': 'Frais de retard',
                'quantity': 1,
                'price_unit': self.late_fee,
            }))

        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.customer_id.id,
            'invoice_date': fields.Date.today(),
            'invoice_line_ids': invoice_lines,
        })

        self.invoice_id = invoice.id

        # Ouvrir la facture créée
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facture',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'view_mode': 'form',
            'target': 'current',
        }

    def action_cancel(self):
        """Annuler la location"""
        for rec in self:
            if rec.state in ['in_progress', 'returned']:
                raise UserError("Impossible d'annuler une location déjà démarrée ou retournée.")
        
        self.write({'state': 'cancelled'})

    def action_view_invoice(self):
        """Ouvrir la facture associée"""
        self.ensure_one()
        if not self.invoice_id:
            raise UserError("Aucune facture n'a été créée pour cette location.")
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Facture',
            'res_model': 'account.move',
            'res_id': self.invoice_id.id,
            'view_mode': 'form',
            'target': 'current',
        }