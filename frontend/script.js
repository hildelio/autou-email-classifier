/**
 * Frontend JavaScript - Autou Email Classifier
 */

const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const loading = document.getElementById('loading');
const result = document.getElementById('result');

// Event listeners para drag and drop
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-indigo-500', 'bg-indigo-50');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-indigo-500', 'bg-indigo-50');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-indigo-500', 'bg-indigo-50');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

/**
 * Handle file upload
 * @param {File} file - The file to upload
 */
async function handleFileUpload(file) {
    // Validate file type
    const validTypes = ['application/pdf', 'text/plain'];
    if (!validTypes.includes(file.type)) {
        alert('Por favor, envie um arquivo PDF ou TXT');
        return;
    }

    // Show loading state
    loading.classList.remove('hidden');
    result.classList.add('hidden');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Erro ao processar o arquivo');
        }

        const data = await response.json();
        displayResult(data);
    } catch (error) {
        console.error('Error:', error);
        alert('Erro ao processar arquivo: ' + error.message);
    } finally {
        loading.classList.add('hidden');
    }
}

/**
 * Display result
 * @param {Object} data - Result data
 */
function displayResult(data) {
    document.getElementById('resultCategory').textContent = data.category || 'N/A';
    document.getElementById('resultReply').textContent = data.reply || 'N/A';
    result.classList.remove('hidden');
}

/**
 * Reset form
 */
function resetForm() {
    fileInput.value = '';
    result.classList.add('hidden');
}
