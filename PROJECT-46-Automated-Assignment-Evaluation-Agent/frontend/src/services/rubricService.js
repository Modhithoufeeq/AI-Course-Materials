import api from './api';

export const rubricService = {
  getTemplates: async () => {
    const response = await api.get('/rubrics/templates');
    return response.data;
  },

  getRubric: async (id) => {
    const response = await api.get(`/rubrics/${id}`);
    return response.data;
  },

  createOrUpdateRubric: async (rubricData) => {
    const response = await api.post('/rubrics', rubricData);
    return response.data;
  }
};
