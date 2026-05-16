import FilterSection from "./FilterSection";
import ProductSection from "./ProductSection";
import { useState,useEffect } from "react";
import { apiFetch } from "@/api/env";
import { useAuth } from "@/auth/AuthContext";

function ClothesSection({ categories, selectedProducts,setSelectedProducts,loading }) {
  const { token } = useAuth();
  const [products, setProducts] = useState([]);
  const [categoriesSelected, setCategoriesSelected] = useState([]);
  const [minPrice, setMinPrice] = useState(0);
  const [maxPrice, setMaxPrice] = useState(3000);
  const [pageSize, setPageSize] = useState(100);
  const [productLoading,setProductLoading] = useState(false);
  const [nextPage,setNextPage] = useState(null);
  const [prevPage,setPrevPage] = useState(null);

  async function fetchByUrl(url){
    if (!url) return;
    setProductLoading(true);
    try{
      const response = await apiFetch(url, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`,
        }
      });
      if (!response.ok) {
        throw new Error("Failed to fetch Products");
      }
      const data = await response.json();
      setProducts(data['results'] || []);
      setNextPage(data['next'] || null);
      setPrevPage(data['previous'] || null);
    } catch(error){
      console.error("Error fetching Products:", error);
    }
    setProductLoading(false);
  }

  useEffect(()=>{
    if (!token) return;

    async function fetchProducts() {
      setProductLoading(true);
      try{
        const categoryIds = categoriesSelected;

        const params = new URLSearchParams();

        if (categoryIds.length) {
            params.append("category_ids", categoryIds.join(","));
        }

        if (minPrice !== undefined) {
            params.append("min_price", minPrice);
        }

        if (maxPrice !== undefined) {
            params.append("max_price", maxPrice);
        }
        if (pageSize !== undefined) {
            params.append("page_size", pageSize);
        }
        const response = await apiFetch(`/api/products/?${params.toString()}`, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`,
          }
        });
        if (!response.ok) {
          throw new Error("Failed to fetch Products");
        }
        const data = await response.json();
        setProducts(data['results'] || []);
        setNextPage(data['next'] || null);
        setPrevPage(data['previous'] || null);
      }
      catch(error){
        console.error("Error fetching Products:", error);
      }
      setProductLoading(false);
    }
    fetchProducts();
  },[categoriesSelected,minPrice,maxPrice,pageSize,token]);

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
      <ProductSection 
        products={products} 
        loading={productLoading}
        selectedProducts={selectedProducts} 
        setSelectedProducts={setSelectedProducts} 
        nextPage={nextPage} 
        prevPage={prevPage}
        onFetchPage={fetchByUrl}
      />
    </div>
  );
}

export { ClothesSection };
