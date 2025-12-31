import { ProductGrid } from "./ProductGrid";

function ProductList(){
    const items = [
        { id: 1, name: "Black T-Shirt",  price: "$32" },
        { id: 2, name: "Formal Shirt",   price: "$54" },
        { id: 3, name: "Brown Jacket",   price: "$120" },
        { id: 4, name: "Cotton Hoodie",  price: "$75" },
        { id: 5, name: "Black T-Shirt",  price: "$32" },
        { id: 6, name: "Formal Shirt",   price: "$54" },
        { id: 7, name: "Brown Jacket",   price: "$120" },
        { id: 8, name: "Cotton Hoodie",  price: "$75" },
        { id: 9, name: "Black T-Shirt",  price: "$32" },
        { id: 10, name: "Formal Shirt",   price: "$54" },
        { id: 11, name: "Brown Jacket",   price: "$120" },
        { id: 12, name: "Cotton Hoodie",  price: "$75" },
    ];

    return <ProductGrid products={items} />;
}

export { ProductList };
