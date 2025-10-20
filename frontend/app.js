// Ad Cloner Frontend Application

const API_BASE = window.location.origin + '/api';
let socket = null;
let currentSessionId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeWebSocket();
    checkAPIHealth();
    initializeUpload();
    updateCostEstimate(); // Initialize cost estimate
    updateAggressionLevel(); // Initialize aggression slider
    initializeInputMethods(); // Initialize input method tabs
});

// Initialize input method tabs
function initializeInputMethods() {
    // Set default active tab
    switchInputMethod('video-url');
}

// Switch between input methods
function switchInputMethod(method) {
    // Remove active class from all tabs and content
    document.querySelectorAll('.method-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.input-method-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Add active class to selected tab and content
    document.querySelector(`[data-method="${method}"]`).classList.add('active');
    document.getElementById(`${method}-input`).classList.add('active');
}

// Check API health
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        const data = await response.json();

        const statusEl = document.getElementById('api-status');
        if (data.status === 'ok' && data.openai_key_configured && data.gemini_key_configured) {
            statusEl.className = 'status-badge status-ok';
            statusEl.textContent = 'API Ready';
        } else {
            statusEl.className = 'status-badge status-error';
            statusEl.textContent = 'API Error';
        }
    } catch (error) {
        console.error('Health check failed:', error);
        document.getElementById('api-status').className = 'status-badge status-error';
        document.getElementById('api-status').textContent = 'API Offline';
    }
}

// Initialize WebSocket
function initializeWebSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('WebSocket connected');
        updateConnectionStatus(true);
    });

    socket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        updateConnectionStatus(false);
    });

    socket.on('pipeline_started', (data) => {
        console.log('Pipeline started:', data);
        showProgress();
    });

    socket.on('pipeline_completed', (data) => {
        console.log('Pipeline completed:', data);
        showResults(data.results);

        // Load detailed logs
        if (currentSessionId) {
            loadDetailedLogs(currentSessionId);
        }
    });

    socket.on('pipeline_failed', (data) => {
        console.error('Pipeline failed:', data);
        addLog('error', `Pipeline failed: ${data.error}`);
    });

    socket.on('progress_update', (data) => {
        console.log('Progress update:', data);
        updateProgress(data.progress);
    });

    socket.on('event', (data) => {
        console.log('Event:', data);
        addLog(data.event.level.toLowerCase(), data.event.message, data.event.data);
    });
}

// Update connection status
function updateConnectionStatus(connected) {
    const dot = document.getElementById('connection-dot');
    const text = document.getElementById('connection-text');
    const wsStatus = document.getElementById('ws-status');

    if (connected) {
        dot.className = 'connection-dot connected';
        text.textContent = 'Connected';
        wsStatus.className = 'status-badge status-ok';
        wsStatus.textContent = 'WebSocket Connected';
    } else {
        dot.className = 'connection-dot disconnected';
        text.textContent = 'Disconnected';
        wsStatus.className = 'status-badge status-error';
        wsStatus.textContent = 'WebSocket Disconnected';
    }
}

// Start cloning
async function startCloning() {
    // Determine which input method is active
    const activeTab = document.querySelector('.method-tab.active');
    const inputMethod = activeTab ? activeTab.dataset.method : 'video-url';
    
    let videoPath = '';
    let productScript = '';
    
    // Get input based on active method
    if (inputMethod === 'video-url') {
        videoPath = document.getElementById('video-path').value.trim();
        if (!videoPath) {
            alert('Please enter a video URL or file path');
            return;
        }
    } else if (inputMethod === 'video-upload') {
        const fileInput = document.getElementById('video-file');
        if (!fileInput.files || fileInput.files.length === 0) {
            alert('Please select a video file to upload');
            return;
        }
        // Handle file upload (existing logic)
        videoPath = await handleFileUpload();
        if (!videoPath) {
            alert('File upload failed');
            return;
        }
    } else if (inputMethod === 'script-only') {
        productScript = document.getElementById('script-only-text').value.trim();
        if (!productScript) {
            alert('Please enter your product script');
            return;
        }
        // For script-only, we'll use a placeholder video path
        videoPath = 'script-only-mode';
    }

    // Get aggression level from slider
    const aggressionSlider = document.getElementById('aggression-slider');
    const aggressionLevels = ['soft', 'medium', 'aggressive', 'ultra'];
    const aggressionLevel = aggressionLevels[parseInt(aggressionSlider.value)];

    // Get other parameters
    const outputDimension = document.getElementById('output-dimension').value;
    const soraModel = document.getElementById('sora-model').value;

    // Disable button
    const btn = document.getElementById('start-btn');
    btn.disabled = true;
    btn.textContent = 'Starting...';

    try {
        const response = await fetch(`${API_BASE}/clone`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                video_path: videoPath, 
                aggression_level: aggressionLevel,
                product_script: productScript,
                output_dimension: outputDimension,
                sora_model: soraModel,
                input_method: inputMethod
            })
        });

        const data = await response.json();
        currentSessionId = data.session_id;

        // Subscribe to session updates
        socket.emit('subscribe', { session_id: currentSessionId });

        // Show progress section
        showProgress();

        // Start polling for updates
        startPolling(currentSessionId);

    } catch (error) {
        console.error('Failed to start cloning:', error);
        alert(`Error: ${error.message}`);
        btn.disabled = false;
        btn.textContent = 'Start Cloning';
    }
}

// Show progress sections
function showProgress() {
    document.querySelectorAll('.progress-section').forEach(el => {
        el.classList.add('active');
    });

    // Initialize stages
    const stages = ['analysis', 'variants', 'prompts', 'generation', 'assembly'];
    const container = document.getElementById('stages-container');
    container.innerHTML = '';

    stages.forEach(stage => {
        const stageEl = createStageElement(stage, 'pending', 0);
        container.appendChild(stageEl);
    });
}

// Create stage element
function createStageElement(name, status, progress) {
    const div = document.createElement('div');
    div.className = `stage ${status}`;
    div.id = `stage-${name}`;

    const title = name.charAt(0).toUpperCase() + name.slice(1);
    const statusText = status.replace('_', ' ');

    div.innerHTML = `
        <div class="stage-header">
            <div class="stage-title">${getStageIcon(name)} ${title}</div>
            <div class="stage-status ${status}">${statusText}</div>
        </div>
        ${progress > 0 ? `
            <div class="progress-bar">
                <div class="progress-bar-fill" style="width: ${progress}%"></div>
            </div>
        ` : ''}
    `;

    return div;
}

// Get stage icon
function getStageIcon(stage) {
    const icons = {
        'analysis': '🔍',
        'variants': '🎨',
        'prompts': '✍️',
        'generation': '🎬',
        'assembly': '🎞️'
    };
    return icons[stage] || '•';
}

// Update progress
function updateProgress(progress) {
    // Update stages
    Object.entries(progress.stages).forEach(([name, stage]) => {
        const stageEl = document.getElementById(`stage-${name}`);
        if (stageEl) {
            stageEl.className = `stage ${stage.status.replace('_', '-')}`;

            const statusEl = stageEl.querySelector('.stage-status');
            if (statusEl) {
                statusEl.className = `stage-status ${stage.status.replace('_', '-')}`;
                statusEl.textContent = stage.status.replace('_', ' ');
            }

            // Update or add progress bar
            let progressBar = stageEl.querySelector('.progress-bar');
            if (stage.progress > 0) {
                if (!progressBar) {
                    progressBar = document.createElement('div');
                    progressBar.className = 'progress-bar';
                    progressBar.innerHTML = '<div class="progress-bar-fill"></div>';
                    stageEl.appendChild(progressBar);
                }
                const fill = progressBar.querySelector('.progress-bar-fill');
                fill.style.width = `${stage.progress}%`;
            }
        }
    });

    // Update variants
    if (progress.variants && Object.keys(progress.variants).length > 0) {
        updateVariants(progress.variants);
    }
}

// Update variants display
function updateVariants(variants) {
    const grid = document.getElementById('variants-grid');
    grid.innerHTML = '';

    Object.entries(variants).forEach(([name, variant]) => {
        const card = document.createElement('div');
        card.className = `variant-card ${variant.status}`;

        const completedScenes = Object.values(variant.scenes || {}).filter(s => s.status === 'completed').length;
        const totalScenes = Object.keys(variant.scenes || {}).length;

        card.innerHTML = `
            <div class="variant-name">${name}</div>
            <div class="variant-progress">
                ${variant.status}<br>
                ${completedScenes}/${totalScenes} scenes
            </div>
        `;

        grid.appendChild(card);
    });
}

// Add log entry
function addLog(level, message, data) {
    const container = document.getElementById('log-container');
    const entry = document.createElement('div');
    entry.className = `log-entry ${level}`;

    const timestamp = new Date().toLocaleTimeString();

    let content = `<span class="log-timestamp">[${timestamp}]</span> ${message}`;
    if (data && Object.keys(data).length > 0) {
        content += `\n${JSON.stringify(data, null, 2)}`;
    }

    entry.innerHTML = content;
    container.appendChild(entry);
    container.scrollTop = container.scrollHeight;
}

// Poll for updates
let pollInterval = null;

function startPolling(sessionId) {
    if (pollInterval) clearInterval(pollInterval);

    pollInterval = setInterval(async () => {
        try {
            const response = await fetch(`${API_BASE}/sessions/${sessionId}`);
            const data = await response.json();

            if (data.progress) {
                updateProgress(data.progress);

                // Add recent events to logs
                if (data.events && data.events.length > 0) {
                    data.events.slice(-10).forEach(event => {
                        if (!document.querySelector(`[data-event-time="${event.timestamp}"]`)) {
                            addLog(event.level.toLowerCase(), event.message, event.data);
                            document.querySelector('#log-container').lastChild.setAttribute('data-event-time', event.timestamp);
                        }
                    });
                }

                // Check if completed
                if (data.progress.status === 'completed') {
                    clearInterval(pollInterval);
                    showResults(data.progress.final_results);
                } else if (data.progress.status === 'failed') {
                    clearInterval(pollInterval);
                    addLog('error', 'Pipeline failed');
                }
            }
        } catch (error) {
            console.error('Polling error:', error);
        }
    }, 2000); // Poll every 2 seconds
}

// Show results
async function showResults(results) {
    const section = document.getElementById('results-section');
    const content = document.getElementById('results-content');

    section.classList.add('active');

    const elapsed = results.elapsed_time;
    const minutes = Math.floor(elapsed / 60);
    const seconds = Math.floor(elapsed % 60);

    // Fetch generated videos from cloud
    let generatedVideos = [];
    let finalVideos = [];

    if (currentSessionId) {
        try {
            const response = await fetch(`${API_BASE}/sessions/${currentSessionId}/generated-videos`);
            if (response.ok) {
                const data = await response.json();
                generatedVideos = data.generated_videos || [];
                finalVideos = data.final_videos || [];
            }
        } catch (error) {
            console.error('Failed to fetch generated videos:', error);
        }
    }

    content.innerHTML = `
            <div style="margin-bottom: 20px;">
                <p><strong>Status:</strong> ✅ Complete</p>
                <p><strong>Time Elapsed:</strong> ${minutes}m ${seconds}s</p>
                <p><strong>Scene 1 Generated:</strong> ${results.hook_result?.level || 'Unknown'} intensity</p>
            </div>

        ${generatedVideos.length > 0 ? `
            <h3 style="margin-top: 30px; margin-bottom: 15px;">📹 Generated Scene Videos (${generatedVideos.length})</h3>
            <div class="video-grid">
                ${generatedVideos.map(video => `
                    <div class="video-card">
                        <h3>${video.filename}</h3>
                        <div class="video-preview">
                            <video controls width="100%" style="max-height: 200px;">
                                <source src="${video.url}" type="video/mp4">
                            </video>
                        </div>
                        <div class="video-info">
                            ${video.size_mb} MB
                        </div>
                        <a href="${video.url}" download="${video.filename}" class="btn" style="margin-top: 10px; display: block; text-decoration: none; padding: 10px;">
                            ⬇️ Download
                        </a>
                    </div>
                `).join('')}
            </div>
        ` : ''}

            ${results.hook_result?.success ? `
                <h3 style="margin-top: 30px; margin-bottom: 15px;">🎬 Generated Scene 1</h3>
                <div class="video-grid">
                    <div class="video-card">
                        <h3>${results.hook_result.level} Intensity Scene 1</h3>
                        <div class="video-preview">
                            <video controls width="100%">
                                <source src="${results.hook_result.path}" type="video/mp4">
                            </video>
                        </div>
                        <div class="video-info">
                            Enhanced Scene 1 ready!
                        </div>
                        <a href="${results.hook_result.path}" download="scene1_${results.hook_result.level}.mp4" class="btn" style="margin-top: 10px; display: block; text-decoration: none; padding: 10px;">
                            ⬇️ Download Scene 1
                        </a>
                    </div>
                </div>
            ` : ''}

        ${generatedVideos.length === 0 && finalVideos.length === 0 ? `
            <div style="margin-top: 30px; padding: 20px; background: #f9fafb; border-radius: 8px; text-align: center;">
                <p>No videos found in cloud storage. Videos are saved locally.</p>
                ${results.final_ads ? `
                    <h3 style="margin-top: 20px; margin-bottom: 15px;">Local Videos</h3>
                    <div class="video-grid">
                        ${Object.entries(results.final_ads).map(([variant, path]) => `
                            <div class="video-card">
                                <h3>${variant} Variant</h3>
                                <div class="video-info">
                                    <code>${path}</code>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        ` : ''}

        <div style="margin-top: 30px;">
            <button class="btn" onclick="location.reload()">Clone Another Ad</button>
        </div>
    `;

    // Scroll to results
    section.scrollIntoView({ behavior: 'smooth' });
}

// Initialize upload functionality
function initializeUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('video-file');
    const videoPathInput = document.getElementById('video-path');

    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // File selected via input
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            uploadFile(file);
        }
    });

    // Drag and drop
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
        if (file) {
            uploadFile(file);
        }
    });
}

// Upload file to server
async function uploadFile(file) {
    const uploadArea = document.getElementById('upload-area');
    const uploadContent = uploadArea.querySelector('.upload-content');
    const uploadProgress = document.getElementById('upload-progress');
    const progressFill = document.getElementById('upload-progress-fill');
    const progressText = document.getElementById('upload-progress-text');

    // Check file type
    const validTypes = ['video/mp4', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/webm'];
    if (!validTypes.includes(file.type)) {
        alert('Invalid file type. Please upload a video file (MP4, MOV, AVI, MKV, WEBM)');
        return;
    }

    // Check file size (500MB)
    const maxSize = 500 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File too large. Maximum size is 500MB');
        return;
    }

    // Show progress
    uploadArea.classList.add('uploading');
    uploadContent.style.display = 'none';
    uploadProgress.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = 'Uploading...';

    try {
        const formData = new FormData();
        formData.append('video', file);

        // Create XHR for progress tracking
        const xhr = new XMLHttpRequest();

        // Track upload progress
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressFill.style.width = percentComplete + '%';
                progressText.textContent = `Uploading... ${Math.round(percentComplete)}%`;
            }
        });

        // Handle completion
        xhr.addEventListener('load', () => {
            if (xhr.status === 200) {
                const response = JSON.parse(xhr.responseText);

                // Set video path
                document.getElementById('video-path').value = response.path;

                // Show success
                progressText.textContent = `✓ Uploaded: ${response.filename} (${response.size_mb}MB)`;
                progressFill.style.width = '100%';

                addLog('success', `File uploaded: ${response.filename}`, {
                    size_mb: response.size_mb,
                    path: response.path
                });

                // Reset after 2 seconds
                setTimeout(() => {
                    uploadArea.classList.remove('uploading');
                    uploadContent.style.display = 'block';
                    uploadProgress.style.display = 'none';
                }, 2000);
            } else {
                throw new Error('Upload failed');
            }
        });

        // Handle error
        xhr.addEventListener('error', () => {
            throw new Error('Upload failed');
        });

        // Send request
        xhr.open('POST', `${API_BASE}/upload`);
        xhr.send(formData);

    } catch (error) {
        console.error('Upload error:', error);
        alert(`Upload failed: ${error.message}`);

        // Reset UI
        uploadArea.classList.remove('uploading');
        uploadContent.style.display = 'block';
        uploadProgress.style.display = 'none';
    }
}

// Cost estimation
function updateCostEstimate() {
    // Get selected Sora model
    const soraModelSelect = document.getElementById('sora-model');
    const selectedModel = soraModelSelect ? soraModelSelect.value : 'sora-2';
    
    // Pricing based on model selection
    const SORA_2_COST_PER_SECOND = 0.064;
    const SORA_2_PRO_COST_PER_SECOND = 0.08;
    
    const costPerSecond = selectedModel === 'sora-2-pro' ? SORA_2_PRO_COST_PER_SECOND : SORA_2_COST_PER_SECOND;
    const SECONDS_PER_SCENE = 12;
    const SCENES_GENERATED = 1; // Single Scene 1 only

    // Calculate cost for single Scene 1
    const totalSeconds = SCENES_GENERATED * SECONDS_PER_SCENE;
    const totalCost = totalSeconds * costPerSecond;

    // Update UI
    const costAmount = document.getElementById('cost-amount');
    const costDetails = document.getElementById('cost-details');
    const costNote = document.getElementById('cost-note');

    costAmount.textContent = `$${totalCost.toFixed(2)}`;
    costDetails.textContent = `1 Scene 1 × ${SECONDS_PER_SCENE}s × $${costPerSecond}/s = $${totalCost.toFixed(2)}`;
    
    // Update cost note based on model
    if (costNote) {
        if (selectedModel === 'sora-2-pro') {
            costNote.textContent = 'Using Sora 2 Pro • Higher quality and consistency';
        } else {
            costNote.textContent = 'Using Sora 2 (regular) • 80% cheaper than Pro';
        }
    }
    
    // Show cost optimization if using Sora 2 Pro
    const costOptimization = document.getElementById('cost-optimization');
    const optimizationText = document.getElementById('optimization-text');
    
    if (selectedModel === 'sora-2-pro' && costOptimization && optimizationText) {
        const savings = (SORA_2_PRO_COST_PER_SECOND - SORA_2_COST_PER_SECOND) * totalSeconds;
        optimizationText.textContent = `Save $${savings.toFixed(2)} by using Sora 2 for simple scenes`;
        costOptimization.style.display = 'block';
    } else if (costOptimization) {
        costOptimization.style.display = 'none';
    }
}

// Update aggression level display
function updateAggressionLevel() {
    const slider = document.getElementById('aggression-slider');
    const valueDisplay = document.getElementById('aggression-value');
    const description = document.getElementById('aggression-desc');
    
    const levels = ['Soft', 'Medium', 'Aggressive', 'Ultra'];
    const descriptions = [
        'Gentle persuasion with subtle emotional appeal',
        'Balanced approach with proven viral potential',
        'High energy with strong emotional impact',
        'Maximum intensity for explosive viral potential'
    ];
    
    const levelIndex = parseInt(slider.value);
    valueDisplay.textContent = levels[levelIndex];
    description.textContent = descriptions[levelIndex];
}

// Toggle detailed logs panel
function toggleDetailedLogs() {
    const content = document.getElementById('detailed-logs-content');
    const button = document.getElementById('detailed-logs-toggle');

    if (content.style.display === 'none') {
        content.style.display = 'block';
        button.textContent = 'Hide Details ▲';
    } else {
        content.style.display = 'none';
        button.textContent = 'Show Details ▼';
    }
}

// Toggle individual detail sections
function toggleSection(sectionId) {
    const content = document.getElementById(sectionId);
    const header = content.previousElementSibling;

    if (content.classList.contains('collapsed')) {
        content.classList.remove('collapsed');
        header.classList.remove('collapsed');
    } else {
        content.classList.add('collapsed');
        header.classList.add('collapsed');
    }
}

// Update detailed logs with real data
function updateDetailedLogs(data) {
    // Update analysis section
    if (data.analysis) {
        const analysisEl = document.getElementById('analysis-data');
        analysisEl.textContent = JSON.stringify(data.analysis, null, 2);
    }

    // Update transformation section
    if (data.transformation) {
        const transformEl = document.getElementById('transform-data');
        let transformText = `Detected Vertical: ${data.transformation.vertical_name}\n\n`;
        transformText += `Scene Structure:\n`;
        transformText += `- Character scenes: ${data.transformation.character_scenes}\n`;
        transformText += `- B-roll scenes: ${data.transformation.broll_scenes}\n\n`;
        transformText += `Transformed Scenes:\n`;
        transformText += JSON.stringify(data.transformation.scenes, null, 2);
        transformEl.textContent = transformText;
    }

    // Update prompts section
    if (data.prompts) {
        const promptsEl = document.getElementById('prompts-data');
        let promptsText = '';

        Object.entries(data.prompts).forEach(([variant, scenes]) => {
            promptsText += `\n${'='.repeat(70)}\n`;
            promptsText += `VARIANT: ${variant.toUpperCase()}\n`;
            promptsText += `${'='.repeat(70)}\n\n`;

            scenes.forEach((scene, idx) => {
                promptsText += `\n--- Scene ${idx + 1} ---\n`;
                promptsText += `Timestamp: ${scene.timestamp}\n`;
                promptsText += `Purpose: ${scene.purpose}\n\n`;
                promptsText += `FULL PROMPT:\n`;
                promptsText += scene.prompt;
                promptsText += `\n\n`;
            });
        });

        promptsEl.textContent = promptsText;
    }

    // Update evaluation section
    if (data.evaluation) {
        const evalEl = document.getElementById('eval-data');
        const eval = data.evaluation;

        let evalText = `OVERALL SCORE: ${eval.ratings?.overall_score?.toFixed(1) || 'N/A'}/10\n`;
        evalText += `PREDICTION: ${eval.ratings?.predicted_performance || 'N/A'}\n\n`;
        evalText += `RATINGS:\n`;
        evalText += `- Visual Quality: ${eval.ratings?.visual_quality?.toFixed(1) || 'N/A'}/10\n`;
        evalText += `- Message Clarity: ${eval.ratings?.message_clarity?.toFixed(1) || 'N/A'}/10\n`;
        evalText += `- Pacing: ${eval.ratings?.pacing?.toFixed(1) || 'N/A'}/10\n`;
        evalText += `- Storytelling: ${eval.ratings?.storytelling?.toFixed(1) || 'N/A'}/10\n\n`;

        if (eval.comparison) {
            evalText += `COMPARISON:\n`;
            evalText += `- Original Vertical: ${eval.comparison.original_vertical}\n`;
            evalText += `- Generated Vertical: ${eval.comparison.generated_vertical}\n`;
            evalText += `- Vertical Match: ${eval.comparison.vertical_match ? '✓ YES' : '✗ NO'}\n`;
            evalText += `- Scene Count: ${eval.comparison.original_scenes} → ${eval.comparison.generated_scenes}\n\n`;
        }

        if (eval.recommendations && eval.recommendations.length > 0) {
            evalText += `RECOMMENDATIONS:\n`;
            eval.recommendations.forEach((rec, idx) => {
                evalText += `\n${idx + 1}. [${rec.severity}] ${rec.issue}\n`;
                evalText += `   Details: ${rec.details}\n`;
                evalText += `   Fix: ${rec.fix}\n`;
            });
        }

        evalEl.textContent = evalText;
    }
}

// Fetch detailed logs from session
async function loadDetailedLogs(sessionId) {
    try {
        const response = await fetch(`${API_BASE}/sessions/${sessionId}/detailed`);
        if (response.ok) {
            const data = await response.json();
            updateDetailedLogs(data);
        }
    } catch (error) {
        console.error('Failed to load detailed logs:', error);
    }
}

// Library View Functions
let currentFilter = 'all';
let allGenerations = [];

// Initialize navigation
document.addEventListener('DOMContentLoaded', () => {
    // Attach nav item click handlers
    document.querySelectorAll('.nav-item').forEach((item, index) => {
        item.addEventListener('click', (e) => {
            e.preventDefault();

            // Update active state
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');

            // Switch views based on index
            const views = ['generate-view', 'analytics-view', 'library-view', 'settings-view'];
            const viewName = views[index];

            // Hide all views
            document.querySelectorAll('.view-container').forEach(v => v.style.display = 'none');

            // Show selected view
            const selectedView = document.getElementById(viewName);
            if (selectedView) {
                selectedView.style.display = 'block';

                // Load library data if switching to library view
                if (viewName === 'library-view') {
                    loadLibrary();
                }
            }
        });
    });

    // Attach filter button handlers
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Apply filter
            currentFilter = btn.dataset.filter;
            renderLibrary();
        });
    });
});

// Load library from API
async function loadLibrary() {
    const grid = document.getElementById('library-grid');
    grid.innerHTML = '<div class="loading-spinner">Loading generations...</div>';

    try {
        const response = await fetch(`${API_BASE}/history/generations?limit=50`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();
        allGenerations = data.generations || [];

        renderLibrary();

    } catch (error) {
        console.error('Failed to load library:', error);
        grid.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #6b7280;">
                <p style="font-size: 18px; margin-bottom: 10px;">⚠️ Failed to load generation history</p>
                <p style="font-size: 14px;">${error.message}</p>
                <button class="btn" onclick="loadLibrary()" style="margin-top: 20px;">Retry</button>
            </div>
        `;
    }
}

// Render library with current filter
function renderLibrary() {
    const grid = document.getElementById('library-grid');

    // Filter generations
    let filtered = allGenerations;
    if (currentFilter !== 'all') {
        filtered = allGenerations.filter(g => g.status === currentFilter);
    }

    // Sort by created_at descending (newest first)
    filtered.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));

    if (filtered.length === 0) {
        grid.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #6b7280;">
                <p style="font-size: 18px;">No ${currentFilter === 'all' ? '' : currentFilter} generations found</p>
            </div>
        `;
        return;
    }

    // Render generation cards
    grid.innerHTML = filtered.map(gen => renderGenerationCard(gen)).join('');
}

// Render individual generation card
function renderGenerationCard(gen) {
    const createdDate = new Date(gen.created_at);
    const timeAgo = getTimeAgo(createdDate);

    // Get status badge
    const statusBadges = {
        'completed': '<span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">✓ Completed</span>',
        'processing': '<span style="background: #3b82f6; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">⏳ Processing</span>',
        'failed': '<span style="background: #ef4444; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">✗ Failed</span>',
        'pending': '<span style="background: #6b7280; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">⏸ Pending</span>'
    };

    const statusBadge = statusBadges[gen.status] || statusBadges['pending'];

    // Count completed variants and scenes
    const completedVariants = gen.variants?.filter(v => v.status === 'completed').length || 0;
    const totalVariants = gen.variants?.length || 0;

    const completedScenes = gen.variants?.reduce((sum, v) =>
        sum + (v.scenes?.filter(s => s.status === 'completed').length || 0), 0) || 0;
    const totalScenes = gen.variants?.reduce((sum, v) =>
        sum + (v.scenes?.length || 0), 0) || 0;

    // Get first available video thumbnail
    let thumbnailUrl = null;
    if (gen.variants) {
        for (const variant of gen.variants) {
            if (variant.scenes && variant.scenes.length > 0) {
                const scene = variant.scenes.find(s => s.thumbnail_url);
                if (scene) {
                    thumbnailUrl = scene.thumbnail_url;
                    break;
                }
            }
        }
    }

    return `
        <div class="generation-card" style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; transition: all 0.2s;">
            <div class="generation-thumbnail" style="aspect-ratio: 16/9; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); position: relative; overflow: hidden;">
                ${thumbnailUrl ? `
                    <img src="${thumbnailUrl}" alt="Thumbnail" style="width: 100%; height: 100%; object-fit: cover;">
                ` : `
                    <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: white; font-size: 48px;">
                        🎬
                    </div>
                `}
                <div style="position: absolute; top: 12px; right: 12px;">
                    ${statusBadge}
                </div>
            </div>

            <div style="padding: 16px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                    <div>
                        <div style="font-size: 14px; font-weight: 600; color: #111827; margin-bottom: 4px;">
                            Generation ${gen.id.substring(0, 8)}
                        </div>
                        <div style="font-size: 12px; color: #6b7280;">
                            ${timeAgo}
                        </div>
                    </div>
                </div>

                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 12px; padding: 12px; background: #f9fafb; border-radius: 8px;">
                    <div>
                        <div style="font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Variants</div>
                        <div style="font-size: 16px; font-weight: 600; color: #111827;">${completedVariants}/${totalVariants}</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #6b7280; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Scenes</div>
                        <div style="font-size: 16px; font-weight: 600; color: #111827;">${completedScenes}/${totalScenes}</div>
                    </div>
                </div>

                ${gen.status === 'completed' && gen.actual_cost ? `
                    <div style="font-size: 12px; color: #6b7280; margin-bottom: 12px;">
                        Cost: <span style="font-weight: 600; color: #111827;">$${gen.actual_cost.toFixed(2)}</span>
                    </div>
                ` : ''}

                ${gen.variants && gen.variants.length > 0 ? `
                    <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                        ${gen.variants.map(v => `
                            <span style="padding: 4px 8px; background: #f3f4f6; border-radius: 6px; font-size: 11px; color: #6b7280; font-weight: 500;">
                                ${v.variant_type}
                            </span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        </div>
    `;
}

// Get human-readable time ago
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    if (seconds < 60) return 'Just now';

    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;

    const days = Math.floor(hours / 24);
    if (days < 7) return `${days}d ago`;

    const weeks = Math.floor(days / 7);
    if (weeks < 4) return `${weeks}w ago`;

    return date.toLocaleDateString();
}

// Export functions
window.startCloning = startCloning;
window.uploadFile = uploadFile;
window.updateCostEstimate = updateCostEstimate;
window.updateAggressionLevel = updateAggressionLevel;
window.toggleDetailedLogs = toggleDetailedLogs;
window.toggleSection = toggleSection;
window.loadLibrary = loadLibrary;
