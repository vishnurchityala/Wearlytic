import ProductCard from "./ProductCard";

function ProductList({products}){
    return (
        <div className="flex flex-wrap p-2">
            {products.map((product, index) => (
                <ProductCard product={product}/>
            ))}
        </div>
    );
}

export default ProductList;