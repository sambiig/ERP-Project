# -*- coding: utf-8 -*-
{
    'name': "My Bike Shop",
    'summary': """
        Module de gestion complète pour un magasin de vélos
        Vente, location, gestion du stock et reporting
    """,
    'description': """
        Bike Shop Management System
        ============================
        
        Module complet pour gérer un magasin de vélos offrant :
        
        * **Vente de vélos et accessoires**
            - Catalogue produits (vélos, pièces détachées, accessoires)
            - Gestion des marques, modèles, tailles et couleurs
            - Prix de vente et tarifs de location
        
        * **Location de vélos**
            - Contrats de location (heure, jour, semaine)
            - Gestion des disponibilités et réservations
            - Calcul automatique des prix
            - Gestion du stock en temps réel
            - Frais de retard automatiques
        
        * **Gestion clients**
            - Fiches clients complètes
            - Historique des ventes et locations
        
        * **Reporting et statistiques**
            - Dashboard des locations
            - Graphiques et analyses
            - Vélos les plus loués
            - Revenus par période
        
        * **Fonctionnalités avancées**
            - Facturation automatique
            - Mouvements de stock automatiques
            - Notifications et suivi (chatter)
            - Vue calendrier des locations
            - Détection des locations en retard
    """,
    'author': "Yazbeck John et Jose Bigoro",
    'website': "https://github.com/sambiig/ERP-Project",
    'category': 'Sales',
    'version': '1.0.0',
    
    # Dépendances
    'depends': [
        'base',
        'mail',                # Pour le chatter et les notifications
        'sale_management',     # Pour la gestion des ventes
        'stock',              # Pour la gestion du stock
        'account',            # Pour la facturation
        'contacts',           # Pour les clients
    ],
    
    # Fichiers de données
    'data': [
        # Sécurité
        'security/ir.model.access.csv',
        
        # Séquences
        'data/sequence_data.xml',
        
        #pour les donné du demo
        'data/demo_data.xml', 
        
        # Vues
        'views/bike_menus.xml',
    ],
    
  
    
    
    # Installation
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # Licence
    'license': 'LGPL-3',
    
    # Images
    'images': ['static/description/icon.png'],
    
    # Prix (si module payant)
    # 'price': 0.00,
    # 'currency': 'EUR',
}