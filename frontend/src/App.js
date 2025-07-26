import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import './App.css';
import Calculator from './components/Calculator';
import History from './components/History';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

function App() {
  const [sessionId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load calculation history on component mount
  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/history/${sessionId}`);
      setHistory(response.data.history || []);
    } catch (err) {
      console.error('Failed to load history:', err);
      setError('Failed to load calculation history');
    } finally {
      setIsLoading(false);
    }
  };

  const addToHistory = useCallback((calculation) => {
    setHistory(prev => [calculation, ...prev]);
  }, []);

  const clearHistory = async () => {
    try {
      await axios.delete(`${API_BASE_URL}/api/history/${sessionId}`);
      setHistory([]);
    } catch (err) {
      console.error('Failed to clear history:', err);
      setError('Failed to clear history');
    }
  };

  const performCalculation = async (expression, mode, numberSystem) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await axios.post(`${API_BASE_URL}/api/calculate`, {
        expression,
        mode,
        number_system: numberSystem,
        session_id: sessionId
      });

      const result = response.data;
      addToHistory(result);
      
      return result;
    } catch (err) {
      console.error('Calculation failed:', err);
      const errorMessage = err.response?.data?.detail || 'Calculation failed';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const convertNumber = async (value, fromBase, toBase) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/convert-number`, {
        value,
        from_base: fromBase,
        to_base: toBase
      });
      return response.data;
    } catch (err) {
      console.error('Number conversion failed:', err);
      throw new Error(err.response?.data?.detail || 'Number conversion failed');
    }
  };

  const performFinancialCalculation = async (calculationType, parameters) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/financial-calculation`, {
        calculation_type: calculationType,
        parameters
      });
      return response.data;
    } catch (err) {
      console.error('Financial calculation failed:', err);
      throw new Error(err.response?.data?.detail || 'Financial calculation failed');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      <div className="container mx-auto px-4 py-6">
        <div className="calculator-container">
          <header className="text-center mb-6">
            <h1 className="text-4xl font-bold text-white mb-2">Advanced Calculator</h1>
            <p className="text-gray-300">Scientific • Financial • Programming</p>
          </header>

          {error && (
            <div className="mb-4 p-4 bg-red-500 text-white rounded-lg">
              {error}
              <button 
                onClick={() => setError(null)}
                className="ml-2 text-red-200 hover:text-white"
              >
                ×
              </button>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              <Calculator
                onCalculate={performCalculation}
                onConvertNumber={convertNumber}
                onFinancialCalculation={performFinancialCalculation}
                isLoading={isLoading}
              />
            </div>
            
            <div className="lg:col-span-1">
              <History
                history={history}
                isLoading={isLoading}
                onClearHistory={clearHistory}
                onRefreshHistory={loadHistory}
              />
            </div>
          </div>

          <footer className="mt-8 text-center text-gray-400 text-sm">
            <p>Cross-platform calculator • Works on Windows & Android</p>
            <p className="mt-1">Session ID: {sessionId.slice(-8)}</p>
          </footer>
        </div>
      </div>
    </div>
  );
}

export default App;