const authService = require('./auth.service');
const { success, error } = require('../../utils/response');

async function register(req, res) {
  try {
    const user = await authService.register(req.body);
    return success(res, user, 'Usuario registrado exitosamente', 201);
  } catch (err) {
    console.error('Auth.register error:', err);
    return error(res, err.message || 'Error al registrar usuario', err.status || 500, err.errors);
  }
}

async function login(req, res) {
  try {
    const result = await authService.login(req.body);
    return success(res, result, 'Inicio de sesión exitoso');
  } catch (err) {
    console.error('Auth.login error:', err);
    return error(res, err.message || 'Error al iniciar sesión', err.status || 500);
  }
}

async function refreshToken(req, res) {
  try {
    const { refreshToken: token } = req.body;
    const result = await authService.refreshToken(token);
    return success(res, result, 'Token renovado exitosamente');
  } catch (err) {
    console.error('Auth.refreshToken error:', err);
    return error(res, err.message || 'Error al renovar token', err.status || 500);
  }
}

async function getProfile(req, res) {
  try {
    const user = await authService.getProfile(req.user.id);
    return success(res, user, 'Perfil obtenido exitosamente');
  } catch (err) {
    console.error('Auth.getProfile error:', err);
    return error(res, err.message || 'Error al obtener perfil', err.status || 500);
  }
}

async function updateProfile(req, res) {
  try {
    const data = req.body || {};
    if (req.file) {
      data.avatar = `/uploads/auth/${req.file.filename}`;
    }
    const user = await authService.updateProfile(req.user.id, data);
    return success(res, user, 'Perfil actualizado exitosamente');
  } catch (err) {
    console.error('Auth.updateProfile error:', err);
    return error(res, err.message || 'Error al actualizar perfil', err.status || 500);
  }
}

async function changePassword(req, res) {
  try {
    const { currentPassword, newPassword } = req.body;
    const result = await authService.changePassword(req.user.id, currentPassword, newPassword);
    return success(res, result, 'Contraseña actualizada exitosamente');
  } catch (err) {
    console.error('Auth.changePassword error:', err);
    return error(res, err.message || 'Error al cambiar contraseña', err.status || 500);
  }
}

async function forgotPassword(req, res) {
  try {
    const result = await authService.forgotPassword(req.body.email);
    return success(res, result, result.message);
  } catch (err) {
    console.error('Auth.forgotPassword error:', err);
    return error(res, err.message || 'Error al procesar solicitud', err.status || 500);
  }
}

async function resetPassword(req, res) {
  try {
    const { token, password } = req.body;
    const result = await authService.resetPassword(token, password);
    return success(res, result, 'Contraseña restablecida exitosamente');
  } catch (err) {
    console.error('Auth.resetPassword error:', err);
    return error(res, err.message || 'Error al restablecer contraseña', err.status || 500);
  }
}

module.exports = {
  register,
  login,
  refreshToken,
  getProfile,
  updateProfile,
  changePassword,
  forgotPassword,
  resetPassword,
};
