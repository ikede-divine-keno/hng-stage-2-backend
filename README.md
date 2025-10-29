# hng-stage-2-backend Country Currency & Exchange API

GitHub repo for HNG Stage 2 backend track

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115.2-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)
![Railway](https://img.shields.io/badge/Deployed-Railway-blueviolet.svg)

## Country Currency & Exchange API

A production-grade RESTful API built with **FastAPI** that:

- Fetches country data from `https://restcountries.com`
- Fetches exchange rates from `https://open.er-api.com`
- Computes `estimated_gdp = population × random(1000–2000) ÷ exchange_rate`
- Caches everything in **MySQL**
- Supports **CRUD**, **filters**, **sorting**, **image generation**, and **robust error handling**

Fully persistent — data survives restarts  
Case-insensitive name matching  
Exact 400/404/503 JSON formats

---

## Features

| Feature | Endpoint | Description |
|---------|----------|-------------|
| **Refresh Cache** | `POST /countries/refresh` | Fetch + store all countries + rates |
| **List Countries** | `GET /countries` | Filter by `region`, `currency`, sort by `gdp_desc` |
| **Get One Country** | `GET /countries/{name}` | Case-insensitive |
| **Delete Country** | `DELETE /countries/{name}` | Case-insensitive |
| **Status** | `GET /status` | Total + last refresh timestamp |
| **Summary Image** | `GET /countries/image` | PNG with top 5 GDP + total |
| **Interactive Docs** | `/docs`, `/redoc` | Swagger + ReDoc |
| **CORS** | `*` | Enabled for cross-origin access |
| **Error Handling** | 400, 404, 503 | Exact JSON format |

---

## Project Structure

```
country-exchange-api/
├── main.py              # FastAPI app, routes, background tasks
├── database.py          # Async SQLAlchemy + MySQL setup
├── models/
│   └── country.py       # SQLAlchemy Country model
├── schemas/
│   └── country.py       # Pydantic models (input/output)
├── crud/
│   └── country.py       # Upsert logic + GDP calculation
├── services/
│   ├── fetch.py         # External API calls
│   └── image.py         # Matplotlib + PIL image generation
├── utils/
│   └── errors.py        # 404 JSON helper
├── cache/
│   └── summary.png      # Generated image
├── .env                 # DB + API config
├── requirements.txt     # Dependencies
└── README.md            # This file
```

---

## Prerequisites

- Python 3.12
- MySQL 8.0+
- Git
- Virtual Environment (`venv`)
- Railway account (optional)

---

## Setup Instructions

### 1. Fork and Clone the Repository

```bash
git clone https://github.com/your-username/country-exchange-api.git
cd country-exchange-api
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

* **Windows**: `venv\Scripts\activate`  
* **Mac/Linux**: `source venv/bin/activate`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create `.env` File

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=root
DB_PASS=your_password
DB_NAME=countries_db
ALLOWED_ORIGINS=*
COUNTRIES_API=https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies
EXCHANGE_API=https://open.er-api.com/v6/latest/USD
```

> Replace `your_password` with your MySQL root password.

### 5. Start MySQL

```bash
# Using Docker (recommended)
docker run -d --name mysql-db \
  -e MYSQL_ROOT_PASSWORD=your_password \
  -e MYSQL_DATABASE=countries_db \
  -p 3306:3306 \
  mysql:8.0
```

---

## Running Locally

```bash
uvicorn main:app --reload --port 8000
```

* **URL**: http://127.0.0.1:8000  
* **Swagger UI**: http://127.0.0.1:8000/docs  
* **ReDoc**: http://127.0.0.1:8000/redoc

> **First run**: Call `POST /countries/refresh` to populate the database

---

## API Usage

### 1. Refresh Data

```bash
curl -X POST http://127.0.0.1:8000/countries/refresh
```

### 2. Get All Countries

```bash
curl http://127.0.0.1:8000/countries
```

### 3. Filter + Sort

```bash
curl "http://127.0.0.1:8000/countries?region=Africa&sort=gdp_desc"
```

### 4. Get One Country

```bash
curl http://127.0.0.1:8000/countries/nigeria
```

### 5. Delete Country

```bash
curl -X DELETE http://127.0.0.1:8000/countries/Nigeria
```

### 6. Status

```bash
curl http://127.0.0.1:8000/status
```

### 7. Download Image

```bash
curl http://127.0.0.1:8000/countries/image --output summary.png
```

---

## Deployment on Railway

### Prerequisites

* Push to GitHub
* Railway account

### Steps

#### 1. Push to GitHub

```bash
git add .
git commit -m "Deploy to Railway"
git push origin main
```

#### 2. Deploy on Railway

* Go to [railway.app](https://railway.app)
* New Project → Deploy from GitHub
* Select your repo

#### 3. Add MySQL Plugin

* Click `+ New` → Database → MySQL
* Railway auto-generates credentials

#### 4. Set Environment Variables

| Key | Value |
|-----|-------|
| `DB_HOST` | `${{MySQL.MYSQLHOST}}` |
| `DB_PORT` | `${{MySQL.MYSQLPORT}}` |
| `DB_USER` | `${{MySQL.MYSQLUSER}}` |
| `DB_PASS` | `${{MySQL.MYSQLPASSWORD}}` |
| `DB_NAME` | `${{MySQL.MYSQLDATABASE}}` |

#### 5. Start Command

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

#### 6. Deploy

Your API will be live at: `https://your-app.up.railway.app`

---

## Production Considerations

* **MySQL** → Persistent storage
* **Async SQLAlchemy** → High performance
* **Background Tasks** → Non-blocking image generation
* **Case-Insensitive Matching** → Robust name lookup
* **Exact JSON Errors** → Consistent responses
* **Image Generation** → Matplotlib + PIL
* **No `--reload` in production**

---

## Troubleshooting

| Issue | Fix |
|------|-----|
| 503 on refresh | Check external APIs or network |
| 404 for country | Use lowercase or check spelling |
| Image not loading | Wait 3s after refresh (background task) |
| DB connection error | Verify `.env` and MySQL running |
| 500 on GET | Ensure `CountryResponse` allows `population=0` |

---

## Contributing

1. Fork the repo
2. Create branch: `git checkout -b feature/xyz`
3. Commit: `git commit -m "Add feature"`
4. Push & open PR
```
```