(function renderAveragePricingComponent() {
    const wrapper = document.getElementById("pricing-wrapper");
    const container = document.getElementById("pricing-container");
  
    if (!wrapper || !container) return;
  
    // Inject styles
    const style = document.createElement("style");
    style.textContent = `
      #pricing-wrapper {
        max-width: 1000px;
        margin: 40px auto;
        font-family: 'Inter', sans-serif;
      }
  
      .pricing-title {
        font-size: 1.8rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 20px;
        color: #222;
      }
  
      #pricing-container {
        display: flex;
        gap: 16px;
        overflow-x: auto;
        padding-bottom: 12px;
        scrollbar-width: thin;
      }
  
      .pricing-card {
        flex: 0 0 180px;
        background: #ffffff;
        border-radius: 16px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.06);
        padding: 20px;
        text-align: center;
        transition: transform 0.2s;
      }
  
      .category-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 8px;
        color: #111;
        text-transform: capitalize;
      }
  
      .average-price {
        font-size: 1.4rem;
        font-weight: bold;
        color: #2b2b2b;
      }
    `;
    document.head.appendChild(style);
  
    const productData = [
      { category: "tshirts", price: 499 },
      { category: "tshirts", price: 599 },
      { category: "shirts", price: 899 },
      { category: "shirts", price: 999 },
      { category: "pants", price: 1299 },
      { category: "pants", price: 1399 },
      { category: "cargos", price: 1099 },
      { category: "cargos", price: 1199 },
      { category: "hoodies", price: 1499 },
      { category: "jackets", price: 1999 },
      { category: "shorts", price: 799 },
      { category: "sweaters", price: 999 },
      { category: "blazers", price: 2199 }
    ];
  
    const calculateAveragePrices = (data) => {
      const totals = {};
      const counts = {};
  
      data.forEach(({ category, price }) => {
        totals[category] = (totals[category] || 0) + price;
        counts[category] = (counts[category] || 0) + 1;
      });
  
      return Object.keys(totals).map((category) => ({
        category,
        average: Math.round(totals[category] / counts[category]),
      }));
    };
  
    const renderPricingCards = (avgData) => {
      container.innerHTML = "";
  
      avgData.forEach(({ category, average }) => {
        const card = document.createElement("div");
        card.className = "pricing-card";
        card.innerHTML = `
          <div class="category-title">${category}</div>
          <div class="average-price">₹${average}</div>
        `;
        container.appendChild(card);
      });
    };
  
    const avgPrices = calculateAveragePrices(productData);
    renderPricingCards(avgPrices);
  })();
  
// Sample data from the provided JSON
const productData = [
    {
        description: "Drop-Shoulder Sleeves Pure Cotton T-shirt",
        product_url: "https://www.myntra.com/tshirts/mango/mango-drop-shoulder-sleeves-pure-cotton-t-shirt/31842183/buy",
        source: "myntra.com",
        product_name: "MANGO Tshirts",
        image_url: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/2024/DECEMBER/13/JBfnmNFX_bdf9082b330f420c92eb4c28dc9911af.jpg",
        category: "Tshirts",
        price: "₹623",
        colors: ["purple"],
        brand: "MANGO",
        material: "Pure Cotton",
        timestamp: 1739500100.13495
    },
    {
        description: "Men Spread Collar Self Design Casual Bomber Jacket",
        product_url: "https://www.myntra.com/jackets/stylecast+x+revolte/stylecast-x-revolte-men-spread-collar-self-design-casual-bomber-jacket/31426384/buy",
        source: "myntra.com",
        product_name: "StyleCast x Revolte Jackets",
        image_url: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/2024/OCTOBER/26/7bVABZJL_71ec12eca4794eadaee638b808749e2e.jpg",
        category: "Jackets",
        price: "₹1477",
        colors: ["white"],
        brand: "StyleCast x Revolte",
        material: "Wool",
        timestamp: 1739500450.74818
    },
    {
        description: "Women Black Veronica Skinny Fit High-Rise Slash Knee Stretchable Jeans",
        product_url: "https://www.myntra.com/jeans/flying+machine/flying-machine-women-black-veronica-skinny-fit-high-rise-slash-knee-stretchable-jeans/14030738/buy",
        source: "myntra.com",
        product_name: "Flying Machine Jeans",
        image_url: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/14030738/2021/5/17/1cdac6b3-c755-47cd-88d1-f8b7ada62dca1621254721436WomensCottonPolyLycraSkinnyFitBlackJeans1.jpg",
        category: "Jeans",
        price: "₹1299",
        colors: ["black"],
        brand: "Flying Machine",
        material: null,
        timestamp: 1739501278.4255
    },
    {
        description: "Women Longline Open Front Jacket",
        product_url: "https://www.myntra.com/jackets/stylecast+x+revolte/stylecast-x-revolte-women-longline-open-front-jacket/31055114/buy",
        source: "myntra.com",
        product_name: "StyleCast x Revolte Jackets",
        image_url: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/2024/SEPTEMBER/20/nANufnD7_c28da022b28a4ea3a02dac793d6466d1.jpg",
        category: "Jackets",
        price: "₹1249",
        colors: ["silver"],
        brand: "StyleCast x Revolte",
        material: "Polyester",
        timestamp: 1739500518.62439
    },
    {
        description: "Men Wide Leg Low-Rise Light Fade Stretchable Jeans",
        product_url: "https://www.myntra.com/jeans/jack+%26+jones/jack--jones-men-wide-leg-low-rise-light-fade-stretchable-jeans/32680028/buy",
        source: "myntra.com",
        product_name: "Jack & Jones Jeans",
        image_url: "https://assets.myntassets.com/h_720,q_90,w_540/v1/assets/images/2025/FEBRUARY/7/G2dMxRTf_34d2e2fda42a474b8c9f50f794d2de72.jpg",
        category: "Jeans",
        price: "₹ 5999",
        colors: ["gray"],
        brand: "Jack & Jones",
        material: null,
        timestamp: 1739501098.78247
    }
];

// Helper function to extract numeric price from price string
function getNumericPrice(priceStr) {
    return parseFloat(priceStr.replace('₹', '').replace(/\s+/g, ''));
}

// Process data for charts
function processData() {
    // Price ranges
    const priceRanges = {
        '0-1000': 0,
        '1000-2000': 0,
        '2000-5000': 0,
        '5000+': 0
    };

    // Category counts
    const categoryCounts = {};
    
    // Brand prices
    const brandPrices = {};
    
    // Material counts
    const materialCounts = {};
    
    // Color counts
    const colorCounts = {};

    productData.forEach(product => {
        const price = getNumericPrice(product.price);
        
        // Price distribution
        if (price <= 1000) priceRanges['0-1000']++;
        else if (price <= 2000) priceRanges['1000-2000']++;
        else if (price <= 5000) priceRanges['2000-5000']++;
        else priceRanges['5000+']++;

        // Category distribution
        categoryCounts[product.category] = (categoryCounts[product.category] || 0) + 1;

        // Brand prices
        if (!brandPrices[product.brand]) {
            brandPrices[product.brand] = [];
        }
        brandPrices[product.brand].push(price);

        // Material distribution
        const material = product.material || 'Unknown';
        materialCounts[material] = (materialCounts[material] || 0) + 1;

        // Color distribution
        product.colors.forEach(color => {
            colorCounts[color] = (colorCounts[color] || 0) + 1;
        });
    });

    return {
        priceRanges,
        categoryCounts,
        brandPrices,
        materialCounts,
        colorCounts
    };
}

// Create charts
function createCharts() {
    const data = processData();
    
    // Price Distribution Chart
    new Chart(document.getElementById('priceDistributionChart'), {
        type: 'bar',
        data: {
            labels: Object.keys(data.priceRanges),
            datasets: [{
                label: 'Number of Products',
                data: Object.values(data.priceRanges),
                backgroundColor: '#1560BD',  // Denim Blue
                borderColor: '#1560BD',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // Category Distribution Chart
    new Chart(document.getElementById('categoryDistributionChart'), {
        type: 'pie',
        data: {
            labels: Object.keys(data.categoryCounts),
            datasets: [{
                data: Object.values(data.categoryCounts),
                backgroundColor: [
                    '#1560BD',  // Denim Blue
                    '#E2725B',  // Terracotta
                    '#B2BEB5'   // Soft Sage
                ],
                borderColor: '#ffffff',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        boxWidth: 12,
                        padding: 15,
                        font: {
                            weight: 'bold'
                        }
                    }
                }
            }
        }
    });
}

// Initialize charts when the page loads
document.addEventListener('DOMContentLoaded', createCharts);
  