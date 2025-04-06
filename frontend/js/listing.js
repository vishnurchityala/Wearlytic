document.addEventListener("DOMContentLoaded", async function () {
    const apiUrlBase = "https://wearlytic-backend.vercel.app/api/products";
    const listingsContainer = document.getElementById("listings");
    const loader = document.getElementById("loader");
    const sortSelect = document.getElementById("sortProducts");
    const materialSelect = document.getElementById("selectMaterial");
    const materialSelectModal = document.getElementById("selectMaterialModal");
    let currentPage = 1;
    let productList = [];
    let originalProductList = [];

    async function fetchProducts(page = 1, perPage = 12) {
        try {
            showLoader();
            const url = new URL(apiUrlBase);
            url.searchParams.append('page', page);
            url.searchParams.append('per_page', perPage);
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error("Failed to fetch products");
            }
            const data = await response.json();
            originalProductList = data.products || [];
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

    function extractPrice(priceString) {
        return parseFloat(priceString.replace(/[^0-9.]/g, '')) || 0;
    }

    function sortProducts(order) {
        if (order === "low-high") {
            productList.sort((a, b) => extractPrice(a.price) - extractPrice(b.price));
        } else if (order === "high-low") {
            productList.sort((a, b) => extractPrice(b.price) - extractPrice(a.price));
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