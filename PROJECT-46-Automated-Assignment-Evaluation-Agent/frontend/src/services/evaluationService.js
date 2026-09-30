import api from './api';

export const evaluationService = {
  startEvaluation: async (submissionId) => {
    const response = await api.post(`/evaluations/${submissionId}/start`);
    return response.data;
  },

  reevaluate: async (submissionId) => {
    const response = await api.post(`/evaluations/${submissionId}/reevaluate`);
    return response.data;
  },

  getEvaluation: async (submissionId) => {
    const response = await api.get(`/evaluations/${submissionId}`);
    return response.data;
  },

  reviewEvaluation: async (evaluationId, reviewData) => {
    const response = await api.put(`/evaluations/${evaluationId}/review`, reviewData);
    return response.data;
  },

  approveEvaluation: async (evaluationId, approveData) => {
    const response = await api.post(`/evaluations/${evaluationId}/approve`, approveData);
    return response.data;
  }
};
