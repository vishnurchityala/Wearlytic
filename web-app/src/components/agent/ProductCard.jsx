import { faTag, faEllipsis, faCheck } from '@fortawesome/free-solid-svg-icons';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';

function ProductCard({ product, selected, onToggleSelect }) {
  return (
    <div
      className={
        `w-full sm:w-[32%] rounded-md p-3 shadow-sm bg-white border ` +
        (selected ? 'border-green-500' : 'border-gray-300')
      }
    >
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
        <p className="outfit-regular text-sm font-medium text-gray-800 truncate max-w-[70%]">
          {product.name}
        </p>

        <p className="text-sm font-medium text-gray-800 whitespace-nowrap flex items-center gap-1">
          {product.price}
          <FontAwesomeIcon icon={faTag} />
        </p>
      </div>

      <p className="outfit-regular text-gray-400 text-xs mb-2">
        Lorem ipsum dolor sit. Lorem ipsum dolor sit.
      </p>

      <div className="flex items-center justify-between mt-auto">
        <button
          type="button"
          onClick={() => onToggleSelect(product.id)}
          className={
            `text-sm font-medium rounded-full px-3 py-1 cursor-pointer ` +
            (selected ? 'bg-green-600 text-white' : 'bg-black text-white')
          }
        >
          {selected ? (
            <span className="flex items-center gap-1">
              <FontAwesomeIcon icon={faCheck} />
              Selected
            </span>
          ) : (
            "Select"
          )}
        </button>

        <button type="button" className="text-gray-700 p-1 text-xs bg-gray-200 rounded-full">
          <FontAwesomeIcon icon={faEllipsis} />
        </button>
      </div>
    </div>
  );
}

export { ProductCard };
