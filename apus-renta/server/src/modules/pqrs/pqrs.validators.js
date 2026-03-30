const { body } = require('express-validator');

const create = [
  body('propertyId')
    .isInt().withMessage('El ID de la propiedad debe ser un entero'),
  body('type')
    .isIn(['PETICION', 'QUEJA', 'RECLAMO', 'SUGERENCIA'])
    .withMessage('Tipo no valido. Debe ser PETICION, QUEJA, RECLAMO o SUGERENCIA'),
  body('subject')
    .notEmpty().withMessage('El asunto es obligatorio')
    .trim(),
  body('description')
    .notEmpty().withMessage('La descripcion es obligatoria')
    .trim(),
];

const update = [
  body('status')
    .isIn(['RADICADA', 'EN_PROCESO', 'RESUELTA', 'CERRADA'])
    .withMessage('Estado no valido'),
  body('resolution')
    .optional()
    .trim(),
];

module.exports = {
  create,
  update,
};
