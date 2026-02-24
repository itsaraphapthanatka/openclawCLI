import { Router } from 'express';
import { getDatabase } from '../database';
import { authMiddleware, AuthRequest } from '../middleware/auth';
import { createOrderSchema } from '../validation';

const router = Router();

// Get user's orders
router.get('/', authMiddleware, (req: AuthRequest, res) => {
  try {
    const db = getDatabase();
    const orders = db.prepare(`
      SELECT o.*, 
        (SELECT SUM(quantity) FROM order_items WHERE order_id = o.id) as item_count
      FROM orders o
      WHERE o.user_id = ?
      ORDER BY o.created_at DESC
    `).all(req.user!.id);

    res.json(orders);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Get single order
router.get('/:id', authMiddleware, (req: AuthRequest, res) => {
  try {
    const db = getDatabase();
    const order = db.prepare('SELECT * FROM orders WHERE id = ? AND user_id = ?').get(
      req.params.id, req.user!.id
    ) as any;

    if (!order) {
      res.status(404).json({ error: 'Order not found' });
      return;
    }

    const items = db.prepare(`
      SELECT oi.*, p.name, p.images
      FROM order_items oi
      JOIN products p ON oi.product_id = p.id
      WHERE oi.order_id = ?
    `).all(req.params.id) as any[];

    const parsedItems = items.map(item => ({
      ...item,
      images: item.images ? JSON.parse(item.images) : []
    }));

    res.json({ ...order, items: parsedItems });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Create order from cart
router.post('/', authMiddleware, (req: AuthRequest, res) => {
  try {
    const data = createOrderSchema.parse(req.body);
    const db = getDatabase();

    // Get cart items
    const cartItems = db.prepare(`
      SELECT ci.*, p.price, p.stock, p.name
      FROM cart_items ci
      JOIN products p ON ci.product_id = p.id
      WHERE ci.user_id = ?
    `).all(req.user!.id) as any[];

    if (cartItems.length === 0) {
      res.status(400).json({ error: 'Cart is empty' });
      return;
    }

    // Verify stock and calculate total
    let totalAmount = 0;
    for (const item of cartItems) {
      if (item.quantity > item.stock) {
        res.status(400).json({ error: `Not enough stock for ${item.name}` });
        return;
      }
      totalAmount += item.price * item.quantity;
    }

    // Create order
    const orderResult = db.prepare(
      'INSERT INTO orders (user_id, total_amount, shipping_address) VALUES (?, ?, ?)'
    ).run(req.user!.id, parseFloat(totalAmount.toFixed(2)), data.shipping_address);

    const orderId = orderResult.lastInsertRowid;

    // Create order items and update stock
    const insertItem = db.prepare(
      'INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES (?, ?, ?, ?)'
    );
    const updateStock = db.prepare('UPDATE products SET stock = stock - ? WHERE id = ?');

    for (const item of cartItems) {
      insertItem.run(orderId, item.product_id, item.quantity, item.price);
      updateStock.run(item.quantity, item.product_id);
    }

    // Clear cart
    db.prepare('DELETE FROM cart_items WHERE user_id = ?').run(req.user!.id);

    const order = db.prepare('SELECT * FROM orders WHERE id = ?').get(orderId);
    res.status(201).json(order);
  } catch (error: any) {
    res.status(400).json({ error: error.errors || error.message });
  }
});

export { router as ordersRouter };
