/**
 * AutoU Email Classifier - Frontend JavaScript
 * Client-side logic for email classification interface
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';
const MAX_FILE_SIZE_MB = 5;
const MAX_TEXT_LENGTH = 1000000;

// State management
let currentFile = null;
let lastResult = null;

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileName = document.getElementById('fileName');
const fileNameText = document.getElementById('fileNameText');
const emailText = document.getElementById('emailText');
const charCount = document.getElementById('charCount');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultsContainer = document.getElementById('resultsContainer');
const successResult = document.getElementById('successResult');
const errorResult = document.getElementById('errorResult');
const rateLimitInfo = document.getElementById('rateLimitInfo');
const rateLimitText = document.getElementById('rateLimitText');

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const tabName = e.currentTarget.dataset.tab;

        // Update buttons
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// File upload handling
dropZone.addEventListener('click', () => fileInput.click());

fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        handleFileSelection(file);
    }
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('border-blue-500', 'bg-blue-100');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('border-blue-500', 'bg-blue-100');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('border-blue-500', 'bg-blue-100');

    const file = e.dataTransfer.files[0];
    if (file) {
        handleFileSelection(file);
    }
});

/**
 * Handle file selection and validation
 */
function handleFileSelection(file) {
    // Validate file type
    const validTypes = ['application/pdf', 'text/plain'];
    if (!validTypes.includes(file.type)) {
        showError('Tipo de arquivo inválido. Use PDF ou TXT.');
        return;
    }

    // Validate file size
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > MAX_FILE_SIZE_MB) {
        showError(`Arquivo muito grande. Máximo ${MAX_FILE_SIZE_MB}MB. Recebido: ${fileSizeMB.toFixed(2)}MB`);
        return;
    }

    currentFile = file;
    fileName.classList.remove('hidden');
    fileNameText.textContent = `✓ ${file.name} (${fileSizeMB.toFixed(2)}MB)`;
}

/**
 * Update character count for textarea
 */
emailText.addEventListener('input', (e) => {
    charCount.textContent = e.target.value.length;
    currentFile = null;
    fileName.classList.add('hidden');
});

/**
 * Analyze email
 */
analyzeBtn.addEventListener('click', analyzeEmail);

async function analyzeEmail() {
    // Validate input
    const activeTab = document.querySelector('.tab-content.active');
    const isUploadTab = activeTab.id === 'upload-tab';

    let content = null;
    let filename = null;

    if (isUploadTab) {
        if (!currentFile) {
            showError('Por favor, selecione um arquivo.');
            return;
        }
        content = currentFile;
        filename = currentFile.name;
    } else {
        const text = emailText.value.trim();
        if (!text) {
            showError('Por favor, cole o conteúdo do email.');
            return;
        }
        if (text.length > MAX_TEXT_LENGTH) {
            showError(`Texto muito longo. Máximo ${MAX_TEXT_LENGTH} caracteres.`);
            return;
        }
        content = text;
    }

    // Disable button and show loading state
    setLoadingState(true);

    try {
        const response = await submitAnalysis(content, isUploadTab);

        // Display results
        displayResults(response.data);

        // Update rate limit info if available
        const headers = response.headers;
        if (headers['x-ratelimit-limit-5min']) {
            updateRateLimitInfo(headers);
        }
    } catch (error) {
        handleError(error);
    } finally {
        setLoadingState(false);
    }
}

/**
 * Submit analysis to backend
 */
async function submitAnalysis(content, isFile) {
    const formData = new FormData();

    if (isFile) {
        formData.append('file', content);
    } else {
        // For text input, we need to create a temporary text file
        const blob = new Blob([content], { type: 'text/plain' });
        const file = new File([blob], 'email.txt', { type: 'text/plain' });
        formData.append('file', file);
    }

    try {
        const response = await axios.post(`${API_BASE_URL}/analyze`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            timeout: 30000, // 30 seconds
        });

        return response;
    } catch (error) {
        if (error.response) {
            // Server responded with error
            throw {
                message: error.response.data.detail || 'Erro ao processar análise',
                status: error.response.status,
            };
        } else if (error.request) {
            // Request made but no response
            throw {
                message: 'Servidor não respondeu. Verifique sua conexão.',
                status: 0,
            };
        } else {
            throw {
                message: error.message || 'Erro ao enviar requisição',
                status: 0,
            };
        }
    }
}

/**
 * Display analysis results
 */
function displayResults(data) {
    lastResult = data;

    // Hide error, show success
    errorResult.classList.add('hidden');
    successResult.classList.remove('hidden');

    // Populate results
    document.getElementById('resultCategory').textContent = capitalizeCategory(data.category);

    // Confidence bar and percentage
    const confidence = Math.round(data.confidence * 100);
    document.getElementById('confidenceFill').style.width = `${confidence}%`;
    document.getElementById('resultConfidence').textContent = `${confidence}% confiança`;

    // Suggested reply
    document.getElementById('resultReply').textContent = data.suggested_reply;

    // Reasoning
    document.getElementById('resultReasoning').textContent = data.reasoning;

    // Show results container
    resultsContainer.classList.remove('hidden');

    // Scroll to results
    setTimeout(() => {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

/**
 * Handle errors
 */
function handleError(error) {
    successResult.classList.add('hidden');
    errorResult.classList.remove('hidden');

    let message = error.message || 'Erro desconhecido';

    // Rate limit errors
    if (error.status === 429) {
        message = 'Muitas requisições. Por favor, aguarde alguns minutos.';
    }
    // File size errors
    else if (error.status === 413) {
        message = 'Arquivo muito grande. Máximo 5MB.';
    }
    // Bad request
    else if (error.status === 400) {
        message = error.message;
    }
    // Server error
    else if (error.status === 500) {
        message = 'Erro no servidor. Tente novamente.';
    }

    document.getElementById('errorMessage').textContent = message;
    resultsContainer.classList.remove('hidden');

    setTimeout(() => {
        resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 100);
}

/**
 * Show error message (quick validation)
 */
function showError(message) {
    handleError({ message, status: 400 });
}

/**
 * Update rate limit information
 */
function updateRateLimitInfo(headers) {
    const limit5min = headers['x-ratelimit-limit-5min'];
    const remaining5min = headers['x-ratelimit-remaining-5min'];
    const limit24h = headers['x-ratelimit-limit-24h'];
    const remaining24h = headers['x-ratelimit-remaining-24h'];

    if (remaining5min && remaining24h) {
        rateLimitText.textContent = `Requisições: ${remaining5min}/${limit5min} (5 min) | ${remaining24h}/${limit24h} (24h)`;
        rateLimitInfo.classList.remove('hidden');

        // Hide after 10 seconds
        setTimeout(() => {
            rateLimitInfo.classList.add('hidden');
        }, 10000);
    }
}

/**
 * Set loading state
 */
function setLoadingState(isLoading) {
    analyzeBtn.disabled = isLoading;
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');

    if (isLoading) {
        btnText.textContent = 'Analisando...';
        btnSpinner.classList.remove('hidden');
    } else {
        btnText.textContent = '🔍 Analisar Email';
        btnSpinner.classList.add('hidden');
    }
}

/**
 * Reset form to initial state
 */
function resetForm() {
    // Clear inputs
    currentFile = null;
    fileInput.value = '';
    emailText.value = '';
    charCount.textContent = '0';

    // Reset UI
    fileName.classList.add('hidden');
    resultsContainer.classList.add('hidden');
    successResult.classList.add('hidden');
    errorResult.classList.add('hidden');
    rateLimitInfo.classList.add('hidden');

    // Switch to upload tab
    document.querySelectorAll('.tab-btn')[0].click();

    // Focus on drop zone
    dropZone.focus();
}

/**
 * Copy result to clipboard
 */
async function copyResult() {
    if (!lastResult) return;

    const text = `
CLASSIFICAÇÃO DE EMAIL
======================

Categoria: ${capitalizeCategory(lastResult.category)}
Confiança: ${Math.round(lastResult.confidence * 100)}%

Resposta Sugerida:
${lastResult.suggested_reply}

Análise:
${lastResult.reasoning}
    `.trim();

    try {
        await navigator.clipboard.writeText(text);

        // Show feedback
        const btn = event.target;
        const originalText = btn.textContent;
        btn.textContent = '✓ Copiado!';

        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    } catch (error) {
        console.error('Erro ao copiar:', error);
        alert('Erro ao copiar resultado');
    }
}

/**
 * Capitalize category name
 */
function capitalizeCategory(category) {
    return category
        .split('_')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1))
        .join(' ');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('AutoU Email Classifier - Frontend iniciado');
    console.log('API Base URL:', API_BASE_URL);
});
