// Check if the URL fragment identifier is #home or #index
if (window.location.hash === '#home' || window.location.hash === '#index') {
    // Navigate to the root path
    window.location.href = '/';
}

// ##########################################
// #            Services Section            #
// ##########################################
function startService(serviceName) {
    fetch(`/api/start/${serviceName}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
}

function stopService(serviceName) {
    fetch(`/api/stop/${serviceName}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
}

function restartService(serviceName) {
    fetch(`/api/restart/${serviceName}`, { method: 'POST' })
        .then(response => response.json())
        .then(data => console.log(data))
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
        // Show toast notification
        showToast(data.message);
        // Close modal if needed
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
