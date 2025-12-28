import { ProductGrid } from "./ProductGrid";

function ProductList(){
    const items = [
        { id: 1, name: "Black T-Shirt",  price: "$32" },
        { id: 2, name: "Formal Shirt",   price: "$54" },
        { id: 3, name: "Brown Jacket",   price: "$120" },
        { id: 4, name: "Cotton Hoodie",  price: "$75" },
        { id: 1, name: "Black T-Shirt",  price: "$32" },
        { id: 2, name: "Formal Shirt",   price: "$54" },
        { id: 3, name: "Brown Jacket",   price: "$120" },
        { id: 4, name: "Cotton Hoodie",  price: "$75" },
        { id: 1, name: "Black T-Shirt",  price: "$32" },
        { id: 2, name: "Formal Shirt",   price: "$54" },
        { id: 3, name: "Brown Jacket",   price: "$120" },
        { id: 4, name: "Cotton Hoodie",  price: "$75" },
    ];

    return <ProductGrid products={items} />;
}

export { ProductList };
