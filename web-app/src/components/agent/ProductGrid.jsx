import { ProductCard } from "./ProductCard";

function ProductGrid({ products }){
    return (
        <div className="grid  grid-cols-2 sm:grid-cols-3 gap-2">
            {products.map((item) => <ProductCard key={item.id} product={item} />)}
        </div>
    );
}

export { ProductGrid };
