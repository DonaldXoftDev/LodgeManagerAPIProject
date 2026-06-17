document.addEventListener('DOMContentLoaded', async () => {
    const lodgeId = localStorage.getItem('active_lodge_id');
    const lodgeName = localStorage.getItem('active_lodge_name');
    
    if (!lodgeId) {
        window.location.href = 'lodges.html';
        return;
    }
    
    document.getElementById('lodge-name-display').textContent = lodgeName;
    await loadRecentPayments();
    
    // Auto-open modal if lease_id is in query string AND open_modal is true
    const urlParams = new URLSearchParams(window.location.search);
    const leaseId = urlParams.get('lease_id');
    const openModal = urlParams.get('open_modal');
    if (leaseId && openModal === 'true') {
        openPaymentModal();
        setTimeout(() => {
            document.getElementById('payment-lease').value = leaseId;
        }, 50);
    }
});

let leasesLoaded = false;
let activeLeases = [];

async function loadRecentPayments() {
    const activeLodgeId = parseInt(localStorage.getItem('active_lodge_id'), 10);
    const tbody = document.getElementById('payments-tbody');
    
    try {
        // Fetch leases, rooms, and tenants in parallel to resolve IDs
        const [leases, rooms, tenants] = await Promise.all([
            apiFetch(`/leases/${activeLodgeId}`),
            apiFetch('/rooms/?skip=0&limit=100').catch(() => []),
            apiFetch(`/lodges/${activeLodgeId}/tenants`).catch(() => [])
        ]);
        
        // Build maps for quick lookup
        const roomMap = {};
        rooms.forEach(r => roomMap[r.id] = r.room_no);
        
        const tenantMap = {};
        tenants.forEach(t => {
            if (t.user) {
                tenantMap[t.id] = `${t.user.first_name} ${t.user.last_name}`;
            } else {
                tenantMap[t.id] = `Tenant ${t.id}`;
            }
        });
        
        // Enrich leases for the dropdown
        activeLeases = leases.map(l => ({
            ...l,
            _room_no: roomMap[l.room_id] || l.room_id,
            _tenant_name: tenantMap[l.tenant_id] || `Tenant ${l.tenant_id}`
        }));
        
        // Filter leases if URL specifies a lease_id
        const urlParams = new URLSearchParams(window.location.search);
        const urlLeaseId = urlParams.get('lease_id');
        const leasesToFetch = urlLeaseId ? activeLeases.filter(l => l.id == urlLeaseId) : activeLeases;
        
        let allPayments = [];
        
        // Fetch payments for the relevant leases
        for (const lease of leasesToFetch) {
            try {
                const payments = await apiFetch(`/payments/${lease.id}`);
                payments.forEach(p => {
                    p._lease_id = lease.id;
                    p._room_no = lease._room_no;
                    p._tenant_name = lease._tenant_name;
                });
                allPayments = allPayments.concat(payments);
            } catch(e) {}
        }
        
        // Sort by payment_date descending
        allPayments.sort((a, b) => new Date(b.payment_date) - new Date(a.payment_date));
        
        tbody.innerHTML = '';
        if (allPayments.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 24px; color: var(--muted)">No payments found.</td></tr>`;
            return;
        }

        allPayments.forEach(payment => {
            const tr = document.createElement('tr');
            const amtStr = new Intl.NumberFormat('en-NG', { style: 'currency', currency: 'NGN' }).format(payment.amount_paid);
            
            let statusBadge = `<span class="room-badge badge-safe">Completed</span>`;

            tr.innerHTML = `
                <td>${new Date(payment.payment_date).toLocaleString()}</td>
                <td style="font-weight: 600; color: var(--text)">${payment._tenant_name} (Room ${payment._room_no})</td>
                <td style="font-weight: 500">${amtStr}</td>
                <td>BANK_TRANSFER</td>
                <td>${statusBadge}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        showError(err.message);
    }
}

function openPaymentModal() {
    document.getElementById('payment-modal').classList.add('active');
    
    if (!leasesLoaded) {
        const select = document.getElementById('payment-lease');
        select.innerHTML = '<option value="">-- Select Active Lease --</option>';
        activeLeases.forEach(l => {
            const opt = document.createElement('option');
            opt.value = l.id;
            opt.textContent = `${l._tenant_name} (Room ${l._room_no}) - ₦${l.agreed_rent_amt}`;
            select.appendChild(opt);
        });
        leasesLoaded = true;
    }
}

function closePaymentModal() {
    document.getElementById('payment-modal').classList.remove('active');
}

document.getElementById('create-payment-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const payload = {
        lease_id: parseInt(document.getElementById('payment-lease').value, 10),
        amount_paid: parseFloat(document.getElementById('payment-amount').value)
    };

    try {
        await apiFetch('/payments/create-payment', {
            method: 'POST',
            body: JSON.stringify(payload)
        });
        
        closePaymentModal();
        showToast('Payment recorded successfully!');
        e.target.reset();
        loadRecentPayments();
    } catch (err) {
        alert('Failed to record payment: ' + err.message);
    }
});
