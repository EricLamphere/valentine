(function () {
    var canvas = document.getElementById('fireworks');
    var ctx = canvas.getContext('2d');
    var particles = [];
    var rockets = [];
    var colors = [
        '#ff4081', '#e91e63', '#c2185b', '#f48fb1',
        '#ff80ab', '#ffd700', '#ffecb3', '#ffffff'
    ];

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    function random(min, max) {
        return Math.random() * (max - min) + min;
    }

    function launchRocket() {
        rockets.push({
            x: random(canvas.width * 0.2, canvas.width * 0.8),
            y: canvas.height,
            vx: random(-1, 1),
            vy: random(-12, -8),
            life: 0
        });
    }

    function explode(x, y) {
        var count = Math.floor(random(60, 100));
        for (var i = 0; i < count; i++) {
            var angle = Math.random() * Math.PI * 2;
            var speed = random(1, 6);
            var color = colors[Math.floor(Math.random() * colors.length)];
            particles.push({
                x: x,
                y: y,
                vx: Math.cos(angle) * speed,
                vy: Math.sin(angle) * speed,
                alpha: 1,
                color: color,
                decay: random(0.01, 0.025),
                size: random(1.5, 3.5)
            });
        }
    }

    function update() {
        // Update rockets
        for (var i = rockets.length - 1; i >= 0; i--) {
            var r = rockets[i];
            r.x += r.vx;
            r.y += r.vy;
            r.vy += 0.05; // gravity
            r.life++;
            if (r.vy >= -2 || r.life > 80) {
                explode(r.x, r.y);
                rockets.splice(i, 1);
            }
        }

        // Update particles
        for (var j = particles.length - 1; j >= 0; j--) {
            var p = particles[j];
            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.04; // gravity
            p.vx *= 0.99; // drag
            p.alpha -= p.decay;
            if (p.alpha <= 0) {
                particles.splice(j, 1);
            }
        }
    }

    function draw() {
        ctx.globalCompositeOperation = 'destination-out';
        ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.globalCompositeOperation = 'lighter';

        // Draw rockets
        for (var i = 0; i < rockets.length; i++) {
            var r = rockets[i];
            ctx.beginPath();
            ctx.arc(r.x, r.y, 2, 0, Math.PI * 2);
            ctx.fillStyle = '#ffd700';
            ctx.fill();
        }

        // Draw particles
        for (var j = 0; j < particles.length; j++) {
            var p = particles[j];
            ctx.globalAlpha = p.alpha;
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.fill();
        }

        ctx.globalAlpha = 1;
    }

    function loop() {
        update();
        draw();
        requestAnimationFrame(loop);
    }

    // Launch rockets at intervals
    launchRocket();
    setInterval(function () {
        var count = Math.floor(random(1, 4));
        for (var i = 0; i < count; i++) {
            setTimeout(launchRocket, i * 200);
        }
    }, 800);

    loop();

    // Show continue button after configured delay
    setTimeout(function () {
        document.getElementById('continue-btn').classList.add('show');
    }, {{ delay_ms }});
})();
