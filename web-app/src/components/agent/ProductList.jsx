import ProductCard from "./ProductCard";

function ProductList({products,setSelectedProducts,selectedProducts}){
    return (
        <div className="flex flex-wrap p-2">
            {products.map((product) => {
                const isSelected = selectedProducts?.some?.((p) => p.id === product.id) || false;
                return (
                    <ProductCard
                        key={product.id}
                        product={product}
                        selected={isSelected}
                        setSelectedProducts={setSelectedProducts}
                    />
                );
            })}
        </div>
    );
}

export default ProductList;