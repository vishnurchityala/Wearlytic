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
  