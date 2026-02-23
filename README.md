# 📚 Mangable

A metadata-focused comic book library API built with **FastAPI** + **PostgreSQL**.  
Stores full ComicInfo standard metadata — **no comic file content is ever stored**.

---

## Features

| Feature | Details |
|---|---|
| 🔐 Auth | JWT bearer tokens + API keys |
| 📚 Comics DB | Full ComicInfo v2.1 field support |
| 🔍 Search | Multi-field search with filters & pagination |
| 📄 ComicInfo.xml | Download per-comic XML file |
| 🖼 Cover URLs | External cover image URL management |
| 🚫 No content | Only metadata, never comic files |

---

## Quick Start

### With Docker Compose

```bash
cp .env.example .env
# Edit .env with your settings
docker compose up -d
```

API available at: http://localhost:8000  
Swagger docs: http://localhost:8000/docs

### Without Docker

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up PostgreSQL and create database
createdb mangable

# 3. Configure environment
cp .env.example .env
# Edit DATABASE_URL and SECRET_KEY in .env

# 4. Run
uvicorn app.main:app --reload
```

---

## API Overview

### Authentication

**Register:**
```bash
POST /v1/auth/register
{
  "username": "alice",
  "email": "alice@example.com",
  "password": "securepassword"
}
```

**Login (get JWT):**
```bash
POST /v1/auth/login
{
  "username": "alice",
  "password": "securepassword"
}
# Returns: { "access_token": "...", "token_type": "bearer", "user": {...} }
```

Use token via header: `Authorization: Bearer <token>`

---

### API Keys

**Create API key:**
```bash
POST /v1/api-keys
Authorization: Bearer <token>
{
  "name": "My Application",
  "expires_at": null
}
# Returns full_key ONCE - store it securely!
```

Use API key via header: `X-API-Key: mng_...`

**List / Revoke:**
```bash
GET  /v1/api-keys
DELETE /v1/api-keys/{key_id}
```

---

### Comics

**Create:**
```bash
POST /v1/comics
Authorization: Bearer <token>
{
  "title": "Batman",
  "series": "Batman",
  "number": "1",
  "year": 2022,
  "publisher": "DC Comics",
  "writer": "Tom King",
  "genre": "Superhero",
  "summary": "The Dark Knight returns...",
  "cover_url": "https://covers.example.com/batman-1.jpg",
  "page_count": 32,
  "language_iso": "en",
  "manga": "No"
}
```

**Search:**
```bash
GET /v1/comics?q=batman&publisher=DC&year_from=2020&sort_by=year&sort_order=desc
GET /v1/comics?series=One+Piece&language=ja&manga=YesAndRightToLeft
```

Query parameters:
- `q` – full-text search (title, series, writer, publisher, summary)
- `series`, `publisher`, `writer`, `genre` – field filters
- `year_from`, `year_to` – year range
- `language` – ISO language code
- `manga` – Yes / No / YesAndRightToLeft
- `age_rating`
- `page`, `page_size` (max 100)
- `sort_by`: title | year | publisher | community_rating | created_at
- `sort_order`: asc | desc

**Get / Update / Delete:**
```bash
GET    /v1/comics/{id}
PATCH  /v1/comics/{id}
DELETE /v1/comics/{id}
```

**Download ComicInfo.xml:**
```bash
GET /v1/comics/{id}/comicinfo.xml
# Downloads ComicInfo.xml conforming to ComicRack/Kavita/Komga standard
```

**Get cover URL:**
```bash
GET /v1/comics/{id}/cover
# Returns: { "comic_id": "...", "cover_url": "https://..." }
```

---

## Project Structure

```
mangable/
├── app/
│   ├── api/
│   │   ├── auth.py          # Register, login, /me
│   │   ├── api_keys.py      # Create, list, revoke API keys
│   │   └── comics.py        # CRUD, search, comicinfo.xml, cover
│   ├── core/
│   │   ├── config.py        # Settings from .env
│   │   ├── database.py      # SQLAlchemy async engine
│   │   ├── security.py      # JWT, password hashing, API key generation
│   │   └── deps.py          # Auth dependencies
│   ├── models/
│   │   └── models.py        # SQLAlchemy models (User, ApiKey, Comic)
│   ├── schemas/
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── services/
│   │   └── comicinfo.py     # ComicInfo.xml generator
│   └── main.py              # FastAPI app
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## ComicInfo.xml Fields Supported

All standard ComicInfo v2.1 fields:

`Title`, `Series`, `Number`, `Count`, `Volume`, `AlternateSeries`, `AlternateNumber`, `AlternateCount`, `SeriesGroup`, `Summary`, `Notes`, `Year`, `Month`, `Day`, `Publisher`, `Imprint`, `Writer`, `Penciller`, `Inker`, `Colorist`, `Letterer`, `CoverArtist`, `Editor`, `Translator`, `Genre`, `Tags`, `Web`, `Format`, `AgeRating`, `LanguageISO`, `Manga`, `BlackAndWhite`, `CommunityRating`, `Review`, `PageCount`, `ISBN`, `Barcode`

---

## Security Notes

- Passwords are hashed with bcrypt
- API keys are stored as SHA-256 hashes (full key shown only once on creation)
- JWT tokens expire after 7 days by default
- API key expiry supported
- Max 10 active API keys per user
