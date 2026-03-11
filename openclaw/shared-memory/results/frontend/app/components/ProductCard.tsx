'use client';

import { Product } from '@/lib/api';
import Link from 'next/link';

interface ProductCardProps {
  product: Product;
}

export default function ProductCard({ product }: ProductCardProps) {
  const imageUrl = product.images?.[0] || 'https://via.placeholder.com/300x300?text=No+Image';

  return (
    <Link href={`/products/${product.id}`} className="group">
      <div className="bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-lg transition-shadow duration-300">
        <div className="relative aspect-square overflow-hidden bg-gray-100">
          <img
            src={imageUrl}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
          {product.stock === 0 && (
            <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
              <span className="text-white font-semibold">Out of Stock</span>
            </div>
          )}
        </div>
        <div className="p-4">
          <p className="text-xs text-primary-600 font-medium uppercase tracking-wide">
            {product.category_name || 'Uncategorized'}
          </p>
          <h3 className="mt-1 text-lg font-semibold text-gray-900 line-clamp-2">
            {product.name}
          </h3>
          <p className="mt-1 text-sm text-gray-500 line-clamp-2">
            {product.description}
          </p>
          <div className="mt-3 flex items-center justify-between">
            <span className="text-xl font-bold text-gray-900">
              ${product.price.toFixed(2)}
            </span>
            {product.stock > 0 && product.stock < 10 && (
              <span className="text-xs text-orange-600 font-medium">
                Only {product.stock} left
              </span>
            )}
          </div>
        </div>
      </div>
    </Link>
  );
}
