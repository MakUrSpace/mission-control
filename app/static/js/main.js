// Check if the URL fragment identifier is #home or #index
if (window.location.hash === '#home' || window.location.hash === '#index') {
    // Navigate to the root path
    window.location.href = '/';
}

// ##########################################
// #            Websocket Section           #
// ##########################################
const socket = io();
const service_socket = io('/service');

socket.on('connect_error', (error) => {
    console.error('Error connecting to websocket server:', error);
});

socket.on('connect', () => {
    console.info('Connected to websocket server');
});

socket.on('disconnect', () => {
    console.info('Disconnected from websocket server');
});

// ##########################################
// #            Services Section            #
// ##########################################
function launchService(url) {
    window.open(url, '_blank');
}

function startService(serviceId, btn) {
    toggleButtonsDisabled(serviceId, true);
    btn.classList.add('is-loading');
    
    service_socket.emit('start_service', serviceId);

    service_socket.on('service_started', function(data) {
        if (data.service_id === serviceId) {
            showToast(data.message);
            updateLaunchButtonState(serviceId, true);
            refreshSocketConnection(serviceId, true);
            toggleButtonsDisabled(serviceId, false);
            btn.classList.remove('is-loading');
            service_socket.off('service_started');
        }
    });

    service_socket.on('service_start_error', function(data) {
        if (data.service_id === serviceId) {
            showToast(data.message);
            console.error(data.error)
            toggleButtonsDisabled(serviceId, false);
            btn.classList.remove('is-loading');
            service_socket.off('service_start_error');
        }
    });
}

function stopService(serviceId, btn) {
    toggleButtonsDisabled(serviceId, true);
    btn.classList.add('is-loading');

    service_socket.emit('stop_service', serviceId);

    service_socket.on('service_stopped', function(data) {
        if (data.service_id === serviceId) {
            showToast(data.message);
            updateLaunchButtonState(serviceId, false);
            refreshSocketConnection(serviceId, false);
            toggleButtonsDisabled(serviceId, false);
            btn.classList.remove('is-loading');
            service_socket.off('service_stopped');
        }
    });

    service_socket.on('service_stop_error', function(data) {
        if (data.service_id === serviceId) {
            showToast(data.message);
            console.error(data.error)
            toggleButtonsDisabled(serviceId, false);
            btn.classList.remove('is-loading');
            service_socket.off('service_stop_error');
        }
    });
}

function restartService(serviceId, btn) {
    toggleButtonsDisabled(serviceId, true);
    btn.classList.add('is-loading');

    service_socket.emit('restart_service', serviceId);

    service_socket.on('service_restarted', function(data) {
        if (data.service_id === serviceId) {
            showToast(data.message);
            updateLaunchButtonState(serviceId, true);
            refreshSocketConnection(serviceId, true);
            toggleButtonsDisabled(serviceId, false);            
            btn.classList.remove('is-loading');
            service_socket.off('service_restarted');
        }
    });

    service_socket.on('service_restart_error', function(data) {
        if (data.service_id === serviceId) {
            showToast(data.message);
            console.error(data.error)
            toggleButtonsDisabled(serviceId, false);
            btn.classList.remove('is-loading');
            service_socket.off('service_restart_error');
        }
    });
}

function updateLaunchButtonState(serviceId, is_running) {
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

// Refresh socket connection helper
function refreshSocketConnection(serviceId, is_opening_modal) {
    serviceId = parseInt(serviceId);
    if(is_opening_modal) {
        // Open the socket connection

        // Request the logs
        service_socket.emit('get_logs', { serviceId: serviceId, command: 'start' });

        service_socket.on('get_logs_failed', function(data) {
            if (data.service_id === serviceId) {
                showToast(data.message);
                console.error(data.error);
                service_socket.off('get_logs_failed');
            }
        });

        // Listen for log messages
        service_socket.on('log_message', function(data) {
            var logElement = document.querySelector('#logs-' + data.service_id);
            if (logElement) {
                var logLine = document.createElement('div');
                logLine.className = 'log-line';
                logLine.textContent = data.log;
        
                logElement.appendChild(logLine);
            }
        });

        // Request the stats
        service_socket.emit('get_stats', { serviceId: serviceId, command: 'start' });

        service_socket.on('get_stats_failed', function(data) {
            if (data.service_id === serviceId) {
                showToast(data.message);
                console.error(data.error);
                service_socket.off('get_stats_failed');
            }
        });

        // Listen for stats
        service_socket.on('stats_message', function(data) {
            if (data.service_id === serviceId) {
                var cpuElement = document.querySelector('#cpu-usage-' + data.service_id);
                var memoryElement = document.querySelector('#mem-usage-' + data.service_id);
                var diskElement = document.querySelector('#disk-usage-' + data.service_id);

                if (cpuElement) {
                    cpuElement.value = data.stats.cpu_usage;
                }
                if (memoryElement) {
                    memoryElement.value = data.stats.memory_usage;
                }
                if (diskElement) {
                    diskElement.value = data.stats.disk_usage;
                }
            }
        });
    } else {
        // Close the socket connections
        service_socket.emit('get_logs', { serviceId: serviceId, command: 'stop' });
        service_socket.off('get_logs_failed');
        service_socket.off('log_message');

        service_socket.emit('get_stats', { serviceId: serviceId, command: 'stop' });
        service_socket.off('get_stats_failed');
        service_socket.off('stats_message');
    }
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

document.querySelectorAll('.modal-card').forEach(function(modalCard) {
    modalCard.addEventListener('click', function(event) {
        event.stopPropagation();  // Prevents the modal background click handler from being called
    });
});

function openModal(serviceId) {
    var modal = document.querySelector('#modal-' + serviceId);
    if (modal) {
        modal.classList.add('is-active');
    }
    refreshSocketConnection(serviceId, true);
}

function closeModal(serviceId) {
    var modal = document.querySelector('#modal-' + serviceId);
    if (modal) {
        modal.classList.remove('is-active');
    }
    refreshSocketConnection(serviceId, false);
}

function clearLogs(serviceId) {
    var logElement = document.querySelector('#logs-' + serviceId);
    if (logElement) {
        logElement.innerHTML = '';
    }
}

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

