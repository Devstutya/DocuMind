const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('token');
  }

  setToken(token) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  async request(endpoint, options = {}) {
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const config = {
      ...options,
      headers,
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, config);

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'An error occurred');
    }

    return response.json();
  }

  // Auth endpoints
  async login(username, password) {
    const response = await this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    });
    this.setToken(response.access_token);
    return response;
  }

  async register(email, username, password) {
    return this.request('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, username, password }),
    });
  }

  logout() {
    this.setToken(null);
  }

  async getMe() {
    return this.request('/api/auth/me');
  }

  // Demo endpoints (no auth required)
  async demoUploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseURL}/api/demo/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  // Document endpoints
  async uploadDocument(file) {
    const formData = new FormData();
    formData.append('file', file);

    const headers = {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseURL}/api/documents/upload`, {
      method: 'POST',
      headers,
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Upload failed');
    }

    return response.json();
  }

  async getDocuments() {
    return this.request('/api/documents');
  }

  async deleteDocument(documentId) {
    return this.request(`/api/documents/${documentId}`, {
      method: 'DELETE',
    });
  }

  // RAG endpoints
  async query(question, documentIds = null, conversationId = null) {
    return this.request('/api/rag/query', {
      method: 'POST',
      body: JSON.stringify({
        question,
        document_ids: documentIds,
        conversation_id: conversationId,
      }),
    });
  }

  async getConversationHistory(conversationId) {
    return this.request(`/api/rag/conversations/${conversationId}`);
  }
}

export default new ApiService();
