document.addEventListener("DOMContentLoaded", function () {
    const products = [
        {
            id: 1,
            name: "Classic White T-Shirt",
            price: 25,
            image: "https://picsum.photos/250/200?random=1",
            category: "clothing",
            source: "example.com"
        },
        {
            id: 2,
            name: "Leather Watch",
            price: 150,
            image: "https://picsum.photos/250/200?random=2",
            category: "accessories",
            source: "watchstore.com"
        },
        {
            id: 3,
            name: "Running Shoes",
            price: 80,
            image: "https://picsum.photos/250/200?random=3",
            category: "footwear",
            source: "shoemarket.com"
        },
        {
            id: 4,
            name: "Sunglasses",
            price: 50,
            image: "https://picsum.photos/250/200?random=4",
            category: "accessories",
            source: "sunglassshop.com"
        },
        {
            id: 5,
            name: "Denim Jacket",
            price: 120,
            image: "https://picsum.photos/250/200?random=5",
            category: "clothing",
            source: "fashionstore.com"
        },
        {
            id: 6,
            name: "Backpack",
            price: 90,
            image: "https://picsum.photos/250/200?random=6",
            category: "accessories",
            source: "bagshop.com"
        },
        {
            id: 7,
            name: "Backpack",
            price: 90,
            image: "https://picsum.photos/250/200?random=6",
            category: "accessories",
            source: "bagshop.com"
        },
        {
            id: 8,
            name: "Backpack",
            price: 90,
            image: "https://picsum.photos/250/200?random=6",
            category: "accessories",
            source: "bagshop.com"
        }
    ];

    function renderListings(products) {
        const listingsContainer = document.getElementById("listings");
        listingsContainer.innerHTML = "";

        const currentDate = new Date().toLocaleDateString();

        products.forEach((product, index) => {
            const productCard = `
                <div class="col-12 col-md-6 col-lg-3 mb-3">
                    <div class="card shadow-sm border-0 rounded-3 p-2">
                        <img id="product-image-${index}" src="${product.image}" class="card-img-top rounded-3" alt="${product.name}" style="height: 200px; object-fit: cover;">
                        <div class="card-body p-2">
                            <p class="fw-bold text-dark mb-1 small">$${product.price}</p>
                            <h6 class="fw-semibold mb-1 small">${product.name}</h6>
                            <p class="text-muted mb-2 small">Source: <a href="https://${product.source}" target="_blank" class="text-decoration-none small">${product.source}</a></p>
                            <p class="text-muted mb-2 small">Date Fetched: ${currentDate}</p>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-sm btn-dark rounded-pill px-3 small">View Product</button>
                                <button class="btn btn-sm btn-outline-secondary rounded-pill px-2 refresh-btn" data-index="${index}">
                                    <i class="fas fa-sync-alt"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            listingsContainer.innerHTML += productCard;
        });

        document.querySelectorAll(".refresh-btn").forEach(button => {
            button.addEventListener("click", function () {
                const index = this.getAttribute("data-index");
                refreshProduct(index);
            });
        });
    }

    function refreshProduct(index) {
        const newImageUrl = `https://picsum.photos/250/200?random=${Math.random() * 1000}`;
        document.getElementById(`product-image-${index}`).src = newImageUrl;
    }

    try {
        const priceRangeSlider = document.getElementById("priceRange");
        const minPriceInput = document.getElementById("minPrice");
        const maxPriceInput = document.getElementById("maxPrice");

        if (priceRangeSlider && minPriceInput && maxPriceInput) {
            priceRangeSlider.value = maxPriceInput.value;

            priceRangeSlider.addEventListener("input", function () {
                maxPriceInput.value = this.value;
            });

            maxPriceInput.addEventListener("input", function () {
                if (parseInt(this.value) < parseInt(minPriceInput.value)) {
                    this.value = minPriceInput.value;
                }
                priceRangeSlider.value = this.value;
            });

            minPriceInput.addEventListener("input", function () {
                if (parseInt(this.value) > parseInt(maxPriceInput.value)) {
                    this.value = maxPriceInput.value;
                }
            });
        }

        const modalPriceRangeSlider = document.getElementById("modalPriceRange");
        const modalMinPriceInput = document.getElementById("modalMinPrice");
        const modalMaxPriceInput = document.getElementById("modalMaxPrice");

        if (modalPriceRangeSlider && modalMinPriceInput && modalMaxPriceInput) {
            modalPriceRangeSlider.value = modalMaxPriceInput.value;

            modalPriceRangeSlider.addEventListener("input", function () {
                modalMaxPriceInput.value = this.value;
            });

            modalMaxPriceInput.addEventListener("input", function () {
                modalPriceRangeSlider.value = this.value;
            });

            modalMinPriceInput.addEventListener("input", function () {
                if (parseInt(this.value) > parseInt(modalMaxPriceInput.value)) {
                    this.value = modalMaxPriceInput.value;
                }
            });
        }
    } catch (error) {
        console.error("Error setting up price range sliders:", error);
    }

    renderListings(products);
});
