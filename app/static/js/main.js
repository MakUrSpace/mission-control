// Handle the dynamic name in the header
const header = document.getElementById('main-header');
const dynamicName = document.getElementById('dynamic-name');
const originalName = document.querySelector('.hero-section h1');

// Check if the URL fragment identifier is #home or #index
if (window.location.hash === '#home' || window.location.hash === '#index') {
    // Navigate to the root path
    window.location.href = '/';
}

const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', function (event) {
        event.preventDefault();  // Prevent the form from submitting through the browser

        let form = this;
        let data = new FormData(form);

        fetch(form.action, {
            method: 'POST',
            body: data,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    throw new Error('Server returned ' + response.status + ' : ' + response.statusText);
                }
            })
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                } else {
                    alert('Login failed: ' + data.message);
                    form.password.focus();
                }
            })
            .catch(error => {
                // Handle network errors or other exceptions
                console.error('Error:', error);
            });
    });
}