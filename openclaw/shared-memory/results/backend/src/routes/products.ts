import { Router } from 'express';
import { getDatabase } from '../database';
import { authMiddleware, adminMiddleware, AuthRequest } from '../middleware/auth';
import { createProductSchema, updateProductSchema } from '../validation';
import { Product } from '../types';

const router = Router();

// Get all products (public)
router.get('/', (req, res) => {
  try {
    const db = getDatabase();
    const { category, search, page = '1', limit = '20' } = req.query;
    
    let query = `
      SELECT p.*, c.name as category_name 
      FROM products p 
      LEFT JOIN categories c ON p.category_id = c.id
      WHERE 1=1
    `;
    const params: any[] = [];

    if (category) {
      query += ' AND c.slug = ?';
      params.push(category);
    }

    if (search) {
      query += ' AND (p.name LIKE ? OR p.description LIKE ?)';
      params.push(`%${search}%`, `%${search}%`);
    }

    query += ' ORDER BY p.created_at DESC';

    const pageNum = parseInt(page as string);
    const limitNum = parseInt(limit as string);
    const offset = (pageNum - 1) * limitNum;

    query += ' LIMIT ? OFFSET ?';
    params.push(limitNum, offset);

    const products = db.prepare(query).all(...params) as any[];
    
    // Parse images JSON
    const parsedProducts = products.map(p => ({
      ...p,
      images: p.images ? JSON.parse(p.images) : []
    }));

    res.json({
      products: parsedProducts,
      pagination: {
        page: pageNum,
        limit: limitNum,
        total: db.prepare('SELECT COUNT(*) as count FROM products').get().count
      }
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get single product (public)
router.get('/:id', (req, res) => {
  try {
    const db = getDatabase();
    const product = db.prepare(`
      SELECT p.*, c.name as category_name 
      FROM products p 
      LEFT JOIN categories c ON p.category_id = c.id
      WHERE p.id = ?
    `).get(req.params.id) as any;

    if (!product) {
      res.status(404).json({ error: 'Product not found' });
      return;
    }

    product.images = product.images ? JSON.parse(product.images) : [];
    res.json(product);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Create product (admin only)
router.post('/', authMiddleware, adminMiddleware, (req: AuthRequest, res) => {
  try {
    const data = createProductSchema.parse(req.body);
    const db = getDatabase();

    const result = db.prepare(
      'INSERT INTO products (name, description, price, stock, category_id, images) VALUES (?, ?, ?, ?, ?, ?)'
    ).run(data.name, data.description, data.price, data.stock, data.category_id, JSON.stringify(data.images || []));

    const product = db.prepare('SELECT * FROM products WHERE id = ?').get(result.lastInsertRowid) as Product;
    res.status(201).json({ ...product, images: data.images || [] });
  } catch (error: any) {
    res.status(400).json({ error: error.errors || error.message });
  }
});

// Update product (admin only)
router.put('/:id', authMiddleware, adminMiddleware, (req: AuthRequest, res) => {
  try {
    const data = updateProductSchema.parse(req.body);
    const db = getDatabase();

    const existing = db.prepare('SELECT id FROM products WHERE id = ?').get(req.params.id);
    if (!existing) {
      res.status(404).json({ error: 'Product not found' });
      return;
    }

    const updates: string[] = [];
    const values: any[] = [];

    if (data.name) { updates.push('name = ?'); values.push(data.name); }
    if (data.description !== undefined) { updates.push('description = ?'); values.push(data.description); }
    if (data.price !== undefined) { updates.push('price = ?'); values.push(data.price); }
    if (data.stock !== undefined) { updates.push('stock = ?'); values.push(data.stock); }
    if (data.category_id !== undefined) { updates.push('category_id = ?'); values.push(data.category_id); }
    if (data.images) { updates.push('images = ?'); values.push(JSON.stringify(data.images)); }

    values.push(req.params.id);
    db.prepare(`UPDATE products SET ${updates.join(', ')} WHERE id = ?`).run(...values);

    const product = db.prepare('SELECT * FROM products WHERE id = ?').get(req.params.id) as Product;
    res.json({ ...product, images: data.images || JSON.parse(product.images as any) });
  } catch (error: any) {
    res.status(400).json({ error: error.errors || error.message });
  }
});

// Delete product (admin only)
router.delete('/:id', authMiddleware, adminMiddleware, (req: AuthRequest, res) => {
  try {
    const db = getDatabase();
    const existing = db.prepare('SELECT id FROM products WHERE id = ?').get(req.params.id);
    if (!existing) {
      res.status(404).json({ error: 'Product not found' });
      return;
    }

    db.prepare('DELETE FROM products WHERE id = ?').run(req.params.id);
    res.json({ message: 'Product deleted successfully' });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export { router as productsRouter };
