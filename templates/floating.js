(function() {
    var container = document.querySelector('.hearts');
    var symbols = {{ symbols_json }};
    var count = {{ count }};
    var spawned = 0;

    function spawnHeart() {
        if (spawned >= count) return;
        var el = document.createElement('div');
        el.className = 'heart';
        el.textContent = symbols[spawned % symbols.length];
        el.style.left = Math.random() * 100 + '%';
        var dur = {{ min_duration }} + Math.random() * {{ duration_range }};
        el.style.animationDuration = dur + 's';
        el.style.fontSize = ({{ min_size }} + Math.random() * {{ size_range }}) + 'rem';
        el.style.animationIterationCount = 'infinite';
        container.appendChild(el);
        spawned++;
    }

    setInterval(spawnHeart, {{ spawn_interval_ms }});
})();
