document.addEventListener('DOMContentLoaded', function() {

    // ==========================================
    // CUSTOM JS TOAST FUNCTION
    // ==========================================
    function showCustomToast(message, type = 'success') {
        // Pehle check karo ki toast-container page par hai ya nahi
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container';
            document.body.appendChild(container); // Agar nahi hai to body me jod do
        }

    // Naya toast element banao
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        // Icon set karo
        let iconHtml = '<i class="fa-solid fa-circle-check"></i>';
        if (type === 'warning') iconHtml = '<i class="fa-solid fa-trash-can"></i>';

        // Toast ke andar ka content
        toast.innerHTML = `${iconHtml} <span>${message}</span>`;

        // Container me dikhao
        container.appendChild(toast);

        // 3.5 second baad auto-hide kardo
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 400);
        }, 3500);
    }
    
    // ==========================================
    // 1. APPOINTMENT DELETE CONFIRMATION
    // ==========================================
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(event) {
            const userConfirmed = confirm('Kya aap sach me is appointment ko delete karna chahte hain?');
            if (!userConfirmed) {
                event.preventDefault();
            }
        });
    });

    // ==========================================
    // 2. TOAST AUTO-HIDE LOGIC
    // ==========================================
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => {
                toast.remove();
            }, 400);
        }, 3500); 
    });

    // ==========================================
    // 3. STATUS DONUT CHART
    // ==========================================
    const chartDataElement = document.getElementById('chartData');
    if (chartDataElement && chartDataElement.textContent.trim() !== "") {
        try {
            const statusData = JSON.parse(chartDataElement.textContent);
            const ctx = document.getElementById('statusChart').getContext('2d');
            new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Completed', 'Pending', 'Cancelled'],
                    datasets: [{
                        data: statusData,
                        backgroundColor: ['#16a34a', '#ea580c', '#dc2626'],
                        borderWidth: 0,
                        hoverOffset: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    plugins: { legend: { display: false } }
                }
            });
        } catch (e) {
            console.error("Error parsing status chart data", e);
        }
    }

    // ==========================================
    // 4. LINE CHART (APPOINTMENT TRENDS)
    // ==========================================
    const trendLabelsElement = document.getElementById('trendLabels');
    const trendDataElement = document.getElementById('trendData');
    
    if (trendLabelsElement && trendDataElement && trendLabelsElement.textContent.trim() !== "") {
        try {
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
                        borderColor: '#0284c7',
                        backgroundColor: 'rgba(2, 132, 199, 0.1)',
                        borderWidth: 2,
                        pointBackgroundColor: '#ffffff',
                        pointBorderColor: '#0284c7',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        tension: 0.3,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, ticks: { stepSize: 1 } },
                        x: { grid: { display: false } }
                    }
                }
            });
        } catch (e) {
            console.error("Error parsing trend chart data", e);
        }
    }

    // ==========================================
    // 5. EARNINGS BAR CHART
    // ==========================================
    const earnLabelsEl = document.getElementById('earnLabels');
    const earnDataEl = document.getElementById('earnData');
    
    if (earnLabelsEl && earnDataEl && earnLabelsEl.textContent.trim() !== "") {
        try {
            const labels = JSON.parse(earnLabelsEl.textContent);
            const data = JSON.parse(earnDataEl.textContent);
            const earnCtx = document.getElementById('earningsBarChart').getContext('2d');
            
            new Chart(earnCtx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Earnings (₹)',
                        data: data,
                        backgroundColor: '#10b981',
                        borderRadius: 6,
                        barThickness: 30
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { borderDash: [5, 5] } },
                        x: { grid: { display: false } }
                    }
                }
            });
        } catch (e) {
            console.error("Error parsing earnings chart data", e);
        }
    }

    // ==========================================
    // 6. SLOT MANAGEMENT & MODAL
    // ==========================================
    const addSlotBtn = document.getElementById('addSlotBtn');
    const slotsContainer = document.getElementById('slots-container');
    const emptyState = document.getElementById('empty-state');
    const slotTemplate = document.getElementById('slot-template');
    const dayTabs = document.querySelectorAll('.day-tab');
    const saveScheduleBtn = document.getElementById('saveScheduleBtn');
    
    // Modal Elements
    const deleteModal = document.getElementById('deleteModal');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    let slotToDelete = null;

    let currentDay = 'Monday';
    let weeklySchedule = {
        'Monday': [], 'Tuesday': [], 'Wednesday': [], 'Thursday': [],
        'Friday': [], 'Saturday': [], 'Sunday': []
    };


    function saveScreenToMemory() {
        if (!slotsContainer) return;
        const slots = [];
        const slotRows = slotsContainer.querySelectorAll('.slot-row');
        
        slotRows.forEach(row => {
            const selects = row.querySelectorAll('select');
            const inputs = row.querySelectorAll('input[type="time"]');
            slots.push({
                type: selects[0].value,
                start: inputs[0].value,
                end: inputs[1].value
            });
        });
        weeklySchedule[currentDay] = slots; // Jo din abhi open hai, usme data save kar do
    }

    // --- 3. MEMORY SE DATA SCREEN PAR DIKHANA ---
    function loadMemoryToScreen(day) {
        // Pehle screen par jo bhi purane slots hain, unhe hata do
        const existingRows = slotsContainer.querySelectorAll('.slot-row');
        existingRows.forEach(row => row.remove());

        const daySlots = weeklySchedule[day];
        
        if (daySlots.length === 0) {
            emptyState.style.display = 'block'; // Agar data nahi hai to empty state dikhao
        } else {
            emptyState.style.display = 'none';
            // Agar data hai, to ek-ek karke naye slots banao aur screen par lagao
            daySlots.forEach(slotData => {
                const newSlot = slotTemplate.content.cloneNode(true);
                const selects = newSlot.querySelectorAll('select');
                const inputs = newSlot.querySelectorAll('input[type="time"]');

                selects[0].value = slotData.type || 'Available';
                inputs[0].value = slotData.start || '';
                inputs[1].value = slotData.end || '';

                slotsContainer.appendChild(newSlot);
            });
        }
    }

    // --- 4. TABS CLICK LOGIC ---
    if (dayTabs.length > 0) {
        dayTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                // Naye din par jaane se pehle, purane din ka data save kar lo
                saveScreenToMemory();

                // UI me Tab ka color change karo (Blue line)
                dayTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');

                // Naya din set karo aur uska data load karo
                currentDay = this.innerText.trim();
                loadMemoryToScreen(currentDay);
            });
        });
    }



    // --- 5. ADD SLOT LOGIC ---
    if (addSlotBtn && slotTemplate) {
        addSlotBtn.addEventListener('click', function() {
            emptyState.style.display = 'none';
            const newSlot = slotTemplate.content.cloneNode(true);
            slotsContainer.appendChild(newSlot);
           
        });
    }
    
// --- 6. DELETE MODAL LOGIC ---
if (slotsContainer) {
    slotsContainer.addEventListener('click', function(e) {
        const deleteBtn = e.target.closest('.delete-slot-btn');
        if (deleteBtn) {
            slotToDelete = deleteBtn.closest('.slot-row');
            deleteModal.style.display = 'flex';
        }
    });
}

if (cancelDeleteBtn) {
    cancelDeleteBtn.addEventListener('click', function() {
        deleteModal.style.display = 'none';
        slotToDelete = null;
    });
}

if (confirmDeleteBtn) {
    confirmDeleteBtn.addEventListener('click', function() {
        if (slotToDelete) {
            slotToDelete.remove();
            deleteModal.style.display = 'none';
            slotToDelete = null;
            
            if (slotsContainer.querySelectorAll('.slot-row').length === 0) {
                emptyState.style.display = 'block';
            }
        }
    });
}


    // CONFIRM DELETE LOGIC
    // --- 7. SAVE SCHEDULE BUTTON LOGIC ---
    if (saveScheduleBtn) {
        saveScheduleBtn.addEventListener('click', function() {
            saveScreenToMemory(); // Jo last din open tha, usko bhi memory me save karo
            
            // Checking the data in console
            console.log("FINAL SCHEDULE DATA: ", weeklySchedule);
            
            // Abhi ke liye ek alert dikha rahe hain
            showCustomToast('New time slot added successfully!', 'success');
        });
    }



    // ==========================================
    // APPLY LEAVE LOGIC (Form to Table)
    // ==========================================
    const applyLeaveBtn = document.getElementById('applyLeaveBtn');
    const leaveModal = document.getElementById('leaveModal');
    const closeLeaveBtn = document.getElementById('closeLeaveBtn');
    const cancelLeaveBtn = document.getElementById('cancelLeaveBtn');
    const leaveForm = document.getElementById('leaveForm');
    const leaveTableBody = document.getElementById('leaveTableBody');

    if (applyLeaveBtn && leaveModal) {
        
        // 1. Modal Open karna
        applyLeaveBtn.addEventListener('click', () => {
            leaveModal.style.display = 'flex';
        });

        // 2. Modal Close karne ka function (sath me form reset bhi hoga)
        const closeLeaveModal = () => {
            leaveModal.style.display = 'none';
            leaveForm.reset(); 
        };

        closeLeaveBtn.addEventListener('click', closeLeaveModal);
        cancelLeaveBtn.addEventListener('click', closeLeaveModal);

        // 3. Form Submit Logic
        leaveForm.addEventListener('submit', function(e) {
            e.preventDefault(); // Page refresh hone se rokne ke liye
            
            const startVal = document.getElementById('leaveStart').value;
            const endVal = document.getElementById('leaveEnd').value;
            const reasonVal = document.getElementById('leaveReason').value;

            // Dates check karna ki Start Date, End Date se aage na ho
            const startDate = new Date(startVal);
            const endDate = new Date(endVal);
            
            if (endDate < startDate) {
                alert("End date cannot be before start date!");
                return;
            }

            // Duration calculate karna (Days me)
            const diffTime = Math.abs(endDate - startDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1; // +1 kiya taaki same day par 1 day show ho

            // Nayi row ka HTML banana
            const newRow = document.createElement('tr');
            newRow.innerHTML = `
                <td>${startVal} <i class="fa-solid fa-arrow-right arrow-sm"></i> ${endVal}</td>
                <td>${reasonVal}</td>
                <td><span class="status-badge pending">Pending</span></td>
                <td>${diffDays} days</td>
                <td><button class="btn-icon danger"><i class="fa-regular fa-trash-can"></i></button></td>
            `;

            // Table ke sabse upar nayi row add karna
            leaveTableBody.prepend(newRow);
            
            // Sab kaam hone ke baad modal close kardo
            closeLeaveModal();
            showCustomToast('Leave application submitted successfully!', 'success');
        });
    }


// Chart ke liye logic hai review vale section me 
// Canvas element ko select karein
const chartCanvas = document.getElementById('reviewChart');
    
    if (chartCanvas) {
        console.log("Review Chart waala element mil gaya hai!"); // Console me check karne ke liye
        
        try {
            const reviewCtx = chartCanvas.getContext('2d');
            
            // HTML se raw text nikalte hain
            const rawLabels = chartCanvas.getAttribute('data-labels');
            const rawValues = chartCanvas.getAttribute('data-values');
            
            console.log("JS me Labels aaye:", rawLabels);
            console.log("JS me Values aaye:", rawValues);

            // Data ko parse karke array banate hain
            const labels = JSON.parse(rawLabels);
            const data = JSON.parse(rawValues);
            
            new Chart(reviewCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Total Reviews',
                        data: data,
                        borderColor: '#5a4fcf',
                        backgroundColor: 'rgba(90, 79, 207, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4, 
                        pointBackgroundColor: '#5a4fcf',
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false } 
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { stepSize: 1, precision: 0 },
                            grid: { borderDash: [4, 4] }
                        },
                        x: {
                            grid: { display: false }
                        }
                    }
                }
            });
            console.log("Chart successfully create ho gaya hai!");
            
        } catch (err) {
            console.error("Bhai, JSON parse karne me ya Chart banane me ye error aayi hai:", err);
        }
    } else {
        console.log("Review Chart waala element is page par nahi mila.");
    }

// 1. EARNINGS TREND CHART (Bar Chart)
    const trendCanvas = document.getElementById('earningsTrendChart');
    if (trendCanvas) {
        const trendCtx = trendCanvas.getContext('2d');
        const labels = JSON.parse(trendCanvas.getAttribute('data-labels') || '[]');
        const data = JSON.parse(trendCanvas.getAttribute('data-values') || '[]');
        
        new Chart(trendCtx, {
            type: 'bar', // Isko line ki jagah bar kar diya hai
            data: {
                labels: labels,
                datasets: [{
                    label: 'Earnings (₹)',
                    data: data,
                    backgroundColor: '#10b981', // Green color
                    borderRadius: 4,
                    barThickness: 20 // Bar ki motayi
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, grid: { borderDash: [4, 4] } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 2. EARNING BREAKDOWN CHART (Doughnut Chart)
    const breakdownCanvas = document.getElementById('earningBreakdownChart');
    if (breakdownCanvas) {
        try {
            const breakdownCtx = breakdownCanvas.getContext('2d');
            
            // HTML se dynamic data nikal rahe hain
            const bLabels = JSON.parse(breakdownCanvas.getAttribute('data-labels') || '[]');
            const bData = JSON.parse(breakdownCanvas.getAttribute('data-values') || '[]');
            
            new Chart(breakdownCtx, {
                type: 'doughnut',
                data: {
                    // Agar data hai toh asli labels, warna "No Data"
                    labels: bLabels.length > 0 ? bLabels : ['No Data'],
                    datasets: [{
                        data: bData.length > 0 ? bData : [1], 
                        // Green (Completed), Orange (Pending), Pink (Withdrawn). Agar khali hai toh Grey.
                        backgroundColor: bData.length > 0 ? ['#10b981', '#f59e0b', '#ec4899'] : ['#e5e7eb'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    cutout: '75%',
                    plugins: {
                        legend: { position: 'bottom', labels: { boxWidth: 10, font: {size: 11} } }
                    }
                }
            });
        } catch (error) {
            console.error("Pie Chart error:", error);
        }
    }

    const calcGroups = document.querySelectorAll('.calc-group');

    function calculatePricing(group) {
        let basePrice = parseFloat(group.querySelector('.base-price').value) || 0;
        let feePct = parseFloat(group.querySelector('.fee-pct').value) || 0;
        let taxPct = parseFloat(group.querySelector('.tax-pct').value) || 0;

        let feeAmount = basePrice * (feePct / 100);
        let taxAmount = feeAmount * (taxPct / 100);
        let finalPrice = basePrice + feeAmount + taxAmount;

        group.querySelector('.fee-amt').textContent = feeAmount.toFixed(2);
        group.querySelector('.tax-amt').textContent = taxAmount.toFixed(2);
        group.querySelector('.final-price').textContent = Math.round(finalPrice); // Round off value
    }

    calcGroups.forEach(group => {
        calculatePricing(group);

        let inputs = group.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', function() {
                calculatePricing(group);
            });
        });
    });

});


/* =========================================================================
   SERVICE AREA SETTINGS PAGE - PINCODE & MAP LOGIC (NEW FEATURE)
   ========================================================================= */
   document.addEventListener("DOMContentLoaded", function() {
    
    // SAFETY CHECK: Yeh check karega ki kya hum Service Area wale page par hain?
    // Agar nahi hain, toh ye script yahin ruk jayegi aur baaki pages ko disturb nahi karegi.
    const pincodeInput = document.getElementById('pincode-input');
    if (!pincodeInput) return; 

    // Global variables for this page
    var map, marker;
    const cityInput = document.getElementById('city-input');

    // 1. PINCODE SE CITY FETCH KARNA AUR MAP UPDATE KARNA
    pincodeInput.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^0-9]/g, ''); 
        let pin = this.value;

        if(pin.length === 6) {
            cityInput.value = "Fetching City & Map..."; 
            
            fetch(`https://api.postalpincode.in/pincode/${pin}`)
            .then(response => response.json())
            .then(data => {
                if(data[0].Status === "Success") {
                    let district = data[0].PostOffice[0].District;
                    let state = data[0].PostOffice[0].State;
                    
                    cityInput.value = district;
                    cityInput.style.borderColor = "#10b981"; 
                    
                    // Map ko naye Pincode par le jana
                    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${pin},+${district},+${state},+India`)
                    .then(res => res.json())
                    .then(mapData => {
                        if(mapData.length > 0) {
                            var newLat = parseFloat(mapData[0].lat); // parse flot string to number
                            var newLng = parseFloat(mapData[0].lon);
                            
                            if(map && marker) {
                                map.setView([newLat, newLng], 13); // map set kar dega 
                                marker.setLatLng([newLat, newLng]); // marker ko bhi map me set kar dega.
                            }
                            
                            document.getElementById('lat-display').innerText = newLat.toFixed(5);
                            document.getElementById('lng-display').innerText = newLng.toFixed(5);
                            document.getElementById('input-lat').value = newLat.toFixed(5); //databse me hide value ko update ka kar dega 
                            document.getElementById('input-lng').value = newLng.toFixed(5);
                        }
                    });

                } else {
                    cityInput.value = "";
                    alert("Invalid PIN Code!");
                    cityInput.style.borderColor = "#ef4444"; 
                }
            })
            .catch(error => {
                cityInput.value = "";
                alert("Internet Connection Error.");
            });
        } else {
            cityInput.value = "";
            cityInput.style.borderColor = "#e2e8f0";
        }
    });


    // 2. MAP INITIALIZATION & INTERACTION
    var latInput = document.getElementById('input-lat');
    var lngInput = document.getElementById('input-lng');
    var latDisplay = document.getElementById('lat-display');
    var lngDisplay = document.getElementById('lng-display');

    var savedLat = parseFloat(latInput.value) || 26.42555;
    var savedLng = parseFloat(lngInput.value) || 80.34391;

    map = L.map('service-map').setView([savedLat, savedLng], 13); //Leaflet map create karta hai.
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {      // OpenStreetMap ki roads, buildings, etc. load karta hai ye 
        maxZoom: 19,
        attribution: '© OpenStreetMap'
    }).addTo(map);

    marker = L.marker([savedLat, savedLng], {draggable: true}).addTo(map); // marker create karega 

    marker.on('dragend', function (e) {
        var position = marker.getLatLng();
        latDisplay.innerText = position.lat.toFixed(5);
        lngDisplay.innerText = position.lng.toFixed(5);
        latInput.value = position.lat.toFixed(5);
        lngInput.value = position.lng.toFixed(5);
        map.panTo(position); 
    });

    map.on('click', function(e) {
        marker.setLatLng(e.latlng);
        latDisplay.innerText = e.latlng.lat.toFixed(5);
        lngDisplay.innerText = e.latlng.lng.toFixed(5);
        latInput.value = e.latlng.lat.toFixed(5);
        lngInput.value = e.latlng.lng.toFixed(5);
    });  // User map pe kahin click kare.  Marker wahi jump kar jayega.  Coordinates update ho jayenge.

    document.getElementById('btn-search-map').addEventListener('click', function() {
        var query = document.getElementById('map-search-input').value;
        if(query) {
            fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${query}`)
            .then(res => res.json())
            .then(data => {
                if(data.length > 0) {
                    var newLat = parseFloat(data[0].lat);
                    var newLng = parseFloat(data[0].lon);
                    
                    map.setView([newLat, newLng], 14);
                    marker.setLatLng([newLat, newLng]);
                    
                    latDisplay.innerText = newLat.toFixed(5);
                    lngDisplay.innerText = newLng.toFixed(5);
                    latInput.value = newLat.toFixed(5);
                    lngInput.value = newLng.toFixed(5);
                } else {
                    alert("Location not found! Try spelling it differently.");
                }
            });
        }
    });

    // Make map globally accessible for the GPS function
    window.serviceMap = map;
    window.serviceMarker = marker;
});

// 3. CURRENT LOCATION FETCH (GPS) - Global Function
function getUserCurrentLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            var myLat = position.coords.latitude;
            var myLng = position.coords.longitude;
            
            if(window.serviceMap && window.serviceMarker) {
                window.serviceMap.setView([myLat, myLng], 14);
                window.serviceMarker.setLatLng([myLat, myLng]);
            }
            
            document.getElementById('input-lat').value = myLat.toFixed(5);
            document.getElementById('input-lng').value = myLng.toFixed(5);
            document.getElementById('lat-display').innerText = myLat.toFixed(5);
            document.getElementById('lng-display').innerText = myLng.toFixed(5);
            document.getElementById('map-search-input').value = "My Current Location";
            
        }, function(error) {
            alert("Please allow location access in your browser to use this feature.");
        });
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}