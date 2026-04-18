import { pythonAPI } from './api';

export const fetchDashboardOverview = async () => {
  const res = await pythonAPI.get('/dashboard/overview');
  return res.data;
};

export const fetchPracticeProblems = async () => {
  const res = await pythonAPI.get('/dashboard/problems');
  return res.data.problems || [];
};
