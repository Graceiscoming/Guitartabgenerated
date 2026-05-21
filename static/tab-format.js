/**
 * จัดรูปแบบแทปมาตรฐาน — คอลัมน์เท่ากันทุกสาย
 */
(function (global) {
    function legatoSegment(pos) {
        if (pos.legatoToFret == null) return null;
        const link = pos.legatoType === 'pull' ? 'p' : 'h';
        return `${pos.fret}${link}${pos.legatoToFret}`;
    }

    function appendColumn(lines, getCell) {
        const cells = {};
        let maxW = 0;
        for (let s = 1; s <= 6; s++) {
            cells[s] = getCell(s);
            maxW = Math.max(maxW, cells[s].length);
        }
        for (let s = 1; s <= 6; s++) {
            const c = cells[s];
            lines[s] += c + '-'.repeat(Math.max(0, maxW - c.length));
        }
    }

    function drawTabFromSequence(seq) {
        if (!seq?.length) return '';
        const lines = { 1: 'e|', 2: 'B|', 3: 'G|', 4: 'D|', 5: 'A|', 6: 'E|' };

        seq.forEach((pos, idx) => {
            const seg = legatoSegment(pos);
            if (seg) {
                appendColumn(lines, (s) => (s === pos.string ? `-${seg}-` : '-'));
                return;
            }
            if (pos.slideToFret != null) {
                const token = `${pos.fret}/${pos.slideToFret}`;
                appendColumn(lines, (s) => (s === pos.string ? `-${token}-` : '-'));
                return;
            }
            const fretStr = String(pos.fret);
            const isSlide = pos.modifier === '/';
            const slideNext =
                idx + 1 < seq.length &&
                seq[idx + 1].modifier === '/' &&
                seq[idx + 1].string === pos.string;
            appendColumn(lines, (s) => {
                if (s !== pos.string) return '-';
                return (isSlide ? '/' : '-') + fretStr + (slideNext ? '' : '-');
            });
        });

        return [1, 2, 3, 4, 5, 6].map((s) => lines[s] + '---|').join('\n');
    }

    function drawFromApiPath(tabData) {
        if (!tabData?.length) return '';
        return drawTabFromSequence(
            tabData.map((p) => ({
                string: p.string,
                fret: p.fret,
                modifier: p.modifier,
                slideToFret: p.slideToFret,
                legatoToFret: p.legatoToFret,
                legatoType:
                    p.legatoType ||
                    (p.modifier === 'pull' ? 'pull' : p.modifier === 'hammer' ? 'hammer' : null),
            }))
        );
    }

    function defaultMeta(proj) {
        return {
            title: proj?.title || 'Untitled',
            artist: proj?.artist || '',
            tuning: proj?.tuning || 'E A D G B E',
            capo: proj?.capo || '',
            tempo: proj?.tempo || '',
        };
    }

    function buildSongHeader(proj) {
        const m = defaultMeta(proj);
        const lines = [
            '══════════════════════════════════════',
            `  ${m.title}`,
        ];
        if (m.artist) lines.push(`  Artist: ${m.artist}`);
        lines.push(`  Tuning: ${m.tuning}`);
        if (m.capo) lines.push(`  Capo: ${m.capo}`);
        if (m.tempo) lines.push(`  Tempo: ${m.tempo}`);
        lines.push('══════════════════════════════════════');
        return lines.join('\n');
    }

    function buildSectionBlock(sec, tabText) {
        const name = sec?.name || 'Section';
        const body = tabText?.trim() || '(ว่าง)';
        return `\n[ ${name} ]\n${'─'.repeat(40)}\n${body}\n`;
    }

    function buildFullSongDocument(proj, sectionsWithTabs) {
        let doc = buildSongHeader(proj);
        sectionsWithTabs.forEach(({ section, tabText }) => {
            doc += buildSectionBlock(section, tabText);
        });
        doc += `\nGenerated: ${new Date().toLocaleString('th-TH')}\n`;
        return doc;
    }

    function downloadText(filename, content) {
        const link = document.createElement('a');
        link.href = URL.createObjectURL(new Blob([content], { type: 'text/plain;charset=utf-8' }));
        link.download = filename;
        link.click();
        URL.revokeObjectURL(link.href);
    }

    global.TabFormat = {
        legatoSegment,
        drawTabFromSequence,
        drawFromApiPath,
        buildSongHeader,
        buildSectionBlock,
        buildFullSongDocument,
        downloadText,
        defaultMeta,
    };
})(window);
