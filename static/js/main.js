document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const previewArea = document.getElementById('preview-area');
    const previewImage = document.getElementById('preview-image');
    const uploadContent = document.getElementById('upload-content');
    const resultContainer = document.getElementById('result-container');
    const resultText = document.getElementById('result-text');
    const probabilityFill = document.getElementById('probability-fill');
    const probabilityText = document.getElementById('probability-text');
    const riskLevel = document.getElementById('risk-level');
    const loading = document.getElementById('loading');

    // Handle drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const file = e.dataTransfer.files[0];
        handleFile(file);
    });

    // Handle file input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        handleFile(file);
    });

    function handleFile(file) {
        if (file && file.type.startsWith('image/')) {
            console.log('Processing file:', file.name);
            
            // Show preview
            const reader = new FileReader();
            reader.onload = function(e) {
                previewImage.src = e.target.result;
                previewArea.style.display = 'block';
                uploadContent.style.display = 'none';
                resultContainer.style.display = 'none';
                loading.style.display = 'block';
            }
            reader.readAsDataURL(file);

            // Upload and process image
            const formData = new FormData();
            formData.append('image', file);

            console.log('Sending request to server...');
            fetch('/predict', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                console.log('Server response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Received data:', data);
                loading.style.display = 'none';
                resultContainer.style.display = 'block';
                
                if (data.error) {
                    throw new Error(data.error);
                }

                // Update result text with cancer type
                resultText.textContent = `Detected: ${data.details.type}`;
                
                // Update probability bar and text
                const probability = parseFloat(data.probability);
                probabilityFill.style.width = `${probability * 100}%`;
                probabilityText.textContent = data.percentage;
                
                // Update risk level with appropriate styling
                riskLevel.textContent = data.details.risk_level;
                riskLevel.className = 'risk-level ' + data.details.risk_level.toLowerCase();
            })
            .catch(error => {
                console.error('Error:', error);
                loading.style.display = 'none';
                resultContainer.style.display = 'block';
                resultText.textContent = 'Error: ' + error.message;
                probabilityFill.style.width = '0%';
                probabilityText.textContent = '';
                riskLevel.textContent = '';
                alert('Error: ' + error.message);
            });
        } else {
            alert('Please upload an image file');
        }
    }

    // Reset upload function
    window.resetUpload = function() {
        // Reset file input
        fileInput.value = '';
        
        // Reset preview
        previewImage.src = '#';
        
        // Hide preview and results
        previewArea.style.display = 'none';
        resultContainer.style.display = 'none';
        loading.style.display = 'none';
        
        // Show upload content
        uploadContent.style.display = 'block';
    };

    // Simulate analysis (replace with actual API call)
    function simulateAnalysis() {
        // Show loading
        loading.style.display = 'block';
        
        // Simulate API delay
        setTimeout(() => {
            loading.style.display = 'none';
            resultContainer.style.display = 'block';
            
            // Example result (replace with actual API response handling)
            const resultText = document.getElementById('result-text');
            const riskLevel = document.getElementById('risk-level');
            const probabilityFill = document.getElementById('probability-fill');
            const probabilityText = document.getElementById('probability-text');
            
            resultText.textContent = 'Potential melanoma detected';
            riskLevel.textContent = 'High Risk';
            riskLevel.className = 'risk-level high';
            probabilityFill.style.width = '75%';
            probabilityText.textContent = 'Confidence: 75%';
        }, 2000);
    }
}); 