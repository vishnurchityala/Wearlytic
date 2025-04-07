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
  const container = document.querySelector('#trendingColor:nth-of-type(2)');
  if (!container || !data) return;
  
  // Get top 5 designs by count
  const topDesigns = Object.entries(data.designData)
    .sort((a, b) => b[1].count - a[1].count)
    .slice(0, 5);
  
  // Update product cards
  const productCardsContainer = container.querySelector('.d-flex.flex-wrap');
  if (productCardsContainer) {
    productCardsContainer.innerHTML = '';
    
    // Get products from top designs
    const topProducts = [];
    topDesigns.forEach(([design, designData]) => {
      if (designData.products && designData.products.length > 0) {
        topProducts.push(...designData.products.slice(0, 2));
      }
    });
    
    // Limit to 5 products
    const productsToShow = topProducts.slice(0, 5);
    
    productsToShow.forEach(product => {
      const card = document.createElement('div');
      card.className = 'card shadow-sm border-0 rounded-3 p-2';
      card.style.width = '160px';
      
      // Extract brand from title
      const brand = product.title.split(' ')[0];
      
      card.innerHTML = `
        <img src="https://via.placeholder.com/160x150?text=${encodeURIComponent(brand)}" 
             class="card-img-top rounded-3" alt="${product.title}" style="height: 150px; object-fit: cover;">
        <div class="card-body p-2 text-center">
          <div class="d-grid mt-2">
            <a href="${product.url}" class="btn btn-dark fw-semibold rounded-pill btn-sm btn-tiny">View Product</a>
          </div>
          <p class="fw-bold text-dark mb-1 mt-2">${product.price}</p>
          <h6 class="fw-semibold mb-1 small">${brand}</h6>
        </div>
      `;
      
      productCardsContainer.appendChild(card);
    });
  }
}

// Render trending clothes
function renderTrendingClothes(data) {
  const container = document.getElementById("trendingClothes");
  if (!container || !data) return;
  
  // Get all products from colors and designs
  const allProducts = [];
  
  // Add products from colors
  Object.values(data.colorData).forEach(colorData => {
    if (colorData.products && colorData.products.length > 0) {
      allProducts.push(...colorData.products);
    }
  });
  
  // Add products from designs
  Object.values(data.designData).forEach(designData => {
    if (designData.products && designData.products.length > 0) {
      allProducts.push(...designData.products);
    }
  });
  
  // Remove duplicates based on URL
  const uniqueProducts = [];
  const seenUrls = new Set();
  
  allProducts.forEach(product => {
    if (!seenUrls.has(product.url)) {
      seenUrls.add(product.url);
      uniqueProducts.push(product);
    }
  });
  
  // Sort by price (ascending) to show affordable options first
  uniqueProducts.sort((a, b) => {
    const priceA = getNumericPrice(a.price);
    const priceB = getNumericPrice(b.price);
    return priceA - priceB;
  });
  
  // Get top 5 products
  const topProducts = uniqueProducts.slice(0, 5);
  
  // Update product cards
  const productCardsContainer = container.querySelector('.d-flex.flex-wrap');
  if (productCardsContainer) {
    productCardsContainer.innerHTML = '';
    
    topProducts.forEach(product => {
      const card = document.createElement('div');
      card.className = 'card shadow-sm border-0 rounded-3 p-2';
      card.style.width = '160px';
      
      // Extract brand from title
      const brand = product.title.split(' ')[0];
      
      card.innerHTML = `
        <img src="https://via.placeholder.com/160x150?text=${encodeURIComponent(brand)}" 
             class="card-img-top rounded-3" alt="${product.title}" style="height: 150px; object-fit: cover;">
        <div class="card-body p-2 text-center">
          <div class="d-grid mt-2">
            <a href="${product.url}" class="btn btn-dark fw-semibold rounded-pill btn-sm btn-tiny">View Product</a>
          </div>
          <p class="fw-bold text-dark mb-1 mt-2">${product.price}</p>
          <h6 class="fw-semibold mb-1 small">${brand}</h6>
        </div>
      `;
      
      productCardsContainer.appendChild(card);
    });
  }
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
  