import { useState, useCallback } from 'react';

export default function useApi() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (apiCallFn) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiCallFn();
      const result = response.data?.data ?? response.data;
      setData(result);
      return result;
    } catch (err) {
      const message =
        err.response?.data?.message ||
        err.response?.data?.error ||
        err.message ||
        'Error inesperado';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, execute };
}
