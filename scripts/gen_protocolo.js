const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, ImageRun,
  Table, TableRow, TableCell, WidthType, AlignmentType, ShadingType,
  LevelFormat, BorderStyle,
} = require("docx");

const IMG = {
  framing: "runs/externo_in/lateblightTom_lesion_jpg.rf.aab882d46e684bf40a99f3e89b4730ec.jpg",
  lesiones: "runs/detect/runs/pruebas/externo/tomato_D2b-Early-blight---RPitblado_zoom_jpg.rf.034713d2b2b80c355aee74ac97ce5623.jpg",
  minador: "runs/detect/runs/pruebas/pred/tom_005706.jpg",
};

function bullet(text, bold) {
  return new Paragraph({
    numbering: { reference: "lista", level: 0 },
    spacing: { after: 80 },
    children: [new TextRun({ text, bold: !!bold })],
  });
}

function parr(runs, opts = {}) {
  return new Paragraph({ spacing: { after: 120 }, ...opts, children: runs });
}

function img(path, w, h, caption) {
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 100, after: 40 },
      children: [new ImageRun({ type: "jpg", data: fs.readFileSync(path), transformation: { width: w, height: h } })],
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 160 },
      children: [new TextRun({ text: caption, italics: true, size: 18, color: "555555" })],
    }),
  ];
}

function cell(text, widthDxa, header) {
  return new TableCell({
    width: { size: widthDxa, type: WidthType.DXA },
    shading: header ? { type: ShadingType.CLEAR, fill: "2E7D32", color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    children: [new Paragraph({ children: [new TextRun({ text, bold: !!header, color: header ? "FFFFFF" : "000000", size: 20 })] })],
  });
}

function filaSiNo(si, no) {
  return new TableRow({
    children: [cell(si, 4680), cell(no, 4680)],
  });
}

const H = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 100 }, children: [new TextRun({ text: t, color: "2E7D32" })] });

const doc = new Document({
  numbering: {
    config: [{
      reference: "lista",
      levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 420, hanging: 240 } } } }],
    }],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1300, bottom: 1300, left: 1300, right: 1300 } } },
    children: [
      new Paragraph({ heading: HeadingLevel.TITLE, spacing: { after: 60 }, children: [new TextRun({ text: "Cómo tomar y etiquetar fotos para la IA", color: "1B5E20" })] }),
      new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: "Proyecto TerraOrbis — Modelo de tomate · Guía sencilla de campo", italics: true, color: "555555" })] }),

      parr([new TextRun({ text: "¿Para qué sirve esto? ", bold: true }), new TextRun("La inteligencia artificial del robot ya detecta bien varias enfermedades, pero para mejorar necesita fotos REALES tomadas por nosotros en el campo. Sobre todo de: mancha bacteriana, deficiencias de nutrientes (magnesio, nitrógeno, potasio), minador de hoja y spotted wilt. Regla de oro: entre más fotos reales y variadas, mejor aprende.")]),

      H("1. Cómo tomar las fotos"),
      bullet("Acércate a la hoja para que la mancha o el daño LLENE la foto (no fotos lejanas de toda la planta).", true),
      bullet("Enfoca bien y mantén el pulso firme (fotos nítidas, sin movida)."),
      bullet("Toma la hoja por ARRIBA (haz) y también por ABAJO (envés) — muchas lesiones se ven distinto del otro lado."),
      bullet("Varía el ángulo: de frente, y también inclinada (como a 30° y 45°)."),
      bullet("Varía la luz: toma en la mañana/tarde (luz suave) y al mediodía (luz fuerte con sombras)."),
      bullet("Toma TAMBIÉN hojas y plantas SANAS: le enseñan a la IA a no inventar enfermedades."),
      bullet("Muchas fotos: la meta son cientos por cada enfermedad (varias plantas, varios días)."),
      bullet("NO edites ni gires las fotos de cabeza. Guárdalas tal cual, en una carpeta por enfermedad."),
      ...img(IMG.framing, 300, 300, "Ejemplo de una buena foto: de cerca, la hoja enferma llena el cuadro y está enfocada."),

      H("2. Cómo etiquetar las fotos"),
      parr([new TextRun("Etiquetar = marcar en cada foto dónde está la enfermedad. Lo haremos en "), new TextRun({ text: "Roboflow", bold: true }), new TextRun(" (roboflow.com, cuenta gratis, desde el navegador).")]),
      bullet("Sube tus fotos a un proyecto de Roboflow (tipo \"Object Detection\")."),
      bullet("Dibuja una CAJA ajustada alrededor de cada lesión o grupo de lesiones. No marques toda la hoja: solo la parte dañada."),
      bullet("Minador de hoja: la caja envuelve TODA el área con las galerías blancas (no cada curvita por separado)."),
      bullet("Deficiencias (Mg/N/K): la caja cubre la zona amarillenta o quemada."),
      bullet("Ponle a cada caja el NOMBRE correcto de la enfermedad (la misma palabra siempre)."),
      bullet("Hojas sanas: déjalas SIN ninguna caja."),
      bullet("Al terminar, exporta en formato \"YOLOv8\" y pásame el archivo."),
      ...img(IMG.lesiones, 290, 290, "Lesiones marcadas con cajas ajustadas (cada mancha dentro de su caja, sin incluir hoja sana de más)."),
      ...img(IMG.minador, 290, 290, "Minador de hoja: la caja envuelve toda el área con galerías, no cada línea."),

      H("3. Resumen rápido: Sí / No"),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [4680, 4680],
        rows: [
          new TableRow({ tableHeader: true, children: [cell("HAZ esto", 4680, true), cell("EVITA esto", 4680, true)] }),
          filaSiNo("Acercarte a la hoja (que llene la foto)", "Fotos lejanas de toda la planta"),
          filaSiNo("Fotos nítidas y enfocadas", "Fotos movidas o borrosas"),
          filaSiNo("Tomar haz y envés, varios ángulos y luces", "Solo una foto de frente con una luz"),
          filaSiNo("Incluir hojas sanas (sin cajas)", "Solo fotografiar enfermas"),
          filaSiNo("Cajas ajustadas a la lesión", "Marcar toda la hoja completa"),
          filaSiNo("Mismo nombre de clase siempre", "Nombres distintos para lo mismo"),
        ],
      }),

      H("Checklist antes de empezar"),
      bullet("Celular con buena cámara y batería."),
      bullet("Una carpeta por enfermedad (ej: \"mancha_bacteriana\", \"deficiencia_magnesio\")."),
      bullet("Fotografiar de cerca, nítido, haz y envés, varias luces."),
      bullet("Incluir plantas sanas."),
      bullet("Subir a Roboflow, marcar cajas, exportar en YOLOv8 y enviar."),
      parr([new TextRun({ text: "Cualquier duda, pregúntame y te ayudo paso a paso. ", italics: true, color: "555555" })], { spacing: { before: 160 } }),
    ],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Protocolo_Fotos_Tomate.docx", buf);
  console.log("OK: Protocolo_Fotos_Tomate.docx");
});
