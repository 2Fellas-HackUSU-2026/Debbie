// Application State
let currentDocId = null;
let selectedElements = new Set();
let documentStructure = null;
let configuredSelections = [];

// --- DOM Elements ---
const els = {
    uploadSection: document.getElementById('upload-section'),
    uploadLoading: document.getElementById('upload-loading'),
    sidebar: document.getElementById('sidebar'),
    docView: document.getElementById('document-view'),
    headerActions: document.getElementById('header-actions'),
    selectionPanel: document.getElementById('selection-panel'),
    selectionCount: document.getElementById('selection-count'),
    configuredList: document.getElementById('configured-fields-list'),
    configModal: document.getElementById('config-modal'),
    modalContent: document.getElementById('modal-content'),
    modalVarName: document.getElementById('modalVarName'),
    modalContext: document.getElementById('modalContext'),
    tableSelectionActions: document.getElementById('table-selection-actions'),
    toast: document.getElementById('toast'),
    toastContent: document.getElementById('toast-content'),
    toastIcon: document.getElementById('toast-icon'),
    toastTitle: document.getElementById('toast-title'),
    toastMessage: document.getElementById('toast-message'),
    toastActions: document.getElementById('toast-actions'),
};

// --- Toast Notifications ---
function showToast(options) {
    const { title, message, type = 'info', duration = 3000, actions = [] } = options;
    
    // Set content
    els.toastTitle.textContent = title;
    els.toastMessage.textContent = message;
    
    // Set icon and colors based on type
    const iconConfigs = {
        success: { bg: 'bg-green-100', color: 'text-green-600', icon: '✓' },
        error: { bg: 'bg-red-100', color: 'text-red-600', icon: '✕' },
        warning: { bg: 'bg-amber-100', color: 'text-amber-600', icon: '⚠' },
        info: { bg: 'bg-blue-100', color: 'text-blue-600', icon: 'ℹ' }
    };
    
    const config = iconConfigs[type] || iconConfigs.info;
    els.toastIcon.className = `flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${config.bg} ${config.color}`;
    els.toastIcon.textContent = config.icon;
    
    // Set actions
    els.toastActions.innerHTML = '';
    if (actions.length === 0) {
        // Default close after duration
        setTimeout(() => hideToast(), duration);
    } else {
        actions.forEach(action => {
            const btn = document.createElement('button');
            btn.className = action.primary 
                ? 'px-4 py-2 text-sm font-medium bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors'
                : 'px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-md transition-colors';
            btn.textContent = action.label;
            btn.onclick = () => {
                action.onClick?.();
                hideToast();
            };
            els.toastActions.appendChild(btn);
        });
    }
    
    // Show toast
    els.toast.classList.remove('hidden');
    setTimeout(() => {
        els.toastContent.classList.remove('scale-95', 'opacity-0');
        els.toastContent.classList.add('scale-100', 'opacity-100');
    }, 10);
}

function hideToast() {
    els.toastContent.classList.remove('scale-100', 'opacity-100');
    els.toastContent.classList.add('scale-95', 'opacity-0');
    setTimeout(() => {
        els.toast.classList.add('hidden');
    }, 200);
}

// --- API Interactions ---
async function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    if (!fileInput.files[0]) return;

    els.uploadLoading.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const resp = await fetch('/upload', { method: 'POST', body: formData });
        if (!resp.ok) throw new Error('Upload failed');

        const data = await resp.json();
        currentDocId = data.doc_id;
        documentStructure = data.structure;

        renderDocument(documentStructure);

        // Switch UI state
        els.uploadLoading.classList.add('hidden');
        els.uploadSection.classList.add('hidden');
        els.docView.classList.remove('hidden');
        els.sidebar.classList.remove('hidden');
        els.headerActions.classList.remove('hidden');
    } catch (err) {
        console.error(err);
        showToast({
            title: 'Upload Failed',
            message: "Failed to upload document. Ensure it's a valid .docx file.",
            type: 'error',
            duration: 5000
        });
        els.uploadLoading.classList.add('hidden');
    }
}

async function finalizeDocument() {
    if (!currentDocId) return;
    if (configuredSelections.length === 0) {
        return new Promise((resolve) => {
            showToast({
                title: 'No Fields Configured',
                message: 'No fields have been configured. Do you want to finalize anyway?',
                type: 'warning',
                actions: [
                    { label: 'Cancel', onClick: () => resolve() },
                    { label: 'Finalize', primary: true, onClick: () => proceedToFinalize() }
                ]
            });
        });
    } else {
        await proceedToFinalize();
    }
}

async function proceedToFinalize() {
    try {
        const resp = await fetch('/process', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ doc_id: currentDocId, selections: configuredSelections })
        });

        if (!resp.ok) throw new Error("Failed to process document");

        const data = await resp.json();
        
        showToast({
            title: 'Document Finalized',
            message: 'Document saved',
            type: 'success',
            duration: 4000
        });
    } catch (err) {
        console.error(err);
        showToast({
            title: 'Error',
            message: 'Error finalizing document.',
            type: 'error',
            duration: 5000
        });
    }
}

// --- Rendering ---

function createFormattedText(runs) {
    if (!runs || runs.length === 0) return document.createTextNode("");

    const container = document.createDocumentFragment();
    runs.forEach(run => {
        let span = document.createElement('span');
        span.innerText = run.text;

        if (run.formatting) {
            if (run.formatting.bold) span.style.fontWeight = 'bold';
            if (run.formatting.italic) span.style.fontStyle = 'italic';
            if (run.formatting.underline) span.style.textDecoration = 'underline';
        }

        container.appendChild(span);
    });
    return container;
}

function renderParagraph(p) {
    const div = document.createElement('div');
    div.id = p.id;
    div.className = 'selectable mb-2 px-2 py-1 min-h-[1.5em]';

    // Apply alignment
    if (p.alignment) {
        div.style.textAlign = p.alignment;
    }

    // Checkboxes
    if (p.has_checkbox) {
        div.innerHTML = `<span class="text-blue-600 font-bold mr-2">[Checkbox]</span>`;
    }

    // Runs formatting
    if (p.runs && p.runs.length > 0) {
        div.appendChild(createFormattedText(p.runs));
    } else if (p.text) {
        div.innerText = p.text;
    } else if (p.is_blank) {
        // Keep blank lines visible
        div.innerHTML = '&nbsp;';
    }

    div.onclick = (e) => handleSelection(e, p.id);
    return div;
}

function renderDocument(structure) {
    els.docView.innerHTML = '';

    const fragment = document.createDocumentFragment();

    structure.paragraphs.forEach(p => {
        fragment.appendChild(renderParagraph(p));
    });

    structure.tables.forEach(t => {
        const tableWrapper = document.createElement('div');
        tableWrapper.className = 'overflow-x-auto my-6';

        const table = document.createElement('table');
        table.id = t.id;
        table.className = 'doc-table';

        t.rows.forEach((row, rIdx) => {
            const tr = document.createElement('tr');

            row.forEach((cell, cIdx) => {
                const td = document.createElement('td');
                td.id = cell.id;
                td.className = 'selectable align-top';
                td.onclick = (e) => {
                    e.stopPropagation();
                    handleSelection(e, cell.id);
                };

                // Column selector on first row - always visible and prominent
                if (rIdx === 0) {
                    const colBtn = document.createElement('div');
                    colBtn.className = 'col-select-btn';
                    colBtn.id = `${t.id}_colbtn_${cIdx}`;
                    colBtn.innerHTML = String.fromCharCode(65 + cIdx); // A, B, C, etc.
                    colBtn.title = `Column ${String.fromCharCode(65 + cIdx)} - Click to select entire column`;
                    colBtn.style.cssText = 'width: 28px; height: 28px; font-weight: bold; font-size: 12px;';
                    colBtn.onclick = (e) => {
                        e.stopPropagation();
                        handleColumnSelection(e, t.id, cIdx, t.rows.length);
                    };
                    td.appendChild(colBtn);
                }

                // Render cell content preserving paragraphs
                if (cell.paragraphs && cell.paragraphs.length > 0) {
                    cell.paragraphs.forEach(cp => {
                        const pDiv = document.createElement('div');
                        pDiv.className = 'mb-1';
                        if (cp.alignment) pDiv.style.textAlign = cp.alignment;

                        if (cell.has_checkbox) {
                            pDiv.innerHTML += `<span class="text-blue-600 font-bold mr-1">[CB]</span>`;
                        }

                        if (cp.runs && cp.runs.length > 0) {
                            pDiv.appendChild(createFormattedText(cp.runs));
                        } else {
                            pDiv.innerText = cp.text || '\u00A0';
                        }
                        td.appendChild(pDiv);
                    });
                } else {
                    if (cell.has_checkbox) {
                        td.innerHTML = `<span class="text-blue-600 font-bold mr-1">[CB]</span>`;
                    }
                    td.appendChild(document.createTextNode(cell.text || '\u00A0'));
                }

                tr.appendChild(td);
            });
            table.appendChild(tr);
        });

        tableWrapper.appendChild(table);
        fragment.appendChild(tableWrapper);
    });

    els.docView.appendChild(fragment);
}

// --- Selection Logic ---

function handleSelection(e, id) {
    const isCtrl = e.ctrlKey || e.metaKey;

    if (isCtrl) {
        if (selectedElements.has(id)) {
            removeFromSelection(id);
        } else {
            addToSelection(id);
        }
    } else {
        clearSelection();
        addToSelection(id);
    }

    updateSelectionUI();
}

function handleColumnSelection(e, tableId, colIdx, rowCount) {
    const isCtrl = e.ctrlKey || e.metaKey;

    // Create a virtual ID for column selection
    const colId = `${tableId}_col_${colIdx}`;

    if (!isCtrl) clearSelection();

    if (selectedElements.has(colId)) {
        selectedElements.delete(colId);
        highlightColumn(tableId, colIdx, false);
        document.getElementById(`${tableId}_colbtn_${colIdx}`).classList.remove('active');
    } else {
        selectedElements.add(colId);
        highlightColumn(tableId, colIdx, true);
        document.getElementById(`${tableId}_colbtn_${colIdx}`).classList.add('active');
    }

    updateSelectionUI();
}

function highlightColumn(tableId, colIdx, active) {
    const table = document.getElementById(tableId);
    if (!table) return;

    for (let r = 0; r < table.rows.length; r++) {
        const cell = table.rows[r].cells[colIdx];
        if (cell) {
            if (active) cell.classList.add('selected');
            else cell.classList.remove('selected');
        }
    }
}

function addToSelection(id) {
    selectedElements.add(id);
    const el = document.getElementById(id);
    if (el) el.classList.add('selected');
}

function removeFromSelection(id) {
    selectedElements.delete(id);
    const el = document.getElementById(id);
    if (el) el.classList.remove('selected');
}

function clearSelection() {
    selectedElements.forEach(id => {
        if (id.includes('_col_')) {
            const parts = id.split('_col_');
            highlightColumn(parts[0], parseInt(parts[1]), false);
            const btn = document.getElementById(`${parts[0]}_colbtn_${parts[1]}`);
            if (btn) btn.classList.remove('active');
        } else {
            const el = document.getElementById(id);
            if (el) el.classList.remove('selected');
        }
    });
    selectedElements.clear();
}

function updateSelectionUI() {
    els.selectionCount.innerText = selectedElements.size;

    if (selectedElements.size > 0) {
        els.selectionPanel.classList.remove('opacity-50', 'pointer-events-none');
        
        // Show Select Entire Column button if a single table cell is selected
        const firstSelected = Array.from(selectedElements)[0];
        const isSingleTableCell = selectedElements.size === 1 && 
                                 typeof firstSelected === 'string' && 
                                 firstSelected.includes('_r_') && 
                                 firstSelected.includes('_c_');
        
        if (isSingleTableCell) {
            els.tableSelectionActions.classList.remove('hidden');
        } else {
            els.tableSelectionActions.classList.add('hidden');
        }
    } else {
        els.selectionPanel.classList.add('opacity-50', 'pointer-events-none');
        els.tableSelectionActions.classList.add('hidden');
    }

    els.modalVarName.value = '';
    els.modalContext.value = '';
}

function selectCurrentColumn() {
    if (selectedElements.size !== 1) return;
    const id = Array.from(selectedElements)[0];
    if (typeof id !== 'string' || !id.includes('_r_') || !id.includes('_c_')) return;

    // ID format: t_{table_idx}_r_{row_idx}_c_{col_idx}
    const parts = id.split('_');
    const tableId = `t_${parts[1]}`;
    const colIdx = parseInt(parts[5]);

    // Select entire column
    handleColumnSelection({ ctrlKey: false }, tableId, colIdx);
}

// --- Modal Configuration ---
function openConfigModal() {
    if (selectedElements.size === 0) return;

    els.configModal.classList.remove('hidden');
    els.configModal.classList.add('flex');

    // Trigger animation
    setTimeout(() => {
        els.modalContent.classList.remove('scale-95', 'opacity-0');
        els.modalContent.classList.add('scale-100', 'opacity-100');
    }, 10);

    els.modalVarName.focus();
}

function closeConfigModal() {
    els.modalContent.classList.remove('scale-100', 'opacity-100');
    els.modalContent.classList.add('scale-95', 'opacity-0');

    setTimeout(() => {
        els.configModal.classList.add('hidden');
        els.configModal.classList.remove('flex');
    }, 200);
}

function generateAISuggestion() {
    // Collect all text from selected elements
    let allText = [];
    selectedElements.forEach(id => {
        // Check if this is a column selection
        if (typeof id === 'string' && id.includes('_col_')) {
            // Column selection: collect text from all cells in that column
            const parts = id.split('_col_');
            const tableId = parts[0];
            const colIdx = parseInt(parts[1]);
            
            const table = document.getElementById(tableId);
            if (table) {
                for (let r = 0; r < table.rows.length; r++) {
                    const cell = table.rows[r].cells[colIdx];
                    if (cell) {
                        const cellText = cell.innerText || cell.textContent;
                        if (cellText && cellText.trim()) {
                            allText.push(cellText.trim());
                        }
                    }
                }
            }
        } else {
            // Regular cell selection
            const el = document.getElementById(id);
            if (el) {
                const text = el.innerText || el.textContent;
                if (text && text.trim()) {
                    allText.push(text.trim());
                }
            }
        }
    });

    const selectedText = allText.join('\n').trim();
    
    if (!selectedText) {
        showToast({
            title: 'No Content',
            message: 'No text content found in selected elements.',
            type: 'warning',
            duration: 3000
        });
        return;
    }

    // Call API to generate suggestion
    generateVariableSuggestion(selectedText);
}

async function generateVariableSuggestion(text) {
    const btn = event?.target?.closest('button');
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = `
            <i data-lucide="loader-2" class="w-4 h-4 spinner"></i>
            <span>Generating...</span>
        `;
        lucide.createIcons();
    }

    try {
        const resp = await fetch('/suggest', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });

        if (!resp.ok) throw new Error('Failed to generate suggestion');

        const data = await resp.json();
        const suggestion = data.suggestion || '';

        if (suggestion) {
            els.modalVarName.value = suggestion;
            els.modalVarName.focus();
            
            // Reset button
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = `
                    <i data-lucide="sparkles" class="w-4 h-4"></i>
                    <span>AI Suggest</span>
                `;
                lucide.createIcons();
            }
        } else {
            showToast({
                title: 'No Suggestion',
                message: 'No suggestion generated. Please enter a variable name manually.',
                type: 'info',
                duration: 3000
            });
            if (btn) {
                btn.disabled = false;
                btn.innerHTML = `
                    <i data-lucide="sparkles" class="w-4 h-4"></i>
                    <span>AI Suggest</span>
                `;
                lucide.createIcons();
            }
        }
    } catch (err) {
        console.error(err);
        showToast({
            title: 'AI Error',
            message: 'Failed to generate AI suggestion.',
            type: 'error',
            duration: 5000
        });
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = `
                <i data-lucide="sparkles" class="w-4 h-4"></i>
                <span>AI Suggest</span>
            `;
            lucide.createIcons();
        }
    }
}

function preventPipeCharacter(event) {
    if (event.key === '|') {
        event.preventDefault();
    }
}

function saveConfiguration() {
    const varName = els.modalVarName.value.trim();
    const context = els.modalContext.value.trim();

    if (!varName) {
        showToast({
            title: 'Required Field',
            message: 'Variable Name is required.',
            type: 'warning',
            duration: 3000
        });
        els.modalVarName.focus();
        return;
    }

    // Generate group ID for this batch of selections
    const groupId = Date.now().toString(36);
    
    // Save for each selected element with unique incremented variable names
    let selectionArray = Array.from(selectedElements);
    
    // Sort columns by column index (leftmost = first)
    selectionArray.sort((a, b) => {
        const aIsCol = a.includes('_col_');
        const bIsCol = b.includes('_col_');
        
        if (aIsCol && bIsCol) {
            const aColIdx = parseInt(a.split('_col_')[1]);
            const bColIdx = parseInt(b.split('_col_')[1]);
            return aColIdx - bColIdx;
        }
        return 0;
    });
    
    selectionArray.forEach((id, index) => {
        // Check if replacing existing configuration
        const existingIdx = configuredSelections.findIndex(s => s.id === id);
        if (existingIdx >= 0) {
            configuredSelections.splice(existingIdx, 1);
        }

        // Generate unique variable name with increment
        let uniqueVarName = varName;
        if (selectionArray.length > 1) {
            uniqueVarName = `${varName}||${index + 1}`;
        }

        configuredSelections.push({
            id: id,
            variable_name: uniqueVarName,
            description: context,
            group_id: groupId
        });

        // Apply styling visually to document
        if (id.includes('_col_')) {
            const parts = id.split('_col_');
            const tableId = parts[0];
            const colIdx = parseInt(parts[1]);

            const table = document.getElementById(tableId);
            if (table) {
                for (let r = 0; r < table.rows.length; r++) {
                    const cell = table.rows[r].cells[colIdx];
                    if (cell) cell.classList.add('configured');
                }
            }
            const btn = document.getElementById(`${tableId}_colbtn_${colIdx}`);
            if (btn) btn.classList.add('bg-green-500'); // Indicate configured
        } else {
            const el = document.getElementById(id);
            if (el) el.classList.add('configured');
        }
    });

    updateConfiguredListUI();
    clearSelection();
    updateSelectionUI();
    closeConfigModal();
}

function updateConfiguredListUI() {
    if (configuredSelections.length === 0) {
        els.configuredList.innerHTML = '<p class="text-sm text-slate-400 italic">No fields configured yet.</p>';
        return;
    }

    els.configuredList.innerHTML = '';

    // Group by group_id to show grouped selections together
    const grouped = {};
    configuredSelections.forEach(s => {
        const groupKey = s.group_id || s.id;
        if (!grouped[groupKey]) grouped[groupKey] = [];
        grouped[groupKey].push(s);
    });

    Object.keys(grouped).forEach(groupKey => {
        let group = grouped[groupKey];
        const count = group.length;
        
        // Sort group by variable name numeric suffix to ensure correct order
        if (count > 1) {
            group.sort((a, b) => {
                const aNum = parseInt(a.variable_name.match(/\|\|(\d+)$/)?.[1] || 0);
                const bNum = parseInt(b.variable_name.match(/\|\|(\d+)$/)?.[1] || 0);
                return aNum - bNum;
            });
        }
        
        const baseName = group[0].variable_name.replace(/\|\|\d+$/, '');

        const item = document.createElement('div');
        item.className = 'bg-white border border-slate-200 rounded p-3 shadow-sm';
        
        if (count > 1) {
            // Show all unique variable names for grouped items
            const varNames = group.map(g => g.variable_name).join(', ');
            item.innerHTML = `
                <div class="flex items-center justify-between mb-1">
                    <span class="font-mono text-sm text-blue-700 font-semibold truncate" title="${varNames}">${baseName} (${count} fields)</span>
                    <span class="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded border border-blue-200">Grouped</span>
                </div>
                <p class="text-xs text-slate-400 line-clamp-1 mb-1">Vars: ${varNames}</p>
                <p class="text-xs text-slate-500 line-clamp-2" title="${group[0].description || 'No description'}">
                    ${group[0].description || '<span class="italic opacity-50">No description provided</span>'}
                </p>
            `;
        } else {
            item.innerHTML = `
                <div class="flex items-center justify-between mb-1">
                    <span class="font-mono text-sm text-blue-700 font-semibold truncate" title="${group[0].variable_name}">${group[0].variable_name}</span>
                    <span class="text-xs bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded border border-slate-200">${count} el</span>
                </div>
                <p class="text-xs text-slate-500 line-clamp-2" title="${group[0].description || 'No description'}">
                    ${group[0].description || '<span class="italic opacity-50">No description provided</span>'}
                </p>
            `;
        }
        els.configuredList.appendChild(item);
    });
}

// Initialize Lucide icons when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();
});
