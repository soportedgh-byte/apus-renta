const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Configuracion de almacenamiento en disco
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    // Determinar subdirectorio segun la entidad (e.g., properties, tenants, payments)
    const entity = req.baseUrl.split('/').pop() || 'general';
    const uploadDir = path.join(__dirname, '../../uploads', entity);

    // Crear directorio si no existe
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }

    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = `${Date.now()}-${Math.round(Math.random() * 1e9)}`;
    const ext = path.extname(file.originalname);
    cb(null, `${file.fieldname}-${uniqueSuffix}${ext}`);
  },
});

// Filtro de tipos de archivo permitidos
const fileFilter = (req, file, cb) => {
  const allowedMimes = [
    // Imagenes
    'image/jpeg',
    'image/jpg',
    'image/png',
    'image/gif',
    'image/webp',
    // PDF
    'application/pdf',
    // Documentos comunes
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/csv',
  ];

  if (allowedMimes.includes(file.mimetype)) {
    cb(null, true);
  } else {
    cb(new Error('Tipo de archivo no permitido. Se aceptan: imagenes (jpg, png, gif, webp), PDF y documentos (doc, docx, xls, xlsx, csv)'), false);
  }
};

// Configuracion base de multer
const upload = multer({
  storage,
  fileFilter,
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB
  },
});

/**
 * Sube un solo archivo con el nombre de campo indicado.
 * @param {string} fieldName - Nombre del campo del formulario
 */
const uploadSingle = (fieldName) => upload.single(fieldName);

/**
 * Sube multiples archivos con el nombre de campo indicado.
 * @param {string} fieldName - Nombre del campo del formulario
 * @param {number} maxCount - Numero maximo de archivos (default: 5)
 */
const uploadMultiple = (fieldName, maxCount = 5) => upload.array(fieldName, maxCount);

module.exports = {
  uploadSingle,
  uploadMultiple,
};
