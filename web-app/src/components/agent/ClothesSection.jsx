import FilterSection from "./FilterSection";
import ProductSection from "./ProductSection";
import { useState,useEffect } from "react";
import { useAuth } from "../../auth/AuthProvider";

function ClothesSection({ categories, selectedProducts,loading }) {
  const { token } = useAuth();
  const [products, setProducts] = useState([]);
  const [categoriesSelected, setCategoriesSelected] = useState([]);
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(3000);
  const [pageSize, setPageSize] = useState(100);
  const [productLoading,setProductLoading] = useState(false);

  useEffect(()=>{
    async function fetchProducts() {
      setProductLoading(true);
      try{
        const response = await fetch("https://wearlytic-zbas.onrender.com/api/products", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          },
        });
        if (!response.ok) {
          throw new Error("Failed to fetch categories");
        }
        const data = await response.json();
        console.log(data);
        setProducts(data['results']);
      }
      catch(error){
        console.error("Error fetching categories:", error);
      }
      setProductLoading(false);
    }
    fetchProducts();
  },[categoriesSelected,minPrice,maxPrice,pageSize]);
  
  if (loading) {
        return (
        <div className="flex justify-center items-center h-screen">
            <div className="w-10 h-10 border-4 border-t-black border-gray-300 rounded-full animate-spin"></div>
        </div>
        );
  }
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
      <ProductSection products={products} loading={productLoading}/>
    </div>
  );
}

export { ClothesSection };
