import api from './api';

export const dashboardService = {
  getTeacherDashboard: async () => {
    const response = await api.get('/dashboard/teacher');
    return response.data;
  },

  getStudentDashboard: async () => {
    const response = await api.get('/dashboard/student');
    return response.data;
  }
};
