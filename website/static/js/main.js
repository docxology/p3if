/**
 * P3IF Website Main JavaScript
 * Provides interactive functionality for the P3IF website
 */

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initNavigation();
    initVisualizationGallery();
    initDomainExplorer();
    initCodeHighlighting();
    initMobileMenu();
});

/**
 * Initialize the main navigation functionality
 */
function initNavigation() {
    // Set active nav links based on current path
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');
    
    navLinks.forEach(link => {
        // Mark link as active if it matches the current path
        // Use startsWith to match parent paths
        if (link.getAttribute('href') === currentPath || 
            (link.getAttribute('href') !== '/' && currentPath.startsWith(link.getAttribute('href')))) {
            link.classList.add('active');
        }
    });

    // Add scroll event listener for sticky header effects
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.header');
        if (window.scrollY > 10) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
}

/**
 * Initialize mobile menu functionality
 */
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navbarNav = document.querySelector('.navbar-nav');
    
    if (!menuToggle || !navbarNav) return;
    
    menuToggle.addEventListener('click', function() {
        navbarNav.classList.toggle('show');
        menuToggle.classList.toggle('active');
    });
}

/**
 * Initialize the visualization gallery
 */
function initVisualizationGallery() {
    const gallery = document.querySelector('.viz-gallery');
    if (!gallery) return;
    
    // Add lightbox functionality for visualization images
    const vizImages = document.querySelectorAll('.viz-img-container img');
    vizImages.forEach(img => {
        img.addEventListener('click', function() {
            const src = this.getAttribute('src');
            const alt = this.getAttribute('alt');
            
            // Create lightbox elements
            const lightbox = document.createElement('div');
            lightbox.className = 'lightbox';
            
            const lightboxContent = document.createElement('div');
            lightboxContent.className = 'lightbox-content';
            
            const image = document.createElement('img');
            image.src = src;
            image.alt = alt;
            
            const caption = document.createElement('div');
            caption.className = 'lightbox-caption';
            caption.textContent = alt;
            
            const closeBtn = document.createElement('button');
            closeBtn.className = 'lightbox-close';
            closeBtn.innerHTML = '&times;';
            closeBtn.addEventListener('click', function() {
                document.body.removeChild(lightbox);
            });
            
            // Build lightbox
            lightboxContent.appendChild(image);
            lightboxContent.appendChild(caption);
            lightboxContent.appendChild(closeBtn);
            lightbox.appendChild(lightboxContent);
            
            // Add lightbox to body
            document.body.appendChild(lightbox);
            
            // Close lightbox when clicking outside content
            lightbox.addEventListener('click', function(e) {
                if (e.target === lightbox) {
                    document.body.removeChild(lightbox);
                }
            });
        });
    });
    
    // Add filter functionality if filter options exist
    const filterBtns = document.querySelectorAll('.viz-filter-btn');
    if (filterBtns.length > 0) {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const filter = this.getAttribute('data-filter');
                
                // Remove active class from all buttons
                filterBtns.forEach(b => b.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Filter gallery items
                const items = gallery.querySelectorAll('.viz-card');
                items.forEach(item => {
                    const type = item.getAttribute('data-type');
                    if (filter === 'all' || type === filter) {
                        item.style.display = 'block';
                    } else {
                        item.style.display = 'none';
                    }
                });
            });
        });
    }
}

/**
 * Initialize the domain explorer functionality
 */
function initDomainExplorer() {
    const domainExplorer = document.querySelector('.domain-explorer');
    if (!domainExplorer) return;
    
    // Initialize search functionality if search box exists
    const searchBox = document.querySelector('.domain-search');
    if (searchBox) {
        searchBox.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const domains = document.querySelectorAll('.domain-card');
            
            domains.forEach(domain => {
                const title = domain.querySelector('.card-title').textContent.toLowerCase();
                const desc = domain.querySelector('.card-text').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || desc.includes(searchTerm)) {
                    domain.style.display = 'block';
                } else {
                    domain.style.display = 'none';
                }
            });
        });
    }
    
    // Initialize domain pattern browser if it exists
    const patternBrowser = document.querySelector('.domain-patterns');
    if (patternBrowser) {
        const patternTabs = patternBrowser.querySelectorAll('.pattern-tab');
        const patternPanels = patternBrowser.querySelectorAll('.pattern-panel');
        
        patternTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const target = this.getAttribute('data-target');
                
                // Deactivate all tabs and panels
                patternTabs.forEach(t => t.classList.remove('active'));
                patternPanels.forEach(p => p.classList.remove('active'));
                
                // Activate clicked tab and corresponding panel
                this.classList.add('active');
                document.querySelector(target).classList.add('active');
            });
        });
    }
}

/**
 * Initialize code syntax highlighting
 */
function initCodeHighlighting() {
    // Check if code blocks with 'language-' class exist
    const codeBlocks = document.querySelectorAll('pre code[class*="language-"]');
    if (codeBlocks.length > 0 && typeof Prism !== 'undefined') {
        // If Prism is loaded, initialize highlighting
        Prism.highlightAll();
    }
}

/**
 * Utility function to fetch API data
 */
async function fetchFromAPI(endpoint) {
    try {
        const response = await fetch(`/api${endpoint}`);
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('API fetch error:', error);
        return null;
    }
}

/**
 * Initialize interactive visualizations if any are present
 */
function initInteractiveViz() {
    // Check for cube visualization
    const cubeContainer = document.getElementById('cube-viz');
    if (cubeContainer && typeof init3DCube === 'function') {
        // Assumes init3DCube is defined in a separate visualization.js file
        init3DCube(cubeContainer);
    }
    
    // Check for force graph visualization
    const graphContainer = document.getElementById('force-graph');
    if (graphContainer && typeof initForceGraph === 'function') {
        // Assumes initForceGraph is defined in a separate visualization.js file
        initForceGraph(graphContainer);
    }
} 