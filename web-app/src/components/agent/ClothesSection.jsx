import FilterSection from "./FilterSection";
import ProductSection from "./ProductSection";
import { useState,useEffect } from "react";
import { useAuth } from "../../auth/AuthProvider";

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
    const ensureHttps = (inputUrl) => {
      try {
        const u = new URL(inputUrl, window.location.origin);
        if (u.protocol === "http:") u.protocol = "https:";
        return u.toString();
      } catch {
        if (inputUrl.startsWith("//")) return `https:${inputUrl}`;
        return inputUrl.replace(/^http:/, "https:");
      }
    };
    const safeUrl = ensureHttps(url);
    setProductLoading(true);
    try{
      const response = await fetch(safeUrl, {
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
        const response = await fetch(`https://wearlytic-zbas.onrender.com/api/products/?${params.toString()}`, {
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
      <ProductSection 
        products={products} 
        loading={productLoading}
        selectedProducts={selectedProducts} 
        setSelectedProducts={setSelectedProducts} 
        nextPage={nextPage} 
        prevPage={prevPage}
        setNextPage={setNextPage}
        setPrevPage={setPrevPage}
        onFetchPage={fetchByUrl}
      />
    </div>
  );
}

export { ClothesSection };
