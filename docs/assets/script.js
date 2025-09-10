// Data Wiping Tool - Web Interface JavaScript
// Educational demonstration of data wiping concepts

class DataWipingTool {
    constructor() {
        this.selectedFiles = [];
        this.isWiping = false;
        this.init();
    }

    init() {
        this.setupFileUpload();
        this.setupNavigation();
        this.setupEventListeners();
    }

    setupFileUpload() {
        const fileInput = document.getElementById('fileInput');
        const uploadArea = document.getElementById('fileUploadArea');
        const startBtn = document.getElementById('startWipeBtn');

        // File input change event
        fileInput.addEventListener('change', (e) => {
            this.handleFiles(e.target.files);
        });

        // Drag and drop functionality
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFiles(e.dataTransfer.files);
        });

        // Click to upload
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
    }

    setupNavigation() {
        // Smooth scrolling for navigation links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const targetId = link.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Mobile menu toggle
        const navToggle = document.querySelector('.nav-toggle');
        const navMenu = document.querySelector('.nav-menu');
        
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.toggle('active');
            });
        }
    }

    setupEventListeners() {
        // Navbar scroll effect
        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            if (window.scrollY > 100) {
                navbar.style.background = 'rgba(15, 23, 42, 0.98)';
            } else {
                navbar.style.background = 'rgba(15, 23, 42, 0.95)';
            }
        });

        // Animation on scroll
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);

        // Observe elements for animation
        const animatedElements = document.querySelectorAll('.feature-card, .standard-card, .download-card');
        animatedElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }

    handleFiles(files) {
        this.selectedFiles = Array.from(files);
        this.updateFileDisplay();
        this.updateStartButton();
    }

    updateFileDisplay() {
        const uploadArea = document.getElementById('fileUploadArea');
        const fileCount = this.selectedFiles.length;
        
        if (fileCount > 0) {
            const totalSize = this.formatFileSize(
                this.selectedFiles.reduce((total, file) => total + file.size, 0)
            );
            
            uploadArea.innerHTML = `
                <div class="upload-icon">
                    <i class="fas fa-check-circle" style="color: var(--success-color);"></i>
                </div>
                <h3>${fileCount} File${fileCount > 1 ? 's' : ''} Selected</h3>
                <p>Total size: ${totalSize}</p>
                <button class="btn btn-outline" onclick="document.getElementById('fileInput').click()">
                    Change Selection
                </button>
            `;
        }
    }

    updateStartButton() {
        const startBtn = document.getElementById('startWipeBtn');
        startBtn.disabled = this.selectedFiles.length === 0 || this.isWiping;
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async startWipe() {
        if (this.selectedFiles.length === 0 || this.isWiping) return;

        this.isWiping = true;
        this.updateStartButton();

        const method = document.getElementById('wipeMethod').value;
        const verify = document.getElementById('verifyWipe').checked;
        const generateCert = document.getElementById('generateCert').checked;

        // Show progress panel
        const progressPanel = document.getElementById('progressPanel');
        progressPanel.style.display = 'block';
        progressPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });

        try {
            await this.simulateWipeProcess(method, verify, generateCert);
        } catch (error) {
            console.error('Wipe process error:', error);
            this.showError('An error occurred during the wipe process.');
        } finally {
            this.isWiping = false;
            this.updateStartButton();
        }
    }

    async simulateWipeProcess(method, verify, generateCert) {
        const progressFill = document.getElementById('progressFill');
        const progressPercentage = document.getElementById('progressPercentage');
        const progressStatus = document.getElementById('progressStatus');
        const fileList = document.getElementById('fileList');
        const wipeResults = document.getElementById('wipeResults');
        const resultSummary = document.getElementById('resultSummary');

        // Reset UI
        wipeResults.style.display = 'none';
        fileList.innerHTML = '';

        const totalSteps = this.selectedFiles.length * (method === 'dod' ? 3 : 1) + (verify ? this.selectedFiles.length : 0);
        let currentStep = 0;

        // Update progress
        const updateProgress = (percentage, status) => {
            progressFill.style.width = percentage + '%';
            progressPercentage.textContent = Math.round(percentage) + '%';
            progressStatus.textContent = status;
        };

        updateProgress(0, 'Initializing wipe process...');
        await this.sleep(1000);

        // Create file list items
        this.selectedFiles.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <span class="file-name">${file.name}</span>
                <span class="file-status" id="status-${file.name}">Pending</span>
            `;
            fileList.appendChild(fileItem);
        });

        const results = {
            totalFiles: this.selectedFiles.length,
            successfulWipes: 0,
            errors: 0,
            method: method,
            verified: verify,
            startTime: new Date(),
            endTime: null
        };

        // Simulate wiping each file
        for (let i = 0; i < this.selectedFiles.length; i++) {
            const file = this.selectedFiles[i];
            const fileItem = fileList.children[i];
            const statusElement = document.getElementById(`status-${file.name}`);

            // Simulate wipe passes
            const passes = method === 'dod' ? 3 : 1;
            for (let pass = 1; pass <= passes; pass++) {
                currentStep++;
                const progress = (currentStep / totalSteps) * 70; // 70% for wiping
                
                let passDescription = '';
                if (method === 'dod') {
                    const patterns = ['zeros', 'ones', 'random'];
                    passDescription = `Pass ${pass}/3 (${patterns[pass - 1]})`;
                } else {
                    passDescription = 'Random overwrite';
                }

                updateProgress(progress, `Wiping ${file.name} - ${passDescription}`);
                statusElement.textContent = `Wiping... (${passDescription})`;
                statusElement.className = 'file-status';

                await this.sleep(1000 + Math.random() * 2000); // Simulate variable time
            }

            // Simulate verification
            if (verify) {
                currentStep++;
                const progress = (currentStep / totalSteps) * 70;
                updateProgress(progress, `Verifying ${file.name}...`);
                statusElement.textContent = 'Verifying...';
                await this.sleep(500 + Math.random() * 1000);
            }

            // Simulate success/failure (95% success rate)
            const success = Math.random() > 0.05;
            if (success) {
                results.successfulWipes++;
                fileItem.classList.add('success');
                statusElement.textContent = 'Successfully wiped';
                statusElement.classList.add('success');
            } else {
                results.errors++;
                fileItem.classList.add('error');
                statusElement.textContent = 'Error occurred';
                statusElement.classList.add('error');
            }
        }

        // Finalization
        updateProgress(85, 'Finalizing wipe process...');
        await this.sleep(1000);

        if (generateCert) {
            updateProgress(95, 'Generating certificate...');
            await this.sleep(1500);
        }

        updateProgress(100, 'Wipe process completed!');
        results.endTime = new Date();

        // Show results
        await this.sleep(500);
        this.showResults(results, generateCert);
    }

    showResults(results, generateCert) {
        const wipeResults = document.getElementById('wipeResults');
        const resultSummary = document.getElementById('resultSummary');
        const downloadCertBtn = document.getElementById('downloadCertBtn');

        const duration = ((results.endTime - results.startTime) / 1000).toFixed(1);
        const successRate = ((results.successfulWipes / results.totalFiles) * 100).toFixed(1);

        resultSummary.innerHTML = `
            <div class="result-item">
                <span class="result-label">Files Processed:</span>
                <span class="result-value">${results.totalFiles}</span>
            </div>
            <div class="result-item">
                <span class="result-label">Successful:</span>
                <span class="result-value" style="color: var(--success-color);">${results.successfulWipes}</span>
            </div>
            <div class="result-item">
                <span class="result-label">Errors:</span>
                <span class="result-value" style="color: ${results.errors > 0 ? 'var(--danger-color)' : 'var(--success-color)'};">${results.errors}</span>
            </div>
            <div class="result-item">
                <span class="result-label">Success Rate:</span>
                <span class="result-value">${successRate}%</span>
            </div>
            <div class="result-item">
                <span class="result-label">Method:</span>
                <span class="result-value">${results.method.toUpperCase()}</span>
            </div>
            <div class="result-item">
                <span class="result-label">Duration:</span>
                <span class="result-value">${duration}s</span>
            </div>
        `;

        wipeResults.style.display = 'block';

        if (generateCert) {
            downloadCertBtn.style.display = 'block';
            this.certificateData = results;
        }
    }

    downloadCertificate() {
        if (!this.certificateData) return;

        const certificate = this.generateCertificateContent(this.certificateData);
        const blob = new Blob([certificate], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `wipe-certificate-${Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    generateCertificateContent(results) {
        const certificateId = this.generateUUID();
        const timestamp = new Date().toISOString();
        
        return `
====================================================
         CERTIFICATE OF SECURE DATA ERASURE
====================================================

Certificate ID: ${certificateId}
Generated: ${timestamp}
Tool: DataWipe Pro (Web Demo)
Licensed to: Aniket Tegginamath

OPERATION DETAILS:
--------------------------------------------------
Start Time: ${results.startTime.toISOString()}
End Time: ${results.endTime.toISOString()}
Duration: ${((results.endTime - results.startTime) / 1000).toFixed(1)} seconds
Wipe Method: ${results.method.toUpperCase()}
Verification: ${results.verified ? 'Enabled' : 'Disabled'}

RESULTS SUMMARY:
--------------------------------------------------
Total Files: ${results.totalFiles}
Successfully Wiped: ${results.successfulWipes}
Errors: ${results.errors}
Success Rate: ${((results.successfulWipes / results.totalFiles) * 100).toFixed(1)}%

METHOD SPECIFICATIONS:
--------------------------------------------------
${results.method === 'dod' ? 
  'DoD 5220.22-M Standard:\n- Pass 1: Overwrite with zeros (0x00)\n- Pass 2: Overwrite with ones (0xFF)\n- Pass 3: Overwrite with random data' :
  'Quick/NIST Standard:\n- Single pass with cryptographic random data\n- Compliant with NIST SP 800-88 Rev. 1'
}

VERIFICATION:
--------------------------------------------------
${results.verified ? 
  'File verification was performed using hash comparison\nand random sampling to ensure complete erasure.' :
  'Verification was disabled for this operation.'
}

DISCLAIMER:
--------------------------------------------------
This is a web-based demonstration for educational
purposes. For actual secure data erasure, please
use the desktop application with appropriate
administrative privileges.

Generated by DataWipe Pro Web Tool
https://aniket886.github.io/datawipingtool/
====================================================
        `.trim();
    }

    generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            const r = Math.random() * 16 | 0;
            const v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }

    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    showError(message) {
        const progressStatus = document.getElementById('progressStatus');
        progressStatus.textContent = `Error: ${message}`;
        progressStatus.style.color = 'var(--danger-color)';
    }
}

// Global functions for button events
function startWipe() {
    if (window.wipeTool) {
        window.wipeTool.startWipe();
    }
}

function downloadCertificate() {
    if (window.wipeTool) {
        window.wipeTool.downloadCertificate();
    }
}

// Initialize the tool when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.wipeTool = new DataWipingTool();
    
    // Add some interactive effects
    addInteractiveEffects();
});

function addInteractiveEffects() {
    // Add hover effects to cards
    const cards = document.querySelectorAll('.feature-card, .standard-card, .download-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Add typing effect to hero title
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        const text = heroTitle.textContent;
        heroTitle.textContent = '';
        heroTitle.style.opacity = '1';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                heroTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 50);
            }
        };
        
        // Start typing effect after a delay
        setTimeout(typeWriter, 1000);
    }

    // Add parallax effect to hero section
    window.addEventListener('scroll', () => {
        const hero = document.querySelector('.hero');
        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        if (hero) {
            hero.style.transform = `translateY(${rate}px)`;
        }
    });

    // Add loading animation
    const body = document.body;
    body.style.opacity = '0';
    body.style.transition = 'opacity 0.5s ease';
    
    window.addEventListener('load', () => {
        body.style.opacity = '1';
    });
}

// Service Worker registration for PWA capabilities (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Analytics and performance monitoring (placeholder)
function trackEvent(eventName, properties = {}) {
    console.log('Event tracked:', eventName, properties);
    // Implement analytics tracking here
}

// Export for potential use in other scripts
window.DataWipingTool = DataWipingTool;
