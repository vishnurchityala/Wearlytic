import { useMemo, useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown,faChevronUp,faShirt,faArrowRight,faArrowLeft } from "@fortawesome/free-solid-svg-icons";
import ProductList from "./ProductList";

function ProductSection({products,loading,selectedProducts,setSelectedProducts,nextPage,prevPage,onFetchPage}){
    const [collapsed, setCollapsed] = useState(false);
    const combinedProducts = useMemo(() => {
        const pageIds = new Set(products.map(p => p.id));
        const selectedNotInPage = (selectedProducts || []).filter(sp => !pageIds.has(sp.id));
        return [...selectedNotInPage, ...products];
    }, [products, selectedProducts]);
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
            <button
                onClick={() => setCollapsed(!collapsed)}
                className="w-full ms-auto px-4 py-2 text-left text-sm font-medium flex items-center justify-between cursor-pointer"
            >
                 <span className="text-center my-auto text-sm">
                    Clothes <FontAwesomeIcon icon={faShirt}/>
                </span>
                <FontAwesomeIcon icon={collapsed ? faChevronDown : faChevronUp} />
            </button>

            {!collapsed && (
                <>
                    <div className="flex ms-4 gap-2 mt-1">
                        {prevPage !== null &&
                            <button
                                type="button"
                                onClick={() => onFetchPage && prevPage && onFetchPage(prevPage)}
                                className={`text-xs px-2 py-1 rounded-2xl flex items-center gap-1 text-white bg-black cursor-pointer`}
                            >
                                <FontAwesomeIcon icon={faArrowLeft} className="text-xs" /> Prev Page
                            </button>
                        }
                        {nextPage !== null &&
                            <button
                                type="button"
                                onClick={() => onFetchPage && nextPage && onFetchPage(nextPage)}
                                className={`text-xs px-2 py-1 rounded-2xl flex items-center gap-1 text-white bg-black cursor-pointer`}
                            >
                                Next Page<FontAwesomeIcon icon={faArrowRight} className="text-xs" />
                            </button>
                        }   
                    </div>
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

                    {productCount > 0 && (
                        <ProductList
                            products={combinedProducts}
                            setSelectedProducts={setSelectedProducts}
                            selectedProducts={selectedProducts}
                        />
                    )}
                </>
            )}
        </div>
    );
}

export default ProductSection;
