(function () {
    'use strict';

    function initHeroSlider(sliderRoot) {
        const track = sliderRoot.querySelector('.slides');
        const slides = Array.from(sliderRoot.querySelectorAll('[data-hero-slide]'));
        const dots = Array.from(sliderRoot.querySelectorAll('.dot'));
        const dotsContainer = sliderRoot.querySelector('.dots');
        const prevBtn = sliderRoot.querySelector('.hero-arrow.prev');
        const nextBtn = sliderRoot.querySelector('.hero-arrow.next');

        if (!track || slides.length === 0) return;

        const slidesCount = slides.length;
        let currentIndex = 0;
        let autoplayId = null;
        let touchX = null;
        let touchY = null;

        function updateSlide() {
            track.style.transform = `translateX(-${currentIndex * 100}%)`;

            slides.forEach((slide, index) => {
                const isActive = index === currentIndex;
                slide.setAttribute('aria-hidden', String(!isActive));
                slide.toggleAttribute('inert', !isActive);
            });

            dots.forEach((dot, index) => {
                const isActive = index === currentIndex;
                dot.classList.toggle('active', isActive);
                dot.setAttribute('aria-current', isActive ? 'true' : 'false');
            });
        }

        function goTo(index) {
            currentIndex = (index + slidesCount) % slidesCount;
            updateSlide();
        }

        function stopAutoplay() {
            if (autoplayId !== null) {
                window.clearInterval(autoplayId);
                autoplayId = null;
            }
        }

        function startAutoplay() {
            stopAutoplay();
            if (
                slidesCount < 2 ||
                document.hidden ||
                window.matchMedia('(prefers-reduced-motion: reduce)').matches
            ) {
                return;
            }
            autoplayId = window.setInterval(() => goTo(currentIndex + 1), 10000);
        }

        function goManually(delta) {
            goTo(currentIndex + delta);
            startAutoplay();
        }

        const hasMultipleSlides = slidesCount > 1;
        if (prevBtn) prevBtn.classList.toggle('is-hidden', !hasMultipleSlides);
        if (nextBtn) nextBtn.classList.toggle('is-hidden', !hasMultipleSlides);
        if (dotsContainer) dotsContainer.hidden = !hasMultipleSlides;

        if (prevBtn) prevBtn.addEventListener('click', () => goManually(-1));
        if (nextBtn) nextBtn.addEventListener('click', () => goManually(1));

        dots.forEach((dot) => {
            dot.addEventListener('click', () => {
                goTo(Number.parseInt(dot.dataset.index, 10));
                startAutoplay();
            });
        });

        sliderRoot.addEventListener('touchstart', (event) => {
            const touch = event.changedTouches[0];
            touchX = touch.clientX;
            touchY = touch.clientY;
        }, {passive: true});

        sliderRoot.addEventListener('touchend', (event) => {
            if (touchX === null || touchY === null) return;

            const touch = event.changedTouches[0];
            const deltaX = touch.clientX - touchX;
            const deltaY = Math.abs(touch.clientY - touchY);
            if (Math.abs(deltaX) > 40 && deltaY < 40) {
                goManually(deltaX < 0 ? 1 : -1);
            }
            touchX = null;
            touchY = null;
        }, {passive: true});

        document.addEventListener('visibilitychange', startAutoplay);
        updateSlide();
        startAutoplay();
    }

    document.addEventListener('DOMContentLoaded', function () {
        document.querySelectorAll('[data-hero-slider]').forEach(initHeroSlider);
    });
})();
