import { ClothesSection } from "./ClothesSection";
import { PlaygroundSection } from "./PlaygroundSection";
import { Group, Separator, Panel } from "react-resizable-panels";
import { useEffect, useState } from "react";
import { apiFetch } from "@/api/env";
import { useAuth } from "@/auth/AuthContext";

function MainContent() {
  const { token } = useAuth();
  const [categories, setCategories] = useState([]);
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [loading,setLoading] = useState(false);

  useEffect(() => {
    if (!token) return;

    async function fetchCategories() {
      setLoading(true);
      try{
        const response = await apiFetch("/api/categories", {
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
        setCategories(data);
      }
      catch(error){
        console.error("Error fetching categories:", error);
      }
      setLoading(false);
    }
    fetchCategories();
  }, [token]);

  return (
    <div className="border-t-2 border-gray-300 h-[91%] flex flex-col min-h-0">
      <div className="flex flex-col md:hidden h-full overflow-y-auto">
        <div>
          <ClothesSection
            categories={categories}
            selectedProducts={selectedProducts}
            loading={loading}
            setSelectedProducts={setSelectedProducts}
          />
        </div>
        <div className="h-full">
          <PlaygroundSection selectedProducts={selectedProducts}/>
        </div>
      </div>
      <div className="hidden md:flex h-full min-h-0">
        <Group direction="horizontal" className="h-full w-full">
          <Panel className="h-full min-h-0" minSize="20%" defaultSize={40}>
            <ClothesSection
              categories={categories}
              selectedProducts={selectedProducts}
              loading={loading}
              setSelectedProducts={setSelectedProducts}
            />
          </Panel>
          <Separator className="w-1 bg-gray-300 cursor-col-resize" />
          <Panel className="h-full min-h-0" minSize="30%" defaultSize={40}>
            <PlaygroundSection selectedProducts={selectedProducts}/>
          </Panel>
        </Group>
      </div>
    </div>
  );
}

export { MainContent };
