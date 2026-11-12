(() => {
  const palette = ['#897aff', '#48c9b0', '#f2a45f', '#ea7185', '#63a8e8', '#b18bf1', '#c8d45c'];
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
    new Chart(canvas, {
      type: 'bar',
      data: { labels: data.labels, datasets: [{ data: data.values, backgroundColor: 'rgba(137,122,255,.75)', hoverBackgroundColor: '#a297ff', borderRadius: 5, maxBarThickness: 36 }] },
      options: barOptions
    });
  });
  ['categoryChart', 'monthlyCategoryChart'].forEach(id => {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    const data = readData(canvas);
    new Chart(canvas, {
      type: 'doughnut',
      data: { labels: data.labels, datasets: [{ data: data.values, backgroundColor: palette, borderColor: '#121a26', borderWidth: 4, hoverOffset: 6 }] },
      options: doughnutOptions
    });
  });
})();
