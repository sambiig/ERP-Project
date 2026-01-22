# 🚴 My Bike Shop — ERP Project (Odoo 19)

> **Module Odoo 19.0 Community** pour la gestion complète d’un magasin de vélos : **vente, location, stock et facturation**.

[![Odoo Version](https://img.shields.io/badge/Odoo-19.0-blue.svg)](https://www.odoo.com)
[![License](https://img.shields.io/badge/License-LGPL--3-green.svg)](https://www.gnu.org/licenses/lgpl-3.0.en.html)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

---

## 📋 Table des matières

- [🚴 My Bike Shop — ERP Project (Odoo 19)](#-my-bike-shop--erp-project-odoo-19)
  - [📋 Table des matières](#-table-des-matières)
  - [📋 Contexte du projet](#-contexte-du-projet)
  - [🎯 Objectifs](#-objectifs)
  - [✨ Fonctionnalités](#-fonctionnalités)
    - [🏪 Gestion des produits](#-gestion-des-produits)
    - [🚴 Système de location](#-système-de-location)
    - [🛒 Ventes](#-ventes)
    - [📊 Reporting](#-reporting)
    - [🌐 Interface web publique](#-interface-web-publique)
  - [🔧 Prérequis](#-prérequis)
    - [Logiciels](#logiciels)
    - [Modules Odoo requis](#modules-odoo-requis)
  - [📥 Installation](#-installation)
    - [1️⃣ Cloner le dépôt](#1️⃣-cloner-le-dépôt)
    - [2️⃣ Placer le module](#2️⃣-placer-le-module)
    - [3️⃣ Redémarrer Odoo](#3️⃣-redémarrer-odoo)
    - [4️⃣ Installer le module](#4️⃣-installer-le-module)
    - [🐳 Installation via Docker (optionnel)](#-installation-via-docker-optionnel)
  - [⚙️ Configuration initiale](#️-configuration-initiale)
    - [Produits](#produits)
    - [Clients](#clients)
    - [Locations](#locations)
  - [🚀 Utilisation](#-utilisation)
    - [Créer une location](#créer-une-location)
    - [Consulter les statistiques](#consulter-les-statistiques)
  - [📁 Structure du module](#-structure-du-module)
  - [🔧 Aspects techniques](#-aspects-techniques)
    - [Modèles principaux](#modèles-principaux)
    - [Séquences](#séquences)
  - [🔐 Sécurité](#-sécurité)
  - [🧪 Tests](#-tests)
  - [🚨 Limitations \& problèmes connus](#-limitations--problèmes-connus)
  - [📈 Améliorations futures](#-améliorations-futures)
  - [👥 Équipe](#-équipe)
  - [📄 Licence](#-licence)
  - [🔗 Liens utiles](#-liens-utiles)

---

## 📋 Contexte du projet

**My Bike Shop** est un module **Odoo 19.0 Community** développé dans le cadre d’un **projet ERP académique**.

L’objectif est de fournir une solution **100 % open-source** permettant à un magasin de vélos de :

* gérer ses **ventes**
* organiser la **location de vélos**
* suivre les **stocks en temps réel**
* automatiser la **facturation**

Tout cela **sans dépendre de licences payantes**.

---

## 🎯 Objectifs

* Centraliser la gestion des produits (vélos, pièces, accessoires)
* Automatiser les processus de location (court et long terme)
* Intégrer ventes, locations et stock
* Proposer une interface claire et professionnelle
* Fournir des statistiques et rapports de base

---

## ✨ Fonctionnalités

### 🏪 Gestion des produits

* Catalogue complet : **vélos, accessoires, pièces détachées**
* Attributs personnalisés : marque, modèle, taille, couleur
* Prix de vente et tarifs de location (heure / jour / semaine)
* Suivi automatique du stock
* Alertes de stock faible

### 🚴 Système de location

* Workflow complet :
  `Brouillon → Confirmée → En cours → Retournée → Annulée`
* Calcul automatique : durée, prix total, frais éventuels
* Gestion automatique du stock (sortie / retour)
* Historique des locations par client et par vélo
* Génération de facture en un clic

### 🛒 Ventes

* Intégration avec le module **Sales** d’Odoo
* Gestion des commandes clients
* Facturation automatique

### 📊 Reporting

* Vues Kanban, Liste et Calendrier
* Tableaux croisés et graphiques
* Suivi des revenus par période
* Vélos les plus loués

### 🌐 Interface web publique

* Page publique : `/bike_shop/velos`
* Consultation du catalogue de vélos

---

## 🔧 Prérequis

### Logiciels

* **Odoo 19.0 Community**
* **Python 3.8+**
* **PostgreSQL 12+**
* **Git**

### Modules Odoo requis

* `base`
* `product`
* `sale_management`
* `stock`
* `account`
* `contacts`
* `mail`

---

## 📥 Installation

### 1️⃣ Cloner le dépôt

```bash
git clone https://github.com/sambiig/ERP-Project
```

### 2️⃣ Placer le module

Copier le dossier `my_bike_shop` dans le dossier `addons` d’Odoo.

### 3️⃣ Redémarrer Odoo

```bash
./odoo-bin -c odoo.conf
```

### 4️⃣ Installer le module

* Activer le **mode développeur**
* Apps → Mettre à jour la liste
* Rechercher **My Bike Shop**
* Cliquer sur **Installer**

### 🐳 Installation via Docker (optionnel)

```yaml
version: '3.1'
services:
  odoo:
    image: odoo:19.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    volumes:
      - ./addons:/mnt/extra-addons
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
```

---

## ⚙️ Configuration initiale

### Produits

* Menu → Gestion → Produits
* Créer les catégories : **Bike, Part, Accessory**
* Définir prix de vente et tarifs de location

### Clients

* Gérés via le module **Contacts**
* Historique automatique ventes & locations

### Locations

* Menu → Gestion → Location de vélos
* Sélection du client, du vélo et des dates
* Le prix est calculé automatiquement

---

## 🚀 Utilisation

### Créer une location

1. Gestion → Location de vélos → Créer
2. Sélectionner vélo et client
3. Définir période et type
4. Confirmer → Démarrer → Retour → Facturer

### Consulter les statistiques

```
Gestion → Reporting → Dashboard Locations
```

---

## 📁 Structure du module

```
my_bike_shop/
├── __init__.py
├── __manifest__.py
├── controllers/
│   └── controllers.py
├── models/
│   └── models.py
├── views/
│   └── bike_menus.xml
├── data/
│   ├── sequence_data.xml
│   └── demo_data.xml
├── security/
│   └── ir.model.access.csv
└── static/
    └── description/
        └── icon.png
```

---

## 🔧 Aspects techniques

### Modèles principaux

* **BikeProduct** (hérite de `product.template`)
* **BikeRental** :

  * Workflow à 5 états
  * Calcul automatique durée & prix
  * Intégration stock et facturation

### Séquences

* Numérotation automatique : `LOC/00001`

---

## 🔐 Sécurité

* Groupes : Utilisateur / Vendeur / Manager
* Droits différenciés (CRUD)
* Validations :

  * Date fin > date début
  * Stock suffisant
  * Prix positifs
  * Pas de double réservation

---

## 🧪 Tests

Checklist :

* Création produit
* Définition du stock
* Création client
* Cycle complet de location
* Vérification du stock
* Génération facture

---

## 🚨 Limitations & problèmes connus

* Facturation avancée perfectible
* Pas de paiement en ligne
* Pas de haute disponibilité
* Sauvegardes à configurer manuellement

---

## 📈 Améliorations futures

* Paiement en ligne (Stripe / PayPal)
* Réservation en ligne
* Dashboard avancé
* Application mobile
* Suivi de maintenance des vélos

---

## 👥 Équipe

* **Yazbeck John** — Développeur
* **Jose Bigoro** — Développeur

Projet académique — 2025

---

## 📄 Licence

Ce projet est sous licence **LGPL-3**.

---

## 🔗 Liens utiles

* GitHub : [https://github.com/sambiig/ERP-Project](https://github.com/sambiig/ERP-Project)
* Documentation Odoo : [https://www.odoo.com/documentation/19.0/](https://www.odoo.com/documentation/19.0/)
* Forum Odoo : [https://www.odoo.com/forum](https://www.odoo.com/forum)

---

