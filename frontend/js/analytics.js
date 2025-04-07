// Fetch data from local JSON file
async function fetchAnalyticsData() {
  try {
    // Show loader
    document.getElementById('loader').classList.remove('hidden');
    
    const response = await fetch('./results.json');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching analytics data:', error);
    return null;
  } finally {
    // Hide loader
    document.getElementById('loader').classList.add('hidden');
  }
}

// Helper function to extract numeric price from price string
function getNumericPrice(priceStr) {
  return parseFloat(priceStr.replace('₹', '').replace(/\s+/g, ''));
}

// Process data for charts
function processData(apiData) {
  if (!apiData) return null;
  
  // Price ranges
  const priceRanges = apiData.price_ranges.price_range_counts;
  
  // Category counts and averages
  const categoryData = apiData.categories;
  const categoryCounts = {};
  const categoryAverages = {};
  
  // Process category data
  Object.entries(categoryData).forEach(([category, avgPrice]) => {
    categoryCounts[category] = 0; // We'll need to calculate this from the data
    categoryAverages[category] = Math.round(avgPrice);
  });
  
  // Calculate category counts from top_categories_by_price_range
  Object.values(apiData.price_ranges.top_categories_by_price_range).forEach(rangeData => {
    Object.entries(rangeData).forEach(([category, count]) => {
      if (categoryCounts[category] !== undefined) {
        categoryCounts[category] += count;
      }
    });
  });
  
  // Color data
  const colorData = apiData.colors;
  
  // Design data
  const designData = apiData.designs;
  
  // Season data
  const seasonData = apiData.seasons;
  
  return {
    priceRanges,
    categoryCounts,
    categoryAverages,
    colorData,
    designData,
    seasonData
  };
}

// Create charts
function createCharts(data) {
  if (!data) return;
  
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
          '#B2BEB5',  // Soft Sage
          '#F5F5DC',  // Creamy Beige
          '#000000',  // Black
          '#FFFFFF',  // White
          '#808080'   // Gray
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

// Render average pricing component
function renderAveragePricingComponent(data) {
  const wrapper = document.getElementById("pricing-wrapper");
  const container = document.getElementById("pricing-container");
  
  if (!wrapper || !container || !data) return;
  
  // Inject styles
  const style = document.createElement("style");
  style.textContent = `
    #pricing-wrapper {
      max-width: 1200px;
      margin: 20px auto;
      font-family: 'Inter', sans-serif;
    }

    .pricing-title {
      font-size: 2rem;
      font-weight: 700;
      text-align: center;
      margin-bottom: 20px;
      color: #222;
    }

    #pricing-container {
      display: flex;
      gap: 12px;
      overflow-x: auto;
      padding: 0 12px 12px;
      scrollbar-width: thin;
      -webkit-overflow-scrolling: touch;
      scroll-behavior: smooth;
    }

    #pricing-container::-webkit-scrollbar {
      height: 6px;
    }

    #pricing-container::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 3px;
    }

    #pricing-container::-webkit-scrollbar-thumb {
      background: #888;
      border-radius: 3px;
    }

    .pricing-card {
      flex: 0 0 160px;
      background: #ffffff;
      font-size: 0.6rem;
      border-radius: 12px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
      padding: 12px 8px;
      text-align: center;
      height: 120px;
      width: 200px;
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .category-title {
      font-size: 0.6rem;
      font-weight: 600;
      margin-bottom: 4px;
      color: #444;
      text-transform: capitalize;
      line-height: 1.2;
    }

    .average-price {
      font-size: 1rem;
      font-weight: bold;
      color: #2b2b2b;
      line-height: 1.2;
    }

    @media (max-width: 768px) {
      .pricing-card {
        flex: 0 0 140px;
        height: 70px;
        padding: 8px 6px;
      }
      .category-title {
        font-size: 0.6rem;
        margin-bottom: 2px;
      }
      .average-price {
        font-size: 0.95rem;
      }
    }
  `;
  document.head.appendChild(style);
  
  // Render pricing cards
  container.innerHTML = "";
  
  Object.entries(data.categoryAverages).forEach(([category, average]) => {
    const card = document.createElement("div");
    card.className = "pricing-card";
    card.innerHTML = `
      <div class="category-title">${category}</div>
      <div class="average-price">₹${average}</div>
    `;
    container.appendChild(card);
  });
}

// Render trending colors
function renderTrendingColors(data) {
  const container = document.getElementById("trendingColor");
  if (!container || !data) return;
  
  // Get top 5 colors by count
  const topColors = Object.entries(data.colorData)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 5);
  
  // Update color boxes
  const colorBoxesContainer = container.querySelector('.d-flex.flex-row');
  if (colorBoxesContainer) {
    colorBoxesContainer.innerHTML = '';
    
    topColors.forEach(([color, colorData]) => {
      const colorBox = document.createElement('div');
      colorBox.className = 'text-center';
      
      // Map color names to hex codes
      const colorMap = {
        'black': '#000000',
        'white': '#FFFFFF',
        'gray': '#808080',
        'silver': '#C0C0C0',
        'beige': '#F5F5DC',
        'blue': '#1560BD',
        'red': '#FF0000',
        'green': '#008000',
        'yellow': '#FFFF00',
        'purple': '#800080',
        'pink': '#FFC0CB',
        'orange': '#FFA500',
        'brown': '#A52A2A'
      };
      
      const hexColor = colorMap[color.toLowerCase()] || '#CCCCCC';
      
      colorBox.innerHTML = `
        <div class="color-box rounded-pill mx-auto" style="background-color: ${hexColor}; width: 30px; height: 30px;"></div>
        <div class="small text-muted mt-1 fw-bold">${color.charAt(0).toUpperCase() + color.slice(1)} (${colorData.count})</div>
      `;
      
      colorBoxesContainer.appendChild(colorBox);
    });
  }
  
  // Update product cards
  const productCardsContainer = container.querySelector('.d-flex.flex-wrap');
  if (productCardsContainer) {
    productCardsContainer.innerHTML = '';
    
    // Get one product from each top color
    const topProducts = [];
    topColors.forEach(([color, colorData]) => {
      if (colorData.products && colorData.products.length > 0) {
        topProducts.push(colorData.products[0]); // Get the first product from each color
      }
    });
    
    // Display all products from top colors (up to 5)
    topProducts.forEach(product => {
      const card = document.createElement('div');
      card.className = 'card shadow-sm border-0 rounded-3 p-2';
      card.style.width = '160px';
      
      // Extract brand and product name from title
      const [brand, ...nameParts] = product.title.split(' ');
      const productName = nameParts.join(' ');
      
      card.innerHTML = `
        <img src="${product.image_url}" 
             class="card-img-top rounded-3" alt="${product.title}" style="height: 150px; object-fit: cover;">
        <div class="card-body p-2 text-center">
          <div class="d-grid mt-2">
            <a href="${product.url}" target="_blank" class="btn btn-dark fw-semibold rounded-pill btn-sm btn-tiny">View Product</a>
          </div>
          <p class="fw-bold text-dark mb-1 mt-2">${product.price}</p>
          <h6 class="fw-semibold mb-1 small">${brand}</h6>
        </div>
      `;
      
      productCardsContainer.appendChild(card);
    });
  }
}

// Render trending designs
function renderTrendingDesigns(data) {
  const container = document.getElementById("trendingDesigns");
  if (!container || !data) return;
  
  // Clear existing content
  container.innerHTML = '';
  
  // Add title
  const title = document.createElement('p');
  title.className = 'fw-bold text-center mt-2 mb-3 fs-4';
  title.textContent = 'Trending Designs';
  container.appendChild(title);
  
  // Get designs data and sort by count
  const designsData = Object.entries(data.designData)
    .sort((a, b) => b[1].count - a[1].count);
  
  // Create section for each design category
  designsData.forEach(([design, designData]) => {
    const section = document.createElement('div');
    section.className = 'container mb-4';
    
    const header = document.createElement('div');
    header.className = 'd-flex align-items-center justify-content-center gap-3 mb-4';
    
    // Add design circle
    const designCircle = document.createElement('div');
    designCircle.className = 'rounded-circle d-flex align-items-center justify-content-center flex-shrink-0';
    designCircle.style.cssText = 'width: 40px; height: 40px; background-color: #f8f9fa; border: 1px solid #dee2e6;';
    designCircle.innerHTML = `<span class="fs-6">${design.charAt(0).toUpperCase()}</span>`;
    
    // Add design title and count
    const designTitle = document.createElement('div');
    designTitle.className = 'fs-5 fw-semibold';
    designTitle.innerHTML = `${design.charAt(0).toUpperCase() + design.slice(1)} <span class="text-muted">(${designData.count} items)</span>`;
    
    header.appendChild(designCircle);
    header.appendChild(designTitle);
    section.appendChild(header);
    
    // Create scrollable container for products
    const productsContainer = document.createElement('div');
    productsContainer.className = 'd-flex gap-3 pb-2 justify-content-center flex-wrap';
    productsContainer.style.cssText = 'padding-left: 1rem; padding-right: 1rem;';
    
    // Add products
    const products = designData.products || [];
    products.forEach(product => {
      const card = document.createElement('div');
      card.className = 'card shadow-sm border-0 rounded-3 p-2 m-2';
      card.style.width = '160px';
      
      const [brand, ...nameParts] = product.title.split(' ');
      
      card.innerHTML = `
        <img src="${product.image_url}" 
             class="card-img-top rounded-3" alt="${product.title}" style="height: 150px; object-fit: cover;">
        <div class="card-body p-2 text-center">
          <div class="d-grid mt-2">
            <a href="${product.url}" target="_blank" class="btn btn-dark fw-semibold rounded-pill btn-sm btn-tiny">View Product</a>
          </div>
          <p class="fw-bold text-dark mb-1 mt-2">${product.price}</p>
          <h6 class="fw-semibold mb-1 small">${brand}</h6>
        </div>
      `;
      
      productsContainer.appendChild(card);
    });
    
    section.appendChild(productsContainer);
    container.appendChild(section);
  });
}

// Render trending clothes
function renderTrendingClothes(data) {
  const container = document.getElementById("trendingClothes");
  if (!container || !data) return;
  
  // Add styles for category sections
  const style = document.createElement('style');
  style.textContent = `
    .main-title {
      font-size: 2rem;
      font-weight: 700;
      margin: 2rem 0 1.5rem;
      padding-left: 1rem;
      color: #222;
    }

    .category-section {
      margin-bottom: 2rem;
    }
    
    .category-title {
      font-size: 1.5rem;
      font-weight: 600;
      margin: 1rem 0;
      padding-left: 1rem;
      color: #333;
      text-transform: capitalize;
    }
    
    .products-scroll-container {
      display: flex;
      flex-wrap: nowrap !important;
      overflow-x: auto;
      padding: 1rem;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: thin;
      scroll-behavior: smooth;
    }
    
    .products-scroll-container::-webkit-scrollbar {
      height: 8px;
    }
    
    .products-scroll-container::-webkit-scrollbar-track {
      background: #f1f1f1;
      border-radius: 4px;
    }
    
    .products-scroll-container::-webkit-scrollbar-thumb {
      background: #888;
      border-radius: 4px;
    }
    
    .products-scroll-container::-webkit-scrollbar-thumb:hover {
      background: #555;
    }
    
    .product-card {
      flex: 0 0 auto;
      width: 120px;
    }

    .design-count {
      font-size: 1rem;
      font-weight: normal;
      color: #666;
      margin-left: 0.5rem;
    }
  `;
  document.head.appendChild(style);
  
  // Clear existing content
  container.innerHTML = '';

  // Add main title for Trending Designs
  const mainTitle = document.createElement('h1');
  mainTitle.className = 'main-title';
  mainTitle.textContent = 'Trending Designs';
  container.appendChild(mainTitle);
  
  // Get designs data and sort by count
  const designsData = Object.entries(data.designData)
    .sort((a, b) => b[1].count - a[1].count);
  
  // Create section for each design category
  designsData.forEach(([design, designData]) => {
    const section = document.createElement('div');
    section.className = 'category-section';
    
    const title = document.createElement('h2');
    title.className = 'category-title';
    title.innerHTML = `${design} <span class="design-count">(${designData.count} items)</span>`;
    section.appendChild(title);
    
    const productsContainer = document.createElement('div');
    productsContainer.className = 'products-scroll-container';
    
    const products = designData.products || [];
    products.sort((a, b) => getNumericPrice(a.price) - getNumericPrice(b.price));
    
    products.forEach(product => {
      const card = document.createElement('div');
      card.className = 'card shadow-sm border-0 rounded-3 p-2 product-card';
      
      const [brand, ...nameParts] = product.title.split(' ');
      const category = nameParts.join(' ');
      
      card.innerHTML = `
        <img src="${product.image_url}" 
             class="card-img-top rounded-3" alt="${product.title}" style="height: 150px; object-fit: cover;">
        <div class="card-body p-2 text-center">
          <div class="d-grid mt-2">
            <a href="${product.url}" class="btn btn-dark fw-semibold rounded-pill btn-sm btn-tiny">View Product</a>
          </div>
          <p class="fw-bold text-dark mb-1 mt-2">${product.price}</p>
          <h6 class="fw-semibold mb-1 small">${brand}</h6>
          <p class="text-muted small mb-0">${category}</p>
        </div>
      `;
      
      productsContainer.appendChild(card);
    });
    
    section.appendChild(productsContainer);
    container.appendChild(section);
  });
}

// Initialize analytics when the page loads
document.addEventListener('DOMContentLoaded', async () => {
  // Show loader initially
  document.getElementById('loader').classList.remove('hidden');
  
  const apiData = await fetchAnalyticsData();
  if (apiData) {
    const processedData = processData(apiData);
    if (processedData) {
      createCharts(processedData);
      renderAveragePricingComponent(processedData);
      renderTrendingColors(processedData);
      renderTrendingDesigns(processedData);
      renderTrendingClothes(processedData);
    }
  }
  
  // Hide loader after everything is done
  document.getElementById('loader').classList.add('hidden');
});
  