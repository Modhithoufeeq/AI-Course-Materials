import api from './api';

export const resultService = {
  listResults: async (filters = {}) => {
    const params = {};
    if (filters.assignmentId) params.assignment_id = filters.assignmentId;
    if (filters.studentId) params.student_id = filters.studentId;

    const response = await api.get('/results', { params });
    return response.data;
  },

  getResultDetail: async (resultId) => {
    const response = await api.get(`/results/${resultId}`);
    return response.data;
  }
};
