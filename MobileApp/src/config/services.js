import { createApiInstance } from './api';
import { AUTH_SERVICE_URL, DEFECTS_SERVICE_URL } from './constants';

export const authApi = createApiInstance(AUTH_SERVICE_URL);
export const defectsApi = createApiInstance(DEFECTS_SERVICE_URL);