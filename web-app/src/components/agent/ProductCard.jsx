import { faTag, faEllipsis } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

function ProductCard({ product }){
    return (
        <div className="w-full rounded-md p-3 shadow-sm bg-white">
            <div className="w-full h-40 bg-gray-100 rounded-md mb-2 overflow-hidden flex items-center justify-center">
                {product.image ? (
                    <img 
                        src={product.image} 
                        alt={product.name}
                        className="w-full h-full object-cover"
                    />
                ) : (
                    <div className="w-20 h-24 bg-gray-300 rounded-md" />
                )}
            </div>

            <div className="flex items-center justify-between mb-1">
                <p className="text-sm font-medium text-gray-800 outfit-regular truncate max-w-[70%]">
                    {product.name}
                </p>

                <p className="text-sm font-medium text-gray-800 outfit-regular whitespace-nowrap flex items-center gap-1">
                    {product.price}
                    <FontAwesomeIcon icon={faTag} />
                </p>
            </div>
            <p className='text-gray-400 text-xs outfit-regular mb-2'>Lorem ipsum dolor sit. Lorem ipsum dolor sit.</p>
            <div className="flex items-center justify-between mt-auto">
                <button
                    type="button"
                    className="text-sm font-medium bg-black text-white outfit-regular rounded-full px-3 py-1"
                >
                    Select
                </button>

                <button
                    type="button"
                    className="text-gray-700 p-1 text-xs bg-gray-200 rounded-full"
                >
                    <FontAwesomeIcon icon={faEllipsis} />
                </button>
            </div>
        </div>
    );
}

export { ProductCard };
