import { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown, faChevronUp, faFilter } from "@fortawesome/free-solid-svg-icons";

function CategoryButton({ category, selectedCategories, toggleCategory }) {
  const isSelected = selectedCategories.includes(category.id);

  return (
    <button
      onClick={() => toggleCategory(category.id)}
      className={`px-2.5 py-0.5 rounded-full border transition-colors duration-200 cursor-pointer ${
        isSelected
          ? "bg-black text-white font-semibold border-2 border-black"
          : "border-2 border-gray-200"
      }`}
    >
      {category.name}
    </button>
  );
}

function FilterSection({
  categories = [],
  selectedCategories,
  setSelectedCategories,
  minPrice,
  setMinPrice,
  maxPrice,
  setMaxPrice,
  pageSize,
  setPageSize
}) {
  const [collapsed, setCollapsed] = useState(false);

  const toggleCategory = (id) => {
    setSelectedCategories((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  return (
    <div className="w-full rounded-xl border-2 border-gray-300 outfit-regular h-fit">
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="w-full px-4 py-2 text-left text-sm font-medium flex items-center justify-between cursor-pointer"
      >
        <span>
          Filters <FontAwesomeIcon icon={faFilter} />
        </span>
        <FontAwesomeIcon icon={collapsed ? faChevronDown : faChevronUp} />
      </button>

      {!collapsed && (
        <div className="px-4 pb-4 space-y-3 text-xs">
          <div className="space-y-1">
            <div className="font-medium text-gray-800">Category</div>
            <div className="flex flex-wrap gap-1.5">
              {categories.length > 0 ? (
                categories.map((category) => (
                  <CategoryButton
                    key={category.id}
                    category={category}
                    selectedCategories={selectedCategories}
                    toggleCategory={toggleCategory}
                  />
                ))
              ) : (
                <div className="text-gray-500 text-[11px]">No categories found</div>
              )}
            </div>
          </div>

          <div className="space-y-1">
            <div className="font-medium text-gray-800">Price Range</div>
            <div className="flex items-center gap-2">
              <div>
                <span className="text-[11px] text-gray-700 me-1">₹</span>
                <input
                  type="number"
                  value={minPrice}
                  onChange={(e) => setMinPrice(Number(e.target.value))}
                  placeholder="Min"
                  className="px-2 py-1 rounded-full border w-20 border-gray-300 text-[11px] outline-none"
                />
              </div>
              <span className="text-[12px] text-gray-700">to</span>
              <div>
                <span className="text-[11px] text-gray-700 me-1">₹</span>
                <input
                  type="number"
                  value={maxPrice}
                  onChange={(e) => setMaxPrice(Number(e.target.value))}
                  placeholder="Max"
                  className="px-2 py-1 rounded-full border w-20 border-gray-300 text-[11px] outline-none"
                />
              </div>
            </div>
          </div>

          {pageSize !== undefined && setPageSize && (
            <div className="space-y-1">
              <div className="font-medium text-gray-800">Page Size</div>
              <input
                type="number"
                value={pageSize}
                onChange={(e) => setPageSize(Number(e.target.value))}
                className="px-2 py-1 rounded-full border border-gray-300 text-[11px] outline-none w-20"
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FilterSection;
