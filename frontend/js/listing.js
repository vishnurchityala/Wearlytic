document.addEventListener("DOMContentLoaded", function () {
    const products = [
        { id: 1, name: "BLIVE Printed Men Hooded Neck Dark Green T-Shirt", price: 259, image: "https://rukminim2.flixcart.com/image/832/832/xif0q/t-shirt/m/f/d/s-bogrhdful-z136-blive-original-imah8tc9ah944hcg.jpeg?q=70&crop=false", category: "T-shirts", source: "flipkart.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Hooded Neck", product_url: "https://www.flipkart.com/blive-printed-men-hooded-neck-dark-green-t-shirt/p/itm013161f222511?pid=TSHH8ZY3G6HCRUJS" },
        { id: 2, name: "PrintHolic Solid Couple Polo Neck White T-Shirt", price: 284, image: "https://rukminim2.flixcart.com/image/832/832/xif0q/t-shirt/2/k/6/s-aa-tvs-t-shirt-s-printholic-original-imah7skuenyzggdx.jpeg?q=70&crop=false", category: "T-shirts", source: "flipkart.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Polo Neck", product_url: "https://www.flipkart.com/printholic-solid-couple-polo-neck-white-t-shirt/p/itmb6e65731f88d4?pid=TSHGWRW8RJTAUWZK" },
        { id: 3, name: "rizim Geometric Print Men Polo Neck Black T-Shirt", price: 379, image: "https://rukminim2.flixcart.com/image/832/832/xif0q/t-shirt/c/b/u/l-men-temu-polo-001-rizim-original-imah5yz96xfqphkc.jpeg?q=70&crop=false", category: "T-shirts", source: "flipkart.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Polo Neck", product_url: "https://www.flipkart.com/rizim-geometric-print-men-polo-neck-black-t-shirt/p/itm7140df0459e89?pid=TSHH5YZ9FYJVUSZ9" },
        { id: 4, name: "United Colors of Benetton Boys Striped Polo Collar Pure Cotton Pockets T-Shirt", price: 727, image: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/28099402/2024/3/7/093ca633-5780-40f9-861c-163848cafaed1709822034991UnitedColorsofBenettonBoysStripedPoloCollarPureCottonPockets1.jpg", category: "T-shirts", source: "myntra.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Pure Cotton", product_url: "https://www.myntra.com/tshirts/united+colors+of+benetton/united-colors-of-benetton-boys-striped-polo-collar-pure-cotton-pockets-t-shirt/28099402/buy" },
        { id: 5, name: "United Colors of Benetton Boys Polo Collar Cotton T-Shirt", price: 1799, image: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/25427528/2023/10/10/a613c195-2a63-4388-89f9-7f0e9938343b1696938143339UnitedColorsofBenettonBoysBluePoloCollarPocketsT-shirt1.jpg", category: "T-shirts", source: "myntra.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Cotton", product_url: "https://www.myntra.com/tshirts/united+colors+of+benetton/united-colors-of-benetton-boys-polo-collar-cotton-t-shirt/25427528/buy" },
        { id: 6, name: "t-base Men Blue Solid Crew Neck T-Shirt", price: 974, image: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/19438244/2022/8/9/b308cea5-4f62-42ed-bcfa-d9e094533b7c1659984688665t-baseMenEstateBlueCrewNeckSolidCottont-shirt1.jpg", category: "T-shirts", source: "myntra.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Cotton", product_url: "https://www.myntra.com/tshirts/t-base/t-base-men-blue-solid-crew-neck-t-shirt/19438244/buy" },
        { id: 7, name: "H&M Spread Collar Twill Shirt", price: 1274, image: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/2024/OCTOBER/28/2mRIcEMe_811af75d670e4fd29678ad36e925aa94.jpg", category: "Shirts", source: "myntra.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Twill", product_url: "https://www.myntra.com/shirts/h%26m/-hm-spread-collar-twill-shirt/31437847/buy" },
        { id: 8, name: "HIGHLANDER Men Black Slim Fit Solid Casual Shirt", price: 263, image: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/6491779/2024/8/23/7046ea46-5198-4ad2-9360-395fa67b2a821724406387183-HIGHLANDER-Men-Black-Slim-Fit-Solid-Casual-Shirt-83317244063-2.jpg", category: "Shirts", source: "myntra.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Casual", product_url: "https://www.myntra.com/shirts/highlander/highlander-men-black-slim-fit-solid-casual-shirt/6491779/buy" },
        { id: 9, name: "VeBNoR Solid Men Round Neck Black, Maroon, Grey, Dark Green T-Shirt", price: 379, image: "https://rukminim2.flixcart.com/image/832/832/xif0q/t-shirt/j/3/w/xxl-ts25-vebnor-original-imah4x5vukhuymzq.jpeg?q=70&crop=false", category: "T-shirts", source: "flipkart.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Round Neck", product_url: "https://www.flipkart.com/vebnor-solid-men-round-neck-black-maroon-grey-dark-green-t-shirt/p/itm6ab8f92d02fde?pid=TSHGYZX3VD4QAAGZ" },
        { id: 10, name: "VeBNoR Solid Men Mandarin Collar Blue T-Shirt", price: 234, image: "https://rukminim2.flixcart.com/image/832/832/xif0q/t-shirt/v/w/n/m-ts40-vebnor-original-imagtyvfqhafutuj.jpeg?q=70&crop=false", category: "T-shirts", source: "flipkart.com", colors: ["#2c3e50", "#27ae60", "#f39c12", "#c0392b"], material: "Mandarin Collar", product_url: "https://www.flipkart.com/vebnor-solid-men-mandarin-collar-blue-t-shirt/p/itm9aa0dcb081bb0?pid=TSHGSFAYTUZEMVCY" }
    ];    
    

    function renderListings(products) {
        const listingsContainer = document.getElementById("listings");
        listingsContainer.innerHTML = "";
    
        const currentDate = new Date().toLocaleDateString();
    
        products.forEach((product, index) => {
            const colorCircles = product.colors.map(color => 
                `<span class="color-circle d-inline-block" style="background-color: ${color}; width: 16px; height: 16px; border-radius: 50%; flex-shrink: 0;"></span>`
            ).join('');
            const truncatedName = product.name.length > 40 ? product.name.substring(0, 37) + "..." : product.name;

            const productCard = `
                <div class="col-12 col-md-6 col-lg-3 mb-3">
                    <div class="card shadow-sm border-0 rounded-3 p-2">
                        <img id="product-image-${index}" src="${product.image}" class="card-img-top rounded-3" alt="${product.name}" style="height: 200px; object-fit: cover;">
                        <div class="card-body p-2">
                            <p class="fw-bold text-dark mb-1 small">₹${product.price}</p>
                            <h6 class="fw-semibold mb-1 small" title="${product.name}">${truncatedName}</h6>
                            <p class="text-muted mb-2 small">Source: <a href="https://${product.source}" target="_blank" class="text-decoration-none small">${product.source}</a></p>
                            <p class="text-muted mb-2 small">Date Fetched: ${currentDate}</p>    

                            <!-- Colors and Material in the Same Row -->
                            <div class="d-flex align-items-center justify-content-between">
                                <div class="color-options d-flex overflow-auto" >
                                    ${colorCircles}
                                </div>
                                <span class="badge bg-light text-black border-gray fw-semibold x-small rounded-pill">${product.material}</span>
                            </div>

                            <div class="d-flex justify-content-between mt-3">
                                <a  href="${product.product_url}" target="_blank" class="btn btn-sm btn-dark rounded-pill fw-semibold px-3 small">View Product</a>
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
    }
    

    function refreshProduct(index) {
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
