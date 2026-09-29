# LoyaltyCore - B2B2C Multi-Tenant Loyalty Platform

### 📸 System Interfaces & Demos
- [Ver captura del POS Terminal](https://github.com/Mirko-Lauc/LoyaltyCore/blob/main/assets/caja.png)
- [Ver captura del Manager Dashboard](https://github.com/Mirko-Lauc/LoyaltyCore/blob/main/assets/dashboard.png)
- [Ver captura del VIP Client Portal](https://github.com/Mirko-Lauc/LoyaltyCore/blob/main/assets/cliente.png)

---

🇬🇧 English

LoyaltyCore is a high-retention B2B2C SaaS platform designed for independent businesses (barbershops, cafes, retail). 

Built to provide single-tenant isolation for multi-brand management, it features QR-based point accumulation at the POS, installable PWA VIP cards for clients, real-time auditing, and automated CRM rescue campaigns. It completely bridges the gap between customer retention and seamless daily operations.

### Key Features
- **Multi-Tenant Isolation:** Strict separation of data, balances, and reward catalogs per business.
- **QR POS Terminal:** Optical scanning using mobile or web cameras without needing extra hardware.
- **Anti-Fraud Security:** 4-digit PIN authentication for cashiers with mandatory transaction logs.
- **Client VIP Card (PWA):** Frictionless portal with email/password login, personal QR generation, and real-time balance tracking.
- **Manager Dashboard:** Immutable transaction tracking per employee to prevent internal fraud and dynamic reward catalog management.
- **Automated CRM Rescue:** Detects inactive clients (>14 days) and triggers automated email loyalty campaigns.
- **Dockerized Execution:** Fully containerized with Docker Compose for instant, reliable deployment across any environment.

### Tech Stack
- **Backend:** Python 3.12+, FastAPI, SQLAlchemy (Async), asyncpg, Pydantic
- **Database:** PostgreSQL (Hosted on Neon)
- **Frontend:** HTML5, Tailwind CSS, Vanilla JS, PWA (Service Workers)
- **Infrastructure:** Docker & Docker Compose

### About the Author
Developed by **Mirko Gastón Lauc** — Backend Developer specializing in Python, FastAPI, and robust database design. Passionate about building scalable, production-ready web applications that solve real-world operational challenges.

---

🇪🇸 Español

LoyaltyCore es una plataforma SaaS B2B2C de alta fidelización diseñada para comercios independientes (peluquerías, cafeterías, tiendas de retail). 

Creada para ofrecer gestión aislada por comercio (Multi-Tenant), cuenta con acumulación de puntos vía QR en el mostrador, tarjetas VIP instalables (PWA) para clientes, auditoría en tiempo real y campañas CRM automatizadas. Cierra por completo la brecha entre la retención de clientes y las operaciones diarias sin fricción.

### Características Principales
- **Aislamiento Multi-Tenant:** Separación estricta de datos, saldos y catálogos de premios por cada comercio.
- **Terminal POS con Lector QR:** Escaneo óptico desde la cámara móvil o web sin hardware adicional.
- **Seguridad Antifraude:** Autenticación por PIN de 4 dígitos para cajeros con registro obligatorio de transacciones.
- **Tarjeta VIP del Cliente (PWA):** Portal instalable con login, generación de código QR personal y seguimiento de saldo en vivo.
- **Panel Gerencial:** Seguimiento inmutable de operaciones por empleado para prevenir fraudes internos y gestión dinámica de premios.
- **Rescate CRM Automático:** Detecta clientes inactivos (>14 días) y dispara campañas de fidelización automáticas por correo.
- **Ejecución con Docker:** Completamente containerizado con Docker Compose para un despliegue instantáneo en cualquier entorno.

### Tecnologías Utilizadas
- **Backend:** Python 3.12+, FastAPI, SQLAlchemy (Async), asyncpg, Pydantic
- **Base de Datos:** PostgreSQL (Alojado en Neon)
- **Frontend:** HTML5, Tailwind CSS, Vanilla JS, PWA (Service Workers)
- **Infraestructura:** Docker & Docker Compose

### Sobre el Autor
Desarrollado por **Mirko Gastón Lauc** — Desarrollador Backend especializado en Python, FastAPI y diseño robusto de bases de datos. Apasionado por construir aplicaciones web escalables y listas para producción que resuelven desafíos operativos del mundo real.
