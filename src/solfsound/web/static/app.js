// SolfSound Dispatcher Web Interface
const API_URL = 'http://localhost:8000';

let uploadedFile = null;
let currentAction = null;
let jobId = null;

// DOM Elements
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const actionsSection = document.getElementById('actionsSection');
const optionsSection = document.getElementById('optionsSection');
const optionsContainer = document.getElementById('optionsContainer');
const processBtn = document.getElementById('processBtn');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');

// Upload Zone Events
uploadZone.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
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

// Action Button Events
document.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.action-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentAction = btn.dataset.action;
        showOptions(currentAction);
    });
});

// Process Button Event
processBtn.addEventListener('click', () => {
    if (currentAction && uploadedFile) {
        processAction();
    }
});

// Functions
async function handleFileUpload(file) {
    const formData = new FormData();
    formData.append('file', file);

    try {
        showProgress('Téléchargement du fichier...', 0);

        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.status === 'success') {
            uploadedFile = data;
            showFileInfo(file, data);
            actionsSection.style.display = 'block';
            hideProgress();
        }
    } catch (error) {
        alert('Erreur lors du téléchargement: ' + error.message);
        hideProgress();
    }
}

function showFileInfo(file, uploadData) {
    const sizeInMB = (uploadData.size / 1024 / 1024).toFixed(2);
    fileInfo.innerHTML = `
        <strong>✅ Fichier téléchargé:</strong> ${file.name} (${sizeInMB} MB)
    `;
    fileInfo.classList.remove('hidden');
}

function showOptions(action) {
    optionsSection.style.display = 'block';
    optionsContainer.innerHTML = '';

    switch(action) {
        case 'extract':
            optionsContainer.innerHTML = `
                <div class="form-group">
                    <label>Format de sortie</label>
                    <select id="extractFormat">
                        <option value="wav">WAV (Haute qualité)</option>
                        <option value="mp3">MP3</option>
                        <option value="flac">FLAC</option>
                        <option value="ogg">OGG</option>
                        <option value="aac">AAC</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Bitrate</label>
                    <select id="bitrate">
                        <option value="320k">320 kbps (Très haute)</option>
                        <option value="256k">256 kbps (Haute)</option>
                        <option value="192k">192 kbps (Moyenne)</option>
                        <option value="128k">128 kbps (Standard)</option>
                    </select>
                </div>
            `;
            break;

        case 'separate':
            optionsContainer.innerHTML = `
                <div class="form-group">
                    <label>Modèle de séparation</label>
                    <select id="separateModel">
                        <option value="htdemucs">HTDemucs (Rapide, Haute qualité)</option>
                        <option value="htdemucs_ft">HTDemucs Fine-Tuned (Meilleure qualité)</option>
                        <option value="htdemucs_6s">HTDemucs 6-stems (6 pistes)</option>
                        <option value="mdx_extra">MDX Extra (Qualité maximale, plus lent)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Stems à extraire</label>
                    <div class="checkbox-group">
                        <label class="checkbox-label">
                            <input type="checkbox" name="stems" value="vocals" checked>
                            🎤 Voix
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="stems" value="drums" checked>
                            🥁 Batterie
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="stems" value="bass" checked>
                            🎸 Basse
                        </label>
                        <label class="checkbox-label">
                            <input type="checkbox" name="stems" value="other" checked>
                            🎹 Autres
                        </label>
                    </div>
                </div>
                <div class="form-group">
                    <label>Qualité (shifts: plus élevé = meilleure qualité mais plus lent)</label>
                    <select id="shifts">
                        <option value="1">1 (Rapide)</option>
                        <option value="3">3 (Équilibré)</option>
                        <option value="5">5 (Haute qualité)</option>
                        <option value="10">10 (Qualité maximale)</option>
                    </select>
                </div>
            `;
            break;

        case 'analyze':
            optionsContainer.innerHTML = `
                <p style="color: var(--text-secondary);">
                    L'analyse fournira des informations détaillées sur la composition audio:
                    tempo, nombre de couches sonores, ratios harmoniques, etc.
                </p>
            `;
            break;

        case 'process':
            optionsContainer.innerHTML = `
                <div class="form-group">
                    <label>Modèle de séparation</label>
                    <select id="processModel">
                        <option value="htdemucs">HTDemucs (Rapide)</option>
                        <option value="htdemucs_ft">HTDemucs Fine-Tuned (Recommandé)</option>
                        <option value="htdemucs_6s">HTDemucs 6-stems</option>
                    </select>
                </div>
                <p style="color: var(--text-secondary); margin-top: 10px;">
                    Le pipeline complet effectuera: Extraction → Séparation → Analyse
                </p>
            `;
            break;
    }
}

async function processAction() {
    showProgress('Initialisation...', 0);
    resultsSection.style.display = 'none';

    try {
        let response;

        switch(currentAction) {
            case 'extract':
                response = await extractAudio();
                break;
            case 'separate':
                response = await separateAudio();
                break;
            case 'analyze':
                response = await analyzeAudio();
                break;
            case 'process':
                response = await processComplete();
                break;
        }

        if (response) {
            displayResults(response);
        }
    } catch (error) {
        alert('Erreur: ' + error.message);
        hideProgress();
    }
}

async function extractAudio() {
    const format = document.getElementById('extractFormat').value;
    const bitrate = document.getElementById('bitrate').value;

    showProgress('Extraction de l\'audio...', 50);

    const response = await fetch(`${API_URL}/extract`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            filepath: uploadedFile.filepath,
            output_format: format,
            bitrate: bitrate
        })
    });

    const data = await response.json();
    hideProgress();
    return data;
}

async function separateAudio() {
    const model = document.getElementById('separateModel').value;
    const shifts = parseInt(document.getElementById('shifts').value);
    const selectedStems = Array.from(document.querySelectorAll('input[name="stems"]:checked'))
        .map(cb => cb.value);

    const response = await fetch(`${API_URL}/separate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            audio_file: uploadedFile.filepath,
            model: model,
            stems: selectedStems.length > 0 ? selectedStems : null,
            output_format: 'wav',
            shifts: shifts
        })
    });

    const data = await response.json();

    if (data.job_id) {
        return await pollJobStatus(data.job_id);
    }
}

async function analyzeAudio() {
    showProgress('Analyse en cours...', 50);

    const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            filepath: uploadedFile.filepath
        })
    });

    const data = await response.json();
    hideProgress();
    return data;
}

async function processComplete() {
    const model = document.getElementById('processModel').value;

    const response = await fetch(`${API_URL}/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            filepath: uploadedFile.filepath,
            model: model
        })
    });

    const data = await response.json();

    if (data.job_id) {
        return await pollJobStatus(data.job_id);
    }
}

async function pollJobStatus(jobId) {
    return new Promise((resolve, reject) => {
        const interval = setInterval(async () => {
            try {
                const response = await fetch(`${API_URL}/jobs/${jobId}`);
                const job = await response.json();

                updateProgress(job.message, job.progress);

                if (job.status === 'completed') {
                    clearInterval(interval);
                    hideProgress();
                    resolve(job.result);
                } else if (job.status === 'failed') {
                    clearInterval(interval);
                    hideProgress();
                    reject(new Error(job.error || 'Processing failed'));
                }
            } catch (error) {
                clearInterval(interval);
                hideProgress();
                reject(error);
            }
        }, 1000);
    });
}

function showProgress(message, progress) {
    progressSection.style.display = 'block';
    updateProgress(message, progress);
}

function updateProgress(message, progress) {
    progressText.textContent = message;
    progressFill.style.width = progress + '%';
}

function hideProgress() {
    progressSection.style.display = 'none';
}

function displayResults(data) {
    resultsSection.style.display = 'block';
    resultsContainer.innerHTML = '';

    if (currentAction === 'extract') {
        resultsContainer.innerHTML = `
            <div class="result-item">
                <h3>✅ Audio Extrait avec Succès</h3>
                <p><strong>Fichier:</strong> ${data.output_file}</p>
                <p><strong>Durée:</strong> ${data.info.duration.toFixed(2)}s</p>
                <p><strong>Format:</strong> ${data.info.format}</p>
                <p><strong>Taux d'échantillonnage:</strong> ${data.info.sample_rate} Hz</p>
                <a href="${API_URL}/download/${data.output_file}" class="download-btn" download>
                    📥 Télécharger
                </a>
            </div>
        `;
    } else if (currentAction === 'separate') {
        let html = '<div class="result-item"><h3>✅ Séparation Terminée</h3>';
        for (const [stem, path] of Object.entries(data.stems)) {
            html += `
                <div style="margin: 10px 0;">
                    <strong>${getStemIcon(stem)} ${stem}:</strong>
                    <a href="${API_URL}/download/${path}" class="download-btn" download>
                        📥 Télécharger ${stem}
                    </a>
                </div>
            `;
        }
        html += '</div>';
        resultsContainer.innerHTML = html;
    } else if (currentAction === 'analyze') {
        const analysis = data.analysis;
        resultsContainer.innerHTML = `
            <div class="result-item">
                <h3>📊 Analyse Audio</h3>
                <div class="analysis-grid">
                    <div class="analysis-card">
                        <div class="label">Durée</div>
                        <div class="value">${analysis.duration.toFixed(1)}s</div>
                    </div>
                    <div class="analysis-card">
                        <div class="label">Tempo</div>
                        <div class="value">${analysis.rhythm.tempo.toFixed(0)} BPM</div>
                    </div>
                    <div class="analysis-card">
                        <div class="label">Couches Sonores</div>
                        <div class="value">${analysis.complexity.estimated_sound_layers}</div>
                    </div>
                    <div class="analysis-card">
                        <div class="label">Ratio Harmonique</div>
                        <div class="value">${(analysis.harmony.harmonic_ratio * 100).toFixed(1)}%</div>
                    </div>
                    <div class="analysis-card">
                        <div class="label">Ratio Percussif</div>
                        <div class="value">${(analysis.harmony.percussive_ratio * 100).toFixed(1)}%</div>
                    </div>
                    <div class="analysis-card">
                        <div class="label">Complexité</div>
                        <div class="value">${analysis.complexity.complexity_score.toFixed(2)}</div>
                    </div>
                </div>
            </div>
        `;
    } else if (currentAction === 'process') {
        let html = '<div class="result-item"><h3>✅ Traitement Complet Terminé</h3>';

        // Stems
        html += '<h4>🎼 Stems Séparés:</h4>';
        for (const [stem, path] of Object.entries(data.stems)) {
            html += `
                <div style="margin: 10px 0;">
                    <strong>${getStemIcon(stem)} ${stem}:</strong>
                    <a href="${API_URL}/download/${path}" class="download-btn" download>
                        📥 Télécharger
                    </a>
                </div>
            `;
        }

        // Analysis
        const analysis = data.analysis;
        html += `
            <h4 style="margin-top: 30px;">📊 Analyse:</h4>
            <div class="analysis-grid">
                <div class="analysis-card">
                    <div class="label">Tempo</div>
                    <div class="value">${analysis.rhythm.tempo.toFixed(0)} BPM</div>
                </div>
                <div class="analysis-card">
                    <div class="label">Couches Sonores</div>
                    <div class="value">${analysis.complexity.estimated_sound_layers}</div>
                </div>
                <div class="analysis-card">
                    <div class="label">Stem Dominant</div>
                    <div class="value">${data.stem_comparison.dominant_stem}</div>
                </div>
            </div>
        `;

        // Stem comparison
        html += '<h4 style="margin-top: 20px;">Distribution d\'Énergie:</h4>';
        for (const [stem, stemData] of Object.entries(data.stem_comparison.stems)) {
            html += `
                <div style="margin: 10px 0;">
                    <strong>${getStemIcon(stem)} ${stem}:</strong> ${stemData.percentage.toFixed(1)}%
                    <div style="background: rgba(99, 102, 241, 0.2); border-radius: 4px; height: 20px; margin-top: 5px;">
                        <div style="background: linear-gradient(90deg, #6366f1, #8b5cf6); height: 100%; width: ${stemData.percentage}%; border-radius: 4px;"></div>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        resultsContainer.innerHTML = html;
    }
}

function getStemIcon(stem) {
    const icons = {
        'vocals': '🎤',
        'drums': '🥁',
        'bass': '🎸',
        'other': '🎹',
        'guitar': '🎸',
        'piano': '🎹'
    };
    return icons[stem] || '🎵';
}
