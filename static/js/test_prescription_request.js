/**
 * Test Script for Prescription Request Functionality
 * 
 * This script can be used to test if the prescription request functionality
 * is working properly from the console.
 */

function testPrescriptionRequest() {
    // Get the form
    const form = document.getElementById('prescriptionRequestForm');
    
    if (!form) {
        console.error('Prescription request form not found');
        return;
    }
    
    console.log('Found prescription request form:', form);
    
    // Get form data
    const formData = new FormData(form);
    console.log('Form data:');
    for (let [key, value] of formData.entries()) {
        console.log(`  ${key}: ${value}`);
    }
    
    // Get CSRF token
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
    if (!csrfToken) {
        console.error('CSRF token not found in form');
        return;
    }
    
    console.log('CSRF token found:', csrfToken);
    
    // Get action URL
    const actionUrl = form.getAttribute('action');
    console.log('Form action URL:', actionUrl);
    
    // Show a message that we're testing
    console.log('Test submission will begin in 3 seconds...');
    
    // Add a manual delay to see the console logs
    setTimeout(() => {
        // Test submission using fetch API
        console.log('Sending test request to:', actionUrl);
        
        fetch(actionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            console.log('Response is redirect:', response.redirected);
            
            if (response.redirected) {
                console.log('Redirect URL:', response.url);
                return null;
            }
            
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            
            return response.text();
        })
        .then(html => {
            if (html === null) {
                console.log('Response was a redirect, no content to process');
                return;
            }
            
            console.log('Response content length:', html.length);
            console.log('Response preview:', html.substring(0, 200) + '...');
            
            // Check for success indicators
            if (html.includes('success') || html.includes('prescription-request-detail')) {
                console.log('Success indicators found in response');
                const match = html.match(/prescription-requests\/(\d+)/);
                if (match && match[1]) {
                    console.log('Prescription request ID found:', match[1]);
                    console.log('Redirect URL would be:', `/pharmacy/prescription-requests/${match[1]}/`);
                }
            } else {
                console.log('No success indicators found in response');
            }
        })
        .catch(error => {
            console.error('Error during test request:', error);
        });
    }, 3000);
}

// Export the test function to the global scope for console use
window.testPrescriptionRequest = testPrescriptionRequest;

console.log('Prescription request test script loaded.');
console.log('To test the prescription request, run: testPrescriptionRequest()'); 