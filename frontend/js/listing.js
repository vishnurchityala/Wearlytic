document.addEventListener("DOMContentLoaded", async function () {
    const apiUrlBase = "https://wearlytic-backend.vercel.app/api/products/?format=json";
    const listingsContainer = document.getElementById("listings");
    let currentPageUrl = apiUrlBase; // Default API URL

    async function fetchProducts(pageUrl) {
        try {
            const response = await fetch(pageUrl);
            if (!response.ok) {
                throw new Error("Failed to fetch products");
            }
            const data = await response.json();
            renderListings(data.products);
            renderPagination(data.next_page, data.prev_page);
            currentPageUrl = pageUrl;
        } catch (error) {
            console.error("Error fetching products:", error);
        }
    }

    function renderListings(products) {
        if (!Array.isArray(products)) {
            console.error("Invalid products data. Expected an array.");
            return;
        }
        
        listingsContainer.innerHTML = "";
        const currentDate = new Date().toLocaleDateString();

        products.forEach((product, index) => {
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
    }

    function renderPagination(nextUrl, prevUrl) {

        document.getElementById("prevPage").addEventListener("click", function (event) {
            event.preventDefault();
            if (prevUrl) {
                fetchProducts(prevUrl);
            } else {
                console.log("No previous page available.");
            }
        });
        document.getElementById("nextPage").addEventListener("click", function (event) {
            event.preventDefault();
            if (nextUrl) fetchProducts(nextUrl);
        });
        document.getElementById("prevPage1").addEventListener("click", function (event) {
            event.preventDefault();
            if (prevUrl) {
                fetchProducts(prevUrl);
            } else {
                console.log("No previous page available.");
            }
        });
        document.getElementById("nextPage1").addEventListener("click", function (event) {
            event.preventDefault();
            if (nextUrl) fetchProducts(nextUrl);
        });
    }

    await fetchProducts(currentPageUrl);
});
