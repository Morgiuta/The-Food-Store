import { api } from './api';

export interface CloudinaryResponse {
  secure_url: string;
  public_id: string;
  width: number;
  height: number;
  format: string;
  resource_type: string;
}

export const uploadImagen = async (file: File, folder: string = 'foodstore/productos'): Promise<CloudinaryResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post<CloudinaryResponse>(`/uploads/imagen?folder=${encodeURIComponent(folder)}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const deleteImagen = async (publicId: string): Promise<void> => {
  await api.delete(`/uploads/imagen/${encodeURIComponent(publicId)}`);
};
