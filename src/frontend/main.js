const BASE_URL =
  "http://backend-alb-25600667.ap-southeast-2.elb.amazonaws.com/api/v1";

let marketplaceData = {
  volume: [],
  trade: [],
  labels: [],
  colors: [],
};

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
    case "resale-tokens":
      fetchTopResaleTokens(0);
      document.getElementById("resale-tokens-interval").value = "0";
      break;
    case "token-transaction":
      const tokenDetailsEl = document.getElementById("token-details");
      const tokenImageEl = document.getElementById("token-image");
      const tokenRarityEl = document.getElementById("token-rarity");
      const tokenIdDisplayEl = document.getElementById("token-id-display");
      const tokenIdInput = document.getElementById("token-id");
      const tokenChartEl = document.getElementById("token-transaction-chart");

      tokenDetailsEl.classList.add("hidden");
      tokenChartEl.classList.add("hidden");
      tokenImageEl.src = "assets/placeholder.jpeg";
      tokenRarityEl.textContent = "-";
      tokenIdDisplayEl.textContent = "-";
      tokenIdInput.value = "";
      tokenChartEl.innerHTML = "";
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
  nftImageEl.src = "assets/placeholder.jpeg";
  nftRarityEl.textContent = "-";
  errorTextEl.classList.add("hidden");
  errorTextEl.textContent = "";

  try {
    const response = await fetch(
      `${BASE_URL}/time-based-data?interval=${interval}`
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch time-based data: ${response.status}`);
    }

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
      const nft = await fetchNFTDetails(highestPriceTokenId);

      nftImageEl.src = nft.image_url || "assets/placeholder.jpeg";
      nftRarityEl.textContent = nft.rarity_rank || "N/A";
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
  const errorTextEl = document.getElementById("marketplace-error");

  errorTextEl.textContent = "";
  errorTextEl.classList.add("hidden");

  try {
    const response = await fetch(
      `${BASE_URL}/marketplace-comparison?interval=${interval}`
    );
    if (!response.ok) {
      throw new Error(
        `Failed to fetch marketplace comparison: ${response.status}`
      );
    }

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

    marketplaceData.labels = data.data.map((market) => market.marketplace);
    marketplaceData.volume = data.data.map((market) => market.total_volume);
    marketplaceData.trade = data.data.map((market) => market.transaction_count);
    marketplaceData.colors = data.data.map(
      (market) => marketColors[market.marketplace] || "#808080"
    );

    updateMarketplaceChart("volume");
  } catch (error) {
    console.error("Error fetching marketplace comparison:", error);
    errorTextEl.textContent = "無法顯示市場比較資料，請稍後再試。";
    errorTextEl.classList.remove("hidden");
  }
}

function updateMarketplaceChart(metric) {
  document.getElementById("toggle-volume").classList.remove("active");
  document.getElementById("toggle-trade").classList.remove("active");
  document
    .getElementById(metric === "volume" ? "toggle-volume" : "toggle-trade")
    .classList.add("active");

  const values =
    metric === "volume" ? marketplaceData.volume : marketplaceData.trade;
  const title = metric === "volume" ? "總銷售量比較" : "交易次數比較";

  Plotly.newPlot(
    "marketplace-chart",
    [
      {
        labels: marketplaceData.labels,
        values: values,
        type: "pie",
        textinfo: "label+percent",
        hoverinfo: "label+value+percent",
        hovertemplate: `<b>%{label}</b><br>
                   ${
                     metric === "volume" ? "總銷售量 (USD)" : "交易次數"
                   }: %{value}<br>
                   佔比: %{percent}<extra></extra>`,
        marker: {
          colors: marketplaceData.colors,
        },
      },
    ],
    {
      title: title,
      height: 400,
      width: 600,
      showlegend: true,
    }
  );
}

// Top Resale Tokens Display
async function fetchTopResaleTokens(interval) {
  const nftContainer = document.getElementById("top-resale-tokens");
  const errorTextEl = document.getElementById("resale-tokens-error");
  const loadingSpinner = document.getElementById("resale-loading");

  nftContainer.innerHTML = "";
  errorTextEl.textContent = "";
  errorTextEl.classList.add("hidden");

  try {
    loadingSpinner.classList.remove("hidden");

    const response = await fetch(
      `${BASE_URL}/top-resale-token?interval=${interval}`
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch top resale tokens: ${response.status}`);
    }

    const data = await response.json();

    if (!data.data || data.data.length === 0) {
      errorTextEl.textContent = "沒有資料";
      errorTextEl.classList.remove("hidden");
      return;
    }

    const nftDetails = await Promise.all(
      data.data.map(async (token) => {
        try {
          const nft = await fetchNFTDetails(token.token_id);
          return {
            token_id: token.token_id,
            total_profit: token.total_profit,
            seller_address: token.seller || "N/A",
            image_url: nft.image_url || "assets/placeholder.jpeg",
            rarity_rank: nft.rarity_rank || "N/A",
          };
        } catch (error) {
          console.warn(
            `Failed to fetch NFT details for token ${token.token_id}`,
            error
          );
          return {
            token_id: token.token_id,
            total_profit: token.total_profit,
            seller_address: token.seller || "N/A",
            image_url: "assets/placeholder.jpeg",
            rarity_rank: "N/A",
          };
        }
      })
    );

    nftContainer.innerHTML = nftDetails
      .map(
        (token) => `
                  <div class="nft-card">
                      <img src="${token.image_url}" alt="NFT Image" />
                      <div class="nft-details">
                          <p class="token-id">Token ID: ${token.token_id}</p>
                          <p><strong>利潤:</strong> ${token.total_profit} USD</p>
                          <p><strong>稀有度排名:</strong> ${token.rarity_rank}</p>
                          <p class="seller-address"><strong>賣家:</strong> ${token.seller_address}</p>
                      </div>
                  </div>
              `
      )
      .join("");
  } catch (error) {
    console.error("Error fetching top resale tokens:", error);
    errorTextEl.textContent = "無法顯示轉售資料，請稍後再試。";
    errorTextEl.classList.remove("hidden");
  } finally {
    loadingSpinner.classList.add("hidden");
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

  const tokenDetailsEl = document.getElementById("token-details");
  const tokenImageEl = document.getElementById("token-image");
  const tokenRarityEl = document.getElementById("token-rarity");
  const tokenIdDisplayEl = document.getElementById("token-id-display");
  const tokenChartEl = document.getElementById("token-transaction-chart");

  errorText.textContent = "";
  emptyText.classList.add("hidden");
  chartContainer.innerHTML = "";
  tokenDetailsEl.classList.add("hidden");
  tokenImageEl.src = "assets/placeholder.jpeg";
  tokenRarityEl.textContent = "-";
  tokenIdDisplayEl.textContent = "-";

  const tokenIdInt = parseInt(tokenId, 10);
  if (isNaN(tokenIdInt) || tokenIdInt < 0 || tokenIdInt > 9999) {
    errorText.textContent = "Token ID 必須是 0 到 9999 之間的數字";
    return;
  }

  try {
    const nft = await fetchNFTDetails(tokenIdInt);
    tokenImageEl.src = nft.image_url || "assets/placeholder.jpeg";
    tokenRarityEl.textContent = nft.rarity_rank || "N/A";
    tokenIdDisplayEl.textContent = tokenIdInt;
    tokenDetailsEl.classList.remove("hidden");
    tokenChartEl.classList.remove("hidden");

    const response = await fetch(
      `${BASE_URL}/token-transaction?token_id=${tokenIdInt}&interval=${interval}`
    );
    if (!response.ok) {
      throw new Error(`Failed to fetch token transactions: ${response.status}`);
    }

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
          text: data.data.map((tx) => tx.buyer_address),
          mode: "lines+markers",
          type: "scatter",
          marker: { size: 8, color: "#0078D7" },
          hovertemplate:
            "<b>日期:</b> %{x}<br>" +
            "<b>價格:</b> %{y:.2f} USD<br>" +
            "<b>買家地址:</b> %{text}<extra></extra>",
        },
      ],
      {
        title: `Token ID ${tokenIdInt} 交易記錄`,
        xaxis: {
          title: "交易日期",
          type: "date",
          tickformat: "%Y-%m-%d",
          automargin: true,
        },
        yaxis: { title: "價格(USD)", tickformat: ",d", automargin: true },
        automargin: true,
        height: 400,
      }
    );
  } catch (error) {
    console.error("Error fetching token transactions:", error);
    errorText.textContent = "無法取得交易資料，請稍後再試。";
  }
}

async function fetchNFTDetails(tokenId) {
  try {
    const response = await fetch(`${BASE_URL}/nft-details?token_id=${tokenId}`);
    if (!response.ok) {
      throw new Error(`API call failed with status: ${response.status}`);
    }

    const nft = await response.json();
    return nft;
  } catch (error) {
    console.error(`Error fetching NFT details for token ${tokenId}:`, error);
    return {
      image_url: "assets/placeholder.jpeg",
      rarity_rank: "N/A",
    };
  }
}

document.addEventListener("DOMContentLoaded", () => {
  showSection("time-based");
});
