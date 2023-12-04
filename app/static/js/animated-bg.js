// Initialize canvas and context
const canvas = document.getElementById("animated-bg");
const ctx = canvas.getContext("2d");

// Initialize spirals
const spirals = [];

// Spiral settings
const maxSpirals = 30;

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

function fibonacci(n) {
    let a = 0, b = 1;
    for (let i = 0; i < n; i++) {
        [a, b] = [b, a + b];
    }
    return a;
}

function createSpiral(initial = false) {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height;
    const lifetime = initial ? Math.floor(Math.random() * 200) : 0;
    const maxLifetime = 200 + Math.floor(Math.random() * 200);
    const startAngle = Math.random() * 2 * Math.PI;
    spirals.push({ x, y, lifetime, maxLifetime, startAngle });
}

function drawSpiral(spiral) {
    ctx.save();
    ctx.translate(spiral.x, spiral.y);

    ctx.beginPath();
    for (let i = 0; i <= spiral.lifetime; i++) {
        const angle = i * 0.1 + spiral.startAngle;
        const radius = fibonacci(Math.floor(i / 10)) * 0.5;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        ctx.lineTo(x, y);
    }

    ctx.strokeStyle = `rgba(230, 57, 70, ${1 - spiral.lifetime / spiral.maxLifetime})`;
    ctx.stroke();
    ctx.restore();
}

function animate() {
    setTimeout(() => {
        requestAnimationFrame(animate);
    }, 20);

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw each spiral
    for (const spiral of spirals) {
        drawSpiral(spiral);
    }

    // Update or remove spirals
    for (let i = spirals.length - 1; i >= 0; i--) {
        spirals[i].lifetime++;
        if (spirals[i].lifetime > spirals[i].maxLifetime) {
            spirals.splice(i, 1);
        }
    }

    // Create a new spiral if below maxSpirals
    if (spirals.length < maxSpirals) {
        createSpiral();
    }
}

// Handle window resize
window.addEventListener("resize", resizeCanvas);

// Initialize
resizeCanvas();

// Pre-populate spirals
for (let i = 0; i < maxSpirals; i++) {
    createSpiral(true);
}

animate();
