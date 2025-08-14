// grapeiq_backend/app/static/js/dashboard.js

// Ajusta estos valores según tu entorno:
const BASE_URL = "http://127.0.0.1:8000/api";
const TENANT_ID = "a1b2c3d4-e5f6-7890-1234-567890abcdef";
const FORECAST_SECRET = "super-secret-key-123"; // Solo para demo

let forecastChart;
let salesChart;
let salesByChannelChart;
let accessToken = null;

const loginForm = document.getElementById('login-form');
const loginContainer = document.getElementById('login-container');
const dashboardContainer = document.getElementById('dashboard-container');
const errorMessage = document.getElementById('error-message');

// Colores de la paleta de viñedo para los gráficos
const viñedoColors = {
    primary: '#640E1B',   // Tinto oscuro
    secondary: '#A52A2A', // Marrón rojizo
    tertiary: '#795548',   // Marrón claro
    background: '#F5F5DC', // Pergamino
};

// ===============================================
// LÓGICA DE AUTENTICACIÓN
// ===============================================
async function login(username, password) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);

  try {
    const response = await fetch(`${BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });

    if (!response.ok) throw new Error('Credenciales incorrectas');

    const data = await response.json();
    accessToken = data.access_token;
    
    loginContainer.classList.add('hidden');
    dashboardContainer.classList.remove('hidden');

    // Iniciar la carga de datos del dashboard
    initializeDashboard();

  } catch (error) {
    console.error("Error al iniciar sesión:", error);
    errorMessage.textContent = 'Credenciales incorrectas.';
    errorMessage.classList.remove('hidden');
  }
}

loginForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const username = document.getElementById('username').value;
  const password = document.getElementById('password').value;
  login(username, password);
});


// ===============================================
// LÓGICA DEL DASHBOARD
// ===============================================

async function fetchData(endpoint) {
    const headers = { 'Authorization': `Bearer ${accessToken}` };
    const response = await fetch(`${BASE_URL}${endpoint}/${TENANT_ID}`, { headers });
    if (!response.ok) {
        console.error(`Error fetching ${endpoint}:`, response.statusText);
        return null;
    }
    return response.json();
}

async function fetchKPIs() {
  const totalSales = await fetchData('/data/analytics/total_sales');
  document.getElementById('total-sales').textContent = `${(totalSales?.total_sales || 0).toFixed(2)} €`;

  const totalInventory = await fetchData('/data/analytics/total_inventory');
  document.getElementById('total-inventory').textContent = `${totalInventory?.total_inventory || 0} unidades`;
  
  const totalValue = await fetchData('/data/analytics/total_inventory_value');
  document.getElementById('total-inventory-value').textContent = `${(totalValue?.total_inventory_value || 0).toFixed(2)} €`;

  const salesByChannelData = await fetchData('/data/analytics/sales_by_channel');
  renderSalesByChannelChart(salesByChannelData?.sales_by_channel || {});

  const salesData = await fetchData('/data/sales');
  renderSalesChart(salesData?.data || []);
  renderLists(salesData?.data || [], 'sales-list');

  const productsData = await fetchData('/data/products');
  renderLists(productsData?.data || [], 'products-list');
  
  const inventoryData = await fetchData('/data/inventory');
  renderLists(inventoryData?.data || [], 'inventory-list');
}

// ===============================================
// LÓGICA DE PREDICCIÓN (YA PREPARADA)
// ===============================================

async function runForecast() {
  const url = `${BASE_URL}/forecast/run?tenant_id=${TENANT_ID}&secret=${FORECAST_SECRET}`;
  await fetch(url, { method: "POST" });
  alert('Job de pronóstico iniciado. Los resultados aparecerán en breve.');
}

async function loadForecastResults() {
  const url = `${BASE_URL}/forecast/results/${TENANT_ID}?secret=${FORECAST_SECRET}`;
  try {
    const res = await fetch(url);
    if (!res.ok) return [];
    return await res.json();
  } catch (e) {
    console.error("Error cargando resultados de predicción:", e);
    return [];
  }
}

function renderForecastChart(rows, skuFilter = null) {
  const ctx = document.getElementById('forecastChart').getContext('2d');
  const filteredRows = rows.filter(r => !skuFilter || r.sku === skuFilter);
  const labels = [...new Set(filteredRows.map(p => p.date))].sort();
  
  const skus = [...new Set(filteredRows.map(p => p.sku))];

  const datasets = skus.map(sku => {
      const skuData = filteredRows.filter(r => r.sku === sku);
      return {
          label: sku,
          data: labels.map(label => {
              const point = skuData.find(p => p.date === label);
              return point ? Number(point.predicted_qty) : null;
          }),
          spanGaps: true,
          tension: 0.25,
          borderColor: viñedoColors.secondary,
          backgroundColor: 'transparent',
      };
  });

  if (forecastChart) forecastChart.destroy();
  forecastChart = new Chart(ctx, {
    type: 'line',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, title: { display: true, text: 'Unidades previstas' } },
        x: { title: { display: true, text: 'Fecha' } }
      }
    }
  });
}

document.getElementById('btnRunForecast')?.addEventListener('click', async () => {
  await runForecast();
  setTimeout(async () => {
    const rows = await loadForecastResults();
    const sku = document.getElementById('skuFilter').value.trim() || null;
    renderForecastChart(rows, sku);
  }, 5000); // Espera 5 segundos para dar tiempo al job
});

document.getElementById('btnUploadForecast')?.addEventListener('click', async () => {
  const f = document.getElementById('datasetFile').files[0];
  if (!f) return alert('Selecciona un archivo (.csv/.xlsx/.xls)');
  const form = new FormData();
  form.append('file', f);
  // Aquí faltaría añadir tenant_id y secret si el endpoint lo requiere
  await fetch(`${BASE_URL}/forecast/from-file`, { method: 'POST', body: form });
  alert('Archivo subido, actualizando predicciones...');
  const rows = await loadForecastResults();
  const sku = document.getElementById('skuFilter').value.trim() || null;
  renderForecastChart(rows, sku);
});

document.getElementById('skuFilter')?.addEventListener('input', async () => {
    const rows = await loadForecastResults();
    const sku = document.getElementById('skuFilter').value.trim() || null;
    renderForecastChart(rows, sku);
});


// ===============================================
// FUNCIONES DE RENDERIZADO
// ===============================================
function renderLists(data, elementId) {
    const listElement = document.getElementById(elementId);
    listElement.innerHTML = '';
    if (data.length === 0) {
        listElement.innerHTML = '<li class="p-4 text-center text-gray-500">No hay datos disponibles.</li>';
        return;
    }

    data.forEach(item => {
        const li = document.createElement('li');
        li.className = 'bg-gray-100 rounded-lg p-4 shadow-sm';
        let content = '';
        if (elementId === 'sales-list') {
            content = `<p><strong class="text-[#4A0C2B]">SKU:</strong> ${item.sku}</p>
                       <p><strong class="text-[#4A0C2B]">Cantidad:</strong> ${item.qty}</p>
                       <p><strong class="text-[#4A0C2B]">Precio:</strong> ${item.price} €</p>`;
        } else if (elementId === 'products-list') {
            content = `<p><strong class="text-[#4A0C2B]">SKU:</strong> ${item.sku}</p>
                       <p><strong class="text-[#4A0C2B]">Nombre:</strong> ${item.name}</p>
                       <p><strong class="text-[#4A0C2B]">Categoría:</strong> ${item.category}</p>`;
        } else if (elementId === 'inventory-list') {
            content = `<p><strong class="text-[#4A0C2B]">SKU:</strong> ${item.sku}</p>
                       <p><strong class="text-[#4A0C2B]">Cantidad:</strong> ${item.qty}</p>
                       <p><strong class="text-[#4A0C2B]">Ubicación:</strong> ${item.location}</p>`;
        }
        li.innerHTML = content;
        listElement.appendChild(li);
    });
}

function renderSalesChart(salesData) {
  const salesBySku = salesData.reduce((acc, item) => {
    acc[item.sku] = (acc[item.sku] || 0) + (item.qty * item.price);
    return acc;
  }, {});
  
  const ctx = document.getElementById('salesChart').getContext('2d');
  if (salesChart) salesChart.destroy();
  salesChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: Object.keys(salesBySku),
      datasets: [{
        label: 'Ventas por SKU (€)',
        data: Object.values(salesBySku),
        backgroundColor: viñedoColors.primary,
      }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false, 
        plugins: {
            legend: { display: false }
        }
    }
  });
}

function renderSalesByChannelChart(salesByChannelData) {
  const ctx = document.getElementById('salesByChannelChart').getContext('2d');
  if (salesByChannelChart) salesByChannelChart.destroy();
  salesByChannelChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: Object.keys(salesByChannelData),
      datasets: [{
        data: Object.values(salesByChannelData),
        backgroundColor: [viñedoColors.primary, viñedoColors.secondary, viñedoColors.tertiary],
      }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false, 
        plugins: {
            legend: {
              // ================== CAMBIO AQUÍ ==================
              position: 'right', // Mueve la leyenda a la derecha
              align: 'center',   // La centra verticalmente
              // ===============================================
            }
        }
    }
  });
}

// ===============================================
// INICIALIZACIÓN
// ===============================================
async function initializeDashboard() {
  await fetchKPIs();
  const forecastRows = await loadForecastResults();
  renderForecastChart(forecastRows);
}