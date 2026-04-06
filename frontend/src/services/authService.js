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

function persistAuth(data) {
  localStorage.setItem('algocoach_token', data.access_token);
  localStorage.setItem(
    'algocoach_user',
    JSON.stringify({
      name: data.user_name || data.name || 'User',
      role: data.user_role || data.role || 'Learner',
    }),
  );
}
