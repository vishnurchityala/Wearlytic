import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown,faChevronUp,faShirt } from "@fortawesome/free-solid-svg-icons";
import ProductList from "./ProductList";

function ProductSection({products,loading,setSelectedProducts}){
    const [collapsed, setCollapsed] = useState(false);
    if (loading) {
        return (
        <div className="flex justify-center items-center h-full w-full rounded-xl border-2 border-gray-300 overflow-scroll py-5">
            <div className="w-6 h-6 border-4 border-t-black border-gray-300 rounded-full animate-spin"></div>
        </div>
        );
    }
    const productCount = products.length;
    return (
        <div className="w-full rounded-xl border-2 border-gray-300 overflow-y-scroll outfit-regular max-h-150 sm:max-h-full sm:h-fit">
            <div className="flex align-content-center">
                <span className="text-center ms-3 my-auto text-sm">
                    Clothes <FontAwesomeIcon icon={faShirt}/>
                </span>
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="w-fit ms-auto px-4 py-2 text-left text-sm font-medium flex items-center justify-between cursor-pointer"
                >
                    <FontAwesomeIcon icon={collapsed ? faChevronDown : faChevronUp} />
                </button>
            </div>

            {!collapsed && (
                <>
                    {productCount === 0 && (
                        <div className="py-10">
                            <img
                                src="no-results.png"
                                className="w-23 h-23 ms-auto me-auto"
                                alt="No results"
                            />
                            <p className="text-center text-xl">No Results</p>
                        </div>
                    )}

                    {productCount > 0 && <ProductList products={products} setSelectedProducts={setSelectedProducts}/>}
                </>
            )}
        </div>
    );
}

export default ProductSection;