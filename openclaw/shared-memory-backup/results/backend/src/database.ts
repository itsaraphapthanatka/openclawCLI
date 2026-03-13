import Database from 'better-sqlite3';
import path from 'path';

const DB_PATH = path.join(process.cwd(), 'data', 'ecommerce.db');

let db: Database.Database;

export function getDatabase(): Database.Database {
  if (!db) {
    db = new Database(DB_PATH);
    db.pragma('journal_mode = WAL');
  }
  return db;
}

export function initializeDatabase(): void {
  const database = getDatabase();
  
  // Users table
  database.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE NOT NULL,
      password TEXT NOT NULL,
      name TEXT NOT NULL,
      role TEXT DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `);

  // Categories table
  database.exec(`
    CREATE TABLE IF NOT EXISTS categories (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      slug TEXT UNIQUE NOT NULL
    )
  `);

  // Products table
  database.exec(`
    CREATE TABLE IF NOT EXISTS products (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      description TEXT,
      price REAL NOT NULL,
      stock INTEGER DEFAULT 0,
      category_id INTEGER,
      images TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (category_id) REFERENCES categories(id)
    )
  `);

  // Cart items table
  database.exec(`
    CREATE TABLE IF NOT EXISTS cart_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      quantity INTEGER NOT NULL DEFAULT 1,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
      FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
      UNIQUE(user_id, product_id)
    )
  `);

  // Orders table
  database.exec(`
    CREATE TABLE IF NOT EXISTS orders (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled')),
      total_amount REAL NOT NULL,
      shipping_address TEXT,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(id)
    )
  `);

  // Order items table
  database.exec(`
    CREATE TABLE IF NOT EXISTS order_items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      order_id INTEGER NOT NULL,
      product_id INTEGER NOT NULL,
      quantity INTEGER NOT NULL,
      price_at_time REAL NOT NULL,
      FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
      FOREIGN KEY (product_id) REFERENCES products(id)
    )
  `);

  // Insert sample categories
  const categories = [
    { name: 'Electronics', slug: 'electronics' },
    { name: 'Clothing', slug: 'clothing' },
    { name: 'Home & Garden', slug: 'home-garden' },
    { name: 'Sports', slug: 'sports' },
    { name: 'Books', slug: 'books' }
  ];

  const insertCategory = database.prepare(
    'INSERT OR IGNORE INTO categories (name, slug) VALUES (?, ?)'
  );
  categories.forEach(cat => insertCategory.run(cat.name, cat.slug));

  // Insert sample products
  const products = [
    { name: 'Wireless Headphones', description: 'High-quality wireless headphones with noise cancellation', price: 129.99, stock: 50, category_id: 1, images: JSON.stringify(['https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500']) },
    { name: 'Smart Watch', description: 'Fitness tracking smartwatch with heart rate monitor', price: 199.99, stock: 30, category_id: 1, images: JSON.stringify(['https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500']) },
    { name: 'Laptop Backpack', description: 'Water-resistant laptop backpack with USB charging port', price: 49.99, stock: 100, category_id: 2, images: JSON.stringify(['https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500']) },
    { name: 'Running Shoes', description: 'Lightweight running shoes with cushioned sole', price: 89.99, stock: 75, category_id: 4, images: JSON.stringify(['https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500']) },
    { name: 'Coffee Maker', description: 'Programmable coffee maker with thermal carafe', price: 79.99, stock: 40, category_id: 3, images: JSON.stringify(['https://images.unsplash.com/photo-1517668808822-9ebb02f2a0e6?w=500']) },
    { name: 'Yoga Mat', description: 'Non-slip yoga mat with carrying strap', price: 29.99, stock: 120, category_id: 4, images: JSON.stringify(['https://images.unsplash.com/photo-1601925260368-ae2f83cf8b7f?w=500']) },
    { name: 'Novel - Bestseller', description: 'Latest bestselling fiction novel', price: 14.99, stock: 200, category_id: 5, images: JSON.stringify(['https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=500']) },
    { name: 'Desk Lamp', description: 'LED desk lamp with adjustable brightness', price: 34.99, stock: 60, category_id: 3, images: JSON.stringify(['https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=500']) }
  ];

  const insertProduct = database.prepare(
    'INSERT OR IGNORE INTO products (name, description, price, stock, category_id, images) VALUES (?, ?, ?, ?, ?, ?)'
  );
  products.forEach(p => insertProduct.run(p.name, p.description, p.price, p.stock, p.category_id, p.images));

  console.log('✅ Database initialized with sample data');
}
