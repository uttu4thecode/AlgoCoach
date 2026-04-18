import { pythonAPI } from './api';

export const registerUser = async (name, email, password, college, batch) => {
  const res = await pythonAPI.post('/auth/register', {
    name,
    email,
    password,
    college,
    batch,
  });

  persistAuth(res.data);
  return res.data;
};

export const loginUser = async (email, password) => {
  const res = await pythonAPI.post('/auth/login', { email, password });

  persistAuth(res.data);
  return res.data;
};

export const logoutUser = () => {
  localStorage.removeItem('algocoach_token');
  localStorage.removeItem('algocoach_user');
};

export const isLoggedIn = () => !!localStorage.getItem('algocoach_token');

export const getCurrentUser = () => {
  const user = localStorage.getItem('algocoach_user');

  if (!user) {
    return null;
  }

  try {
    return JSON.parse(user);
  } catch {
    logoutUser();
    return null;
  }
};

export const fetchCurrentUser = async () => {
  const res = await pythonAPI.get('/auth/me');
  const existingUser = getCurrentUser() || {};

  localStorage.setItem(
    'algocoach_user',
    JSON.stringify({
      ...existingUser,
      ...res.data,
      role: res.data.role || existingUser.role || 'Learner',
    }),
  );

  return res.data;
};

function persistAuth(data) {
  const user = data.user || {};

  localStorage.setItem('algocoach_token', data.access_token);
  localStorage.setItem(
    'algocoach_user',
    JSON.stringify({
      id: user.id || null,
      name: user.name || data.user_name || data.name || 'User',
      email: user.email || data.email || '',
      role: user.role || data.user_role || data.role || 'Learner',
      college: user.college || data.college || '',
      batch: user.batch || data.batch || '',
    }),
  );
}
