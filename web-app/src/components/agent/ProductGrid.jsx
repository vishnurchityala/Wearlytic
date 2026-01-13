import { ProductCard } from "./ProductCard";

function ProductGrid({ products, selectedIds, onToggleSelect }) {
  return (
    <div className="flex flex-wrap gap-2">
      {products.map((item) => (
        <ProductCard
          key={item.id}
          product={item}
          selected={selectedIds.has(item.id)}
          onToggleSelect={onToggleSelect}
        />
      ))}
    </div>
  );
}

export { ProductGrid };
