// Check if the URL fragment identifier is #home or #index
if (window.location.hash === '#home' || window.location.hash === '#index') {
    // Navigate to the root path
    window.location.href = '/';
}

// ##########################################
// #            Services Section            #
// ##########################################
function launchService(url) {
    window.open(url, '_blank');
}

function startService(serviceId, btn) {
    toggleButtonsDisabled(serviceId, true);
    btn.querySelector('.spinner').classList.remove('hidden');
    fetch(`/service/${serviceId}/start`, { method: 'POST' })
        .then(response => response.json())
        .then(data => 
            showToast(data.message)
        )
        .catch(error => console.error('Error:', error))
        .finally(() => {
            btn.querySelector('.spinner').classList.add('hidden');
            toggleButtonsDisabled(serviceId, false);
            checkServiceStatusAndUpdateButton(serviceId);
        });
}

function stopService(serviceId, btn) {
    toggleButtonsDisabled(serviceId, true);
    btn.querySelector('.spinner').classList.remove('hidden');
    fetch(`/service/${serviceId}/stop`, { method: 'POST' })
        .then(response => response.json())
        .then(data => 
            showToast(data.message)
        )
        .catch(error => console.error('Error:', error))
        .finally(() => {
            btn.querySelector('.spinner').classList.add('hidden');
            toggleButtonsDisabled(serviceId, false);
            checkServiceStatusAndUpdateButton(serviceId);
        });
}

function restartService(serviceId, btn) {
    toggleButtonsDisabled(serviceId, true);
    btn.querySelector('.spinner').classList.remove('hidden');
    fetch(`/service/${serviceId}/restart`, { method: 'POST' })
        .then(response => response.json())
        .then(data => 
            showToast(data.message)
        )
        .catch(error => console.error('Error:', error))
        .finally(() => {
            btn.querySelector('.spinner').classList.add('hidden');
            toggleButtonsDisabled(serviceId, false);
            checkServiceStatusAndUpdateButton(serviceId);
        });
}

function updateButtonState(serviceId, is_running) {
    const launchButton = document.getElementById('launchButton-' + serviceId);
    if (is_running) {
        launchButton.classList.remove('is-disabled');
        launchButton.classList.add('has-text-white');
        launchButton.href = launchButton.dataset.url;
        launchButton.onclick = null;
    } else {
        launchButton.classList.add('is-disabled');
        launchButton.classList.remove('has-text-white');
        launchButton.href = 'javascript:void(0);'; // Prevent navigation
        launchButton.onclick = function(event) {
            event.preventDefault(); // Further ensure no action on click
        };
    }
}

function checkServiceStatusAndUpdateButton(serviceId) {
    fetch(`/service/${serviceId}/is_running`, { method: 'GET' })
    .then(response => response.json())
    .then(data => {
        updateButtonState(serviceId, data.is_running);
    })
    .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.card').forEach(function(card) {
        var serviceId = card.dataset.serviceId;
        checkServiceStatusAndUpdateButton(serviceId);
    });
});

function updateEnvironmentVars(serviceId) {
    const formData = new FormData(document.getElementById('form-' + serviceId));
    fetch(`/update-environment-vars/${serviceId}`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        showToast(data.message);
    })
    .catch(error => console.error('Error:', error));
    return false; // Prevent default form submission
}

// ##########################################
// #             Modal Section              #
// ##########################################
function toggleButtonsDisabled(serviceId, disabled) {
    const modal = document.querySelector('#modal-' + serviceId);
    const buttons = modal.querySelectorAll('button');
    buttons.forEach(button => {
        button.disabled = disabled;
    });
}

function toggleModal(serviceId) {
    var modal = document.querySelector('#modal-' + serviceId);
    if (modal) {
        modal.classList.toggle('is-active');
    }
}

document.querySelectorAll('.modal-card').forEach(function(modalCard) {
    modalCard.addEventListener('click', function(event) {
        event.stopPropagation();  // Prevents the modal background click handler from being called
    });
});

// ##########################################
// #             Toast Section              #
// ##########################################
function showToast(message) {
    const toast = document.getElementById('toast-notification');
    const messageElement = document.getElementById('toast-message');

    messageElement.textContent = message;
    toast.classList.remove('is-hidden');

    setTimeout(() => {
        toast.classList.add('is-active');
    }, 10);

    // Hide the toast after a delay
    setTimeout(() => {
        toast.classList.remove('is-active');
        setTimeout(() => {
            toast.classList.add('is-hidden');
        }, 500); 
    }, 3000);
}

document.querySelector('#toast-notification .delete').addEventListener('click', () => {
    const toast = document.getElementById('toast-notification');
    toast.classList.remove('is-active');
    toast.classList.add('is-hidden');
});
