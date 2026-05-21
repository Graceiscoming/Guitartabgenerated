/**
 * V2 — โปรเจกต์แยกชัด: หน้า Hub → เข้า Editor ทีละเพลง
 */
(function () {
    const STORAGE_KEY = 'guitar_tab_v2_projects_v1';

    function uid(prefix) {
        return `${prefix}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 7)}`;
    }

    function sanitizeFilename(name) {
        return (name || 'untitled').replace(/[^\w\u0E00-\u0E7F-]+/gi, '_').replace(/_+/g, '_').replace(/^_|_$/g, '') || 'untitled';
    }

    function emptyStore() {
        return {
            version: 2,
            activeProjectId: null,
            activeSectionId: null,
            projects: []
        };
    }

    function loadStore() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) return emptyStore();
            const data = JSON.parse(raw);
            if (!Array.isArray(data.projects)) return emptyStore();
            return migrateStore(data);
        } catch (e) {
            console.warn('[V2Project] load failed', e);
            return emptyStore();
        }
    }

    function saveStore(store) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
    }

    function formatSaveTime(iso) {
        if (!iso) return '';
        try {
            return new Date(iso).toLocaleString('th-TH', { dateStyle: 'short', timeStyle: 'short' });
        } catch (e) {
            return iso;
        }
    }

    function migrateStore(store) {
        store.projects.forEach(proj => {
            if (proj.appSavedAt === undefined) proj.appSavedAt = null;
            if (proj.hasUnsavedChanges === undefined) proj.hasUnsavedChanges = !proj.appSavedAt;
            (proj.sections || []).forEach(sec => {
                if (sec.hasUnsavedChanges === undefined) sec.hasUnsavedChanges = !sec.appSavedAt;
                if (sec.appSavedAt === undefined) sec.appSavedAt = null;
                if (sec.pngExportedAt === undefined) sec.pngExportedAt = null;
            });
        });
        if (!store.activeProjectId || !store.projects.find(p => p.id === store.activeProjectId)) {
            store.activeProjectId = null;
            store.activeSectionId = null;
        }
        return store;
    }

    function sortSections(project) {
        project.sections.sort((a, b) => a.order - b.order);
    }

    const V2Project = {
        store: null,
        persistDebounce: null,
        _toastTimer: null,

        init() {
            try {
                this.store = loadStore();
                this.bindUI();
                if (this.store.activeProjectId && this.getProject()) {
                    this.showEditor();
                } else {
                    this.store.activeProjectId = null;
                    this.store.activeSectionId = null;
                    saveStore(this.store);
                    this.showHub();
                }
            } catch (err) {
                console.error('[V2Project] init failed', err);
            }
        },

        bindUI() {
            document.getElementById('btnHubNewProject')?.addEventListener('click', () => this.openModal('modalNewProject'));
            document.getElementById('btnEditorNewSong')?.addEventListener('click', () => this.requestNewProjectFromEditor());
            document.getElementById('btnBackToHub')?.addEventListener('click', () => this.goToHub());
            document.getElementById('btnNewSection')?.addEventListener('click', () => this.openNewSectionFlow());
            document.getElementById('btnDeleteSection')?.addEventListener('click', () => this.deleteCurrentSection());
            document.getElementById('btnSaveWeb')?.addEventListener('click', () => this.saveProjectToWeb());
            document.getElementById('btnSavePng')?.addEventListener('click', () => this.saveSectionAsPng());
            document.getElementById('btnClearSection')?.addEventListener('click', () => this.clearCurrentSection());

            const songTitle = document.getElementById('songTitle');
            const sectionName = document.getElementById('sectionName');
            songTitle?.addEventListener('change', () => this.onSongTitleChange());
            songTitle?.addEventListener('blur', () => this.onSongTitleChange());
            sectionName?.addEventListener('change', () => this.onSectionNameChange());
            sectionName?.addEventListener('blur', () => this.onSectionNameChange());

            document.addEventListener('keydown', (e) => {
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                    e.preventDefault();
                    if (this.isEditorOpen()) this.saveProjectToWeb();
                }
            });

            document.querySelectorAll('[data-modal-close]').forEach(el => {
                el.addEventListener('click', () => this.closeAllModals());
            });
            document.getElementById('btnConfirmNewProject')?.addEventListener('click', () => this.confirmNewProject());
            document.getElementById('btnConfirmNewSection')?.addEventListener('click', () => this.confirmNewSection());
            document.querySelectorAll('.preset-chip').forEach(chip => {
                chip.addEventListener('click', () => {
                    const input = document.getElementById('newSectionNameInput');
                    if (input) input.value = chip.dataset.name || '';
                });
            });
        },

        isEditorOpen() {
            const ed = document.getElementById('projectEditor');
            return ed && !ed.hidden;
        },

        getProject() {
            if (!this.store?.activeProjectId) return null;
            return this.store.projects.find(p => p.id === this.store.activeProjectId) || null;
        },

        getSection(sectionId) {
            const proj = this.getProject();
            if (!proj) return null;
            const id = sectionId || window.__v2ActiveSectionId;
            return proj.sections.find(s => s.id === id) || proj.sections[0] || null;
        },

        showHub() {
            document.getElementById('projectHub')?.removeAttribute('hidden');
            document.getElementById('projectEditor')?.setAttribute('hidden', '');
            document.body.classList.remove('in-project');
            this.renderProjectHub();
        },

        showEditor() {
            const proj = this.getProject();
            if (!proj) {
                this.showHub();
                return;
            }
            if (!this.store.activeSectionId || !proj.sections.find(s => s.id === this.store.activeSectionId)) {
                sortSections(proj);
                this.store.activeSectionId = proj.sections[0]?.id;
            }
            window.__v2ActiveSectionId = this.store.activeSectionId;
            saveStore(this.store);

            document.getElementById('projectHub')?.setAttribute('hidden', '');
            document.getElementById('projectEditor')?.removeAttribute('hidden');
            document.body.classList.add('in-project');

            const songTitle = document.getElementById('songTitle');
            if (songTitle) songTitle.value = proj.title;

            this.renderSectionTabs();
            this.loadSectionIntoEditor(this.store.activeSectionId);
            this.updateProjectStatusBar();
            this.updateSaveStatusUI();
        },

        openProject(projectId) {
            const proj = this.store.projects.find(p => p.id === projectId);
            if (!proj) return;
            this.store.activeProjectId = projectId;
            sortSections(proj);
            this.store.activeSectionId = proj.sections[0]?.id;
            saveStore(this.store);
            this.showEditor();
            this.showToast(`เปิดโปรเจกต์ "${proj.title}"`);
        },

        async goToHub() {
            if (this.isEditorOpen() && this.hasUnsavedChanges()) {
                const ok = confirm('มีการแก้ไขยังไม่บันทึก — ออกจากโปรเจกต์นี้? (กดยกเลิกแล้วบันทึกในเว็บก่อน)');
                if (!ok) return;
            }
            if (this.isEditorOpen()) this.persistCurrentSection();
            this.store.activeProjectId = null;
            this.store.activeSectionId = null;
            saveStore(this.store);
            this.showHub();
        },

        hasUnsavedChanges() {
            const proj = this.getProject();
            if (!proj) return false;
            return proj.hasUnsavedChanges || proj.sections.some(s => s.hasUnsavedChanges);
        },

        requestNewProjectFromEditor() {
            if (this.hasUnsavedChanges()) {
                const ok = confirm('เพลงใหม่ = โปรเจกต์ใหม่แยกต่างหาก\nมีข้อมูลยังไม่บันทึก — ไปต่อ?');
                if (!ok) return;
            }
            this.persistCurrentSection();
            this.store.activeProjectId = null;
            this.store.activeSectionId = null;
            saveStore(this.store);
            this.openModal('modalNewProject');
        },

        renderProjectHub() {
            const list = document.getElementById('projectList');
            const empty = document.getElementById('hubEmpty');
            if (!list) return;

            const projects = [...this.store.projects].sort(
                (a, b) => new Date(b.updatedAt || b.createdAt) - new Date(a.updatedAt || a.createdAt)
            );

            list.innerHTML = '';
            if (projects.length === 0) {
                empty?.removeAttribute('hidden');
                return;
            }
            empty?.setAttribute('hidden', '');

            projects.forEach(proj => {
                const n = proj.sections?.length || 0;
                const saved = proj.appSavedAt;
                const dirty = proj.hasUnsavedChanges || proj.sections.some(s => s.hasUnsavedChanges);
                let status = 'ร่าง';
                if (saved && !dirty) status = 'บันทึกแล้ว';
                else if (dirty) status = 'แก้แล้วยังไม่บันทึก';

                const card = document.createElement('div');
                card.className = 'project-card';
                card.innerHTML = `
                    <div class="project-card-title">${this.escapeHtml(proj.title)}</div>
                    <div class="project-card-meta">${n} แทป/ท่อน · ${status}</div>
                    <div class="project-card-date">${saved ? 'บันทึก ' + formatSaveTime(proj.appSavedAt) : 'ยังไม่เคยบันทึก'}</div>
                    <div class="project-card-actions">
                        <button type="button" class="btn-open-project">เปิดแก้ไข</button>
                        <button type="button" class="btn-delete-project btn-secondary btn-small">ลบ</button>
                    </div>
                `;
                card.querySelector('.btn-open-project').onclick = () => this.openProject(proj.id);
                card.querySelector('.btn-delete-project').onclick = (e) => {
                    e.stopPropagation();
                    this.deleteProject(proj.id);
                };
                list.appendChild(card);
            });
        },

        deleteProject(projectId) {
            const proj = this.store.projects.find(p => p.id === projectId);
            if (!proj) return;
            if (!confirm(`ลบโปรเจกต์ "${proj.title}" ทั้งหมด? กู้คืนไม่ได้`)) return;
            this.store.projects = this.store.projects.filter(p => p.id !== projectId);
            if (this.store.activeProjectId === projectId) {
                this.store.activeProjectId = null;
                this.store.activeSectionId = null;
            }
            saveStore(this.store);
            this.showHub();
            this.showToast('ลบโปรเจกต์แล้ว');
        },

        updateProjectStatusBar() {
            const proj = this.getProject();
            const sec = this.getSection();
            const nameEl = document.getElementById('currentProjectName');
            const secEl = document.getElementById('currentSectionLabel');
            const pill = document.getElementById('projectStatusPill');
            if (!proj || !nameEl) return;

            nameEl.textContent = proj.title;
            if (secEl && sec) secEl.textContent = sec.name;

            if (pill) {
                const dirty = this.hasUnsavedChanges();
                if (dirty) {
                    pill.className = 'status-pill unsaved';
                    pill.textContent = 'แก้แล้วยังไม่บันทึก';
                } else if (proj.appSavedAt) {
                    pill.className = 'status-pill saved';
                    pill.textContent = 'บันทึกในเว็บแล้ว';
                } else {
                    pill.className = 'status-pill draft';
                    pill.textContent = 'ร่าง — ยังไม่บันทึก';
                }
            }
        },

        openModal(id) {
            document.getElementById(id)?.classList.add('open');
        },

        closeAllModals() {
            document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('open'));
        },

        showToast(message) {
            const el = document.getElementById('toast');
            if (!el) return;
            el.textContent = message;
            el.classList.add('show');
            clearTimeout(this._toastTimer);
            this._toastTimer = setTimeout(() => el.classList.remove('show'), 3200);
        },

        escapeHtml(s) {
            return String(s)
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;')
                .replace(/"/g, '&quot;');
        },

        markDirty() {
            const proj = this.getProject();
            const sec = this.getSection();
            if (proj) proj.hasUnsavedChanges = true;
            if (sec) sec.hasUnsavedChanges = true;
        },

        persistCurrentSection() {
            const proj = this.getProject();
            const sec = this.getSection();
            if (!proj || !sec) return;

            sec.sequence = JSON.parse(JSON.stringify(window.manualSequence || []));
            const tabEl = document.getElementById('visual-tab');
            const tabText = tabEl?.innerText?.trim() || '';
            if (tabText && tabText !== 'รอกดปุ่ม Generate...' && !tabText.startsWith('เกิดข้อผิดพลาด')) {
                sec.tabAscii = tabText;
            }
            const sectionNameEl = document.getElementById('sectionName');
            if (sectionNameEl?.value.trim()) sec.name = sectionNameEl.value.trim();

            const songTitle = document.getElementById('songTitle');
            if (songTitle?.value.trim()) proj.title = songTitle.value.trim();

            proj.updatedAt = new Date().toISOString();
            saveStore(this.store);
            this.updateProjectStatusBar();
            this.updateSaveStatusUI();
        },

        schedulePersist() {
            if (!this.isEditorOpen()) return;
            clearTimeout(this.persistDebounce);
            this.persistDebounce = setTimeout(() => this.persistCurrentSection(), 400);
        },

        updateSaveStatusUI() {
            const el = document.getElementById('saveStatus');
            if (!el || !this.isEditorOpen()) return;
            const proj = this.getProject();
            const sec = this.getSection();
            if (!proj) return;

            if (this.hasUnsavedChanges()) {
                el.className = 'unsaved';
                el.textContent = `⚠ โปรเจกต์ "${proj.title}" · ท่อน "${sec?.name}" — ยังไม่บันทึก (Ctrl+S)`;
            } else if (proj.appSavedAt) {
                el.className = 'saved';
                el.textContent = `✓ โปรเจกต์ "${proj.title}" บันทึกแล้ว ${formatSaveTime(proj.appSavedAt)}`;
            } else {
                el.className = 'unsaved';
                el.textContent = `⚠ โปรเจกต์ "${proj.title}" — กดบันทึกในเว็บเมื่อเสร็จ`;
            }
        },

        async saveProjectToWeb() {
            if (!this.getProject()) return;
            this.persistCurrentSection();
            const proj = this.getProject();

            if (!proj.sections.some(s => (s.sequence || []).length > 0)) {
                alert('ยังไม่มีโน้ต — จิ้มคอกีตาร์ในแทป/ท่อนก่อนครับ');
                return;
            }

            const sec = this.getSection();
            const tabEl = document.getElementById('visual-tab');
            let tabText = tabEl?.innerText?.trim() || '';
            if (sec?.sequence?.length && (!tabText || tabText === 'รอกดปุ่ม Generate...')) {
                if (typeof window.generateTab === 'function') {
                    await window.generateTab();
                    tabText = tabEl?.innerText?.trim() || '';
                }
                if (tabText && tabText !== 'รอกดปุ่ม Generate...') sec.tabAscii = tabText;
            }

            const now = new Date().toISOString();
            proj.appSavedAt = now;
            proj.hasUnsavedChanges = false;
            proj.sections.forEach(s => {
                s.appSavedAt = now;
                s.hasUnsavedChanges = false;
            });

            saveStore(this.store);
            this.renderSectionTabs();
            this.updateProjectStatusBar();
            this.updateSaveStatusUI();
            this.showToast(`บันทึกโปรเจกต์ "${proj.title}" ในเว็บแล้ว`);
        },

        onSongTitleChange() {
            const proj = this.getProject();
            if (!proj) return;
            const el = document.getElementById('songTitle');
            if (el) proj.title = el.value.trim() || proj.title;
            this.markDirty();
            saveStore(this.store);
            this.updateProjectStatusBar();
            this.updateSaveStatusUI();
        },

        onSectionNameChange() {
            const sec = this.getSection();
            const el = document.getElementById('sectionName');
            if (sec && el) {
                sec.name = el.value.trim() || sec.name;
                this.markDirty();
                saveStore(this.store);
                this.renderSectionTabs();
                this.updateProjectStatusBar();
                this.updateSaveStatusUI();
            }
        },

        renderSectionTabs() {
            const bar = document.getElementById('sectionTabs');
            const proj = this.getProject();
            if (!bar || !proj) return;
            bar.innerHTML = '';
            sortSections(proj);

            proj.sections.forEach(sec => {
                const btn = document.createElement('button');
                btn.type = 'button';
                btn.className = 'section-tab' + (sec.id === window.__v2ActiveSectionId ? ' active' : '');
                let icon = sec.hasUnsavedChanges ? '• ' : (sec.appSavedAt ? '💾 ' : '• ');
                if (sec.pngExportedAt) icon += '🖼 ';
                btn.textContent = icon + sec.name;
                btn.onclick = () => this.switchSection(sec.id);
                bar.appendChild(btn);
            });

            const countEl = document.getElementById('sectionCountLabel');
            if (countEl) countEl.textContent = `${proj.sections.length} แทปในโปรเจกต์นี้`;
        },

        loadSectionIntoEditor(sectionId) {
            const proj = this.getProject();
            const sec = proj?.sections.find(s => s.id === sectionId);
            if (!sec) return;

            window.__v2ActiveSectionId = sectionId;
            this.store.activeSectionId = sectionId;
            window.manualSequence = JSON.parse(JSON.stringify(sec.sequence || []));

            const sectionName = document.getElementById('sectionName');
            if (sectionName) sectionName.value = sec.name;

            const tabEl = document.getElementById('visual-tab');
            if (tabEl) tabEl.innerText = sec.tabAscii || 'รอกดปุ่ม Generate...';

            if (typeof window.renderList === 'function') window.renderList();
            saveStore(this.store);
            this.renderSectionTabs();
            this.updateProjectStatusBar();
            this.updateSaveStatusUI();
        },

        switchSection(sectionId) {
            if (sectionId === window.__v2ActiveSectionId) return;
            this.persistCurrentSection();
            this.loadSectionIntoEditor(sectionId);
        },

        confirmNewProject() {
            const input = document.getElementById('newProjectTitleInput');
            const title = (input?.value || '').trim();
            if (!title) {
                alert('กรุณาตั้งชื่อเพลง / โปรเจกต์ก่อนครับ');
                return;
            }

            const projId = uid('proj');
            const secId = uid('sec');
            const project = {
                id: projId,
                title,
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
                appSavedAt: null,
                hasUnsavedChanges: true,
                sections: [{
                    id: secId,
                    name: 'Intro',
                    order: 0,
                    status: 'draft',
                    sequence: [],
                    tabAscii: null,
                    appSavedAt: null,
                    pngExportedAt: null,
                    hasUnsavedChanges: true
                }]
            };

            this.store.projects.unshift(project);
            this.store.activeProjectId = projId;
            this.store.activeSectionId = secId;
            saveStore(this.store);
            this.closeAllModals();
            if (input) input.value = '';
            this.showEditor();
            this.showToast(`สร้างโปรเจกต์ "${title}" — เพิ่ม/ลบแทปได้ในโปรเจกต์นี้เท่านั้น`);
        },

        openNewSectionFlow() {
            const proj = this.getProject();
            if (!proj) return;
            const input = document.getElementById('newSectionNameInput');
            if (input) input.value = `แทป ${proj.sections.length + 1}`;
            this.openModal('modalNewSection');
        },

        confirmNewSection() {
            const proj = this.getProject();
            if (!proj) return;
            const input = document.getElementById('newSectionNameInput');
            const name = (input?.value || '').trim() || 'แทปใหม่';
            this.persistCurrentSection();

            const secId = uid('sec');
            const maxOrder = proj.sections.reduce((m, s) => Math.max(m, s.order), -1);
            proj.sections.push({
                id: secId,
                name,
                order: maxOrder + 1,
                status: 'draft',
                sequence: [],
                tabAscii: null,
                appSavedAt: null,
                pngExportedAt: null,
                hasUnsavedChanges: true
            });
            this.markDirty();
            saveStore(this.store);
            this.closeAllModals();
            if (input) input.value = '';
            this.loadSectionIntoEditor(secId);
            this.showToast(`เพิ่มแทป "${name}" ในโปรเจกต์นี้`);
        },

        deleteCurrentSection() {
            const proj = this.getProject();
            if (!proj || proj.sections.length <= 1) {
                alert('ต้องมีอย่างน้อย 1 แทปในโปรเจกต์');
                return;
            }
            const sec = this.getSection();
            if (!confirm(`ลบแทป "${sec.name}" ออกจากโปรเจกต์นี้?`)) return;

            const idx = proj.sections.findIndex(s => s.id === sec.id);
            proj.sections.splice(idx, 1);
            sortSections(proj);
            proj.sections.forEach((s, i) => { s.order = i; });
            this.markDirty();

            const next = proj.sections[Math.min(idx, proj.sections.length - 1)];
            this.store.activeSectionId = next.id;
            saveStore(this.store);
            this.loadSectionIntoEditor(next.id);
            this.showToast('ลบแทปแล้ว');
        },

        clearCurrentSection() {
            if (!confirm('ล้างโน้ตและแทปของแทปนี้?')) return;
            window.manualSequence = [];
            const sec = this.getSection();
            if (sec) {
                sec.sequence = [];
                sec.tabAscii = null;
                sec.hasUnsavedChanges = true;
            }
            this.markDirty();
            document.getElementById('isSlide').checked = false;
            document.getElementById('visual-tab').innerText = 'รอกดปุ่ม Generate...';
            if (typeof window.renderList === 'function') window.renderList();
            saveStore(this.store);
            this.renderSectionTabs();
            this.updateProjectStatusBar();
            this.updateSaveStatusUI();
        },

        buildExportFilename(proj, sec) {
            const order = String((sec.order ?? 0) + 1).padStart(2, '0');
            return `${sanitizeFilename(proj.title)}_${order}_${sanitizeFilename(sec.name)}.png`;
        },

        buildExportCardHtml(proj, sec, tabText) {
            const dateStr = new Date().toLocaleString('th-TH');
            const noteCount = (sec.sequence || []).length;
            return `
                <div style="font-family: 'Segoe UI', Arial, sans-serif; padding: 28px 32px; background: #1a1a1a; color: #fff; min-width: 520px;">
                    <div style="font-size: 22px; font-weight: 600; color: #FF5722;">${this.escapeHtml(proj.title)}</div>
                    <div style="font-size: 16px; color: #ccc; margin: 20px 0;">แทป: ${this.escapeHtml(sec.name)}</div>
                    <pre style="margin:0;padding:20px;background:#0d0d0d;border-radius:8px;font-family:Consolas,monospace;font-size:15px;color:#fff;white-space:pre;border:1px solid #333;">${this.escapeHtml(tabText)}</pre>
                    <div style="margin-top:16px;font-size:12px;color:#888;">${noteCount} โน้ต · ${dateStr}</div>
                </div>`;
        },

        async saveSectionAsPng() {
            if (!window.manualSequence?.length) {
                alert('กรุณาเพิ่มโน้ตก่อน');
                return;
            }
            const proj = this.getProject();
            const sec = this.getSection();
            const tabEl = document.getElementById('visual-tab');
            let tabText = tabEl?.innerText?.trim() || '';
            if (!tabText || tabText === 'รอกดปุ่ม Generate...') {
                if (typeof window.generateTab === 'function') await window.generateTab();
                tabText = tabEl?.innerText?.trim() || '';
            }
            if (!tabText || tabText === 'รอกดปุ่ม Generate...') {
                alert('กด Generate ก่อนครับ');
                return;
            }

            this.persistCurrentSection();
            sec.tabAscii = tabText;

            const card = document.getElementById('export-card');
            card.innerHTML = this.buildExportCardHtml(proj, sec, tabText);
            card.style.display = 'block';

            if (typeof html2canvas !== 'function') {
                alert('โหลด html2canvas ไม่ได้ — ต้องมีเน็ต');
                card.style.display = 'none';
                return;
            }

            try {
                const canvas = await html2canvas(card, { backgroundColor: '#1a1a1a', scale: 2, logging: false });
                canvas.toBlob(blob => {
                    if (!blob) return;
                    const link = document.createElement('a');
                    link.href = URL.createObjectURL(blob);
                    link.download = this.buildExportFilename(proj, sec);
                    link.click();
                    URL.revokeObjectURL(link.href);
                    sec.pngExportedAt = new Date().toISOString();
                    saveStore(this.store);
                    this.renderSectionTabs();
                    this.updateSaveStatusUI();
                }, 'image/png');
            } catch (err) {
                alert('Export ไม่สำเร็จ: ' + err.message);
            } finally {
                card.style.display = 'none';
                card.innerHTML = '';
            }
        },

        onSequenceChanged() {
            if (!this.isEditorOpen()) return;
            this.markDirty();
            this.schedulePersist();
            this.renderSectionTabs();
            this.updateProjectStatusBar();
            this.updateSaveStatusUI();
        },

        async onTabGenerated(tabText) {
            const sec = this.getSection();
            if (sec) sec.tabAscii = tabText;
            this.onSequenceChanged();
        }
    };

    window.V2Project = V2Project;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => V2Project.init());
    } else {
        V2Project.init();
    }
})();
