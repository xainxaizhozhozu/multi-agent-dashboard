import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock axios
vi.mock('axios', () => {
  const mockAxiosInstance = {
    get: vi.fn().mockResolvedValue({}),
    post: vi.fn().mockResolvedValue({}),
    interceptors: {
      request: { use: vi.fn() },
      response: { use: vi.fn() },
    },
  };
  return {
    default: {
      create: vi.fn().mockReturnValue(mockAxiosInstance),
    },
  };
});

import axios from 'axios';
import api, { dashboardApi, agentApi } from '../api';

describe('API Module', () => {
  it('creates axios instance with correct base URL', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        baseURL: '/api/v1',
      })
    );
  });

  it('creates axios instance with correct timeout', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        timeout: 60000,
      })
    );
  });

  it('creates axios instance with JSON content type', () => {
    expect(axios.create).toHaveBeenCalledWith(
      expect.objectContaining({
        headers: { 'Content-Type': 'application/json' },
      })
    );
  });

  describe('dashboardApi', () => {
    it('has getStats function', () => {
      expect(typeof dashboardApi.getStats).toBe('function');
    });

    it('has getMonthlyTrend function', () => {
      expect(typeof dashboardApi.getMonthlyTrend).toBe('function');
    });

    it('has getDailyTrend function', () => {
      expect(typeof dashboardApi.getDailyTrend).toBe('function');
    });

    it('has getByRegion function', () => {
      expect(typeof dashboardApi.getByRegion).toBe('function');
    });

    it('has getByCategory function', () => {
      expect(typeof dashboardApi.getByCategory).toBe('function');
    });
  });

  describe('agentApi', () => {
    it('has chat function', () => {
      expect(typeof agentApi.chat).toBe('function');
    });

    it('has status function', () => {
      expect(typeof agentApi.status).toBe('function');
    });
  });

  describe('default export', () => {
    it('exports the axios instance', () => {
      expect(api).toBeDefined();
      expect(api.get).toBeDefined();
      expect(api.post).toBeDefined();
    });
  });
});
