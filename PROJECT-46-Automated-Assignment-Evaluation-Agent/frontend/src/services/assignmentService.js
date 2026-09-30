import api from './api';

export const assignmentService = {
  listAssignments: async (statusFilter = null) => {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const response = await api.get('/assignments', { params });
    return response.data;
  },

  getAssignment: async (id) => {
    const response = await api.get(`/assignments/${id}`);
    return response.data;
  },

  createAssignment: async (assignmentData) => {
    const response = await api.post('/assignments', assignmentData);
    return response.data;
  },

  updateAssignment: async (id, updateData) => {
    const response = await api.put(`/assignments/${id}`, updateData);
    return response.data;
  },

  deleteAssignment: async (id) => {
    const response = await api.delete(`/assignments/${id}`);
    return response.data;
  },

  uploadReference: async (assignmentId, title, file) => {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', file);
    const response = await api.post(`/assignments/${assignmentId}/references`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }
};
