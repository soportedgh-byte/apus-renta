const htmlPdfNode = require('html-pdf-node');

/**
 * Genera un buffer PDF a partir de contenido HTML.
 * @param {string} htmlContent - Cadena HTML para convertir a PDF
 * @returns {Promise<Buffer>} Buffer con el contenido del PDF
 */
const generatePDF = async (htmlContent) => {
  const file = { content: htmlContent };

  const options = {
    format: 'A4',
    margin: {
      top: '20mm',
      right: '15mm',
      bottom: '20mm',
      left: '15mm',
    },
    printBackground: true,
  };

  const pdfBuffer = await htmlPdfNode.generatePdf(file, options);
  return pdfBuffer;
};

module.exports = { generatePDF };
