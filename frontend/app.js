// ======================================================
// BANK ROLL
// FRONTEND JAVASCRIPT
// ======================================================

const API_BASE = window.BANKROLL_API_BASE || "http://127.0.0.1:8000";

// ======================================================
// GENERAL HELPERS
// ======================================================

function money(value) {
  const number = Number(value || 0);

  return number.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
  });
}

function prettyLabel(text) {
  return String(text)
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`);

  if (!response.ok) {
    throw new Error(`GET ${path} failed: ${response.status}`);
  }

  return response.json();
}

async function apiPost(path) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
  });

  if (!response.ok) {
    throw new Error(`POST ${path} failed: ${response.status}`);
  }

  return response.json();
}

// ======================================================
// DASHBOARD
// ======================================================

async function loadDashboard() {
  const monthlyBudget = document.getElementById("monthly-budget");

  if (!monthlyBudget) {
    return;
  }

  const status = document.getElementById("dashboard-status");

  try {
    const [dashboard, transactions] = await Promise.all([
      apiGet("/dashboard"),
      apiGet("/transactions"),
    ]);

    monthlyBudget.textContent = money(dashboard.monthly_budget);

    const spent = document.getElementById("total-spent");

    if (spent) {
      spent.textContent = money(dashboard.total_spent);
    }

    const remaining = document.getElementById("remaining");

    if (remaining) {
      remaining.textContent = money(dashboard.remaining);
    }

    const percent = document.getElementById("percent-used");

    if (percent) {
      percent.textContent = `${dashboard.percent_used}% of monthly budget`;
    }

    // --------------------------------
    // CATEGORY SPENDING
    // --------------------------------

    const categoryBox = document.getElementById("category-spending");

    if (categoryBox) {
      categoryBox.innerHTML = "";

      Object.entries(dashboard.category_spending || {}).forEach(
        ([category, amount]) => {
          categoryBox.insertAdjacentHTML(
            "beforeend",
            `
                        <div class="dashboard-detail">

                            <span>
                                ${category}
                            </span>

                            <strong>
                                ${money(amount)}
                            </strong>

                        </div>
                        `,
          );
        },
      );
    }

    // --------------------------------
    // TRANSACTIONS
    // --------------------------------

    const transactionList = document.getElementById("transaction-list");

    if (transactionList) {
      transactionList.innerHTML = "";

      (transactions || []).slice(0, 5).forEach((transaction) => {
        transactionList.insertAdjacentHTML(
          "beforeend",
          `
                            <li>

                                <div>

                                    <strong>
                                        ${transaction.merchant}
                                    </strong>

                                    <span class="muted">
                                        ${transaction.category}
                                    </span>

                                </div>

                                <strong>
                                    ${money(transaction.amount)}
                                </strong>

                            </li>
                            `,
        );
      });
    }

    if (status) {
      status.style.display = "none";
    }

    await Promise.allSettled([loadFinancialAidSummary(), loadBankSummary()]);
  } catch (error) {
    console.error("Dashboard error:", error);

    if (status) {
      status.style.display = "block";

      status.textContent = "We couldn't load your dashboard.";
    }
  }
}

// ======================================================
// FINANCIAL AID SUMMARY
// ======================================================

function formatAidValue(key, value) {
  if (value === null || value === undefined) {
    return "Not found";
  }

  if (key === "student_aid_index") {
    return value;
  }

  if (typeof value === "number") {
    return money(value);
  }

  return value;
}

async function loadFinancialAidSummary() {
  const container = document.getElementById("financial-aid-summary");

  if (!container) {
    return;
  }

  try {
    const data = await apiGet("/financial-aid-summary");

    if (!data || Object.keys(data).length === 0) {
      container.innerHTML = `
                <p class="muted">
                    Add your financial aid to see
                    your award summary here.
                </p>
                `;

      return;
    }

    container.innerHTML = "";

    Object.entries(data).forEach(([key, value]) => {
      container.insertAdjacentHTML(
        "beforeend",
        `
                        <div class="dashboard-detail">

                            <span>
                                ${prettyLabel(key)}
                            </span>

                            <strong>
                                ${formatAidValue(key, value)}
                            </strong>

                        </div>
                        `,
      );
    });
  } catch (error) {
    console.error("Financial aid summary error:", error);

    container.innerHTML = `
            <p class="muted">
                Add your financial aid to see
                your award summary here.
            </p>
            `;
  }
}

// ======================================================
// BANK SUMMARY
// ======================================================

async function loadBankSummary() {
  const container = document.getElementById("bank-summary");

  if (!container) {
    return;
  }

  const connected = localStorage.getItem("bankRollBankConnected");

  if (connected !== "true") {
    container.innerHTML = `
            <p class="muted">
                Connect your bank account to see
                your balance here.
            </p>
            `;

    return;
  }

  try {
    const account = await apiGet("/demo-bank-account");

    if (!account || account.connected !== true) {
      throw new Error("Account unavailable");
    }

    container.innerHTML = `
            <div class="dashboard-detail">

                <span>
                    ${account.nickname || "Checking"}
                </span>

                <strong>
                    ${money(account.balance)}
                </strong>

            </div>

            <p class="connected-text">
                Capital One connected
            </p>
            `;
  } catch (error) {
    console.error("Bank summary error:", error);

    container.innerHTML = `
            <p class="muted">
                Your bank connection is currently unavailable.
            </p>
            `;
  }
}

// ======================================================
// BUDGET
// ======================================================

async function loadBudget() {
  const table = document.getElementById("budget-table");

  if (!table) {
    return;
  }

  const status = document.getElementById("budget-status");

  try {
    const [dashboard, categoryBudgets] = await Promise.all([
      apiGet("/dashboard"),
      apiGet("/category-budgets"),
    ]);

    const limit = document.getElementById("budget-limit");

    if (limit) {
      limit.textContent = money(dashboard.monthly_budget);
    }

    const spent = document.getElementById("budget-spent");

    if (spent) {
      spent.textContent = money(dashboard.total_spent);
    }

    const remaining = document.getElementById("budget-remaining");

    if (remaining) {
      remaining.textContent = money(dashboard.remaining);
    }

    const existingRows = table.querySelectorAll(
      ".budget-row:not(.budget-heading)",
    );

    existingRows.forEach((row) => row.remove());

    Object.entries(categoryBudgets).forEach(([category, data]) => {
      const budgetAmount = Number(data.budget || 0);

      const spentAmount = Number(data.spent || 0);

      const remainingAmount = Number(data.remaining || 0);

      const warning = budgetAmount > 0 && spentAmount / budgetAmount >= 0.8;

      table.insertAdjacentHTML(
        "beforeend",
        `
                    <div
                        class="budget-row
                        ${warning ? "warning-row" : ""}"
                    >

                        <p>
                            ${category}
                        </p>

                        <p>
                            ${money(budgetAmount)}
                        </p>

                        <p>
                            ${money(spentAmount)}
                        </p>

                        <p>
                            ${money(remainingAmount)}
                        </p>

                    </div>
                    `,
      );
    });

    if (status) {
      status.style.display = "none";
    }
  } catch (error) {
    console.error("Budget error:", error);

    if (status) {
      status.style.display = "block";

      status.textContent = "We couldn't load your budget.";
    }
  }
}

// ======================================================
// DEMO LOCATION
// ======================================================

function getDemoLocation() {
  return {
    latitude: 29.7604,
    longitude: -95.3698,
  };
}

// ======================================================
// RECOMMENDATIONS
// ======================================================

async function loadRecommendations() {
  const grid = document.getElementById("recommendation-grid");

  if (!grid) {
    return;
  }

  const status = document.getElementById("recommendation-status");

  const location = getDemoLocation();

  try {
    if (status) {
      status.style.display = "block";

      status.textContent = "Finding options for you...";
    }

    const data = await apiGet(
      `/recommendations?latitude=${location.latitude}&longitude=${location.longitude}`,
    );

    const items = data.cheap_food_options?.length
      ? data.cheap_food_options
      : data.recommendations || [];

    grid.innerHTML = "";

    items.slice(0, 6).forEach((item) => {
      if (item.name) {
        grid.insertAdjacentHTML(
          "beforeend",
          `
                            <div class="rec-card">

                                <h3>
                                    ${item.name}
                                </h3>

                                <p class="rec-desc">
                                    ${item.address || ""}
                                </p>

                                ${
                                  item.rating
                                    ? `
                                        <p class="muted">
                                            ★ ${item.rating}
                                        </p>
                                        `
                                    : ""
                                }

                                ${
                                  item.google_maps_link
                                    ? `
                                        <a
                                            href="${item.google_maps_link}"
                                            target="_blank"
                                            rel="noopener noreferrer"
                                        >
                                            View on Google Maps →
                                        </a>
                                        `
                                    : ""
                                }

                            </div>
                            `,
        );

        return;
      }

      if (item.message) {
        grid.insertAdjacentHTML(
          "beforeend",
          `
                            <div class="rec-card">

                                <h3>
                                    ${item.category || "Recommendation"}
                                </h3>

                                <p class="rec-desc">
                                    ${item.message}
                                </p>

                            </div>
                            `,
        );
      }
    });

    if (status) {
      status.style.display = items.length ? "none" : "block";

      if (items.length === 0) {
        status.textContent = "No recommendations found.";
      }
    }
  } catch (error) {
    console.error("Recommendation error:", error);

    if (status) {
      status.style.display = "block";

      status.textContent = "We couldn't load recommendations.";
    }
  }
}

// ======================================================
// STUDENT DISCOUNTS
// ======================================================

async function loadDiscounts() {
  const list = document.getElementById("discount-list");

  if (!list) {
    return;
  }

  const nearbyList = document.getElementById("nearby-discount-list");

  const status = document.getElementById("discount-status");

  try {
    const data = await apiGet("/student-discounts");

    const items = Array.isArray(data) ? data : data.discounts || [];

    list.innerHTML = "";

    items.forEach((item) => {
      const name = item.name || item.merchant || "Student Discount";

      const discount = item.student_discount || item.discount || "";

      const verification = item.verification || "";

      const url = item.url || "";

      list.insertAdjacentHTML(
        "beforeend",
        `
                    <div class="discount-card">

                        <div>

                            <h3>
                                ${name}
                            </h3>

                            <p>
                                ${discount}
                            </p>

                            ${
                              verification
                                ? `
                                    <small>
                                        ${verification}
                                    </small>
                                    `
                                : ""
                            }

                        </div>

                        ${
                          url
                            ? `
                                <a
                                    href="${url}"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    View offer →
                                </a>
                                `
                            : ""
                        }

                    </div>
                    `,
      );
    });

    if (status) {
      status.style.display = "none";
    }

    // --------------------------------
    // NEARBY DISCOUNTS
    // --------------------------------

    if (nearbyList) {
      const location = getDemoLocation();

      const nearbyData = await apiGet(
        `/nearby-student-discounts?latitude=${location.latitude}&longitude=${location.longitude}`,
      );

      const nearbyItems = nearbyData.nearby_student_discounts || [];

      nearbyList.innerHTML = "";

      nearbyItems.forEach((item) => {
        nearbyList.insertAdjacentHTML(
          "beforeend",
          `
                        <div class="discount-card">

                            <div>

                                <h3>
                                    ${item.name}
                                </h3>

                                <p>
                                    ${item.address || ""}
                                </p>

                                <strong>
                                    ${item.student_discount || ""}
                                </strong>

                            </div>

                            ${
                              item.google_maps_link
                                ? `
                                    <a
                                        href="${item.google_maps_link}"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                    >
                                        View location →
                                    </a>
                                    `
                                : ""
                            }

                        </div>
                        `,
        );
      });

      if (nearbyItems.length === 0) {
        nearbyList.innerHTML = `
                    <p class="muted">
                        No nearby locations found.
                    </p>
                    `;
      }
    }
  } catch (error) {
    console.error("Discount error:", error);

    if (status) {
      status.style.display = "block";

      status.textContent = "We couldn't load student discounts.";
    }
  }
}

// ======================================================
// FINANCIAL AID UPLOAD
// ======================================================

function setupFinancialAidForm() {
  const form = document.getElementById("aid-form");

  if (!form) {
    return;
  }

  const fileInput = document.getElementById("aid-file");

  const status = document.getElementById("aid-status");

  const results = document.getElementById("aid-results");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const file = fileInput?.files?.[0];

    if (!file) {
      if (status) {
        status.style.display = "block";

        status.textContent = "Choose a PDF first.";
      }

      return;
    }

    const formData = new FormData();

    formData.append("file", file);

    if (status) {
      status.style.display = "block";

      status.textContent = "Analyzing your financial aid...";
    }

    try {
      const response = await fetch(`${API_BASE}/upload-financial-aid`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      const data = await response.json();

      if (data.error) {
        throw new Error(data.error);
      }

      const aidData = data.financial_aid_data || {};

      if (results) {
        results.innerHTML = "";

        Object.entries(aidData).forEach(([key, value]) => {
          results.insertAdjacentHTML(
            "beforeend",
            `
                                <div class="dashboard-detail">

                                    <span>
                                        ${prettyLabel(key)}
                                    </span>

                                    <strong>
                                        ${formatAidValue(key, value)}
                                    </strong>

                                </div>
                                `,
          );
        });
      }

      if (status) {
        status.textContent = "Financial aid added successfully.";
      }
    } catch (error) {
      console.error("Financial aid error:", error);

      if (status) {
        status.textContent = "We couldn't analyze the PDF.";
      }
    }
  });
}

// ======================================================
// PERSONA IDENTITY VERIFICATION
// ======================================================

function setupPersonaButton() {
  const button = document.getElementById("verify-identity");

  if (!button) {
    return;
  }

  const status = document.getElementById("setup-status");

  button.addEventListener("click", async () => {
    button.disabled = true;

    button.textContent = "Opening...";

    if (status) {
      status.style.display = "block";

      status.textContent = "Starting identity verification...";
    }

    const verificationWindow = window.open("", "_blank");

    try {
      const data = await apiPost("/persona/create-inquiry");

      if (data.success === false || !data.inquiry_id) {
        throw new Error("Persona inquiry unavailable");
      }

      const personaUrl = `https://inquiry.withpersona.com/verify?inquiry-id=${encodeURIComponent(data.inquiry_id)}`;

      if (verificationWindow) {
        verificationWindow.location.href = personaUrl;
      }

      if (status) {
        status.innerHTML = `
                        <strong>
                            Identity verification started.
                        </strong>

                        <br>

                        Complete the verification
                        in the new window.
                        `;
      }

      button.textContent = "Verification Started";
    } catch (error) {
      console.error("Persona error:", error);

      if (verificationWindow) {
        verificationWindow.close();
      }

      if (status) {
        status.textContent = "We couldn't start identity verification.";
      }

      button.textContent = "Verify Identity";
    } finally {
      button.disabled = false;
    }
  });
}

// ======================================================
// CAPITAL ONE CONNECTION
// ======================================================

function setupBankButton() {
  const button = document.getElementById("connect-bank");

  const modal = document.getElementById("bank-modal");

  const closeButton = document.getElementById("close-bank-modal");

  const form = document.getElementById("bank-login-form");

  const status = document.getElementById("setup-status");

  if (!button || !modal || !form) {
    return;
  }

  // --------------------------------
  // OPEN MODAL
  // --------------------------------

  button.addEventListener("click", () => {
    modal.style.display = "flex";
  });

  // --------------------------------
  // CLOSE MODAL
  // --------------------------------

  if (closeButton) {
    closeButton.addEventListener("click", () => {
      modal.style.display = "none";
    });
  }

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });

  // --------------------------------
  // CONNECT ACCOUNT
  // --------------------------------

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const submitButton = document.getElementById("bank-submit");

    submitButton.disabled = true;

    submitButton.textContent = "Connecting...";

    try {
      // Username and password are intentionally
      // NOT sent anywhere.
      // They are only part of the demo flow.

      const account = await apiGet("/demo-bank-account");

      if (!account || account.connected !== true) {
        throw new Error("Bank connection unavailable");
      }

      localStorage.setItem("bankRollBankConnected", "true");

      localStorage.setItem("bankRollBankName", "Capital One");

      modal.style.display = "none";

      form.reset();

      button.textContent = "Connected ✓";

      if (status) {
        status.style.display = "block";

        status.innerHTML = `
                        <strong>
                            Capital One connected successfully.
                        </strong>

                        <br>

                        ${account.nickname || "Checking"}
                        ·
                        ${money(account.balance)}

                        <br><br>

                        <a href="dashboard.html">
                            View your financial overview →
                        </a>
                        `;
      }
    } catch (error) {
      console.error("Bank connection error:", error);

      if (status) {
        status.style.display = "block";

        status.textContent = "We couldn't connect your account.";
      }
    } finally {
      submitButton.disabled = false;

      submitButton.textContent = "Sign In & Connect";
    }
  });
}

// ======================================================
// RESTORE BANK STATE
// ======================================================

function restoreBankButtonState() {
  const button = document.getElementById("connect-bank");

  if (!button) {
    return;
  }

  const connected = localStorage.getItem("bankRollBankConnected");

  if (connected === "true") {
    button.textContent = "Connected ✓";
  }
}

// ======================================================
// BANK ROLL AI
// ======================================================

function setupBankRollAI() {
  const button = document.getElementById("ask-ai-button");
  const messageBox = document.getElementById("ai-message");
  const responseBox = document.getElementById("ai-response");

  if (!button || !messageBox || !responseBox) {
    return;
  }

  button.addEventListener("click", async () => {
    const message = messageBox.value.trim();

    if (!message) {
      responseBox.textContent = "Enter a question first.";
      return;
    }

    button.disabled = true;
    button.textContent = "Thinking...";
    responseBox.textContent = "Bank Roll AI is thinking...";

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: message,
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat failed: ${response.status}`);
      }

      const data = await response.json();

      responseBox.textContent =
        data.response || "Bank Roll AI couldn't generate a response.";
    } catch (error) {
      console.error("Bank Roll AI error:", error);

      responseBox.textContent =
        "Bank Roll AI is temporarily unavailable. Please try again.";
    } finally {
      button.disabled = false;
      button.textContent = "Ask Bank Roll AI";
    }
  });
}

// ======================================================
// START
// ======================================================

document.addEventListener("DOMContentLoaded", () => {
  loadDashboard();

  loadBudget();

  loadRecommendations();

  loadDiscounts();

  setupFinancialAidForm();

  setupPersonaButton();

  setupBankButton();

  restoreBankButtonState();

  setupBankRollAI();
});
