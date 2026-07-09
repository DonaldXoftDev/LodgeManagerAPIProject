let currentDashboardData = null;
let currentFilter = 'all';
let currentSearch = '';

document.addEventListener('DOMContentLoaded', () => {
    const lodgeId = localStorage.getItem('active_lodge_id');
    const lodgeName = localStorage.getItem('active_lodge_name');
    
    if (!lodgeId) {
        window.location.href = 'lodges.html';
        return;
    }
    
    document.getElementById('lodge-name-display').textContent = lodgeName || `Lodge #${lodgeId}`;
    
    document.querySelectorAll('.filter-chip').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentFilter = e.target.getAttribute('data-filter');
            renderDashboardGrid();
        });
    });

    document.getElementById('search-input').addEventListener('input', (e) => {
        currentSearch = e.target.value.toLowerCase();
        renderDashboardGrid();
    });

    fetchDashboard(lodgeId);
});

async function fetchDashboard(lodgeId) {
    try {
        const data = await apiFetch(`/dashboard-landlord/me/landlord/${lodgeId}`);
        currentDashboardData = data;
        
        // Render financials
        const cF = (val) => {
            if (val === undefined || val === null) return 'N/A';
            return `₦${val.toLocaleString('en-NG')}.00`;
        };
        
        document.getElementById('fin-potential').textContent = cF(data.financials.potential_revenue);
        document.getElementById('fin-expected').textContent = cF(data.financials.expected_revenue);
        document.getElementById('fin-collected').textContent = cF(data.financials.collected_revenue);
        document.getElementById('fin-unpaid').textContent = cF(data.financials.unpaid_rent);
        
        document.getElementById('fact-rooms').textContent = data.entity_counts.total_rooms;
        document.getElementById('fact-tenants').textContent = data.entity_counts.total_tenants;
        
        const occRate = data.entity_counts.occupancy_rate;
        document.getElementById('occ-text').textContent = occRate + '%';
        
        const offset = Math.max(0, 283 - (283 * (occRate / 100)));
        document.getElementById('occ-ring').style.strokeDashoffset = offset;
        
        renderDashboardGrid();
        
    } catch (err) {
        showToast(err.message);
    }
}

function renderDashboardGrid() {
    if (!currentDashboardData) return;
    const grid = document.getElementById('dashboard-grid');
    grid.innerHTML = '';
    
    let roomsToRender = [];
    const d = currentDashboardData;
    
    const safeRooms = d.occupied_rooms_lease?.safe || [];
    const expiringRooms = d.occupied_rooms_lease?.expiring || [];
    const overdueRooms = d.occupied_rooms_lease?.overdue || [];
    const owingRooms = d.occupied_rooms_lease?.owing || [];
    const pendingRooms = d.occupied_rooms_lease?.pending || []; // Pending Termination
    
    // Add Vacant and Maintenance to uniform array shape
    const cF = (val) => {
        if (val === undefined || val === null) return 'N/A';
        // User explicitly said: money is not in kobo yet, just add .00
        return `₦${val.toLocaleString('en-NG')}.00`;
    };

    const toTitleCase = (str) => {
        if (!str) return '';
        return str.toLowerCase().replace(/\b\w/g, s => s.toUpperCase());
    };

    // Vacant and Maintenance already come as RoomGridSummary. Do not overwrite with undefined properties!
    const vRooms = d.vacant_rooms || [];
    const mRooms = d.maintenance_rooms || [];

    if (currentFilter === 'all') {
        roomsToRender = [...safeRooms, ...expiringRooms, ...overdueRooms, ...owingRooms, ...pendingRooms, ...vRooms, ...mRooms];
    } else if (currentFilter === 'Chase Rent') {
        roomsToRender = [...overdueRooms, ...owingRooms];
    } else if (currentFilter === 'Safe') { roomsToRender = safeRooms; }
    else if (currentFilter === 'Expiring') { roomsToRender = expiringRooms; }
    else if (currentFilter === 'Pending') { roomsToRender = pendingRooms; }
    else if (currentFilter === 'Vacant') { roomsToRender = vRooms; }
    else if (currentFilter === 'Maintenance') { roomsToRender = mRooms; }

    if (currentSearch) {
        roomsToRender = roomsToRender.filter(r => 
            String(r.room_no || '').toLowerCase().includes(currentSearch) ||
            String(r.main_display_text || '').toLowerCase().includes(currentSearch)
        );
    }
    
    roomsToRender.sort((a, b) => String(a.room_no || '').localeCompare(String(b.room_no || ''), undefined, {numeric: true, sensitivity: 'base'}));

    document.getElementById('results-count').innerHTML = `Showing <span>${roomsToRender.length}</span> rooms`;
    roomsToRender.forEach(r => {
        const card = document.createElement('div');
        card.className = `room-card`;
        
        const vMap = {
            'Success': 'var(--safe)', 'Warning': 'var(--expiring)', 'Danger': 'var(--owing)',
            'Orange': 'var(--overdue)', 'Purple': 'var(--pending)', 'Info': 'var(--vacant)', 'Inactive': 'var(--maintenance)'
        };
        const badgeColor = vMap[r.badge_variant] || 'var(--accent-base)';
        
        let alertHTML = '';
        if (String(r.badge_text).toLowerCase() === 'pending') {
            alertHTML = `<div style="background:var(--owing-bg); color:var(--owing); padding:8px 12px; border-radius:8px; font-size:12px; font-weight:600; margin-bottom:12px; border:1px solid var(--owing-border);">Termination Requested</div>`;
        }

        const tenantName = toTitleCase(r.main_display_text || 'N/A');
        
        // Progress bar logic.
        let progressPercent = 100;
        const match = (r.sub_display_text || '').match(/(\d+)/);
        if (match) {
            const daysLeft = parseInt(match[1]);
            progressPercent = Math.min(100, Math.max(0, (daysLeft / 365) * 100)); // Rough estimate
        }

        const isVacantOrMaintenance = !r.lease_id;

        card.innerHTML = `
            ${alertHTML}
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px;">
                <h3 style="font-size:24px; font-family:'Outfit',sans-serif; margin:0;">Room ${r.room_no || '??'}</h3>
                <span style="background:${badgeColor}; color:#fff; padding:4px 12px; border-radius:20px; font-size:11px; text-transform:uppercase; font-weight:700; display:inline-flex; align-items:center; gap:6px; box-shadow: 0 0 0 3px ${badgeColor}30, 0 4px 10px ${badgeColor}40;">
                    <span style="width:6px; height:6px; border-radius:50%; background:#fff;"></span>
                    ${r.badge_text || 'N/A'}
                </span>
            </div>
            
            <div style="font-weight:600; font-size:16px; margin-bottom:16px; color:var(--text-primary);">${tenantName}</div>
            
            <div style="margin-bottom:8px;">
                <div style="background:var(--surface-hover); height:8px; border-radius:4px; overflow:hidden; border:1px solid var(--border-glass); margin-bottom:6px;">
                    <div style="width:${isVacantOrMaintenance ? 0 : progressPercent}%; background:${isVacantOrMaintenance ? 'var(--border-glass)' : badgeColor}; height:100%; border-radius:4px; transition:width 0.5s ease;"></div>
                </div>
                <div style="color:${isVacantOrMaintenance ? 'var(--text-tertiary)' : 'var(--text-secondary)'}; font-size:12px; font-weight:600; text-align:right;">
                    ${r.sub_display_text || 'N/A'}
                </div>
            </div>
        `;
        
        card.onclick = () => openRoomSidePanel(r);
        grid.appendChild(card);
    });
}

async function openRoomSidePanel(roomData) {
    document.getElementById('room-panel').classList.add('open');
    
    const contentDiv = document.getElementById('panel-content');
    contentDiv.innerHTML = `<div style="text-align:center; padding: 40px; color:var(--text-tertiary);">Loading details...</div>`;
    
    try {
        let actionButtons = '';
        const vMap = {
            'Success': 'var(--safe)', 'Warning': 'var(--expiring)', 'Danger': 'var(--owing)',
            'Orange': 'var(--overdue)', 'Purple': 'var(--pending)', 'Info': 'var(--vacant)', 'Inactive': 'var(--maintenance)'
        };
        const badgeColor = vMap[roomData.badge_variant] || 'var(--accent-base)';

        // Move badge to header next to room number
        document.getElementById('panel-room-no').innerHTML = `
            <div style="display:flex; align-items:center; gap:12px;">
                <span>Room ${roomData.room_no}</span>
                <span style="background:${badgeColor}; color:#fff; padding:4px 12px; border-radius:20px; font-size:11px; text-transform:uppercase; font-weight:700; display:inline-flex; align-items:center; gap:6px; box-shadow: 0 0 0 3px ${badgeColor}30, 0 4px 10px ${badgeColor}40; letter-spacing:0.5px;">
                    <span style="width:6px; height:6px; border-radius:50%; background:#fff;"></span>
                    ${roomData.badge_text}
                </span>
            </div>
        `;

        if (roomData.lease_id) {
            // Room is occupied
            const leaseInfo = await apiFetch(`/dashboard-landlord/lease-info/${roomData.lease_id}`);
            
            if (String(roomData.badge_text).toLowerCase() === 'pending') {
                actionButtons = `
                    <div style="background:var(--owing-bg); padding:16px; border-radius:12px; border:1px solid var(--owing-border); margin-bottom:16px;">
                        <p style="font-weight:600; color:var(--owing); margin-bottom:8px;">Tenant Requested Termination</p>
                        <button class="btn btn-primary" style="width:100%; background:var(--owing); box-shadow:0 4px 12px rgba(225,29,72,0.3);" onclick="approveTermination(${roomData.lease_id})">Approve Termination</button>
                    </div>
                `;
            } else {
                actionButtons = `
                    <button class="btn btn-outline" style="width:100%; color:var(--owing); border-color:var(--owing-border);" onclick="approveTermination(${roomData.lease_id})">Force Terminate Lease</button>
                `;
            }

            const cF = (val) => {
                if (val === undefined || val === null) return 'N/A';
                return `₦${val.toLocaleString('en-NG')}.00`;
            };
            
            const formatDate = (dateStr) => {
                if(!dateStr) return 'N/A';
                const date = new Date(dateStr);
                const d = date.getDate();
                const suffix = ["th", "st", "nd", "rd"][d % 10 > 3 ? 0 : (d % 100 - d % 10 != 10) * d % 10];
                return `${d}${suffix} ${date.toLocaleString('en-US', { month: 'short', year: 'numeric' })}`;
            };
            
            // Progress bar calculation
            let progressPercent = 100;
            const match = (roomData.sub_display_text || '').match(/(\d+)/);
            if (match) {
                const daysLeft = parseInt(match[1]);
                progressPercent = Math.min(100, Math.max(0, (daysLeft / 365) * 100));
            }

            contentDiv.innerHTML = `
                <div class="glass-panel" style="margin-bottom:24px;">
                    <p style="font-size:20px; font-weight:700; font-family:'Outfit',sans-serif; margin-bottom:16px;">${roomData.main_display_text}</p>
                    
                    <div style="margin-bottom:24px;">
                        <div style="background:var(--surface-hover); height:8px; border-radius:4px; overflow:hidden; border:1px solid var(--border-glass); margin-bottom:6px;">
                            <div style="width:${progressPercent}%; background:${badgeColor}; height:100%; border-radius:4px; transition:width 0.5s ease;"></div>
                        </div>
                        <div style="color:var(--text-secondary); font-size:12px; font-weight:600; text-align:right;">
                            ${roomData.sub_display_text}
                        </div>
                    </div>
                    
                    <div style="padding-top:16px; border-top:1px solid var(--border-color); font-size:14px;">
                        <p style="font-weight:700; color:var(--text-primary); margin-bottom:12px; font-family:'Outfit',sans-serif; font-size:16px;">Lease Terms</p>
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:16px;">
                            <div>
                                <div style="color:var(--text-tertiary); font-size:11px; text-transform:uppercase; font-weight:700; margin-bottom:4px;">Start Date</div>
                                <div style="font-weight:600;">${formatDate(leaseInfo.lease.start_date)}</div>
                            </div>
                            <div>
                                <div style="color:var(--text-tertiary); font-size:11px; text-transform:uppercase; font-weight:700; margin-bottom:4px;">End Date</div>
                                <div style="font-weight:600;">${formatDate(leaseInfo.lease.end_date)}</div>
                            </div>
                        </div>
                    </div>
                    
                    <div style="padding-top:16px; border-top:1px solid var(--border-color); font-size:14px;">
                        <p style="font-weight:700; color:var(--text-primary); margin-bottom:12px; font-family:'Outfit',sans-serif; font-size:16px;">Financials</p>
                        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                            <span style="color:var(--text-secondary);">Agreed Rent:</span>
                            <span style="font-weight:600;">${cF(leaseInfo.finance.agreed_rent)}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
                            <span style="color:var(--text-secondary);">Total Paid:</span>
                            <span style="font-weight:600; color:var(--safe);">${cF(leaseInfo.finance.total_paid)}</span>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding-top:12px; border-top:1px dashed var(--border-color);">
                            <span style="color:var(--text-secondary); font-weight:600;">Remaining Balance:</span>
                            <span style="font-weight:700; color:var(--owing);">${cF(leaseInfo.finance.remaining_balance)}</span>
                        </div>
                    </div>
                </div>
                
                ${actionButtons}
            `;
        } else {
            // Room is vacant or maintenance
            const roomDetails = await apiFetch(`/rooms/${roomData.room_id}`);
            
            if (String(roomData.badge_text).toLowerCase() === 'vacant') {
                actionButtons = `
                    <button class="btn btn-primary" style="width:100%; border-radius:12px; margin-bottom:12px; height:48px; font-size:16px;" onclick="window.location.href='leases.html'">Assign Lease</button>
                    <button class="btn btn-outline" style="width:100%; border-radius:12px; height:44px;" onclick="toggleRoomMaintenance(${roomDetails.id}, 'Maintenance')">Set to Maintenance</button>
                `;
            } else if (String(roomData.badge_text).toLowerCase() === 'maintenance') {
                actionButtons = `
                    <button class="btn btn-outline" style="width:100%; border-radius:12px; height:48px;" onclick="toggleRoomMaintenance(${roomDetails.id}, 'Vacant')">Set to Vacant</button>
                `;
            }

            contentDiv.innerHTML = `
                <div class="glass-panel" style="margin-bottom:24px; text-align:center; padding:32px 16px;">
                    <div style="font-size:48px; margin-bottom:16px;">🏠</div>
                    <p style="font-size:20px; font-weight:700; font-family:'Outfit',sans-serif; margin-bottom:8px;">${roomDetails.room_no}</p>
                    <p style="font-size:14px; color:var(--text-secondary);">This room is currently ${String(roomData.badge_text).toLowerCase()}. It is not assigned to any tenant.</p>
                </div>
                
                ${actionButtons}
            `;
        }
        
    } catch (err) {
        contentDiv.innerHTML = `
            <div style="color:var(--owing); text-align:center; padding:24px; background:var(--owing-bg); border-radius:12px; border:1px solid var(--owing-border);">Secure connection failed: ${err.message}</div>
        `;
    }
}

async function toggleRoomMaintenance(roomId, newStatus) {
    if(!roomId) { showToast("Room ID is missing."); return; }
    try {
        await apiFetch(`/rooms/${roomId}`, {
            method: 'PATCH',
            body: JSON.stringify({ status: newStatus })
        });
        showToast(`Room is now ${newStatus}`, 'success');
        document.getElementById('room-panel').classList.remove('open');
        fetchDashboard(localStorage.getItem('active_lodge_id'));
    } catch (err) {
        showToast(err.message);
    }
}

async function approveTermination(leaseId) {
    if(!leaseId) { showToast("Lease ID missing."); return; }
    if(!confirm("Are you sure you want to terminate this lease? This action is irreversible.")) return;
    
    try {
        await apiFetch(`/leases/terminate/${leaseId}`, {
            method: 'PATCH'
        });
        showToast(`Lease terminated successfully`, 'success');
        document.getElementById('room-panel').classList.remove('open');
        fetchDashboard(localStorage.getItem('active_lodge_id'));
    } catch (err) {
        showToast(err.message);
    }
}
