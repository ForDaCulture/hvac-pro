# HVAC Pro - Business Automation System 🛠️

HVAC Pro is a comprehensive, web-based automation system designed to streamline the daily operations of a small to medium-sized HVAC (Heating, Ventilation, and Air Conditioning) business. It centralizes scheduling, customer management, invoicing, and business analytics into a single, easy-to-use platform.

---

### 😫 The Pain Point We're Addressing

Small field service businesses, like HVAC companies, often struggle with operational chaos. Key challenges include:
* **Manual Scheduling:** Using spreadsheets or paper calendars is inefficient and prone to errors like double-bookings.
* **Lost Customer History:** Critical customer information, service history, and preferences are scattered across different systems (or people's memories), leading to inconsistent service.
* **Reactive, Not Proactive:** Without automated reminders, businesses miss opportunities for preventative maintenance, losing out on recurring revenue and customer loyalty.
* **No Business Insight:** It's difficult to answer key questions like "Who are my most valuable customers?" or "What was my revenue last month?" without tedious manual data analysis.

---

### 🎯 The Goal

HVAC Pro solves these problems by providing a single source of truth that **automates manual tasks**, **improves customer retention**, and **provides data-driven insights** to help the business grow.

---

### ✨ Key Features

* **Smart Scheduling:** An intelligent system that finds the optimal time slots for new jobs based on technician availability, skills, and customer preferences.
* **Customer Relationship Management (CRM):** A centralized database of all customers, including their contact information, service history, and notes.
* **Automated Follow-ups:** A background worker system that automatically sends customer satisfaction surveys and preventative maintenance reminders via SMS and Email.
* **Data-Driven Reporting:** An analytics dashboard that visualizes key business metrics like monthly revenue, job volume, and service type breakdowns.
* **Secure Authentication:** A complete user login and registration system to protect sensitive business data.
* **PDF Invoice Generation:** On-demand creation of professional PDF invoices for completed jobs.

---

### 🚀 Project Roadmap

This roadmap outlines the path from idea to a fully completed project.

* **Phase 1: Foundation & Core Logic** ✅
    * ✅ Project Scaffolding
    * ✅ Database Modeling
    * ✅ Core Backend Services
    * ✅ API Endpoints

* **Phase 2: UI Integration & Feature Activation** ✅
    * ✅ Connect UI to APIs
    * ✅ Implement Job Workflow UI
    * ✅ Build Invoice Interface
    * ✅ Enhance Reports with Interactive Charts

* **Phase 3: Production Hardening** ✅
    * ✅ Implement Authentication & Authorization
    * ✅ Secure Endpoints
    * ✅ Write Unit & Integration Tests
    * ✅ Configure Application Logging

* **Phase 4: Deployment** 🎯
    * 🎯 Connect UI API Hooks to Backend
    * 🎯 Deploy to a Cloud Host (e.g., Heroku)
    * 🎯 Final End-to-End Review

---

### 🛠️ Setup & Installation

To run this project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ForDaCulture/hvac-pro.git](https://github.com/ForDaCulture/hvac-pro.git)
    cd hvac-pro
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up your environment variables:**
    * Copy the `.env.example` file to a new file named `.env`.
    * Fill in the values in the `.env` file, especially the `SECRET_KEY`.

5.  **Initialize and migrate the database (if using PostgreSQL):**
    ```bash
    # This step is for the production setup
    flask db upgrade
    ```

6.  **Run the application:**
    ```bash
    python run.py
    ```
The application will be available at `http://127.0.0.1:5000`.