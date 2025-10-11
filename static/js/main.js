function typeWriterEffect(elementId, words, typingSpeed = 100, erasingSpeed = 50, delayBetweenWords = 2000) {
    let wordIndex = 0;
    let charIndex = 0;
    const element = document.getElementById(elementId);
    if (!element) return;

    function type() {
        if (charIndex === 0) {
            element.textContent = "";
        }
        if (charIndex < words[wordIndex].length) {
            element.textContent += words[wordIndex].charAt(charIndex);
            charIndex++;
            setTimeout(type, typingSpeed);
        } else {
            setTimeout(erase, delayBetweenWords);
        }
    }
    function erase() {
        if (charIndex > 0) {
            element.textContent = words[wordIndex].substring(0, charIndex - 1);
            charIndex--;
            setTimeout(erase, erasingSpeed);
        } else {
            wordIndex = (wordIndex + 1) % words.length;
            setTimeout(type, typingSpeed);
        }
    }
    type();
}



function createStarryBackground() {
    const canvas = document.getElementById('star-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let stars = [];
    const numStars = 250;

    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        createStars();
    }

    function createStars() {
        stars = [];
        for (let i = 0; i < numStars; i++) {
            stars.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                radius: Math.random() * 1.5 + 0.5,
                alpha: Math.random(),
                alphaChange: (Math.random() - 0.5) * 0.02
            });
        }
    }

    function drawStars() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        stars.forEach(star => {
            ctx.save();
            ctx.globalAlpha = star.alpha;
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
            ctx.fillStyle = "white";
            ctx.fill();
            ctx.restore();

            // Twinkle effect
            star.alpha += star.alphaChange;
            if (star.alpha <= 0.3 || star.alpha >= 1) star.alphaChange *= -1;
        });
        requestAnimationFrame(drawStars);
    }

    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();
    drawStars();
}

createStarryBackground();

document.addEventListener("DOMContentLoaded", function() {
    const burger = document.getElementById("navbar-burger");
    const menu = document.getElementById("navbar-menu");
    if (burger && menu) {
        burger.addEventListener("click", function() {
            menu.classList.toggle("opacity-0");
            menu.classList.toggle("scale-y-90");
            menu.classList.toggle("pointer-events-none");
            menu.classList.toggle("opacity-100");
            menu.classList.toggle("scale-y-100");
            menu.classList.toggle("pointer-events-auto");
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    typeWriterEffect(
        "typewriter",
        [
            "Python Developer",
            "Node Developer",
            "Javascript Developer",
            "SQL Developer"
        ],
        100, // typing speed
        50,  // erasing speed
        2000 // delay between words
    );
});