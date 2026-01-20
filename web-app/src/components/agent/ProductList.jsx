import ProductCard from "./ProductCard";

function ProductList({products,setSelectedProducts}){
    return (
        <div className="flex flex-wrap p-2">
            {products.map((product, index) => (
                <ProductCard product={product} setSelectedProducts={setSelectedProducts}/>
            ))}
        </div>
    );
}

export default ProductList;