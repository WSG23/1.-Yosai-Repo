// assets/radio-toggle.js - FIXED VERSION - Simple and Effective

console.log('🎛️ Radio toggle script loading...');

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM ready, initializing radio toggle fix');
    initializeRadioToggleFix();
    
    // Set up observers for dynamic content
    setupDynamicContentObserver();
});

function initializeRadioToggleFix() {
    // Apply the fix immediately
    applyRadioToggleFix();
    
    // Set up event listeners
    setupRadioToggleListeners();
    
    console.log('✅ Radio toggle fix initialized');
}

function applyRadioToggleFix() {
    const container = document.querySelector('#manual-map-toggle');
    
    if (!container) {
        console.log('⚠️ Radio toggle container not found, retrying...');
        setTimeout(applyRadioToggleFix, 100);
        return;
    }
    
    console.log('🎨 Applying radio toggle styling fix');
    
    const radioInputs = container.querySelectorAll('input[type="radio"]');
    const labels = container.querySelectorAll('label');
    
    // Hide radio inputs and style labels
    radioInputs.forEach((input, index) => {
        const label = labels[index];
        if (!label) return;
        
        // Completely hide radio input
        input.style.display = 'none';
        input.style.opacity = '0';
        input.style.position = 'absolute';
        input.style.left = '-9999px';
        input.style.pointerEvents = 'none';
        
        // Apply base label styling
        applyBaseLabelStyling(label);
        
        // Apply checked state if needed
        if (input.checked) {
            applyCheckedStyling(label, input.value);
        }
    });
    
    console.log(`✅ Styled ${radioInputs.length} radio inputs`);
}

function applyBaseLabelStyling(label) {
    // Base styling for all labels
    const baseStyles = {
        display: 'inline-block',
        backgroundColor: '#2D3748',
        color: '#A0AEC0',
        border: '2px solid #4A5568',
        borderRadius: '20px',
        padding: '12px 24px',
        margin: '0 8px',
        cursor: 'pointer',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        fontWeight: '500',
        minWidth: '120px',
        textAlign: 'center',
        userSelect: 'none',
        fontSize: '0.95rem',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
        fontFamily: 'inherit'
    };
    
    Object.assign(label.style, baseStyles);
}

function applyCheckedStyling(label, value) {
    // Common checked styles
    label.style.color = 'white';
    label.style.fontWeight = '600';
    label.style.transform = 'translateY(-1px)';
    
    // Value-specific styles
    if (value === 'yes') {
        label.style.backgroundColor = '#2196F3';
        label.style.borderColor = '#2196F3';
        label.style.boxShadow = '0 4px 12px rgba(33, 150, 243, 0.3)';
    } else if (value === 'no') {
        label.style.backgroundColor = '#E02020';
        label.style.borderColor = '#E02020';
        label.style.boxShadow = '0 4px 12px rgba(224, 32, 32, 0.3)';
    }
}

function setupRadioToggleListeners() {
    const container = document.querySelector('#manual-map-toggle');
    if (!container) return;
    
    console.log('👂 Setting up radio toggle listeners');
    
    // Listen for changes on the container
    container.addEventListener('change', function(e) {
        if (e.target && e.target.type === 'radio') {
            console.log(`📻 Radio changed to: ${e.target.value}`);
            setTimeout(applyRadioToggleFix, 50);
        }
    });
    
    // Add click handlers to labels for better UX
    const labels = container.querySelectorAll('label');
    labels.forEach((label, index) => {
        label.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default to control the interaction
            
            const radioInputs = container.querySelectorAll('input[type="radio"]');
            const targetInput = radioInputs[index];
            
            if (targetInput && !targetInput.checked) {
                // Uncheck all other radios
                radioInputs.forEach(radio => radio.checked = false);
                
                // Check the target radio
                targetInput.checked = true;
                
                console.log(`🖱️ Manually selected: ${targetInput.value}`);
                
                // Trigger Dash callbacks
                triggerDashCallbacks(targetInput, container);
                
                // Update styling immediately
                setTimeout(applyRadioToggleFix, 50);
            }
        });
    });
}

function triggerDashCallbacks(targetInput, container) {
    console.log(`🎯 Triggering Dash callbacks for: ${targetInput.value}`);
    
    // Method 1: Trigger events on the specific input
    ['change', 'input', 'click'].forEach(eventType => {
        const event = new Event(eventType, { 
            bubbles: true, 
            cancelable: true,
            composed: true 
        });
        targetInput.dispatchEvent(event);
    });
    
    // Method 2: Trigger on the container
    const containerEvent = new Event('change', { 
        bubbles: true, 
        cancelable: true 
    });
    container.dispatchEvent(containerEvent);
    
    // Method 3: Custom event for Dash
    const dashEvent = new CustomEvent('dash-radio-change', {
        detail: {
            component_id: 'manual-map-toggle',
            value: targetInput.value
        },
        bubbles: true
    });
    document.dispatchEvent(dashEvent);
    
    console.log('✅ Events dispatched');
}

function setupDynamicContentObserver() {
    console.log('👀 Setting up dynamic content observer');
    
    // Watch for new content being added to the page
    const observer = new MutationObserver(function(mutations) {
        let shouldReinitialize = false;
        
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        // Check if the new node contains or is a radio toggle
                        const hasRadioToggle = node.querySelector && node.querySelector('#manual-map-toggle');
                        const isRadioToggle = node.id === 'manual-map-toggle';
                        
                        if (hasRadioToggle || isRadioToggle) {
                            shouldReinitialize = true;
                        }
                    }
                });
            }
        });
        
        if (shouldReinitialize) {
            console.log('🆕 New radio toggle detected, reinitializing...');
            setTimeout(initializeRadioToggleFix, 100);
        }
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
}

// Periodic fix application (backup method)
setInterval(function() {
    const container = document.querySelector('#manual-map-toggle');
    if (container) {
        const inputs = container.querySelectorAll('input[type="radio"]');
        const hasVisibleInputs = Array.from(inputs).some(input => 
            input.style.display !== 'none' && input.style.opacity !== '0'
        );
        
        if (hasVisibleInputs) {
            console.log('🔄 Periodic radio toggle fix applied');
            applyRadioToggleFix();
        }
    }
}, 2000); // Check every 2 seconds

// Debug function
window.debugRadioToggle = function() {
    console.log('=== RADIO TOGGLE DEBUG ===');
    
    const container = document.querySelector('#manual-map-toggle');
    console.log('Container found:', !!container);
    
    if (container) {
        const inputs = container.querySelectorAll('input[type="radio"]');
        const labels = container.querySelectorAll('label');
        
        console.log(`Found ${inputs.length} inputs, ${labels.length} labels`);
        
        inputs.forEach((input, i) => {
            console.log(`Input ${i}: value=${input.value}, checked=${input.checked}, visible=${input.style.display !== 'none'}`);
        });
        
        labels.forEach((label, i) => {
            console.log(`Label ${i}: bg=${label.style.backgroundColor}, color=${label.style.color}`);
        });
    }
    
    console.log('========================');
};

// Force fix function
window.forceRadioToggleFix = function() {
    console.log('🔧 Forcing radio toggle fix...');
    applyRadioToggleFix();
};

// Test function
window.testRadioToggle = function() {
    console.log('🧪 Testing radio toggle functionality...');
    
    const container = document.querySelector('#manual-map-toggle');
    if (!container) {
        console.log('❌ Container not found');
        return;
    }
    
    const inputs = container.querySelectorAll('input[type="radio"]');
    if (inputs.length === 0) {
        console.log('❌ No radio inputs found');
        return;
    }
    
    // Test selecting each option
    inputs.forEach((input, index) => {
        setTimeout(() => {
            console.log(`Testing option: ${input.value}`);
            input.checked = true;
            triggerDashCallbacks(input, container);
            applyRadioToggleFix();
        }, index * 1000);
    });
};

console.log('🎛️ Radio toggle script loaded');
console.log('💡 Debug functions available:');
console.log('   - window.debugRadioToggle()');
console.log('   - window.forceRadioToggleFix()');
console.log('   - window.testRadioToggle()');