/**
 * Enhanced Prescription Request Functionality
 * 
 * This script improves the prescription request form submission process
 * by handling form submission via AJAX and providing better user feedback.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get form and other elements
    const form = document.getElementById('prescriptionRequestForm');
    
    if (form) {
        console.log('Prescription request form found - initializing');
        
        // Create error message div if it doesn't exist
        let errorDiv = document.getElementById('requestError');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.id = 'requestError';
            errorDiv.className = 'alert alert-danger d-none mb-3';
            errorDiv.innerHTML = '<i class="fas fa-exclamation-circle me-2"></i><span id="errorMessage">Có lỗi xảy ra khi gửi yêu cầu. Vui lòng thử lại sau.</span>';
            
            // Insert before the button
            const button = document.getElementById('requestPrescriptionBtn');
            if (button) {
                button.parentNode.insertBefore(errorDiv, button);
            }
        }
        
        const errorMessage = document.getElementById('errorMessage') || errorDiv.querySelector('span');
        
        // Add submit event listener
        form.addEventListener('submit', function(event) {
            // Prevent default form submission
            event.preventDefault();
            
            // Hide any previous error messages
            errorDiv.classList.add('d-none');
            
            // Get the request button and show loading state
            const button = document.getElementById('requestPrescriptionBtn');
            if (button) {
                button.disabled = true;
                button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i> Đang gửi yêu cầu...';
            }
            
            // Get form data for logging
            const formData = new FormData(form);
            console.log('Submitting prescription request with:');
            for (let [key, value] of formData.entries()) {
                console.log(`  ${key}: ${value}`);
            }
            
            // Submit the form
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                // Handle redirects directly
                if (response.redirected) {
                    window.location.href = response.url;
                    return null;
                }
                
                if (!response.ok) {
                    throw new Error('Lỗi máy chủ khi xử lý yêu cầu');
                }
                
                return response.text();
            })
            .then(html => {
                // Skip if we've already redirected
                if (html === null) return;
                
                // Check if the response contains a success message
                if (html.includes('success') || html.includes('prescription-request-detail')) {
                    // Success - redirect to appropriate page
                    const match = html.match(/prescription-requests\/(\d+)/);
                    if (match && match[1]) {
                        window.location.href = `/pharmacy/prescription-requests/${match[1]}/`;
                    } else {
                        window.location.href = '/pharmacy/prescription-requests/';
                    }
                } else {
                    // Fallback to redirect to the prescription list
                    window.location.href = '/pharmacy/prescription-requests/';
                }
            })
            .catch(error => {
                console.error('Error submitting prescription request:', error);
                
                // Show error message
                errorDiv.classList.remove('d-none');
                if (errorMessage) {
                    errorMessage.textContent = error.message || 'Có lỗi xảy ra khi gửi yêu cầu. Vui lòng thử lại sau.';
                }
                
                // Reset button state
                if (button) {
                    button.disabled = false;
                    button.innerHTML = '<i class="fas fa-paper-plane me-2"></i> Gửi yêu cầu kê đơn thuốc';
                }
            });
        });
    }
}); 