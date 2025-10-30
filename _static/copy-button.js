// Add copy button to code blocks
document.addEventListener('DOMContentLoaded', function() {
    // SVG icon for clipboard
    const clipboardIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect></svg>`;

    // SVG icon for checkmark
    const checkmarkIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

    // Find all code input blocks (from notebooks and regular code blocks)
    // Strategy:
    // 1. For notebooks: explicitly target pre tags inside input_area
    // 2. For regular docs: target all highlight divs, then filter with skip conditions
    let codeBlocks = document.querySelectorAll('div.input_area > div.highlight > pre');

    // Also get regular documentation code blocks
    const docBlocks = document.querySelectorAll('div.highlight > pre');

    // Combine and deduplicate
    codeBlocks = Array.from(codeBlocks).concat(
        Array.from(docBlocks).filter(block => {
            // Skip if already in notebook input_area
            if (block.closest('div.input_area')) return false;
            // Skip if in prompt or output
            if (block.closest('.prompt')) return false;
            if (block.closest('.nboutput')) return false;
            if (block.closest('.output_area')) return false;
            return true;
        })
    );

    codeBlocks.forEach(function(codeBlock) {
        // Don't add button if already present
        if (codeBlock.querySelector('.copy-button') || codeBlock.parentElement.querySelector('.copy-button')) {
            return;
        }

        // Create copy button
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.innerHTML = clipboardIcon;
        button.title = 'Copy code to clipboard';

        // Style the button
        button.style.cssText = `
            position: absolute;
            top: 0.5rem;
            right: 0.5rem;
            padding: 0.4rem;
            background-color: rgba(0, 0, 0, 0.3);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 0.25rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1;
            transition: all 0.2s ease;
            width: 28px;
            height: 28px;
            padding: 0;
        `;

        // Add hover effect
        button.onmouseover = function() {
            this.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';
        };
        button.onmouseout = function() {
            this.style.backgroundColor = 'rgba(0, 0, 0, 0.3)';
        };

        // Make pre block relative positioned
        codeBlock.style.position = 'relative';

        // Add click event
        button.addEventListener('click', function() {
            const code = codeBlock.querySelector('code');
            const text = code ? code.textContent : codeBlock.textContent;

            // Copy to clipboard
            navigator.clipboard.writeText(text).then(function() {
                // Change button icon and color temporarily
                const originalHTML = button.innerHTML;
                button.innerHTML = checkmarkIcon;
                button.style.backgroundColor = 'rgba(34, 197, 94, 0.7)';

                setTimeout(function() {
                    button.innerHTML = originalHTML;
                    button.style.backgroundColor = 'rgba(0, 0, 0, 0.3)';
                }, 2000);
            }).catch(function(err) {
                console.error('Failed to copy:', err);
            });
        });

        // Append button to code block
        codeBlock.appendChild(button);
    });
});
