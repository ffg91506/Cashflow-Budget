// Shared builders for Financial Reviewer Word deliverables.
const d = require('docx');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType,
        BorderStyle, AlignmentType, LevelFormat, HeadingLevel } = d;

const ACCENT = '1D4E89', INK = '1F2933', MUTED = '5F6B7A', BAND = 'EEF2F7', LINE = 'C9D1DC';
const GOOD = '1E7A46', WARN = 'B26B00', BAD = 'B42318';
const PAGE_W = 12240, MARGIN = 900, CONTENT_W = PAGE_W - 2 * MARGIN; // 10440 DXA

// Inline markup: **bold**
function runs(text, opts = {}) {
  const parts = String(text).split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
  return parts.map(p => p.startsWith('**')
    ? new TextRun({ text: p.slice(2, -2), bold: true, ...opts })
    : new TextRun({ text: p, ...opts }));
}
const title = (t) => new Paragraph({ heading: HeadingLevel.TITLE, children: runs(t) });
const subtitle = (t) => new Paragraph({ spacing: { after: 120 }, children: runs(t, { color: MUTED, size: 18 }) });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(t) });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(t) });
const h3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: runs(t) });
const p = (t, o = {}) => new Paragraph({ spacing: { after: 80 }, children: runs(t, o) });
const small = (t) => new Paragraph({ spacing: { before: 80 }, children: runs(t, { color: MUTED, size: 15 }) });
const bullet = (t) => new Paragraph({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 30 }, children: runs(t) });
const num = (t, ref = 'nums') => new Paragraph({ numbering: { reference: ref, level: 0 }, spacing: { after: 30 }, children: runs(t, { bold: true }) });
const status = (label, color) => [new TextRun({ text: '● ', color }), new TextRun({ text: label })];

const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const borders = { top: border, bottom: border, left: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' }, right: { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' } };

// rows: array of arrays; each cell is string (markup ok) or {runs:[TextRun...]} ; widths in DXA summing to CONTENT_W
function table(rows, widths, { head = true, right = [], lastBand = false } = {}) {
  const total = widths.reduce((a, b) => a + b, 0);
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map((row, ri) => new TableRow({
      tableHeader: head && ri === 0,
      children: row.map((c, ci) => {
        const isHead = head && ri === 0;
        const band = isHead || (lastBand && ri === rows.length - 1);
        const kids = (c && c.runs) ? c.runs : runs(c ?? '', { bold: isHead || undefined, size: 17 });
        return new TableCell({
          borders, width: { size: widths[ci], type: WidthType.DXA },
          shading: band ? { fill: BAND, type: ShadingType.CLEAR, color: 'auto' } : undefined,
          margins: { top: 30, bottom: 30, left: 80, right: 80 },
          children: [new Paragraph({ alignment: right.includes(ci) ? AlignmentType.RIGHT : AlignmentType.LEFT, children: kids })],
        });
      }),
    })),
  });
}
const gap = (n = 80) => new Paragraph({ spacing: { after: n }, children: [] });

function doc(children, { numRefs = ['nums'] } = {}) {
  return new Document({
    styles: {
      default: { document: { run: { font: 'Arial', size: 18, color: INK } } },
      paragraphStyles: [
        { id: 'Title', name: 'Title', basedOn: 'Normal', run: { size: 32, bold: true, color: ACCENT, font: 'Arial' }, paragraph: { spacing: { after: 40 } } },
        { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 24, bold: true, color: ACCENT, font: 'Arial' }, paragraph: { spacing: { before: 150, after: 60 }, outlineLevel: 0, border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: ACCENT, space: 2 } } } },
        { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 20, bold: true, color: ACCENT, font: 'Arial' }, paragraph: { spacing: { before: 140, after: 60 }, outlineLevel: 1 } },
        { id: 'Heading3', name: 'Heading 3', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { size: 18, bold: true, color: INK, font: 'Arial' }, paragraph: { spacing: { before: 100, after: 40 }, outlineLevel: 2 } },
      ],
    },
    numbering: {
      config: [
        { reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 220 } } } }] },
        ...numRefs.map(ref => ({ reference: ref, levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 360, hanging: 260 } } } }] })),
      ],
    },
    sections: [{ properties: { page: { size: { width: PAGE_W, height: 15840 }, margin: { top: 560, bottom: 560, left: MARGIN, right: MARGIN } } }, children }],
  });
}
async function save(document, path) { require('fs').writeFileSync(path, await Packer.toBuffer(document)); }

module.exports = { d, title, subtitle, h1, h2, h3, p, small, bullet, num, status, table, gap, doc, save, runs,
  GOOD, WARN, BAD, MUTED, CONTENT_W };
