import api from './api';

export const studentService = {
  listStudents: async () => {
    const response = await api.get('/students');
    return response.data;
  },

  createStudent: async (studentData) => {
    const response = await api.post('/students', studentData);
    return response.data;
  }
};
