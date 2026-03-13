const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001';

export interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  stock: number;
  category_id: number;
  category_name?: string;
  images: string[];
  created_at: string;
}

export interface CartItem {
  id: number;
  product_id: number;
  quantity: number;
  name: string;
  price: number;
  images: string[];
  stock: number;
}

export interface Cart {
  items: CartItem[];
  total: number;
  itemCount: number;
}

export interface Order {
  id: number;
  status: 'pending' | 'paid' | 'shipped' | 'delivered' | 'cancelled';
  total_amount: number;
  shipping_address: string;
  created_at: string;
  item_count?: number;
  items?: OrderItem[];
}

export interface OrderItem {
  id: number;
  product_id: number;
  quantity: number;
  price_at_time: number;
  name: string;
  images: string[];
}

export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
}

// API Helper
async function fetchAPI(endpoint: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: 'Unknown error' }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.status === 204 ? null : response.json();
}

// Auth API
export const authAPI = {
  register: (data: { email: string; password: string; name: string }) =>
    fetchAPI('/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  
  login: (data: { email: string; password: string }) =>
    fetchAPI('/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  
  me: () => fetchAPI('/auth/me'),
};

// Products API
export const productsAPI = {
  getAll: (params?: { category?: string; search?: string; page?: number; limit?: number }) => {
    const query = params ? '?' + new URLSearchParams(params as Record<string, string>).toString() : '';
    return fetchAPI(`/products${query}`);
  },
  
  getById: (id: number) => fetchAPI(`/products/${id}`),
};

// Cart API
export const cartAPI = {
  get: () => fetchAPI('/cart'),
  
  addItem: (data: { product_id: number; quantity: number }) =>
    fetchAPI('/cart/items', { method: 'POST', body: JSON.stringify(data) }),
  
  updateItem: (id: number, data: { quantity: number }) =>
    fetchAPI(`/cart/items/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  
  removeItem: (id: number) =>
    fetchAPI(`/cart/items/${id}`, { method: 'DELETE' }),
  
  clear: () => fetchAPI('/cart', { method: 'DELETE' }),
};

// Orders API
export const ordersAPI = {
  getAll: () => fetchAPI('/orders'),
  
  getById: (id: number) => fetchAPI(`/orders/${id}`),
  
  create: (data: { shipping_address: string }) =>
    fetchAPI('/orders', { method: 'POST', body: JSON.stringify(data) }),
};
