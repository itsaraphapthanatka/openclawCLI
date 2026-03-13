import { z } from 'zod';

export const registerSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
  name: z.string().min(2)
});

export const loginSchema = z.object({
  email: z.string().email(),
  password: z.string()
});

export const createProductSchema = z.object({
  name: z.string().min(1),
  description: z.string(),
  price: z.number().positive(),
  stock: z.number().int().min(0),
  category_id: z.number().int(),
  images: z.array(z.string()).optional()
});

export const updateProductSchema = createProductSchema.partial();

export const addToCartSchema = z.object({
  product_id: z.number().int(),
  quantity: z.number().int().min(1)
});

export const updateCartItemSchema = z.object({
  quantity: z.number().int().min(0)
});

export const createOrderSchema = z.object({
  shipping_address: z.string().min(1)
});
