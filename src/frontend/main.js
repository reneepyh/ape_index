const BASE_URL = "http://localhost:8000/api/v1";

function showSection(sectionId) {
  document.querySelectorAll(".analysis-section").forEach((section) => {
    section.classList.add("hidden");
  });
  document.getElementById(sectionId).classList.remove("hidden");

  switch (sectionId) {
    case "time-based":
      fetchTimeBasedData(0);
      document.getElementById("time-based-interval").value = "0";
      break;
    case "buyers-sellers":
      fetchTopBuyersSellers(0);
      document.getElementById("buyers-sellers-interval").value = "0";
      break;
    case "marketplace":
      fetchMarketplaceComparison(0);
      document.getElementById("marketplace-interval").value = "0";
      break;
    case "flip-tokens":
      fetchTopFlipTokens(0);
      document.getElementById("flip-tokens-interval").value = "0";
      break;
    case "token-transaction":
      break;
  }
}

// Time-Based
async function fetchTimeBasedData(interval) {
  const totalVolumeEl = document.getElementById("total-volume");
  const averagePriceEl = document.getElementById("average-price");
  const transactionCountEl = document.getElementById("transaction-count");
  const nftImageEl = document.getElementById("nft-image");
  const nftRarityEl = document.getElementById("nft-rarity");
  const highestPriceEl = document.getElementById("highest-price");
  const highestPriceTokenIdEl = document.getElementById(
    "highest-price-token-id"
  );
  const errorTextEl = document.getElementById("time-based-error");

  totalVolumeEl.textContent = "-";
  averagePriceEl.textContent = "-";
  transactionCountEl.textContent = "-";
  highestPriceEl.textContent = "-";
  highestPriceTokenIdEl.textContent = "-";
  nftImageEl.src = "";
  nftRarityEl.textContent = "-";
  errorTextEl.classList.add("hidden");
  errorTextEl.textContent = "";

  try {
    const response = await fetch(
      `${BASE_URL}/time-based-data?interval=${interval}`
    );
    const data = await response.json();

    if (!data.data || data.data.length === 0) {
      errorTextEl.textContent = "沒有資料";
      errorTextEl.classList.remove("hidden");
      return;
    }

    totalVolumeEl.textContent = `${Math.floor(
      data.data[0].total_volume
    ).toLocaleString()} USD`;
    averagePriceEl.textContent = `${Math.floor(
      data.data[0].average_price
    ).toLocaleString()} USD`;
    transactionCountEl.textContent = `${data.data[0].transaction_count.toLocaleString()} 次`;
    highestPriceEl.textContent = `${Math.floor(
      data.data[0].highest_price
    ).toLocaleString()} USD`;
    highestPriceTokenIdEl.textContent = data.data[0].highest_price_token_id;

    const highestPriceTokenId = data.data[0].highest_price_token_id;

    if (highestPriceTokenId && highestPriceTokenId !== "N/A") {
      await fetchNFTDetails(highestPriceTokenId);
    }
  } catch (error) {
    console.error("Error fetching time-based data:", error);
    errorTextEl.textContent = "無法讀取時間維度資料，請稍後再試。";
    errorTextEl.classList.remove("hidden");
  }
}

// Top Buyers & Sellers
async function fetchTopBuyersSellers(interval) {
  try {
    const response = await fetch(
      `${BASE_URL}/top-buyers-sellers?interval=${interval}`
    );
    const data = await response.json();

    const formatAddress = (address) =>
      `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;

    // Top Buyers
    Plotly.newPlot(
      "top-buyers-chart",
      [
        {
          x: data.top_buyers.map((buyer) => formatAddress(buyer.address)),
          y: data.top_buyers.map((buyer) => buyer.total_volume),
          text: data.top_buyers.map((buyer) => buyer.address),
          type: "bar",
          marker: {
            color: "#4CAF50", // Bar color
          },
          name: "主要買家",
          hoverlabel: {
            bgcolor: "#FFC107", // Background color for hover tooltips (e.g., yellow)
            font: { color: "#000000" }, // Text color for hover tooltips (e.g., black)
          },
          hovertemplate:
            "<b>地址:</b> %{text}<br>" +
            "<b>總銷售量:</b> %{y}<br>" +
            "<extra></extra>",
          textposition: "none",
        },
      ],
      {
        title: "主要買家",
        xaxis: {
          title: {
            text: "買家地址",
            standoff: 20,
          },
          automargin: true,
          showticklabels: true,
        },
        yaxis: {
          title: {
            text: "總銷售量",
            standoff: 20,
          },
          automargin: true,
        },
      }
    );

    // Top Sellers
    Plotly.newPlot(
      "top-sellers-chart",
      [
        {
          x: data.top_sellers.map((seller) => formatAddress(seller.address)),
          y: data.top_sellers.map((seller) => seller.total_volume),
          text: data.top_sellers.map((seller) => seller.address),
          type: "bar",
          marker: {
            color: "#4CAF50", // Bar color
          },
          name: "主要賣家",
          hoverlabel: {
            bgcolor: "#FFC107", // Background color for hover tooltips (e.g., yellow)
            font: { color: "#000000" }, // Text color for hover tooltips (e.g., black)
          },
          hovertemplate:
            "<b>地址:</b> %{text}<br>" +
            "<b>總銷售量:</b> %{y}<br>" +
            "<extra></extra>",
          textposition: "none",
        },
      ],
      {
        title: "主要賣家",
        xaxis: {
          title: {
            text: "賣家地址",
            standoff: 20,
          },
          automargin: true,
          showticklabels: true,
        },
        yaxis: {
          title: {
            text: "總銷售量",
            standoff: 20,
          },
          automargin: true,
        },
      }
    );
  } catch (error) {
    console.error("Error fetching top buyers/sellers:", error);
  }
}

// Marketplace Comparison
async function fetchMarketplaceComparison(interval) {
  try {
    const response = await fetch(
      `${BASE_URL}/marketplace-comparison?interval=${interval}`
    );
    const data = await response.json();

    const marketColors = {
      OpenSea: "#636efa",
      LooksRare: "#EF553B",
      X2Y2: "#00cc96",
      Blur: "#FFA15A",
      Seaport: "#FF6692",
      Rarible: "#B6E880",
      "0x Protocol": "#FF97FF",
    };

    const colors = data.data.map(
      (market) => marketColors[market.marketplace] || "#808080"
    );

    Plotly.newPlot(
      "marketplace-chart",
      [
        {
          labels: data.data.map((market) => market.marketplace),
          values: data.data.map((market) => market.total_volume),
          type: "pie",
          textinfo: "label+percent",
          hoverinfo: "label+value+percent",
          hovertemplate:
            "<b>%{label}</b><br>" +
            "總銷售量: %{value}<br>" +
            "佔比: %{percent}<extra></extra>",
          marker: {
            colors: colors,
          },
        },
      ],
      {
        title: "市場比較",
        height: 400,
        width: 600,
      }
    );
  } catch (error) {
    console.error("Error fetching marketplace comparison:", error);
  }
}

// Top Flip Tokens
async function fetchTopFlipTokens(interval) {
  try {
    const response = await fetch(
      `${BASE_URL}/top-flip-token?interval=${interval}`
    );
    const data = await response.json();

    Plotly.newPlot(
      "top-flip-tokens-chart",
      [
        {
          x: data.data.map((token) => token.token_id),
          y: data.data.map((token) => token.total_profit),
          type: "bar",
        },
      ],
      { title: "高利潤翻轉代幣" }
    );
  } catch (error) {
    console.error("Error fetching top flip tokens:", error);
  }
}

// Token Transactions
async function fetchTokenTransactions() {
  const tokenIdInput = document.getElementById("token-id");
  const tokenId = tokenIdInput.value.trim();
  const interval = document.getElementById("token-transaction-interval").value;
  const errorText = document.getElementById("token-transaction-error");
  const emptyText = document.getElementById("token-transaction-empty");
  const chartContainer = document.getElementById("token-transaction-chart");

  errorText.textContent = "";
  emptyText.classList.add("hidden");
  chartContainer.innerHTML = "";

  const tokenIdInt = parseInt(tokenId, 10);
  if (isNaN(tokenIdInt) || tokenIdInt < 0 || tokenIdInt > 9999) {
    errorText.textContent = "Token ID 必須是 0 到 9999 之間的數字";
    return;
  }

  try {
    const response = await fetch(
      `${BASE_URL}/token-transaction?token_id=${tokenIdInt}&interval=${interval}`
    );
    const data = await response.json();

    if (!data.data || data.data.length === 0) {
      emptyText.classList.remove("hidden");
      return;
    }

    Plotly.newPlot(
      "token-transaction-chart",
      [
        {
          x: data.data.map((tx) => tx.sold_date),
          y: data.data.map((tx) => tx.price),
          mode: "lines+markers",
          type: "scatter",
        },
      ],
      { title: `代幣 ${tokenIdInt} 交易記錄` }
    );
  } catch (error) {
    console.error("Error fetching token transactions:", error);
    errorText.textContent = "無法取得交易資料，請稍後再試。";
  }
}

async function fetchNFTDetails(tokenId) {
  const nftImageEl = document.getElementById("nft-image");
  const nftRarityEl = document.getElementById("nft-rarity");

  nftImageEl.src = "assets/placeholder.jpeg";
  nftRarityEl.textContent = "-";

  try {
    const response = await fetch(
      `http://localhost:8000/api/v1/nft-details?token_id=${tokenId}`
    );
    if (!response.ok) {
      throw new Error(`API call failed with status: ${response.status}`);
    }

    const nft = await response.json();

    nftImageEl.src = nft.image_url;
    nftRarityEl.textContent = nft.rarity_rank || "N/A";
  } catch (error) {
    console.error("Error fetching NFT details:", error);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  showSection("time-based");
});
