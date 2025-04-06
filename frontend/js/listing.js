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
    let currentPage = 1;
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

    async function fetchProducts(page = 1, perPage = 12, searchTerm = '', minPrice = null, maxPrice = null) {
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
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error("Failed to fetch products");
            }
            const data = await response.json();
            
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
            
            originalProductList = filteredProducts;
            productList = [...originalProductList];
            populateMaterialFilter();
            renderPagination(data.pagination);
            applyFilters();
        } catch (error) {
            console.error("Error fetching products:", error);
        } finally {
            hideLoader();
        }
    }

    function populateContainer() {
        showLoader();
        listingsContainer.innerHTML = "";
        const currentDate = new Date().toLocaleDateString();
        
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

        // Update mobile pagination buttons
        document.getElementById("prevPage").onclick = function (event) {
            event.preventDefault();
            if (links.prev) fetchProducts(page - 1);
        };
        document.getElementById("nextPage").onclick = function (event) {
            event.preventDefault();
            if (links.next) fetchProducts(page + 1);
        };

        // Update desktop pagination buttons
        document.getElementById("prevPage1").onclick = function (event) {
            event.preventDefault();
            if (links.prev) fetchProducts(page - 1);
        };
        document.getElementById("nextPage1").onclick = function (event) {
            event.preventDefault();
            if (links.next) fetchProducts(page + 1);
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
            fetchProducts(1, 12, searchTerm, parseInt(minPriceInput.value), parseInt(maxPriceInput.value) || null);
        }, 1000);
    }

    function handlePriceChange() {
        const minPrice = minPriceInput.value ? parseInt(minPriceInput.value) : null;
        const maxPrice = maxPriceInput.value ? parseInt(maxPriceInput.value) : null;
        
        // Validate prices
        if (minPrice !== null && minPrice < 0) {
            minPriceInput.value = 0;
        }
        if (minPrice !== null && maxPrice !== null && minPrice > maxPrice) {
            minPriceInput.value = maxPrice;
        }
        
        clearTimeout(priceTimeout);
        priceTimeout = setTimeout(() => {
            fetchProducts(1, 12, searchInput.value.trim(), minPrice, maxPrice);
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

    await fetchProducts(currentPage);
    populateContainer();
});