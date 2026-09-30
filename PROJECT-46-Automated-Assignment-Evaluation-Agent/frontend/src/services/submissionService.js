import api from './api';

export const submissionService = {
  uploadSubmission: async (assignmentId, file, studentId = null) => {
    const formData = new FormData();
    formData.append('assignment_id', assignmentId);
    if (studentId) {
      formData.append('student_id', studentId);
    }
    formData.append('file', file);

    const response = await api.post('/submissions/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  listSubmissions: async (filters = {}) => {
    const params = {};
    if (filters.assignmentId) params.assignment_id = filters.assignmentId;
    if (filters.studentId) params.student_id = filters.studentId;
    if (filters.status) params.status_filter = filters.status;

    const response = await api.get('/submissions', { params });
    return response.data;
  },

  getSubmission: async (id) => {
    const response = await api.get(`/submissions/${id}`);
    return response.data;
  },

  deleteSubmission: async (id) => {
    const response = await api.delete(`/submissions/${id}`);
    return response.data;
  }
};
