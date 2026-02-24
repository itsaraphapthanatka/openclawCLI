# E-Commerce Backend API

Backend API สำหรับระบบ E-Commerce สร้างด้วย Node.js + Express + TypeScript + SQLite

## 🚀 เริ่มต้นใช้งาน

```bash
# Install dependencies
npm install

# Initialize database with sample data
npm run db:init

# Development mode
npm run dev

# Production build
npm run build
npm start
```

Server จะรันที่ `http://localhost:3001`

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | สมัครสมาชิก | ❌ |
| POST | `/auth/login` | เข้าสู่ระบบ | ❌ |
| GET | `/auth/me` | ดูข้อมูลผู้ใช้ปัจจุบัน | ✅ |

**Register/Login Request:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "name": "John Doe"
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "role": "customer"
  },
  "token": "eyJhbGciOiJIUzI1NiIs..."
}
```

### Products

| Method | Endpoint | Description | Auth Required | Admin Only |
|--------|----------|-------------|---------------|------------|
| GET | `/products` | ดูสินค้าทั้งหมด | ❌ | ❌ |
| GET | `/products/:id` | ดูสินค้ารายการเดียว | ❌ | ❌ |
| POST | `/products` | สร้างสินค้าใหม่ | ✅ | ✅ |
| PUT | `/products/:id` | อัพเดทสินค้า | ✅ | ✅ |
| DELETE | `/products/:id` | ลบสินค้า | ✅ | ✅ |

**Query Parameters for GET /products:**
- `category` - Filter by category slug (electronics, clothing, etc.)
- `search` - Search by name or description
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20)

**Create Product Request:**
```json
{
  "name": "New Product",
  "description": "Product description",
  "price": 99.99,
  "stock": 100,
  "category_id": 1,
  "images": ["https://example.com/image.jpg"]
}
```

### Cart

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/cart` | ดูตะกร้าสินค้า | ✅ |
| POST | `/cart/items` | เพิ่มสินค้าเข้าตะกร้า | ✅ |
| PUT | `/cart/items/:id` | อัพเดทจำนวนสินค้า | ✅ |
| DELETE | `/cart/items/:id` | ลบสินค้าออกจากตะกร้า | ✅ |
| DELETE | `/cart` | ล้างตะกร้า | ✅ |

**Add to Cart Request:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

### Orders

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/orders` | ดูรายการสั่งซื้อทั้งหมด | ✅ |
| GET | `/orders/:id` | ดูรายละเอียดคำสั่งซื้อ | ✅ |
| POST | `/orders` | สร้างคำสั่งซื้อจากตะกร้า | ✅ |

**Create Order Request:**
```json
{
  "shipping_address": "123 Main St, Bangkok, Thailand"
}
```

## 🔐 Authentication

ทุก request ที่ต้องการ authentication ต้องส่ง header:
```
Authorization: Bearer <your_jwt_token>
```

## 📁 Project Structure

```
src/
├── index.ts          # Entry point
├── database.ts       # SQLite database setup
├── types.ts          # TypeScript types
├── validation.ts     # Zod schemas
├── middleware/
│   └── auth.ts       # JWT auth middleware
└── routes/
    ├── auth.ts       # Auth routes
    ├── products.ts   # Product routes
    ├── cart.ts       # Cart routes
    └── orders.ts     # Order routes
```

## 🧪 curl Examples

```bash
# Register
curl -X POST http://localhost:3001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123","name":"Test User"}'

# Login
curl -X POST http://localhost:3001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"password123"}'

# Get products
curl http://localhost:3001/products

# Get products with search
curl "http://localhost:3001/products?search=headphones"

# Add to cart (replace TOKEN with your JWT)
curl -X POST http://localhost:3001/cart/items \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"product_id":1,"quantity":2}'

# Create order
curl -X POST http://localhost:3001/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"shipping_address":"123 Main St"}'
```
