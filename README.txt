Technical Design Document (TDD): Fast_API Ecommerce Backend

1) Purpose
This document describes the architecture, modules, data models, APIs, configuration, and runtime behavior of the Fast_API backend application.

2) Scope
In scope
- FastAPI application structure and request flow
- Domain modules: customers, category, products
- Persistence via SQLAlchemy
- Validation/serialization via Pydantic
- Config via pydantic-settings and .env
- Caching via Redis (async)
- Startup/shutdown behavior

Out of scope (current)
- Automated tests, CI/CD pipelines
- Database migration tooling (Alembic)
- Deployment (Docker/Kubernetes)
- Observability (structured logging, tracing, metrics)

3) Tech Stack
- FastAPI
- SQLAlchemy
- Pydantic
- pydantic-settings
- Redis (async client)

4) High-Level Architecture
The app follows a feature-folder modular structure:

- Router layer (router.py): HTTP endpoints, request validation, dependencies.
- Controller layer (controller.py): business logic, DB operations, auth logic, caching logic.
- DTO layer (dtos.py): Pydantic schemas for input and output.
- Model layer (models.py): SQLAlchemy model definitions (tables/relationships).
- Utilities (src/utils/): shared DB session factory, settings, redis client, helpers.

Request Lifecycle (typical)
1. Client calls a route (example: /category/create)
2. Router validates request body (Pydantic schema)
3. Router injects DB session using Depends(get_db)
4. Router delegates to controller method
5. Controller queries/mutates DB models via SQLAlchemy session
6. Controller returns response object/dict (sometimes wrapped in ResponseSchema)
7. FastAPI serializes the response to JSON

5) Repository Layout
Fast_API/
  main.py
  requirement.txt
  .env
  src/
    utils/
      db.py
      settings.py
      redis.py
      helper.py
    customers/
      router.py
      controller.py
      dtos.py
      models.py
    category/
      router.py
      controller.py
      dtos.py
      models.py
    products/
      router.py
      controller.py
      dtos.py
      models.py

6) Application Entry Point (main.py)
Responsibilities
- Initializes SQLAlchemy tables using BASE.metadata.create_all(engine)
- Creates FastAPI app
- Includes routers:
  - customer_routes
  - category_routes
  - product_routes
- Redis lifecycle:
  - startup: redis_client.ping()
  - shutdown: redis_client.close()
- Provides a simple Redis test endpoint:
  - GET /redis-test sets and gets a key

Note: create_all() is convenient for development but not ideal for production schema evolution (consider Alembic later).

7) Configuration & Secrets
Settings are loaded using pydantic-settings (src/utils/settings.py) from .env.

Expected environment variables
- DB_CONNECTION: SQLAlchemy DB URL
- SECRET_KEY: JWT signing key
- ALGORITHM: JWT algorithm (example: HS256)
- EXP_TIME: access token expiry time in minutes
- REDIS_URL: Redis connection URL (used in src/utils/redis.py)

Security notes
- .env should not be committed to version control.
- SECRET_KEY must be strong and rotated appropriately.

8) Database Architecture (SQLAlchemy)
DB Session Management (src/utils/db.py)
- engine = create_engine(settings.DB_CONNECTION)
- Local_Session = sessionmaker(bind=engine)
- get_db() dependency yields a session and closes it in finally.

Tables and relationships

Category (src/category/models.py)
- Table: category
- Fields:
  - id (PK, autoincrement)
  - name (unique)
  - category_code (sequence starting at 1000)
  - image, description
  - created_date, modified_date
- Relationship:
  - CategoryModel.products ↔ ProductModel.category

Products (src/products/models.py)
- Table: products
- Fields:
  - product_id (PK, autoincrement)
  - product_name
  - product_description
  - product_price
  - product_quantity
  - category_id (FK → category.id)
  - created_date, modified_date
  - product_image_url (optional)

Customers (src/customers/models.py)
- Tables:
  - customers (CustomerModel)
  - customer_credential (CustomerRegistrationModel)
  - refresh_tokens (RefreshTokenModel)
- Notes:
  - CustomerModel.id is generated via helper
  - Credentials store hashed passwords
  - Refresh tokens are stored as hashed tokens with revocation fields

9) Redis Architecture
Redis Client (src/utils/redis.py)
- Uses redis.asyncio client created from REDIS_URL
- decode_responses=True so values are returned as strings

Usage
- Startup: ping to confirm connectivity
- Cache-aside strategy for product reads (see Products module)

10) API Design (Endpoints and Behavior)

10.1) Customers Module (/customers)
Routes (src/customers/router.py)
- POST /customers/create
  - Create a customer record
- GET /customers/all
  - List all customers
- GET /customers/{customer_id}
  - Get customer by id (404 if missing)
- POST /customers/register
  - Register customer credentials (hash password)
  - Requires customer to exist in customers table
  - Rejects duplicate mobile in credential table
- POST /customers/login
  - Validates customer + credentials + password
  - Returns:
    - access_token (JWT)
    - refresh_token (raw token returned to client once; hashed token stored in DB)
- GET /customers/is_auth
  - Validates JWT in header: Authorization: Bearer <token>
  - Returns authenticated mobile, otherwise 401 (missing/expired/invalid)

Auth design (src/customers/controller.py)
- Access tokens are JWT signed with SECRET_KEY and ALGORITHM
- Payload includes:
  - mobile
  - exp (expiry calculated using EXP_TIME minutes)
- Refresh token handling:
  - refresh token is generated (UUID)
  - hashed refresh token is stored in DB
  - raw refresh token is returned to the caller

10.2) Category Module (/category)
Routes (src/category/router.py)
- POST /category/create
  - Request: CategoryCreateSchema
  - Response: ResponseSchema[CategoryResponseSchema]
  - Business rule: prevents duplicate category name (case-insensitive)
- GET /category/all
  - Response: ResponseSchema[List[CategoryResponseSchema]]
- GET /category/{id}?category_code=...
  - Validates category_code matches the category’s stored category_code

DTO design (src/category/dtos.py)
- CategoryBase: name, image, description
- CategoryCreateSchema: request schema (inherits base)
- CategoryResponseSchema: response schema (adds id)
- ResponseSchema[T]:
  - success: bool
  - data: optional payload
  - message: optional message

10.3) Products Module (/products)
Routes (src/products/router.py)
- POST /products/{category_id}/add
  - Adds product under a category
  - Rejects missing category
  - Rejects non-positive price/quantity
  - Prevents duplicate product within same category
- POST /products/{category_id}/bulk-add
  - Upload CSV
  - Validates .csv extension
  - Parses rows and returns inserted_count, failed_count, and per-row errors
- GET /products/all?limit=...
  - Returns a limited list of products
- GET /products/{product_id}
  - Cached get-by-id (Redis)
- PATCH /products/{product_id}
  - Updates product fields from request payload

Redis caching for GET /products/{product_id} (src/products/controller.py)
- Cache key: product:{product_id}
- TTL: 60 seconds
- Flow:
  - If cached: return JSON-decoded value
  - Else: query DB → build dict → store JSON in Redis → return dict

11) Error Handling Strategy (current behavior)
- Customers/products controllers commonly raise HTTPException for validation failures.
- Category uses a ResponseSchema wrapper for both success and failure in many cases.
- Category create/list catches broad exceptions and returns ResponseSchema with message.

Note: Response formats are not fully consistent across modules (some endpoints return wrappers, some return raw dicts or ORM objects).

12) Data Validation Strategy
- Pydantic DTOs enforce request/response shape.
- Controllers enforce domain rules:
  - existence checks (category/customer must exist)
  - uniqueness checks (category name, product name)
  - numeric constraints (price/quantity not zero or negative)
  - password hashing and verification

13) Non-Functional Requirements (Recommended Targets)
Security
- Keep .env out of source control
- Password hashing (already done)
- Refresh tokens stored hashed (already done)
- Consider rate limiting on login endpoints (future)

Performance
- Redis caching for hot product reads (already implemented)
- Bulk insert for CSV upload (already implemented)

Reliability
- Consider graceful fallback if Redis is down (future)
- Prefer DB migrations for schema changes (future)

14) Running the Application (Development)
Command
- fastapi dev main.py --reload

Prereqs
- Database reachable via DB_CONNECTION
- Redis reachable via REDIS_URL

15) Backlog / Future Improvements (Optional)
- Add Alembic migrations (replace create_all)
- Standardize response format across all routes
- Add OpenAPI tags/metadata per router
- Add tests (pytest)
- Enforce refresh-token expiry/revocation logic
- Add structured logging and centralized exception handlers
- Add pagination for list endpoints

16) Glossary
- DTO: Data Transfer Object (Pydantic schema)
- ORM: Object-Relational Mapping (SQLAlchemy)
- JWT: JSON Web Token
- Cache-aside: check cache first; if miss, load from DB and populate cache
