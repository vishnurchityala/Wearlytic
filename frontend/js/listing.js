document.addEventListener("DOMContentLoaded", async function () {
    const apiUrlBase = "https://wearlytic-backend.vercel.app/api/products";
    const listingsContainer = document.getElementById("listings");
    const loader = document.getElementById("loader");
    const sortSelect = document.getElementById("sortProducts");
    const materialSelect = document.getElementById("selectMaterial");
    const materialSelectModal = document.getElementById("selectMaterialModal");
    const searchInput = document.querySelector('.input-group input[type="text"]');
    const modalSearchInput = document.querySelector('#filterModal .input-group input[type="text"]');
    const minPriceInput = document.getElementById("minPrice");
    const maxPriceInput = document.getElementById("maxPrice");
    const modalMinPrice = document.getElementById("modalMinPrice");
    const modalMaxPrice = document.getElementById("modalMaxPrice");
    const categorySelect = document.getElementById("selectCategory");
    const categorySelectModal = document.getElementById("selectCategoryModal");
    const colorFilters = document.getElementById("colorFilters");
    const colorFiltersModal = document.getElementById("colorFiltersModal");
    const pageSizeSelect = document.getElementById("pageSize");
    const pageSizeSelectModal = document.getElementById("pageSizeModal");
    let currentPage = 1;
    let itemsPerPage = 12;
    let productList = [];
    let originalProductList = [];
    let searchTimeout;
    let priceTimeout;

    // Helper function to extract numeric price from string
    function extractNumericPrice(priceString) {
        if (!priceString) return 0;
        // Remove rupee symbol and any other non-numeric characters except decimal point
        const numericValue = priceString.replace(/[^0-9.]/g, '');
        return parseFloat(numericValue) || 0;
    }

    function populateCategoryFilter() {
        const categories = new Set(["all"]);
        originalProductList.forEach(product => {
            if (product.category) {
                categories.add(product.category.toLowerCase());
            }
        });

        const categoryOptions = Array.from(categories)
            .map(category => `<option value="${category}">${category.charAt(0).toUpperCase() + category.slice(1)}</option>`)
            .join('');

        categorySelect.innerHTML = categoryOptions;
        categorySelectModal.innerHTML = categoryOptions;
    }

    function filterByCategory(category) {
        if (category === "all") {
            productList = [...originalProductList];
        } else {
            productList = originalProductList.filter(product => 
                product.category && product.category.toLowerCase() === category
            );
        }
        populateContainer();
    }

    function populateColorFilters() {
        const colors = new Set(["all"]);
        originalProductList.forEach(product => {
            if (product.colors && Array.isArray(product.colors)) {
                product.colors.forEach(color => {
                    if (color) {
                        colors.add(color.toLowerCase());
                    }
                });
            }
        });

        const colorOptions = Array.from(colors)
            .map(color => {
                const colorClass = color === 'all' ? 'bg-light border' : `bg-${color}`;
                return `
                    <label class="color-radio">
                        <input type="radio" name="color" value="${color}" ${color === 'all' ? 'checked' : ''}>
                        <span class="color-circle ${colorClass}">${color === 'all' ? 'All' : ''}</span>
                    </label>
                `;
            })
            .join('');

        colorFilters.innerHTML = colorOptions;
        colorFiltersModal.innerHTML = colorOptions.replace(/name="color"/g, 'name="modalColor"');
    }

    function filterByColor(color) {
        if (color === "all") {
            productList = [...originalProductList];
        } else {
            productList = originalProductList.filter(product => 
                product.colors && 
                Array.isArray(product.colors) && 
                product.colors.some(c => c.toLowerCase() === color)
            );
        }
        populateContainer();
    }

    async function fetchProducts(page = 1, perPage = itemsPerPage, searchTerm = '', minPrice = 0, maxPrice = null, category = 'all', color = 'all') {
        try {
            showLoader();
            const url = new URL(apiUrlBase);
            url.searchParams.append('page', page);
            url.searchParams.append('per_page', perPage);
            
            if (searchTerm) {
                url.searchParams.append('search', searchTerm);
            }
            if (minPrice !== null && minPrice !== '') {
                url.searchParams.append('min_price', minPrice);
            }
            if (maxPrice !== null && maxPrice !== '') {
                url.searchParams.append('max_price', maxPrice);
            }
            if (category !== 'all') {
                url.searchParams.append('category', category);
            }
            if (color !== 'all') {
                url.searchParams.append('color', color);
            }
            
            console.log('API Request URL:', url.toString());
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error("Failed to fetch products");
            }
            const data = await response.json();
            
            console.log('API Response:', {
                totalProducts: data.products ? data.products.length : 0,
                pagination: data.pagination,
                firstProduct: data.products && data.products.length > 0 ? data.products[0] : null
            });
            
            // Check if we have products in the response
            if (!data.products || data.products.length === 0) {
                console.warn('No products returned from API for search term:', searchTerm);
                // Try a direct fetch to see if it's a caching issue
                const directUrl = new URL(apiUrlBase);
                directUrl.searchParams.append('search', searchTerm);
                console.log('Trying direct fetch with URL:', directUrl.toString());
                
                const directResponse = await fetch(directUrl);
                const directData = await directResponse.json();
                console.log('Direct API Response:', {
                    totalProducts: directData.products ? directData.products.length : 0,
                    pagination: directData.pagination
                });
                
                // Use the direct response data if it has products
                if (directData.products && directData.products.length > 0) {
                    console.log('Using direct response data instead');
                    data.products = directData.products;
                    data.pagination = directData.pagination;
                }
            }
            
            // Filter products based on price range
            let filteredProducts = data.products || [];
            if (minPrice !== null && minPrice !== '') {
                filteredProducts = filteredProducts.filter(product => 
                    extractNumericPrice(product.price) >= minPrice
                );
            }
            if (maxPrice !== null && maxPrice !== '') {
                filteredProducts = filteredProducts.filter(product => 
                    extractNumericPrice(product.price) <= maxPrice
                );
            }
            
            console.log('After price filtering:', filteredProducts.length, 'products');
            
            originalProductList = filteredProducts;
            productList = [...originalProductList];
            
            console.log('Product list before filters:', productList.length, 'products');
            
            populateMaterialFilter();
            populateCategoryFilter();
            populateColorFilters();
            renderPagination(data.pagination);
            
            console.log('Before applying filters:', productList.length, 'products');
            applyFilters();
            console.log('After applying filters:', productList.length, 'products');
            
            // Make sure to call populateContainer after all filters are applied
            populateContainer();
        } catch (error) {
            console.error("Error fetching products:", error);
        } finally {
            hideLoader();
        }
    }

    function populateContainer() {
        showLoader();
        console.log('Populating container with', productList.length, 'products');
        listingsContainer.innerHTML = "";
        const currentDate = new Date().toLocaleDateString();
        
        if (productList.length === 0) {
            console.log('No products to display');
            listingsContainer.innerHTML = '<div class="col-12 text-center"><p>No products found matching your criteria.</p></div>';
            hideLoader();
            return;
        }
        
        productList.forEach(product => {
            const colorCircles = (product.colors || []).map(color => 
                `<span class="color-circle d-inline-block" style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; flex-shrink: 0;"></span>`
            ).join('');
            
            const truncatedName = product.product_name && product.product_name.length > 40 
                ? product.product_name.substring(0, 37) + "..." 
                : product.product_name || "Unnamed Product";

            const productCard = `
                <div class="col-12 col-md-6 col-lg-3 mb-3">
                    <div class="card shadow-sm border-0 rounded-3 p-2">
                        <img src="${product.image_url || ''}" class="card-img-top rounded-3" alt="${product.product_name || 'Product Image'}" style="height: 200px; object-fit: cover;">
                        <div class="card-body p-2">
                            <p class="fw-bold text-dark mb-1 small">${product.price || 'N/A'}</p>
                            <h6 class="fw-semibold mb-1 small" title="${product.product_name || ''}">${truncatedName}</h6>
                            <p class="text-muted mb-2 small">Source: <a href="${product.source || '#'}" target="_blank" class="text-decoration-none small">${product.source || 'Unknown'}</a></p>
                            <p class="text-muted mb-2 small">Date Fetched: ${currentDate}</p>
                            <div class="d-flex align-items-center justify-content-between">
                                <div class="color-options d-flex overflow-auto">
                                    ${colorCircles}
                                </div>
                                <span class="badge bg-light text-black border-gray fw-semibold x-small rounded-pill">${product.material || 'N/A'}</span>
                            </div>
                            <div class="d-flex justify-content-between mt-3">
                                <a href="${product.product_url || '#'}" target="_blank" class="btn btn-sm btn-dark rounded-pill fw-semibold px-3 small">View Product</a>
                            </div>
                        </div>
                    </div>
                </div>`;

            listingsContainer.innerHTML += productCard;
        });
        console.log('Container populated with', productList.length, 'products');
        hideLoader();
    }

    function sortProducts(order) {
        if (order === "low-high") {
            productList.sort((a, b) => extractNumericPrice(a.price) - extractNumericPrice(b.price));
        } else if (order === "high-low") {
            productList.sort((a, b) => extractNumericPrice(b.price) - extractNumericPrice(a.price));
        }
        populateContainer();
    }

    function populateMaterialFilter() {
        const materials = new Set(["all"]);
        originalProductList.forEach(product => {
            if (product.material) {
                materials.add(product.material.toLowerCase());
            }
        });

        const materialOptions = Array.from(materials)
            .map(material => `<option value="${material}">${material.charAt(0).toUpperCase() + material.slice(1)}</option>`)
            .join('');

        materialSelect.innerHTML = materialOptions;
        materialSelectModal.innerHTML = materialOptions;
    }

    function filterByMaterial(material) {
        if (material === "all") {
            productList = [...originalProductList];
        } else {
            productList = originalProductList.filter(product => product.material && product.material.toLowerCase() === material);
        }
        populateContainer();
    }

    function renderPagination(pagination) {
        const { page, total_pages, links } = pagination;
        currentPage = page;

        // Get current filter values
        const currentSearchTerm = searchInput.value.trim();
        const currentMinPrice = minPriceInput.value ? parseInt(minPriceInput.value) : 0;
        const currentMaxPrice = maxPriceInput.value ? parseInt(maxPriceInput.value) : null;
        const currentCategory = categorySelect.value;
        const selectedColor = document.querySelector('input[name="color"]:checked').value;

        // Update mobile pagination buttons
        document.getElementById("prevPage").onclick = function (event) {
            event.preventDefault();
            if (links.prev) {
                fetchProducts(
                    page - 1,
                    itemsPerPage,
                    currentSearchTerm,
                    currentMinPrice,
                    currentMaxPrice,
                    currentCategory,
                    selectedColor
                );
            }
        };
        document.getElementById("nextPage").onclick = function (event) {
            event.preventDefault();
            if (links.next) {
                fetchProducts(
                    page + 1,
                    itemsPerPage,
                    currentSearchTerm,
                    currentMinPrice,
                    currentMaxPrice,
                    currentCategory,
                    selectedColor
                );
            }
        };

        // Update desktop pagination buttons
        document.getElementById("prevPage1").onclick = function (event) {
            event.preventDefault();
            if (links.prev) {
                fetchProducts(
                    page - 1,
                    itemsPerPage,
                    currentSearchTerm,
                    currentMinPrice,
                    currentMaxPrice,
                    currentCategory,
                    selectedColor
                );
            }
        };
        document.getElementById("nextPage1").onclick = function (event) {
            event.preventDefault();
            if (links.next) {
                fetchProducts(
                    page + 1,
                    itemsPerPage,
                    currentSearchTerm,
                    currentMinPrice,
                    currentMaxPrice,
                    currentCategory,
                    selectedColor
                );
            }
        };

        // Disable/enable buttons based on current page
        const prevButtons = [document.getElementById("prevPage"), document.getElementById("prevPage1")];
        const nextButtons = [document.getElementById("nextPage"), document.getElementById("nextPage1")];

        prevButtons.forEach(btn => {
            btn.classList.toggle("disabled", !links.prev);
            btn.style.pointerEvents = links.prev ? "auto" : "none";
            btn.style.opacity = links.prev ? "1" : "0.5";
        });

        nextButtons.forEach(btn => {
            btn.classList.toggle("disabled", !links.next);
            btn.style.pointerEvents = links.next ? "auto" : "none";
            btn.style.opacity = links.next ? "1" : "0.5";
        });
    }

    function applyFilters() {
        sortProducts(sortSelect.value);
        filterByMaterial(materialSelect.value);
        filterByCategory(categorySelect.value);
        const selectedColor = document.querySelector('input[name="color"]:checked').value;
        filterByColor(selectedColor);
    }

    function showLoader() {
        if (loader) loader.style.display = "flex";
    }

    function hideLoader() {
        if (loader) loader.style.display = "none";
    }

    function handleSearch() {
        const searchTerm = this.value.trim();
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const selectedColor = document.querySelector('input[name="color"]:checked').value;
            console.log('Search parameters:', {
                searchTerm,
                minPrice: parseInt(minPriceInput.value) || 0,
                maxPrice: parseInt(maxPriceInput.value) || null,
                category: categorySelect.value,
                color: selectedColor
            });
            fetchProducts(
                1, 
                itemsPerPage, 
                searchTerm, 
                parseInt(minPriceInput.value) || 0, 
                parseInt(maxPriceInput.value) || null,
                categorySelect.value,
                selectedColor
            );
        }, 1000);
    }

    function handlePriceChange() {
        const minPrice = minPriceInput.value ? parseInt(minPriceInput.value) : 0;
        const maxPrice = maxPriceInput.value ? parseInt(maxPriceInput.value) : null;
        
        // Validate prices
        if (minPrice < 0) {
            minPriceInput.value = 0;
        }
        if (minPrice !== null && maxPrice !== null && minPrice > maxPrice) {
            minPriceInput.value = maxPrice;
        }
        
        clearTimeout(priceTimeout);
        priceTimeout = setTimeout(() => {
            const selectedColor = document.querySelector('input[name="color"]:checked').value;
            fetchProducts(
                1, 
                itemsPerPage, 
                searchInput.value.trim(), 
                minPrice, 
                maxPrice,
                categorySelect.value,
                selectedColor
            );
        }, 1000);
    }

    // Add event listeners for search
    searchInput.addEventListener('input', handleSearch);
    modalSearchInput.addEventListener('input', function() {
        searchInput.value = this.value;
        handleSearch.call(this);
    });

    // Add event listeners for price inputs
    minPriceInput.addEventListener('input', handlePriceChange);
    maxPriceInput.addEventListener('input', handlePriceChange);
    modalMinPrice.addEventListener('input', function() {
        minPriceInput.value = this.value;
        handlePriceChange();
    });
    modalMaxPrice.addEventListener('input', function() {
        maxPriceInput.value = this.value;
        handlePriceChange();
    });

    sortSelect.addEventListener("change", function () {
        sortProducts(this.value);
    });

    materialSelect.addEventListener("change", function () {
        materialSelectModal.value = this.value;
        filterByMaterial(this.value);
    });

    materialSelectModal.addEventListener("change", function () {
        materialSelect.value = this.value;
        filterByMaterial(this.value);
    });

    // Add event listeners for category selection
    categorySelect.addEventListener("change", function () {
        categorySelectModal.value = this.value;
        filterByCategory(this.value);
    });

    categorySelectModal.addEventListener("change", function () {
        categorySelect.value = this.value;
        filterByCategory(this.value);
    });

    // Add event listeners for color selection
    colorFilters.addEventListener("change", function(e) {
        if (e.target.name === 'color') {
            const selectedColor = e.target.value;
            const modalInput = document.querySelector(`input[name="modalColor"][value="${selectedColor}"]`);
            if (modalInput) {
                modalInput.checked = true;
            }
            filterByColor(selectedColor);
        }
    });

    colorFiltersModal.addEventListener("change", function(e) {
        if (e.target.name === 'modalColor') {
            const selectedColor = e.target.value;
            const mainInput = document.querySelector(`input[name="color"][value="${selectedColor}"]`);
            if (mainInput) {
                mainInput.checked = true;
            }
            filterByColor(selectedColor);
        }
    });

    // Add event listeners for page size selection
    pageSizeSelect.addEventListener("change", function() {
        pageSizeSelectModal.value = this.value;
        itemsPerPage = parseInt(this.value);
        handlePageSizeChange();
    });

    pageSizeSelectModal.addEventListener("change", function() {
        pageSizeSelect.value = this.value;
        itemsPerPage = parseInt(this.value);
        handlePageSizeChange();
    });

    function handlePageSizeChange() {
        currentPage = 1; // Reset to first page when changing page size
        const searchTerm = searchInput.value.trim();
        const minPrice = minPriceInput.value ? parseInt(minPriceInput.value) : null;
        const maxPrice = maxPriceInput.value ? parseInt(maxPriceInput.value) : null;
        const selectedColor = document.querySelector('input[name="color"]:checked').value;
        
        fetchProducts(
            currentPage,
            itemsPerPage,
            searchTerm,
            minPrice,
            maxPrice,
            categorySelect.value,
            selectedColor
        );
    }

    await fetchProducts(currentPage);
    populateContainer();
});