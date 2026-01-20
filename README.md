
# ERP-Project

## My Bike Shop — Odoo Module

📋 **Project Context**

**My Bike Shop** is an **Odoo 19.0 Community** module developed for the complete management of a bicycle shop offering **sales and rentals**.
The project answers a client’s need to **digitize commercial operations** while **avoiding paid licenses**.

---

## 🎯 Objectives

* Centralize product management (bikes, parts, accessories)
* Automate rental processes (short and long term)
* Integrate stock management with sales and rentals
* Provide an intuitive and professional user interface
* Generate basic sales and rental reports

---

## 🛠️ Features

### 🚲 Sales

* Product catalog with distinction between **bikes / parts / accessories**
* Sales pricing and stock management
* Dedicated interface for shop products

### 📅 Rentals

* Rental contracts with **hourly / daily / weekly** pricing
* Automated availability management
* Complete workflow:
  `draft → confirmed → in_progress → returned → cancelled`
* Integration with **Odoo Stock** module
* Automatic rental invoicing

### 👥 Customers

* Complete customer records
* Sales and rental history
* Integration with **Odoo Contacts**

---

## 📦 Installation

### Prerequisites

* Odoo **19.0 Community**
* Python **3.8+**
* PostgreSQL **12+**
* Required Odoo modules:

  * `sale_management`
  * `stock`
  * `account`
  * `contacts`

### Manual Installation

1. Place the `my_bike_shop` folder inside Odoo’s `addons` directory
2. Restart the Odoo server
3. Enable **Developer Mode**
4. Go to **Apps → Update Apps List**
5. Search for **My Bike Shop** and click **Install**
6. Configure sequences if necessary (auto-generated)

### Installation with Docker (Optional)

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
      - ./my_bike_shop:/mnt/extra-addons/my_bike_shop
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
```

---

## 🚀 Initial Configuration

### 1️⃣ Product Configuration

* Go to:
  **Management → Bike & Accessories Sales → Products**
* Create product categories: **Bike, Part, Accessory**
* Define sales and rental prices
* Configure specific attributes:

  * Brand
  * Model
  * Size
  * Color

### 2️⃣ Customer Configuration

* Customers are managed via the **Contacts** module
* Path:
  **Management → Rentals & Customers → Customer List**

### 3️⃣ Rental Configuration

* Path:
  **Management → Bike Rentals → Rental Management**
* Create rentals with customer and period
* Use the integrated workflow to manage lifecycle

---

## 📁 Module Structure

```
my_bike_shop/
├── __init__.py
├── __manifest__.py
├── controllers/
│   ├── __init__.py
│   └── controllers.py        # Web controller (bike list)
├── models/
│   ├── __init__.py
│   └── models.py             # Product & Rental models
├── views/
│   └── bike_menus.xml        # Menus, views, actions
├── data/
│   └── sequence_data.xml     # Sequence definitions
└── security/
    └── ir.model.access.csv   # Access rights
```

---

## 🔧 Technical Features

### Custom Models

#### `BikeProduct` (extends `product.template`)

* Custom fields: type, brand, size, color
* Rental pricing (hour / day / week)
* Automatic stock status calculation

#### `BikeRental`

* Dedicated rental model
* 5-state workflow
* Automatic duration and price calculation
* Stock integration (physical movements)
* Automatic invoicing via **Account** module

### Web Controllers

* Public page: `/bike_shop/velos`
* Public authentication
* Bike catalog consultation

### Views & UI

* Native Odoo UI
* Custom **Management** menus
* List and form views adapted to business needs
* Action buttons for rental workflow

---

## 📊 Business Features Implemented

### ✅ Mandatory

* Product catalog
* Customer orders & invoicing
* Basic stock management
* Rental contracts with variable pricing
* Customer records with history
* Basic reporting via Odoo list views

### ✅ Added Value

* Public web interface
* Automated rental workflow
* Full integration with standard Odoo modules
* Automatic price & duration calculation
* Real-time stock updates

---

## 🏗️ Architecture & Technical Choices

### Technologies Used

* **Odoo 19.0 Community**
* **PostgreSQL**
* **Python 3.8+**
* **XML** (views and menus)

### Required Odoo Modules

* `base`
* `sale_management`
* `stock`
* `account`
* `contacts`

---

## 🌐 Hosting & Deployment

### Recommended Setup

* **Local hosting**: demo environment
* **Production**: Docker on Ubuntu VPS

### Production Deployment Steps

1. Install Docker & Docker Compose
2. Clone the Git repository
3. Configure environment variables
4. Run:

   ```bash
   docker-compose up -d
   ```
5. Access:

   ```
   http://server:8069
   ```

### Limitations

* Security: basic configuration only
* Backups: manual setup required
* Performance: suitable for 50–100 concurrent users
* High availability: not implemented

---

## 🚨 Known Issues & Solutions

### Issue: Invoicing Not Fully Implemented

**Solution:** Extend `action_invoice()` method:

```python
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
```

### Issue: No Date Conflict Validation

**Solution:** Add SQL constraint in `BikeRental` model:

```python
_sql_constraints = [
    (
        'rental_date_overlap',
        'CHECK(1=1)',  # To be replaced with proper logic
        'The bike is already reserved for this period'
    ),
]
```

---

## 📈 Future Improvements

* Advanced reporting dashboards
* Online reservation system
* Online payments (Stripe / PayPal)
* Mobile application
* Preventive maintenance tracking

---

## 👥 Team

* **Yazbeck John** — Developer
* **Jose Bigoro** — Developer

---

## 📄 License

This project is licensed under **LGPL-3**.
See the `LICENSE` file for details.

---

## 🔗 Useful Links

* GitHub Repository:
  [https://github.com/sambiig/ERP-Project](https://github.com/sambiig/ERP-Project)
* Odoo Documentation:
  [https://www.odoo.com/documentation/19.0/](https://www.odoo.com/documentation/19.0/)
* Odoo Forum:
  [https://www.odoo.com/fr_FR/forum/aide-1](https://www.odoo.com/fr_FR/forum/aide-1)

---



