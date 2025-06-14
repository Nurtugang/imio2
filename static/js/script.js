// static/js/script.js

// Инициализация приложения
document.addEventListener('DOMContentLoaded', function() {
    initializeParticles();
    setupSmoothScrolling();
    setupScrollAnimations();
    setupMobileMenu();
    setupDropdowns();
    
    // Параллакс только на главной странице
    if (document.querySelector('.hero')) {
        setupParallax();
    }
});

// Создание анимированных частиц
function initializeParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;
    
    const particleCount = window.innerWidth < 768 ? 30 : 50; // Меньше частиц на мобильных
    
    // Очищаем контейнер
    particlesContainer.innerHTML = '';
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Случайные позиции
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        
        // Случайные задержки и длительности анимации
        particle.style.animationDelay = Math.random() * 6 + 's';
        particle.style.animationDuration = (Math.random() * 3 + 3) + 's';
        
        // Случайный размер
        const size = Math.random() * 3 + 2;
        particle.style.width = size + 'px';
        particle.style.height = size + 'px';
        
        particlesContainer.appendChild(particle);
    }
}

// Плавная прокрутка для якорных ссылок
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const navHeight = document.querySelector('.main-nav').offsetHeight;
                const targetPosition = target.offsetTop - navHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Эффект параллакса для hero секции
function setupParallax() {
    let ticking = false;
    
    function updateParallax() {
        const scrolled = window.pageYOffset;
        const hero = document.querySelector('.hero');
        
        if (hero) {
            // Медленное движение hero секции
            hero.style.transform = `translateY(${scrolled * 0.3}px)`;
            
            // Эффект для заголовка
            const heroTitle = hero.querySelector('h1');
            if (heroTitle) {
                heroTitle.style.transform = `translateY(${scrolled * 0.1}px)`;
                heroTitle.style.opacity = Math.max(0, 1 - scrolled / 500);
            }
        }
        
        ticking = false;
    }
    
    window.addEventListener('scroll', () => {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    });
}

// Анимация появления элементов при скролле
function setupScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                
                // Добавляем задержку для множественных элементов
                const delay = Array.from(entry.target.parentNode.children).indexOf(entry.target) * 100;
                entry.target.style.transitionDelay = delay + 'ms';
            }
        });
    }, observerOptions);
    
    // Наблюдаем за карточками
    document.querySelectorAll('.stat-card, .process-card').forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
}

// Мобильное меню
function setupMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navLinks = document.querySelector('.nav-links');
    
    if (!mobileMenuBtn || !navLinks) return;
    
    mobileMenuBtn.addEventListener('click', () => {
        toggleMobileMenu();
    });
}

function toggleMobileMenu() {
    const navLinks = document.querySelector('.nav-links');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    
    if (navLinks && mobileMenuBtn) {
        navLinks.classList.toggle('mobile-active');
        mobileMenuBtn.classList.toggle('active');
        
        // Добавляем стили для мобильного меню
        if (!document.querySelector('#mobile-menu-styles')) {
            const style = document.createElement('style');
            style.id = 'mobile-menu-styles';
            style.textContent = `
                @media (max-width: 768px) {
                    .nav-links.mobile-active {
                        display: flex;
                        flex-direction: column;
                        position: absolute;
                        top: 100%;
                        left: 0;
                        right: 0;
                        background: rgba(15, 23, 42, 0.95);
                        backdrop-filter: blur(20px);
                        border: 1px solid var(--glass-border);
                        border-radius: 0 0 16px 16px;
                        padding: 1rem 2rem;
                        gap: 1rem;
                        animation: fadeInDown 0.3s ease;
                    }
                    
                    .mobile-menu-btn.active span:nth-child(1) {
                        transform: rotate(-45deg) translate(-6px, 6px);
                    }
                    
                    .mobile-menu-btn.active span:nth-child(2) {
                        opacity: 0;
                    }
                    
                    .mobile-menu-btn.active span:nth-child(3) {
                        transform: rotate(45deg) translate(-6px, -6px);
                    }
                }
                
                @keyframes fadeInDown {
                    from { opacity: 0; transform: translateY(-10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Настройка dropdown меню
function setupDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown');
    
    dropdowns.forEach(dropdown => {
        const toggle = dropdown.querySelector('.dropdown-toggle');
        const content = dropdown.querySelector('.dropdown-content');
        
        if (toggle && content) {
            // Показ/скрытие на hover (для десктопа)
            dropdown.addEventListener('mouseenter', () => {
                content.style.display = 'block';
                content.style.animation = 'fadeInUp 0.3s ease';
            });
            
            dropdown.addEventListener('mouseleave', () => {
                content.style.display = 'none';
            });
            
            // Клик для мобильных устройств
            toggle.addEventListener('click', (e) => {
                e.preventDefault();
                const isVisible = content.style.display === 'block';
                
                // Закрываем все другие dropdown
                document.querySelectorAll('.dropdown-content').forEach(other => {
                    if (other !== content) {
                        other.style.display = 'none';
                    }
                });
                
                content.style.display = isVisible ? 'none' : 'block';
                if (!isVisible) {
                    content.style.animation = 'fadeInUp 0.3s ease';
                }
            });
        }
    });
    
    // Закрытие dropdown при клике вне
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-content').forEach(content => {
                content.style.display = 'none';
            });
        }
    });
}

// Утилиты для уведомлений (будет использоваться в других модулях)
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    // Добавляем стили для уведомлений если их нет
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 100px;
                right: 20px;
                background: var(--glass-bg);
                backdrop-filter: blur(20px);
                border: 1px solid var(--glass-border);
                border-radius: 12px;
                padding: 1rem;
                z-index: 10000;
                animation: slideInRight 0.3s ease;
                min-width: 300px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
            }
            
            .notification-info { border-left: 4px solid var(--primary-blue); }
            .notification-success { border-left: 4px solid #10b981; }
            .notification-warning { border-left: 4px solid var(--accent-gold); }
            .notification-error { border-left: 4px solid #ef4444; }
            
            .notification-content {
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 1rem;
            }
            
            .notification-message {
                color: var(--text-light);
                flex: 1;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: var(--text-light);
                font-size: 1.2rem;
                cursor: pointer;
                opacity: 0.7;
                transition: opacity 0.3s ease;
            }
            
            .notification-close:hover {
                opacity: 1;
            }
            
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            
            @keyframes slideOutRight {
                from { transform: translateX(0); opacity: 1; }
                to { transform: translateX(100%); opacity: 0; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Автоматическое удаление
    if (duration > 0) {
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, duration);
    }
}

// Утилита для загрузки состояний
function setLoadingState(element, loading = true) {
    if (loading) {
        element.style.opacity = '0.6';
        element.style.pointerEvents = 'none';
        
        // Добавляем spinner если его нет
        if (!element.querySelector('.loading-spinner')) {
            const spinner = document.createElement('div');
            spinner.className = 'loading-spinner';
            spinner.innerHTML = '⟳';
            spinner.style.cssText = `
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                font-size: 1.5rem;
                animation: spin 1s linear infinite;
                color: var(--accent-gold);
            `;
            element.style.position = 'relative';
            element.appendChild(spinner);
            
            // Добавляем анимацию вращения
            if (!document.querySelector('#spinner-styles')) {
                const style = document.createElement('style');
                style.id = 'spinner-styles';
                style.textContent = `
                    @keyframes spin {
                        from { transform: translate(-50%, -50%) rotate(0deg); }
                        to { transform: translate(-50%, -50%) rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);
            }
        }
    } else {
        element.style.opacity = '1';
        element.style.pointerEvents = 'auto';
        
        const spinner = element.querySelector('.loading-spinner');
        if (spinner) {
            spinner.remove();
        }
    }
}

// Утилита для AJAX запросов с обработкой CSRF
function makeRequest(url, options = {}) {
    const defaults = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        }
    };
    
    const config = Object.assign({}, defaults, options);
    config.headers = Object.assign({}, defaults.headers, options.headers || {});
    
    return fetch(url, config);
}

// Получение CSRF токена
function getCSRFToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// Утилита для форматирования чисел
function formatNumber(num, decimals = 1) {
    return parseFloat(num).toFixed(decimals);
}

// Утилита для дебаунса (полезно для поиска)
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Экспорт функций для использования в других модулях
window.MetallurgyLab = {
    showNotification,
    setLoadingState,
    makeRequest,
    formatNumber,
    debounce,
    getCSRFToken
};