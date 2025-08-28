// Modern Dashboard JavaScript with Chart.js Integration
// Enhanced with animations, dark mode, and interactive features

class DashboardManager {
    constructor() {
        this.isDarkMode = this.getStoredTheme() === 'dark';
        this.charts = new Map();
        this.notifications = [];
        
        this.init();
    }
    
    init() {
        this.setupThemeToggle();
        this.setupMobileMenu();
        this.setupNotifications();
        this.setupChartDefaults();
        this.applyStoredTheme();
        
        // Initialize animations on page load
        this.initializeAnimations();
    }
    
    // Theme Management
    setupThemeToggle() {
        const themeToggle = document.getElementById('theme-toggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                this.toggleTheme();
            });
        }
    }
    
    toggleTheme() {
        this.isDarkMode = !this.isDarkMode;
        const theme = this.isDarkMode ? 'dark' : 'light';
        
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        
        // Update all existing charts with new theme
        this.updateChartsTheme();
        
        // Add smooth transition
        document.body.style.transition = 'all 0.3s ease';
        setTimeout(() => {
            document.body.style.transition = '';
        }, 300);
    }
    
    getStoredTheme() {
        const stored = localStorage.getItem('theme');
        if (stored) return stored;
        
        // Auto-detect system preference
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    
    applyStoredTheme() {
        const theme = this.getStoredTheme();
        document.documentElement.setAttribute('data-theme', theme);
        this.isDarkMode = theme === 'dark';
    }
    
    // Mobile Menu
    setupMobileMenu() {
        const menuButton = document.getElementById('mobile-menu-button');
        const mobileMenu = document.getElementById('mobile-menu');
        
        if (menuButton && mobileMenu) {
            menuButton.addEventListener('click', () => {
                mobileMenu.classList.toggle('hidden');
                
                // Animate menu items
                const menuItems = mobileMenu.querySelectorAll('.mobile-nav-link');
                menuItems.forEach((item, index) => {
                    setTimeout(() => {
                        item.style.animation = 'fadeInLeft 0.3s ease forwards';
                    }, index * 50);
                });
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!menuButton.contains(e.target) && !mobileMenu.contains(e.target)) {
                    mobileMenu.classList.add('hidden');
                }
            });
        }
    }
    
    // Notification System
    setupNotifications() {
        this.notificationContainer = document.getElementById('notification-container');
    }
    
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="flex items-center justify-between">
                <span>${message}</span>
                <button class="ml-4 text-white hover:text-gray-200" onclick="this.parentElement.parentElement.remove()">
                    <i data-lucide="x" class="w-4 h-4"></i>
                </button>
            </div>
        `;
        
        this.notificationContainer.appendChild(notification);
        
        // Initialize Lucide icons for the new notification
        lucide.createIcons();
        
        // Show notification with animation
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Auto-remove after duration
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 300);
        }, duration);
    }
    
    // Chart Configuration
    setupChartDefaults() {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded');
            return;
        }
        
        Chart.defaults.font.family = "'Inter', sans-serif";
        Chart.defaults.font.size = 12;
        Chart.defaults.color = this.isDarkMode ? '#e2e8f0' : '#475569';
        
        // Animation defaults
        Chart.defaults.animation.duration = 1000;
        Chart.defaults.animation.easing = 'easeInOutQuart';
    }
    
    updateChartsTheme() {
        if (typeof Chart === 'undefined') return;
        
        Chart.defaults.color = this.isDarkMode ? '#e2e8f0' : '#475569';
        
        // Update existing charts
        this.charts.forEach(chart => {
            if (chart.options.scales) {
                chart.options.scales = this.getScaleOptions();
            }
            chart.update();
        });
    }
    
    getScaleOptions() {
        return {
            x: {
                grid: {
                    color: this.isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.2)',
                    borderColor: this.isDarkMode ? '#334155' : '#e2e8f0'
                },
                ticks: {
                    color: this.isDarkMode ? '#94a3b8' : '#64748b'
                }
            },
            y: {
                grid: {
                    color: this.isDarkMode ? 'rgba(148, 163, 184, 0.1)' : 'rgba(148, 163, 184, 0.2)',
                    borderColor: this.isDarkMode ? '#334155' : '#e2e8f0'
                },
                ticks: {
                    color: this.isDarkMode ? '#94a3b8' : '#64748b'
                }
            }
        };
    }
    
    // Chart Creation Helpers
    createLineChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            scales: this.getScaleOptions(),
            interaction: {
                intersect: false,
                mode: 'index'
            },
            elements: {
                line: {
                    tension: 0.4
                },
                point: {
                    radius: 6,
                    hoverRadius: 8,
                    borderWidth: 2
                }
            }
        };
        
        const chart = new Chart(ctx, {
            type: 'line',
            data: data,
            options: { ...defaultOptions, ...options }
        });
        
        this.charts.set(canvasId, chart);
        return chart;
    }
    
    createBarChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            scales: this.getScaleOptions()
        };
        
        const chart = new Chart(ctx, {
            type: 'bar',
            data: data,
            options: { ...defaultOptions, ...options }
        });
        
        this.charts.set(canvasId, chart);
        return chart;
    }
    
    createDoughnutChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            cutout: '60%'
        };
        
        const chart = new Chart(ctx, {
            type: 'doughnut',
            data: data,
            options: { ...defaultOptions, ...options }
        });
        
        this.charts.set(canvasId, chart);
        return chart;
    }
    
    createScatterChart(canvasId, data, options = {}) {
        const ctx = document.getElementById(canvasId)?.getContext('2d');
        if (!ctx) return null;
        
        const defaultOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            },
            scales: this.getScaleOptions()
        };
        
        const chart = new Chart(ctx, {
            type: 'scatter',
            data: data,
            options: { ...defaultOptions, ...options }
        });
        
        this.charts.set(canvasId, chart);
        return chart;
    }
    
    // Loading States
    showLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('hidden');
        }
    }
    
    hideLoading() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('hidden');
        }
    }
    
    // API Helpers
    async fetchData(url) {
        try {
            console.log(`[DEBUG] Fetching data from: ${url}`);
            this.showLoading();
            
            const response = await fetch(url);
            console.log(`[DEBUG] Response status: ${response.status}`);
            console.log(`[DEBUG] Response headers:`, response.headers);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error(`[ERROR] HTTP ${response.status}: ${errorText}`);
                throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
            }
            
            const data = await response.json();
            console.log(`[DEBUG] Received data:`, data);
            console.log(`[DEBUG] Data type:`, typeof data);
            console.log(`[DEBUG] Data length/keys:`, Array.isArray(data) ? data.length : Object.keys(data));
            
            return data;
        } catch (error) {
            console.error('[ERROR] Fetch error:', error);
            console.error('[ERROR] Stack trace:', error.stack);
            this.showNotification(`Error loading data: ${error.message}`, 'error');
            throw error;
        } finally {
            this.hideLoading();
        }
    }
    
    // Animation Helpers
    initializeAnimations() {
        // Animate cards on scroll
        const observerCallback = (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animation = 'fadeInUp 0.6s ease forwards';
                }
            });
        };
        
        const observer = new IntersectionObserver(observerCallback, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        // Observe all cards
        document.querySelectorAll('.glass-card, .feature-card').forEach(card => {
            observer.observe(card);
        });
    }
    
    // Color Palettes
    getColorPalette() {
        return {
            primary: [
                'rgb(59, 130, 246)',   // blue-500
                'rgb(147, 51, 234)',   // purple-600
                'rgb(16, 185, 129)',   // emerald-500
                'rgb(249, 115, 22)',   // orange-500
                'rgb(239, 68, 68)',    // red-500
                'rgb(236, 72, 153)',   // pink-500
                'rgb(34, 197, 94)',    // green-500
                'rgb(168, 85, 247)',   // violet-500
                'rgb(6, 182, 212)',    // cyan-500
                'rgb(245, 158, 11)'    // amber-500
            ],
            gradient: [
                'linear-gradient(135deg, rgb(59, 130, 246), rgb(147, 51, 234))',
                'linear-gradient(135deg, rgb(16, 185, 129), rgb(6, 182, 212))',
                'linear-gradient(135deg, rgb(249, 115, 22), rgb(239, 68, 68))',
                'linear-gradient(135deg, rgb(236, 72, 153), rgb(168, 85, 247))'
            ]
        };
    }
    
    // Utility Methods
    formatNumber(num, decimals = 2) {
        if (num === null || num === undefined) return 'N/A';
        return Number(num).toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }
    
    formatPercentage(num, decimals = 1) {
        if (num === null || num === undefined) return 'N/A';
        return `${Number(num).toFixed(decimals)}%`;
    }
    
    debounce(func, wait) {
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
    
    // Chart Export
    exportChart(chartId, filename = 'chart') {
        const chart = this.charts.get(chartId);
        if (!chart) return;
        
        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${filename}.png`;
        link.href = url;
        link.click();
        
        this.showNotification('Chart exported successfully!', 'success');
    }
    
    // Data Processing Helpers
    processTimeSeriesData(data, valueKey = 'value', labelKey = 'year') {
        return {
            labels: data.map(item => item[labelKey]),
            values: data.map(item => parseFloat(item[valueKey]) || 0)
        };
    }
    
    calculateTrend(data) {
        if (data.length < 2) return { direction: 'stable', change: 0 };
        
        const first = data[0];
        const last = data[data.length - 1];
        const change = ((last - first) / first) * 100;
        
        let direction = 'stable';
        if (Math.abs(change) > 1) {
            direction = change > 0 ? 'increasing' : 'decreasing';
        }
        
        return { direction, change: change.toFixed(2) };
    }
    
    // Regional Color Mapping
    getRegionColor(region) {
        const regionColors = {
            'Europe & Central Asia': '#3b82f6',
            'North America': '#10b981',
            'East Asia & Pacific': '#f59e0b',
            'Latin America & Caribbean': '#ef4444',
            'Middle East & North Africa': '#8b5cf6',
            'South Asia': '#06b6d4',
            'Sub-Saharan Africa': '#84cc16'
        };
        
        return regionColors[region] || '#6b7280';
    }
}

// Initialize dashboard when DOM is loaded
let dashboard;

document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for Chart.js to load
    setTimeout(() => {
        if (typeof Chart === 'undefined') {
            console.error('Chart.js failed to load. Please refresh the page.');
            return;
        }
        
        dashboard = new DashboardManager();
        
        // Initialize tooltips and other interactive elements
        initializeTooltips();
        
        // Setup keyboard shortcuts
        setupKeyboardShortcuts();
    }, 100);
});

// Tooltip initialization
function initializeTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', showTooltip);
        trigger.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(e) {
    const text = e.target.getAttribute('data-tooltip');
    if (!text) return;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    tooltip.style.cssText = `
        position: absolute;
        background: rgba(15, 23, 42, 0.9);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        white-space: nowrap;
        z-index: 1000;
        pointer-events: none;
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = e.target.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
}

function hideTooltip() {
    const tooltip = document.querySelector('.tooltip');
    if (tooltip) {
        tooltip.remove();
    }
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + D: Toggle dark mode
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            e.preventDefault();
            dashboard.toggleTheme();
        }
        
        // Escape: Close modals/menus
        if (e.key === 'Escape') {
            const mobileMenu = document.getElementById('mobile-menu');
            if (mobileMenu && !mobileMenu.classList.contains('hidden')) {
                mobileMenu.classList.add('hidden');
            }
        }
    });
}

// Global utility functions
window.showNotification = (message, type, duration) => {
    if (dashboard) {
        dashboard.showNotification(message, type, duration);
    }
};

window.exportChart = (chartId, filename) => {
    if (dashboard) {
        dashboard.exportChart(chartId, filename);
    }
};

// Handle page visibility changes
document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
        // Refresh data when page becomes visible again
        if (dashboard && dashboard.charts.size > 0) {
            dashboard.charts.forEach(chart => {
                chart.resize();
            });
        }
    }
});

// Handle window resize
let resizeTimeout;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimeout);
    resizeTimeout = setTimeout(() => {
        if (dashboard && dashboard.charts.size > 0) {
            dashboard.charts.forEach(chart => {
                chart.resize();
            });
        }
    }, 150);
});