
document.addEventListener('DOMContentLoaded', function () {
    console.log("Reports script loaded.");

    // --- Revenue Trend Chart ---
    const revenueCtx = document.getElementById('revenueTrendChart')?.getContext('2d');
    if (revenueCtx && chartData.revenue_trend) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: chartData.revenue_trend.labels,
                datasets: [
                    {
                        label: 'Daily Revenue',
                        data: chartData.revenue_trend.revenue_data,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        yAxisID: 'y',
                        fill: true,
                    },
                    {
                        label: 'Jobs Completed',
                        data: chartData.revenue_trend.jobs_data,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        yAxisID: 'y1',
                        type: 'bar',
                    }
                ]
            },
            options: {
                responsive: true,
                interaction: { mode: 'index', intersect: false },
                scales: {
                    y: { type: 'linear', display: true, position: 'left', title: { display: true, text: 'Revenue ($)' } },
                    y1: { type: 'linear', display: true, position: 'right', title: { display: true, text: 'Jobs' }, grid: { drawOnChartArea: false } }
                }
            }
        });
    }

    // --- Service Breakdown Chart ---
    const serviceCtx = document.getElementById('serviceBreakdownChart')?.getContext('2d');
    if (serviceCtx && chartData.service_breakdown) {
        new Chart(serviceCtx, {
            type: 'doughnut',
            data: {
                labels: chartData.service_breakdown.labels.map(l => l.charAt(0).toUpperCase() + l.slice(1)),
                datasets: [{
                    label: 'Job Count',
                    data: chartData.service_breakdown.data,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)',
                        'rgba(255, 206, 86, 0.7)', 'rgba(75, 192, 192, 0.7)',
                        'rgba(153, 102, 255, 0.7)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: { position: 'top' }
                }
            }
        });
    }
});
