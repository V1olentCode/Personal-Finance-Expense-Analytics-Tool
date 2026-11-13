(() => {
  const palette = ['#897aff', '#48c9b0', '#f2a45f', '#ea7185', '#63a8e8', '#b18bf1', '#c8d45c'];
  const root = document.documentElement;
  const themeToggle = document.getElementById('themeToggle');
  const chartInstances = [];
  const token = name => getComputedStyle(root).getPropertyValue(name).trim();
  const syncChartTheme = () => {
    const text = token('--chart-tick');
    const grid = token('--chart-grid');
    const tooltip = token('--chart-tooltip');
    const tooltipText = token('--chart-tooltip-text');
    const chartBorder = token('--chart-border');
    chartInstances.forEach(chart => {
      chart.options.plugins.tooltip.backgroundColor = tooltip;
      chart.options.plugins.tooltip.titleColor = tooltipText;
      chart.options.plugins.tooltip.bodyColor = tooltipText;
      chart.options.plugins.tooltip.borderColor = grid;
      if (chart.config.type === 'bar') {
        chart.options.scales.x.ticks.color = text;
        chart.options.scales.y.ticks.color = text;
        chart.options.scales.y.grid.color = grid;
      } else {
        chart.options.plugins.legend.labels.color = text;
        chart.data.datasets.forEach(dataset => { dataset.borderColor = chartBorder; });
      }
      chart.update('none');
    });
  };
  const setTheme = theme => {
    root.dataset.theme = theme;
    try { localStorage.setItem('pennywise-theme', theme); } catch (_) { /* Storage may be disabled. */ }
    if (themeToggle) {
      const isLight = theme === 'light';
      const label = `Switch to ${isLight ? 'dark' : 'light'} mode`;
      themeToggle.setAttribute('aria-label', label);
      themeToggle.setAttribute('title', label);
      themeToggle.setAttribute('aria-pressed', String(isLight));
    }
    syncChartTheme();
  };
  if (themeToggle) {
    setTheme(root.dataset.theme === 'light' ? 'light' : 'dark');
    themeToggle.addEventListener('click', () => {
      setTheme(root.dataset.theme === 'light' ? 'dark' : 'light');
    });
  }
  const csvInput = document.querySelector('.file-picker input[type="file"]');
  if (csvInput) {
    csvInput.addEventListener('change', () => {
      const label = document.querySelector('.file-name');
      if (label) label.textContent = csvInput.files[0]?.name || 'CSV file · up to 5 MB';
    });
  }
  const readData = canvas => ({
    labels: JSON.parse(canvas.dataset.labels || '[]'),
    values: JSON.parse(canvas.dataset.values || '[]')
  });
  const currency = value => `₹${Number(value).toLocaleString('en-IN')}`;

  const barOptions = {
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { callbacks: { label: context => ` ${currency(context.raw)}` } }
    },
    scales: {
      x: { grid: { display: false }, ticks: { color: '#77869b', font: { size: 10 } }, border: { display: false } },
      y: { beginAtZero: true, grid: { color: 'rgba(132,148,171,.12)' }, ticks: { color: '#77869b', font: { size: 9 }, callback: currency }, border: { display: false } }
    }
  };
  const doughnutOptions = {
    maintainAspectRatio: false,
    cutout: '68%',
    plugins: {
      legend: { position: 'bottom', labels: { color: '#9ba8ba', boxWidth: 8, boxHeight: 8, padding: 13, font: { size: 9 } } },
      tooltip: { callbacks: { label: context => ` ${context.label}: ${currency(context.raw)}` } }
    }
  };

  if (!window.Chart) return;
  ['monthlyChart', 'monthlyTrendChart'].forEach(id => {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const data = readData(canvas);
    const chart = new Chart(canvas, {
      type: 'bar',
      data: { labels: data.labels, datasets: [{ data: data.values, backgroundColor: 'rgba(137,122,255,.75)', hoverBackgroundColor: '#a297ff', borderRadius: 5, maxBarThickness: 36 }] },
      options: {
        ...barOptions,
        scales: {
          x: { ...barOptions.scales.x, ticks: { ...barOptions.scales.x.ticks, color: token('--chart-tick') } },
          y: { ...barOptions.scales.y, grid: { ...barOptions.scales.y.grid, color: token('--chart-grid') }, ticks: { ...barOptions.scales.y.ticks, color: token('--chart-tick') } }
        },
        plugins: { ...barOptions.plugins, tooltip: { ...barOptions.plugins.tooltip, backgroundColor: token('--chart-tooltip'), titleColor: token('--chart-tooltip-text'), bodyColor: token('--chart-tooltip-text'), borderColor: token('--chart-grid'), borderWidth: 1 } }
      }
    });
    chartInstances.push(chart);
  });
  ['categoryChart', 'monthlyCategoryChart'].forEach(id => {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const data = readData(canvas);
    const chart = new Chart(canvas, {
      type: 'doughnut',
      data: { labels: data.labels, datasets: [{ data: data.values, backgroundColor: palette, borderColor: token('--chart-border'), borderWidth: 4, hoverOffset: 6 }] },
      options: {
        ...doughnutOptions,
        plugins: {
          legend: { ...doughnutOptions.plugins.legend, labels: { ...doughnutOptions.plugins.legend.labels, color: token('--chart-tick') } },
          tooltip: { ...doughnutOptions.plugins.tooltip, backgroundColor: token('--chart-tooltip'), titleColor: token('--chart-tooltip-text'), bodyColor: token('--chart-tooltip-text'), borderColor: token('--chart-grid'), borderWidth: 1 }
        }
      }
    });
    chartInstances.push(chart);
  });
})();
