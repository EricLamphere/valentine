(function() {
    var noBtn = document.getElementById('no-btn');
    var yesBtn = document.querySelector('.btn-yes');
    var PROXIMITY = 100;
    var BOUND = 250;

    // Position the No button just below the YES button (centered)
    var yesRect = yesBtn.getBoundingClientRect();
    var noBtnWidth = noBtn.offsetWidth;
    var noBtnHeight = noBtn.offsetHeight;
    var originX = yesRect.left + yesRect.width / 2 - noBtnWidth / 2;
    var originY = yesRect.bottom + 20;
    noBtn.style.left = originX + 'px';
    noBtn.style.top = originY + 'px';

    var cursorX = -9999;
    var cursorY = -9999;

    // Create the bubble inside the no button with cycling messages
    var bubbleMessages = [
        'Missed me!',
        'Phew close call...',
        "You can't catch me hehe",
        "I'm too fast",
        'Scram!',
        'Ouch! You got me!... (sike)',
        'Okay for real just clicm yes...'
    ];
    var bubbleIndex = 0;
    var bubble = document.createElement('div');
    bubble.className = 'missed-bubble';
    noBtn.appendChild(bubble);
    var bubbleTimer = null;

    function showBubble() {
        if (bubbleTimer) clearTimeout(bubbleTimer);
        bubble.textContent = bubbleMessages[bubbleIndex];
        bubbleIndex = (bubbleIndex + 1) % bubbleMessages.length;
        bubble.classList.add('show');
        bubbleTimer = setTimeout(function() {
            bubble.classList.remove('show');
        }, 2000);
    }

    function dodge() {
        var rect = noBtn.getBoundingClientRect();
        var btnCX = rect.left + rect.width / 2;
        var btnCY = rect.top + rect.height / 2;

        // Flee directly away from cursor
        var dx = btnCX - cursorX;
        var dy = btnCY - cursorY;
        var dist = Math.sqrt(dx * dx + dy * dy) || 1;
        var angle = Math.atan2(dy, dx);

        // Add slight randomness to the angle so it's not perfectly predictable
        angle += (Math.random() - 0.5) * 0.8;

        // Always jump farther than PROXIMITY so cursor is out of range
        var jumpDist = PROXIMITY + 50 + Math.random() * 50;
        var newX = btnCX + Math.cos(angle) * jumpDist - rect.width / 2;
        var newY = btnCY + Math.sin(angle) * jumpDist - rect.height / 2;

        // Clamp within BOUND px of origin
        newX = Math.max(originX - BOUND, Math.min(originX + BOUND, newX));
        newY = Math.max(originY - BOUND, Math.min(originY + BOUND, newY));

        // Keep on screen
        newX = Math.max(5, Math.min(window.innerWidth - rect.width - 5, newX));
        newY = Math.max(5, Math.min(window.innerHeight - rect.height - 5, newY));

        // Avoid overlapping the YES button
        var yR = yesBtn.getBoundingClientRect();
        var wouldOverlap = (
            newX < yR.right + 10 &&
            newX + rect.width > yR.left - 10 &&
            newY < yR.bottom + 10 &&
            newY + rect.height > yR.top - 10
        );
        if (wouldOverlap) {
            newY = yR.bottom + 20;
        }

        noBtn.style.left = newX + 'px';
        noBtn.style.top = newY + 'px';
    }

    // Dodge on mouse proximity
    document.addEventListener('mousemove', function(e) {
        cursorX = e.clientX;
        cursorY = e.clientY;
        var rect = noBtn.getBoundingClientRect();
        var dx = cursorX - (rect.left + rect.width / 2);
        var dy = cursorY - (rect.top + rect.height / 2);
        if (Math.sqrt(dx * dx + dy * dy) < PROXIMITY) {
            dodge();
        }
    });

    // Dodge on touch proximity
    document.addEventListener('touchmove', function(e) {
        var touch = e.touches[0];
        cursorX = touch.clientX;
        cursorY = touch.clientY;
        var rect = noBtn.getBoundingClientRect();
        var dx = cursorX - (rect.left + rect.width / 2);
        var dy = cursorY - (rect.top + rect.height / 2);
        if (Math.sqrt(dx * dx + dy * dy) < PROXIMITY) {
            dodge();
        }
    });

    // Snap to opposite side of origin on click / tap
    function snapOpposite() {
        var rect = noBtn.getBoundingClientRect();
        var curX = rect.left;
        var curY = rect.top;

        // Vector from origin to current position
        var dx = curX - originX;
        var dy = curY - originY;

        // Halfway between the opposite point and origin
        var newX = originX - dx / 2;
        var newY = originY - dy / 2;

        // Clamp within BOUND with 20px padding
        var PAD = 20;
        newX = Math.max(originX - BOUND + PAD, Math.min(originX + BOUND - PAD, newX));
        newY = Math.max(originY - BOUND + PAD, Math.min(originY + BOUND - PAD, newY));

        // Keep on screen
        newX = Math.max(5, Math.min(window.innerWidth - rect.width - 5, newX));
        newY = Math.max(5, Math.min(window.innerHeight - rect.height - 5, newY));

        // Avoid overlapping the YES button
        var yR = yesBtn.getBoundingClientRect();
        var wouldOverlap = (
            newX < yR.right + 10 &&
            newX + rect.width > yR.left - 10 &&
            newY < yR.bottom + 10 &&
            newY + rect.height > yR.top - 10
        );
        if (wouldOverlap) {
            newY = yR.bottom + 20;
        }

        noBtn.style.left = newX + 'px';
        noBtn.style.top = newY + 'px';
    }

    noBtn.addEventListener('click', function(e) {
        e.preventDefault();
        snapOpposite();
        showBubble();
    });
    noBtn.addEventListener('touchstart', function(e) {
        e.preventDefault();
        snapOpposite();
        showBubble();
    });
})();
