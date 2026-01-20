import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEye, faCheck } from "@fortawesome/free-solid-svg-icons";

function ProductCard({ product, selected, setSelectedProducts }) {

    const handleSelectClick = () => {
        setSelectedProducts(prevProducts => {
            const exists = prevProducts.some(p => p.id === product.id);

            if (!exists && prevProducts.length >= 3) {
                return prevProducts;
            }

            if (exists) {
                return prevProducts.filter(p => p.id !== product.id);
            } else {
                return [...prevProducts, product];
            }
        });
    };

    return (
        <div
            id={product.id}
            className="border-2 border-gray-200 shadow rounded-xl py-2 px-2 w-30 sm:w-40 overflow-hidden ms-auto me-auto mb-5"
            style={{ order: selected ? -1 : 0 }}
        >
            <div className="h-25 sm:h-40 flex items-center justify-center mb-2 overflow-hidden border-2 border-gray-200 rounded-lg">
                <img
                    src={product.image_url}
                    alt={product.title}
                    className="max-h-full max-w-full object-contain"
                />
            </div>

            <p className="text-sm font-medium leading-tight line-clamp-2 mb-1">
                {product.title}
            </p>

            <p className="text-base font-semibold mb-2">
                ₹ {product.price}
            </p>

            <div className="flex items-center justify-between mt-2">
                <button
                    type="button"
                    onClick={handleSelectClick}
                    className={`text-sm px-3 py-1 rounded-xl flex items-center gap-1 border cursor-pointer ${
                        selected
                            ? "bg-green-600 border-green-600 text-white"
                            : "bg-black border-black text-white"
                    }`}
                >
                    Select
                    {selected && (
                        <FontAwesomeIcon icon={faCheck} className="text-xs" />
                    )}
                </button>

                <a
                    href={product.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gray-600 hover:text-black"
                    title="View product"
                >
                    <FontAwesomeIcon icon={faEye} className="text-lg" />
                </a>
            </div>
        </div>
    );
}

export default ProductCard;
