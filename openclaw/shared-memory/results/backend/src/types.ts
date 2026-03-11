export interface User {
  id: number;
  email: string;
  password: string;
  name: string;
  role: 'customer' | 'admin';
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
}

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  stock: number;
  category_id: number;
  images: string[];
  created_at: string;
}

export interface CartItem {
  id: number;
  user_id: number;
  product_id: number;
  quantity: number;
  created_at: string;
  product?: Product;
}

export interface Order {
  id: number;
  user_id: number;
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';
  total_amount: number;
  shipping_address: string;
  created_at: string;
  items?: OrderItem[];
}

export interface OrderItem {
  id: number;
  order_id: number;
  product_id: number;
  quantity: number;
  price_at_time: number;
  product?: Product;
}
