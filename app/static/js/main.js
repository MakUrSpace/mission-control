// Check if the URL fragment identifier is #home or #index
if (window.location.hash === '#home' || window.location.hash === '#index') {
    // Navigate to the root path
    window.location.href = '/';
}
