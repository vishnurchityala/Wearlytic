import { useState } from "react";
import { FiltersBar } from "./FiltersBar";
import { ProductList } from "./ProductList";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faChevronDown, faChevronUp, faFilter } from "@fortawesome/free-solid-svg-icons";

function ClothesSection() {
    const [showFilters, setShowFilters] = useState(true);

    return (
        <div className="w-full bg-white rounded-lg shadow-md overflow-hidden flex flex-col">

            <div className="border border-gray-300 shadow-sm rounded-lg ms-3 outfit-regular me-3">

                <div
                    className="flex items-center justify-between px-4 py-3 cursor-pointer"
                    onClick={() => setShowFilters(!showFilters)}
                >
                    <span className="text-sm font-medium text-gray-800"><FontAwesomeIcon icon={faFilter} className="me-1 text-xs" />Filters</span>
                    <FontAwesomeIcon 
                        icon={showFilters ? faChevronUp : faChevronDown} 
                        className="text-gray-800" 
                    />
                </div>

                {showFilters && <FiltersBar />}

            </div>


            <div className="flex-1 overflow-y-auto px-4 py-4">
                <ProductList />
            </div>

        </div>
    );
}

export { ClothesSection };
