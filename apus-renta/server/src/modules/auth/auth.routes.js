const router = require('express').Router();
const controller = require('./auth.controller');
const { validate } = require('../../middleware/validate');
const validators = require('./auth.validators');
const { verifyToken } = require('../../middleware/auth');

router.post('/register', validators.register, validate, controller.register);
router.post('/login', validators.login, validate, controller.login);
router.post('/refresh-token', controller.refreshToken);
router.post('/forgot-password', validators.forgotPassword, validate, controller.forgotPassword);
router.post('/reset-password', validators.resetPassword, validate, controller.resetPassword);
router.get('/me', verifyToken, controller.getProfile);
router.put('/me', verifyToken, controller.updateProfile);
router.put('/change-password', verifyToken, validators.changePassword, validate, controller.changePassword);

module.exports = router;
