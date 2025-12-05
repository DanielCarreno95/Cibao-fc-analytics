"""
Navigation component for consistent top navigation across all pages
"""
import streamlit as st


def render_top_navigation():
    """
    Renders a top navigation bar that appears on all pages.
    Allows users to navigate between pages without going back to the hub.
    Standardized styling for consistent UX across all pages.
    Also ensures the sidebar toggle button is visible.
    """
    # CSS for navigation bar - standardized across all pages
    # Also ensure sidebar toggle button is always visible
    st.markdown("""
    <style>
    /* Ensure sidebar toggle button is always visible */
    [data-testid="stSidebarCollapseButton"] {
        display: block !important;
        visibility: visible !important;
    }
    
    /* Make sure sidebar can be toggled */
    [data-testid="stSidebar"] {
        transition: transform 0.3s ease;
    }
    
    .top-nav-container {
        background: linear-gradient(135deg, rgba(20, 20, 25, 0.95) 0%, rgba(15, 15, 20, 0.98) 100%);
        border-bottom: 2px solid rgba(255, 140, 0, 0.3);
        padding: 0.8rem 1.5rem;
        margin: -1rem -1rem 1.5rem -1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    }
    .nav-label {
        color: #94A3B8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-right: 0.5rem;
        line-height: 2.5;
    }
    /* Standardize navigation buttons - MAXIMUM specificity to override ALL page-specific styles */
    /* Use multiple selectors with highest possible specificity - MUST match regular buttons exactly */
    /* Match regular button styling: black text, orange background, same size */
    div.top-nav-container div[data-testid="column"] div[data-testid="stButton"] button[key^="nav_"],
    div.top-nav-container div[data-testid="column"] div[data-testid="stButton"] button[key^="nav_"]:not([key^="home_btn"]),
    div.top-nav-container div[data-testid="column"] .stButton button[key^="nav_"],
    div.top-nav-container div[data-testid="column"] button[key^="nav_"],
    .top-nav-container div[data-testid="column"] div[data-testid="stButton"] button[key^="nav_"],
    .top-nav-container div[data-testid="column"] .stButton button[key^="nav_"],
    .top-nav-container .stButton button[key^="nav_"],
    .top-nav-container button[key^="nav_"],
    div[data-testid="column"] div[data-testid="stButton"] button[key^="nav_"],
    div[data-testid="column"] .stButton button[key^="nav_"],
    .stButton button[key^="nav_"],
    button[key^="nav_"] {
        background-color: #ff7b00 !important;
        border: 1px solid #ff7b00 !important;
        color: black !important;
        font-size: 1.3rem !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 6px !important;
        transition: all 0.2s !important;
        height: auto !important;
        min-height: auto !important;
        max-height: none !important;
        line-height: normal !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        font-weight: normal !important;
    }
    div.top-nav-container div[data-testid="column"] div[data-testid="stButton"] button[key^="nav_"]:hover,
    div.top-nav-container div[data-testid="column"] .stButton button[key^="nav_"]:hover,
    .top-nav-container .stButton button[key^="nav_"]:hover,
    .top-nav-container button[key^="nav_"]:hover,
    .stButton button[key^="nav_"]:hover,
    button[key^="nav_"]:hover {
        background-color: #ff8c00 !important;
        border-color: #ff8c00 !important;
        color: black !important;
    }
    div.top-nav-container div[data-testid="column"] div[data-testid="stButton"] button[key="nav_home_top"],
    div.top-nav-container div[data-testid="column"] .stButton button[key="nav_home_top"],
    .top-nav-container .stButton button[key="nav_home_top"],
    .top-nav-container button[key="nav_home_top"],
    .stButton button[key="nav_home_top"],
    button[key="nav_home_top"] {
        font-size: 1.2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Navigation bar using Streamlit columns and buttons
    st.markdown('<div class="top-nav-container">', unsafe_allow_html=True)
    
    # Create columns for navigation - consistent spacing
    col_home, col_spacer1, col_liga_label, col_liga1, col_liga2, col_spacer2, col_copa_label, col_copa1, col_copa2 = st.columns([1, 0.3, 0.8, 2, 2, 0.3, 0.8, 2, 2])
    
    with col_home:
        if st.button("🏠", help="Volver al Inicio", use_container_width=True, key="nav_home_top"):
            st.switch_page("app.py")
    
    with col_liga_label:
        st.markdown('<div class="nav-label">Liga:</div>', unsafe_allow_html=True)
    
    with col_liga1:
        if st.button("Rendimiento Colectivo", key="nav_liga_colectivo_top", use_container_width=True):
            st.switch_page("pages/1_Rendimiento_Colectivo_-_Liga.py")
    
    with col_liga2:
        if st.button("Análisis del Rival", key="nav_liga_rival_top", use_container_width=True):
            st.switch_page("pages/2_Analisis_del_Rival_-_Liga.py")
    
    with col_copa_label:
        st.markdown('<div class="nav-label">Copa:</div>', unsafe_allow_html=True)
    
    with col_copa1:
        if st.button("Rendimiento Colectivo", key="nav_copa_colectivo_top", use_container_width=True):
            st.switch_page("pages/4_Rendimiento_Colectivo_-_Copa.py")
    
    with col_copa2:
        if st.button("Análisis del Rival", key="nav_copa_rival_top", use_container_width=True):
            st.switch_page("pages/5_Analisis_del_Rival_-_Copa.py")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # CRITICAL: JavaScript to enforce navigation button styles after Streamlit re-renders
    # This must run continuously to override any CSS that loads after
    st.markdown("""
    <style>
    /* Additional CSS class for navigation buttons - highest specificity */
    button[key^="nav_"].nav-btn-enforced,
    button[key^="nav_"] {
        background-color: #ff7b00 !important;
        border: 1px solid #ff7b00 !important;
        color: black !important;
        font-size: 1.3rem !important;
        padding: 0.5rem 1.5rem !important;
        height: auto !important;
        min-height: auto !important;
        max-height: none !important;
        line-height: normal !important;
        width: 100% !important;
        min-width: 0 !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        font-weight: normal !important;
    }
    </style>
    <script>
    (function() {
        function enforceNavStyles() {
            const navButtons = document.querySelectorAll('button[key^="nav_"]');
            navButtons.forEach(btn => {
                // Add class for additional CSS specificity
                btn.classList.add('nav-btn-enforced');
                
                // Force inline styles - these override CSS (inline styles have highest specificity)
                btn.style.backgroundColor = '#ff7b00';
                btn.style.border = '1px solid #ff7b00';
                btn.style.color = 'black';
                btn.style.fontSize = '1.3rem';
                btn.style.padding = '0.5rem 1.5rem';
                btn.style.height = 'auto';
                btn.style.minHeight = 'auto';
                btn.style.maxHeight = 'none';
                btn.style.lineHeight = 'normal';
                btn.style.width = '100%';
                btn.style.minWidth = '0';
                btn.style.maxWidth = '100%';
                btn.style.boxSizing = 'border-box';
                btn.style.fontWeight = 'normal';
            });
        }
        
        // Run immediately
        enforceNavStyles();
        
        // Run after DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', enforceNavStyles);
        }
        
        // Run after page fully loads
        window.addEventListener('load', enforceNavStyles);
        
        // Run after short delays (Streamlit loads CSS asynchronously)
        setTimeout(enforceNavStyles, 50);
        setTimeout(enforceNavStyles, 100);
        setTimeout(enforceNavStyles, 300);
        setTimeout(enforceNavStyles, 500);
        setTimeout(enforceNavStyles, 1000);
        setTimeout(enforceNavStyles, 2000);
        
        // Monitor for DOM changes (Streamlit re-renders)
        const observer = new MutationObserver(function(mutations) {
            let shouldEnforce = false;
            mutations.forEach(function(mutation) {
                if (mutation.addedNodes.length > 0) {
                    // Check if any added nodes are navigation buttons
                    mutation.addedNodes.forEach(function(node) {
                        if (node.nodeType === 1) { // Element node
                            if (node.matches && node.matches('button[key^="nav_"]')) {
                                shouldEnforce = true;
                            }
                            if (node.querySelectorAll) {
                                const navBtns = node.querySelectorAll('button[key^="nav_"]');
                                if (navBtns.length > 0) {
                                    shouldEnforce = true;
                                }
                            }
                        }
                    });
                }
                if (mutation.type === 'attributes' && 
                    (mutation.attributeName === 'style' || mutation.attributeName === 'class')) {
                    shouldEnforce = true;
                }
            });
            if (shouldEnforce) {
                setTimeout(enforceNavStyles, 10);
            }
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['style', 'class']
        });
        
        // Periodic check (every 500ms) as fallback
        setInterval(enforceNavStyles, 500);
    })();
    </script>
    """, unsafe_allow_html=True)

