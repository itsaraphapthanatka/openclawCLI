import { Router } from 'express';
import { getDatabase } from '../database';
import { authMiddleware, AuthRequest } from '../middleware/auth';
import { addToCartSchema, updateCartItemSchema } from '../validation';

const router = Router();

// Get user's cart
router.get('/', authMiddleware, (req: AuthRequest, res) => {
  try {
    const db = getDatabase();
    const items = db.prepare(`
      SELECT ci.*, p.name, p.price, p.images, p.stock
      FROM cart_items ci
      JOIN products p ON ci.product_id = p.id
      WHERE ci.user_id = ?
    `).all(req.user!.id) as any[];

    const parsedItems = items.map(item => ({
      ...item,
      images: item.images ? JSON.parse(item.images) : []
    }));

    const total = parsedItems.reduce((sum, item) => sum + (item.price * item.quantity), 0);

    res.json({
      items: parsedItems,
      total: parseFloat(total.toFixed(2)),
      itemCount: parsedItems.reduce((sum, item) => sum + item.quantity, 0)
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Add item to cart
router.post('/items', authMiddleware, (req: AuthRequest, res) => {
  try {
    const data = addToCartSchema.parse(req.body);
    const db = getDatabase();

    // Check product exists and has stock
    const product = db.prepare('SELECT * FROM products WHERE id = ?').get(data.product_id) as any;
    if (!product) {
      res.status(404).json({ error: 'Product not found' });
      return;
    }
    if (product.stock < data.quantity) {
      res.status(400).json({ error: 'Not enough stock available' });
      return;
    }

    // Check if item already in cart
    const existing = db.prepare(
      'SELECT * FROM cart_items WHERE user_id = ? AND product_id = ?'
    ).get(req.user!.id, data.product_id) as any;

    if (existing) {
      // Update quantity
      const newQuantity = existing.quantity + data.quantity;
      if (newQuantity > product.stock) {
        res.status(400).json({ error: 'Not enough stock available' });
        return;
      }
      db.prepare(
        'UPDATE cart_items SET quantity = ? WHERE id = ?'
      ).run(newQuantity, existing.id);
    } else {
      // Insert new item
      db.prepare(
        'INSERT INTO cart_items (user_id, product_id, quantity) VALUES (?, ?, ?)'
      ).run(req.user!.id, data.product_id, data.quantity);
    }

    res.json({ message: 'Item added to cart' });
  } catch (error: any) {
    res.status(400).json({ error: error.errors || error.message });
  }
});

// Update cart item quantity
router.put('/items/:id', authMiddleware, (req: AuthRequest, res) => {
  try {
    const data = updateCartItemSchema.parse(req.body);
    const db = getDatabase();

    const item = db.prepare(
      'SELECT ci.*, p.stock FROM cart_items ci JOIN products p ON ci.product_id = p.id WHERE ci.id = ? AND ci.user_id = ?'
    ).get(req.params.id, req.user!.id) as any;

    if (!item) {
      res.status(404).json({ error: 'Cart item not found' });
      return;
    }

    if (data.quantity === 0) {
      db.prepare('DELETE FROM cart_items WHERE id = ?').run(req.params.id);
      res.json({ message: 'Item removed from cart' });
      return;
    }

    if (data.quantity > item.stock) {
      res.status(400).json({ error: 'Not enough stock available' });
      return;
    }

    db.prepare('UPDATE cart_items SET quantity = ? WHERE id = ?').run(data.quantity, req.params.id);
    res.json({ message: 'Cart updated' });
  } catch (error: any) {
    res.status(400).json({ error: error.errors || error.message });
  }
});

// Remove item from cart
router.delete('/items/:id', authMiddleware, (req: AuthRequest, res) => {
  try {
    const db = getDatabase();
    const item = db.prepare(
      'SELECT * FROM cart_items WHERE id = ? AND user_id = ?'
    ).get(req.params.id, req.user!.id);

    if (!item) {
      res.status(404).json({ error: 'Cart item not found' });
      return;
    }

    db.prepare('DELETE FROM cart_items WHERE id = ?').run(req.params.id);
    res.json({ message: 'Item removed from cart' });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Clear cart
router.delete('/', authMiddleware, (req: AuthRequest, res) => {
  try {
    const db = getDatabase();
    db.prepare('DELETE FROM cart_items WHERE user_id = ?').run(req.user!.id);
    res.json({ message: 'Cart cleared' });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

export { router as cartRouter };
