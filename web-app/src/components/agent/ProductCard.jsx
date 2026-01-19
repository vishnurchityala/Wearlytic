import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faEye } from "@fortawesome/free-solid-svg-icons";

function ProductCard({ product }) {
    return (
        <div className="border-2 border-gray-200 shadow rounded-xl py-2 px-2 w-40 overflow-hidden ms-auto me-auto mb-5" id={product.id}>
            <div className="h-40 flex items-center justify-center mb-2 overflow-hidden border-2 border-gray-200 rounded-lg">
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
                    className="text-sm px-2 py-1 border text-white bg-black rounded-xl"
                >
                    Select
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
