import { ClothesSection } from "./ClothesSection";
import { PlaygroundSection } from "./PlaygroundSection";
import { Group, Separator, Panel } from "react-resizable-panels";
import { useEffect, useState } from "react";
import { useAuth } from "../../auth/AuthProvider";

function MainContent() {
  const { token } = useAuth();
  const [categories, setCategories] = useState([]);
  const [selectedProducts, setSelectedProducts] = useState([]);

  useEffect(() => {
    async function fetchCategories() {
      setCategories([
        { id: "1", name: "T-Shirt" },
        { id: "2", name: "Shirt" },
        { id: "3", name: "Pants" },
      ]);
    }
    fetchCategories();
  }, []);

  const [generations, setGenerations] = useState([]);

  return (
    <div className="border-t-2 border-gray-300 h-screen flex flex-col">
      {/* Mobile layout: dynamic full-height scroll */}
      <div className="flex flex-col md:hidden h-full overflow-y-auto">
        <ClothesSection
            categories={categories}
            selectedProducts={selectedProducts}
        />
        <div className="h-full">
          <PlaygroundSection />
        </div>
      </div>

      {/* Desktop layout: horizontal resizable panels */}
      <div className="hidden md:flex h-full">
        <Group direction="horizontal" className="h-full w-full">
          <Panel className="h-full" minSize="20%" defaultSize={40}>
            <ClothesSection
              categories={categories}
              selectedProducts={selectedProducts}
            />
          </Panel>
          <Separator className="w-1 bg-gray-300 cursor-col-resize" />
          <Panel className="h-full" minSize="30%" defaultSize={40}>
            <PlaygroundSection />
          </Panel>
        </Group>
      </div>
    </div>
  );
}

export { MainContent };
