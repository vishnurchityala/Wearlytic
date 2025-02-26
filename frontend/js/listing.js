
document.addEventListener("DOMContentLoaded", function () {
function updatePriceInputs(value, isMobile = false) {
    if (isMobile) {
        document.getElementById("mobileMinPrice").value = 0;
        document.getElementById("mobileMaxPrice").value = value;
    } else {
        document.getElementById("minPrice").value = 0;
        document.getElementById("maxPrice").value = value;
    }
}

function updatePriceSlider(isMobile = false) {
    if (isMobile) {
        let minPrice = parseInt(document.getElementById("mobileMinPrice").value);
        let maxPrice = parseInt(document.getElementById("mobileMaxPrice").value);
        document.getElementById("mobilePriceRange").value = maxPrice;
    } else {
        let minPrice = parseInt(document.getElementById("minPrice").value);
        let maxPrice = parseInt(document.getElementById("maxPrice").value);
        document.getElementById("priceRange").value = maxPrice;
    }
}

document.getElementById("priceRange").addEventListener("input", function () {
    updatePriceInputs(this.value);
});
document.getElementById("minPrice").addEventListener("input", function () {
    updatePriceSlider();
});
document.getElementById("maxPrice").addEventListener("input", function () {
    updatePriceSlider();
});

document.getElementById("mobilePriceRange").addEventListener("input", function () {
    updatePriceInputs(this.value, true);
});
document.getElementById("mobileMinPrice").addEventListener("input", function () {
    updatePriceSlider(true);
});
document.getElementById("mobileMaxPrice").addEventListener("input", function () {
    updatePriceSlider(true);
});
});

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
        }
        ,
        {
            id: 7,
            name: "Backpack",
            price: 90,
            image: "https://picsum.photos/250/200?random=6",
            category: "accessories",
            source: "bagshop.com"
        }
        ,
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
        listingsContainer.innerHTML = ""; // Clear existing content

        products.forEach((product, index) => {
            const productCard = `
                <div class="col-12 col-md-6 col-lg-3 mb-3">
                    <div class="card shadow-sm border-0 rounded-3 p-2">
                        <img id="product-image-${index}" src="${product.image}" class="card-img-top rounded-3" alt="${product.name}" style="height: 200px; object-fit: cover;">
                        <div class="card-body p-2">
                            <p class="fw-bold text-dark mb-1 small">$${product.price}</p>
                            <h6 class="fw-semibold mb-1 small">${product.name}</h6>
                            <p class="text-muted mb-2 small">Source: <a href="https://${product.source}" target="_blank" class="text-decoration-none small">${product.source}</a></p>
                            <div class="d-flex justify-content-between">
                                <button class="btn btn-sm btn-dark rounded-pill px-2">View Product</button>
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

    renderListings(products);
});
