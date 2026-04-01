const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const prisma = require('../../config/database');

const SALT_ROUNDS = 12;
const MAX_LOGIN_ATTEMPTS = 5;
const LOCK_DURATION_MINUTES = 30;

/**
 * Register a new user.
 */
async function register({ email, password, firstName, lastName, role, tenantId }) {
  const existing = await prisma.user.findUnique({ where: { email } });
  if (existing) {
    throw { status: 409, message: 'El correo electrónico ya está registrado' };
  }

  const hashedPassword = await bcrypt.hash(password, SALT_ROUNDS);

  const user = await prisma.user.create({
    data: {
      email,
      passwordHash: hashedPassword,
      firstName,
      lastName,
      role: role || 'ARRENDATARIO',
      tenantId,
    },
  });

  // If the role is ARRENDATARIO, also create a TenantPerson record
  if ((role || 'ARRENDATARIO') === 'ARRENDATARIO') {
    await prisma.tenantPerson.create({
      data: {
        userId: user.id,
        documentType: 'CC',
        documentNumber: '',
      },
    });
  }

  const { passwordHash: _, ...userWithoutPassword } = user;
  return userWithoutPassword;
}

/**
 * Authenticate a user and return tokens.
 */
async function login({ email, password }) {
  const user = await prisma.user.findUnique({ where: { email } });
  if (!user) {
    throw { status: 401, message: 'Credenciales inválidas' };
  }

  // Check account status
  if (user.status === 'BLOCKED') {
    throw { status: 403, message: 'La cuenta está bloqueada. Contacte al administrador' };
  }
  if (user.status === 'INACTIVE') {
    throw { status: 403, message: 'La cuenta está inactiva' };
  }

  // Check if account is temporarily locked
  if (user.lockedUntil && user.lockedUntil > new Date()) {
    throw { status: 423, message: 'La cuenta está temporalmente bloqueada. Intente más tarde' };
  }

  // Verify password
  const isValid = await bcrypt.compare(password, user.passwordHash);
  if (!isValid) {
    const failedAttempts = (user.failedLoginAttempts || 0) + 1;
    const updateData = { failedLoginAttempts: failedAttempts };

    if (failedAttempts >= MAX_LOGIN_ATTEMPTS) {
      updateData.lockedUntil = new Date(Date.now() + LOCK_DURATION_MINUTES * 60 * 1000);
    }

    await prisma.user.update({
      where: { id: user.id },
      data: updateData,
    });

    throw { status: 401, message: 'Credenciales inválidas' };
  }

  // Successful login: reset attempts and update lastLoginAt
  await prisma.user.update({
    where: { id: user.id },
    data: {
      failedLoginAttempts: 0,
      lockedUntil: null,
      lastLoginAt: new Date(),
    },
  });

  const accessToken = generateAccessToken(user);
  const refreshToken = generateRefreshToken(user);

  const { passwordHash: _, ...userWithoutPassword } = user;
  return { user: userWithoutPassword, accessToken, refreshToken };
}

/**
 * Refresh an access token using a valid refresh token.
 */
async function refreshToken(token) {
  if (!token) {
    throw { status: 400, message: 'Refresh token es obligatorio' };
  }

  let payload;
  try {
    payload = jwt.verify(token, process.env.JWT_REFRESH_SECRET || process.env.JWT_SECRET);
  } catch {
    throw { status: 401, message: 'Refresh token inválido o expirado' };
  }

  const user = await prisma.user.findUnique({ where: { id: payload.id } });
  if (!user) {
    throw { status: 401, message: 'Usuario no encontrado' };
  }

  const accessToken = generateAccessToken(user);
  return { accessToken };
}

/**
 * Get user profile with tenant information.
 */
async function getProfile(userId) {
  const user = await prisma.user.findUnique({
    where: { id: userId },
    include: {
      tenantPerson: true,
      tenant: true,
    },
  });

  if (!user) {
    throw { status: 404, message: 'Usuario no encontrado' };
  }

  const { passwordHash: _, ...userWithoutPassword } = user;
  return userWithoutPassword;
}

/**
 * Update allowed profile fields.
 */
async function updateProfile(userId, data) {
  const allowedFields = ['firstName', 'lastName', 'phone', 'avatar'];
  const updateData = {};
  for (const field of allowedFields) {
    if (data[field] !== undefined) {
      updateData[field] = data[field];
    }
  }

  const user = await prisma.user.update({
    where: { id: userId },
    data: updateData,
  });

  const { passwordHash: _, ...userWithoutPassword } = user;
  return userWithoutPassword;
}

/**
 * Change user password after verifying the current one.
 */
async function changePassword(userId, currentPassword, newPassword) {
  const user = await prisma.user.findUnique({ where: { id: userId } });
  if (!user) {
    throw { status: 404, message: 'Usuario no encontrado' };
  }

  const isValid = await bcrypt.compare(currentPassword, user.passwordHash);
  if (!isValid) {
    throw { status: 401, message: 'La contraseña actual es incorrecta' };
  }

  const hashedPassword = await bcrypt.hash(newPassword, SALT_ROUNDS);
  await prisma.user.update({
    where: { id: userId },
    data: { passwordHash: hashedPassword },
  });

  return { message: 'Contraseña actualizada correctamente' };
}

/**
 * Generate a password reset token and send email (placeholder).
 */
async function forgotPassword(email) {
  // TODO: Implement password reset with email token
  // For now, return a generic message to prevent email enumeration
  return { message: 'Si el correo existe, recibirá instrucciones para restablecer su contraseña' };
}

/**
 * Reset password using a valid reset token.
 */
async function resetPassword(token, password) {
  // TODO: Implement token-based password reset
  // Requires adding resetToken/resetTokenExpiry fields to Prisma schema
  throw { status: 501, message: 'Funcionalidad de restablecimiento de contraseña aún no implementada' };
}

// --- Helpers ---

function generateAccessToken(user) {
  return jwt.sign(
    { id: user.id, tenantId: user.tenantId, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_EXPIRES_IN || '15m' }
  );
}

function generateRefreshToken(user) {
  return jwt.sign(
    { id: user.id, tenantId: user.tenantId, role: user.role },
    process.env.JWT_REFRESH_SECRET || process.env.JWT_SECRET,
    { expiresIn: process.env.JWT_REFRESH_EXPIRES_IN || '7d' }
  );
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
