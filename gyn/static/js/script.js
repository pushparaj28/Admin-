

document.addEventListener('DOMContentLoaded', function() {
    
    // Purana delete wala code yahan upar rahega...
    const deleteButtons = document.querySelectorAll('.delete-btn');
    
    // Har button par click event laga rahe hain
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            // Confirmation popup show karo
            const userConfirmed = confirm('Kya aap sach me is appointment ko delete karna chahte hain?');
            
            // Agar user ne 'Cancel' dabaya, to link open hone se rok do
            if (!userConfirmed) {
                event.preventDefault();
            }
        });
    });

    // --- TOAST AUTO-HIDE LOGIC ---
    const toasts = document.querySelectorAll('.toast');
    
    toasts.forEach(toast => {
        // 3.5 seconds ke baad 'hide' class add kardo
        setTimeout(() => {
            toast.classList.add('hide');
        
            setTimeout(() => {
                toast.remove();
            }, 400);
        }, 3500); 
    });
});


//growth insight ke liye code. 
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Check karein ki page par chart ka data hai ya nahi (taaki doosre pages par error na aaye)
    const chartDataElement = document.getElementById('chartData');
    
    if (chartDataElement) {
        // 2. HTML se chupa hua data nikal kar array me convert karein
        const statusData = JSON.parse(chartDataElement.textContent);
        
        // 3. Donut Chart Setup
        const ctx = document.getElementById('statusChart').getContext('2d');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Completed', 'Pending', 'Cancelled'],
                datasets: [{
                    data: statusData, // Yeh data ab Django se aayega
                    backgroundColor: [
                        '#16a34a', // Green
                        '#ea580c', // Orange
                        '#dc2626'  // Red
                    ],
                    borderWidth: 0,
                    hoverOffset: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '75%', // Beech ka hole
                plugins: {
                    legend: {
                        display: false // Custom HTML legend ke liye hide kiya
                    }
                }
            }
        });
    }


    // LINE CHART (APPOINTMENT TRENDS)
    // ==========================================
    const trendLabelsElement = document.getElementById('trendLabels');
    const trendDataElement = document.getElementById('trendData');
    
    if (trendLabelsElement && trendDataElement) {
        // HTML se data nikalna
        const trendLabels = JSON.parse(trendLabelsElement.textContent);
        const trendData = JSON.parse(trendDataElement.textContent);
        
        const trendCtx = document.getElementById('trendChart').getContext('2d');
        
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: trendLabels,
                datasets: [{
                    label: 'Total Appointments',
                    data: trendData,
                    borderColor: '#0284c7', // Dark Blue line
                    backgroundColor: 'rgba(2, 132, 199, 0.1)', // Light Blue shadow area
                    borderWidth: 2,
                    pointBackgroundColor: '#ffffff',
                    pointBorderColor: '#0284c7',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    tension: 0.3, // Line ko thoda smooth (curved) karne ke liye
                    fill: true // Line ke neeche color fill karne ke liye
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false // Upar se extra label hatane ke liye
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1 // Y-axis par sirf whole numbers (1, 2, 3) dikhane ke liye
                        }
                    },
                    x: {
                        grid: {
                            display: false // Background me se sidhi line hatane ke liye
                        }
                    }
                }
            }
        });
    }

});