document.addEventListener('DOMContentLoaded', () => {
    // 1. Drag & Drop File Upload Binding
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const badge = document.getElementById('file-badge');
    const badgeName = document.getElementById('file-badge-name');
    const badgeSize = document.getElementById('file-badge-size');
    const uploadForm = document.getElementById('upload-form');
    const progressContainer = document.getElementById('progress-container');
    const progressBar = document.getElementById('progress-bar');
    
    if (dropzone && fileInput) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, preventDefaults, false);
            document.body.addEventListener(eventName, preventDefaults, false);
        });

        // Toggle dropzone visual cues
        ['dragenter', 'dragover'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
        });

        // Handle dropped files
        dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                fileInput.files = files;
                updateFileBadge(files[0]);
            }
        });

        // Handle standard input change
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                updateFileBadge(fileInput.files[0]);
            }
        });

        // Click on dropzone to trigger input
        dropzone.addEventListener('click', () => {
            fileInput.click();
        });
    }

    // Prevent default browser redirects
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Update the UI showing selected file details
    function updateFileBadge(file) {
        if (!badge || !badgeName || !badgeSize) return;
        
        badgeName.textContent = file.name;
        badgeSize.textContent = formatBytes(file.size);
        badge.style.display = 'flex';
        
        // Safety warning check for file size (50MB)
        if (file.size > 50 * 1024 * 1024) {
            badgeName.textContent += " (TOO LARGE!)";
            badgeName.style.color = "#ff0055";
            alert("Warning: This file exceeds the 50MB upload limit and may fail.");
        } else {
            badgeName.style.color = "";
        }
    }

    // Helper: format bytes to human readable string
    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // 2. AJAX Uploads with Progress Bars
    if (uploadForm && progressContainer && progressBar) {
        uploadForm.addEventListener('submit', (e) => {
            // Check if file is selected
            if (!fileInput || fileInput.files.length === 0) {
                alert("Please select a file to proceed.");
                e.preventDefault();
                return;
            }

            e.preventDefault();
            
            const formData = new FormData(uploadForm);
            const xhr = new XMLHttpRequest();
            
            progressContainer.style.display = 'block';
            progressBar.style.width = '0%';
            
            // Track upload progress
            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const percent = Math.round((event.loaded / event.total) * 100);
                    progressBar.style.width = percent + '%';
                }
            });
            
            xhr.responseType = 'blob';
            
            xhr.onreadystatechange = () => {
                if (xhr.readyState === XMLHttpRequest.DONE) {
                    progressContainer.style.display = 'none';
                    progressBar.style.width = '0%';
                    
                    if (xhr.status === 200) {
                        const contentType = xhr.getResponseHeader('Content-Type') || '';
                        const disposition = xhr.getResponseHeader('Content-Disposition') || '';
                        
                        // Scenario A: Check if the response is a binary file download (e.g. decrypted output)
                        if (disposition.includes('attachment')) {
                            const blob = xhr.response;
                            const link = document.createElement('a');
                            link.href = window.URL.createObjectURL(blob);
                            
                            // Extract original filename from header
                            let filename = "decrypted_file";
                            const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
                            if (filenameMatch && filenameMatch[1]) {
                                filename = filenameMatch[1];
                            }
                            
                            link.download = filename;
                            document.body.appendChild(link);
                            link.click();
                            document.body.removeChild(link);
                            
                            // Redirect to history to show log update
                            window.location.href = '/history';
                        } 
                        // Scenario B: The server returns HTML (e.g., success screen, check alert, or error flashes)
                        else {
                            const blob = xhr.response;
                            const reader = new FileReader();
                            reader.onload = () => {
                                const responseHtml = reader.result;
                                
                                // Parse and replace the main panel contents
                                const parser = new DOMParser();
                                const doc = parser.parseFromString(responseHtml, 'text/html');
                                const newPanel = doc.querySelector('.glass-panel');
                                const currentPanel = document.querySelector('.glass-panel');
                                
                                if (newPanel && currentPanel) {
                                    currentPanel.innerHTML = newPanel.innerHTML;
                                    // Re-trigger bindings if we replaced the DOM
                                    rebindDropzone();
                                } else {
                                    // Fallback replacement of entire document if structure differs
                                    document.open();
                                    document.write(responseHtml);
                                    document.close();
                                }
                            };
                            reader.readAsText(blob);
                        }
                    } else {
                        alert("An error occurred during file upload. Check your inputs or connection.");
                    }
                }
            };
            
            xhr.open('POST', uploadForm.action, true);
            xhr.send(formData);
        });
    }

    // Helper: Rebind dropzone actions if the DOM was dynamically replaced via AJAX
    function rebindDropzone() {
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('file-input');
        if (dropzone && fileInput) {
            // Unbind and rebind dropzone click and change events
            dropzone.addEventListener('click', () => fileInput.click());
            fileInput.addEventListener('change', () => {
                if (fileInput.files.length > 0) {
                    updateFileBadge(fileInput.files[0]);
                }
            });
            
            // Re-setup drag behavior
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, preventDefaults, false);
            });
            ['dragenter', 'dragover'].forEach(eventName => {
                dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
            });
            ['dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
            });
            dropzone.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files.length > 0) {
                    fileInput.files = files;
                    updateFileBadge(files[0]);
                }
            });
        }
    }
});
