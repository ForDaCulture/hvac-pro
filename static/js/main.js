
console.log("Main interactive script loaded.");

// --- Job Status Update Logic ---
function updateJobStatus(jobId, newStatus) {
    console.log(`Request to update job #${jobId} to status: ${newStatus}`);
    
    // ** API HOOK (currently disabled) **
    // fetch(`/api/update-job-status`, {
    //     method: 'POST',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify({ job_id: jobId, status: newStatus })
    // })
    // .then(response => response.json())
    // .then(data => {
    //     if(data.success) {
    //         // Update the UI on success
    //         const jobRow = document.getElementById(`job-row-${jobId}`);
    //         // ... logic to update badge ...
    //         alert('Status updated!');
    //     } else {
    //         alert('Error updating status: ' + data.error);
    //     }
    // });

    alert(`UI-only: Job #${jobId} status would be set to '${newStatus}'.`);
}

// --- Invoice Modal Logic ---
const invoiceModal = document.getElementById('invoiceModal');
invoiceModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const jobId = button.getAttribute('data-job-id');
    const customerName = button.getAttribute('data-customer-name');
    
    const modalTitle = invoiceModal.querySelector('.modal-title');
    const jobIdInput = invoiceModal.querySelector('#invoiceJobId');

    modalTitle.textContent = `Generate Invoice for ${customerName} (Job #${jobId})`;
    jobIdInput.value = jobId;
});

function addPartRow() {
    const container = document.getElementById('parts-container');
    const partRow = document.createElement('div');
    partRow.className = 'row g-3 mb-2 align-items-center part-row';
    partRow.innerHTML = `
        <div class="col-md-5"><input type="text" class="form-control" placeholder="Part Name/Number"></div>
        <div class="col-md-2"><input type="number" class="form-control" placeholder="Qty" value="1"></div>
        <div class="col-md-3"><input type="number" class="form-control" placeholder="Unit Cost" step="0.01"></div>
        <div class="col-md-2"><button type="button" class="btn btn-sm btn-danger" onclick="this.closest('.part-row').remove()">X</button></div>
    `;
    container.appendChild(partRow);
}

function generateInvoice() {
    const jobId = document.getElementById('invoiceJobId').value;
    const laborHours = document.getElementById('laborHours').value;
    const parts = [];
    document.querySelectorAll('.part-row').forEach(row => {
        parts.push({
            name: row.children[0].firstChild.value,
            quantity: row.children[1].firstChild.value,
            unit_cost: row.children[2].firstChild.value
        });
    });

    const invoiceData = {
        job_id: jobId,
        labor_hours: laborHours,
        parts: parts
    };
    
    console.log('Invoice data to be sent:', invoiceData);
    
    // ** API HOOK (currently disabled) **
    // fetch('/api/generate-invoice', { ... })

    alert(`UI-only: Invoice for job #${jobId} would be generated.`);
    const modal = bootstrap.Modal.getInstance(invoiceModal);
    modal.hide();
}
