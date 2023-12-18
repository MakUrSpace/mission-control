// Check if the URL fragment identifier is #home or #index
if (window.location.hash === '#home' || window.location.hash === '#index') {
    // Navigate to the root path
    window.location.href = '/';
}

// ##########################################
// #            Services Section            #
// ##########################################
function startService(serviceId) {
    fetch(`/service/${serviceId}/start`, { method: 'POST' })
        .then(response => response.json())
        .then(data => 
            showToast(data.message)
        )
        .catch(error => console.error('Error:', error));
}

function stopService(serviceId) {
    fetch(`/service/${serviceId}/stop`, { method: 'POST' })
        .then(response => response.json())
        .then(data => 
            showToast(data.message)
        )
        .catch(error => console.error('Error:', error));
}

function restartService(serviceId) {
    fetch(`/service/${serviceId}/restart`, { method: 'POST' })
        .then(response => response.json())
        .then(data => 
            showToast(data.message)
        )
        .catch(error => console.error('Error:', error));
}

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
