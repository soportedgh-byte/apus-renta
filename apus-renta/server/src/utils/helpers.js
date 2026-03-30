/**
 * Formatea un monto numerico a pesos colombianos: $1,234,567
 * @param {number} amount - Monto a formatear
 * @returns {string} Monto formateado
 */
const formatCurrency = (amount) => {
  const num = Number(amount);
  if (isNaN(num)) return '$0';
  return '$' + num.toLocaleString('es-CO', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  });
};

/**
 * Formatea una fecha a DD/MM/YYYY.
 * @param {Date|string} date - Fecha a formatear
 * @returns {string} Fecha formateada
 */
const formatDate = (date) => {
  const d = new Date(date);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  return `${day}/${month}/${year}`;
};

/**
 * Genera una referencia unica de pago: PAG-YYYYMMDD-XXXX
 * @returns {string} Referencia de pago
 */
const generateReference = () => {
  const now = new Date();
  const datePart = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, '0'),
    String(now.getDate()).padStart(2, '0'),
  ].join('');
  const randomPart = Math.random().toString(36).substring(2, 6).toUpperCase();
  return `PAG-${datePart}-${randomPart}`;
};

/**
 * Convierte texto a un slug URL-friendly.
 * @param {string} text - Texto a convertir
 * @returns {string} Slug generado
 */
const slugify = (text) => {
  return String(text)
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '') // eliminar acentos
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, '')   // eliminar caracteres especiales
    .replace(/[\s_]+/g, '-')         // espacios y guiones bajos a guion
    .replace(/-+/g, '-')             // colapsar guiones multiples
    .replace(/^-+|-+$/g, '');        // eliminar guiones al inicio/fin
};

module.exports = {
  formatCurrency,
  formatDate,
  generateReference,
  slugify,
};
