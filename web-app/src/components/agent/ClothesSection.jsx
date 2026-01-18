import FilterSection from "./FilterSection";
import { useState } from "react";

function ClothesSection({ categories, selectedProducts }) {
  const [products, setProducts] = useState([]);
  const [categoriesSelected, setCategoriesSelected] = useState([]);
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(3000);
  const [pageSize, setPageSize] = useState(100);

  return (
    <div className="p-2 h-full overflow-y-scroll flex flex-col gap-2">
      <FilterSection
        categories={categories}
        selectedCategories={categoriesSelected}
        setSelectedCategories={setCategoriesSelected}
        minPrice={minPrice}
        setMinPrice={setMinPrice}
        maxPrice={maxPrice}
        setMaxPrice={setMaxPrice}
        pageSize={pageSize}
        setPageSize={setPageSize}
      />
    </div>
  );
}

export { ClothesSection };
