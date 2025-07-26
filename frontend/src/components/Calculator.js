import React, { useState, useRef, useEffect } from 'react';

const Calculator = ({ onCalculate, onConvertNumber, onFinancialCalculation, isLoading }) => {
  const [expression, setExpression] = useState('');
  const [result, setResult] = useState('0');
  const [mode, setMode] = useState('basic'); // basic, scientific, financial, programming
  const [numberSystem, setNumberSystem] = useState('decimal'); // decimal, octal, hexadecimal, binary
  const [showingResult, setShowingResult] = useState(false);
  const inputRef = useRef(null);

  const modes = [
    { id: 'basic', name: 'Basic', icon: '🔢' },
    { id: 'scientific', name: 'Scientific', icon: '🧮' },
    { id: 'financial', name: 'Financial', icon: '💰' },
    { id: 'programming', name: 'Programming', icon: '⚙️' }
  ];

  const numberSystems = [
    { id: 'decimal', name: 'DEC', base: 10 },
    { id: 'hexadecimal', name: 'HEX', base: 16 },
    { id: 'octal', name: 'OCT', base: 8 },
    { id: 'binary', name: 'BIN', base: 2 }
  ];

  // Basic calculator buttons
  const basicButtons = [
    ['C', '±', '%', '÷'],
    ['7', '8', '9', '×'],
    ['4', '5', '6', '−'],
    ['1', '2', '3', '+'],
    ['0', '.', '=']
  ];

  // Scientific function buttons
  const scientificButtons = [
    ['sin', 'cos', 'tan', 'ln', 'log', '√'],
    ['sin⁻¹', 'cos⁻¹', 'tan⁻¹', 'e^x', '10^x', 'x²'],
    ['π', 'e', '(', ')', '^', '!']
  ];

  // Programming buttons (for bitwise operations)
  const programmingButtons = [
    ['AND', 'OR', 'XOR', 'NOT'],
    ['<<', '>>', 'A', 'B'],
    ['C', 'D', 'E', 'F']
  ];

  // Financial calculation presets
  const financialPresets = [
    { name: 'Compound Interest', type: 'compound_interest' },
    { name: 'Loan Payment', type: 'loan_payment' },
    { name: 'Present Value', type: 'present_value' }
  ];

  useEffect(() => {
    const handleKeyPress = (event) => {
      const key = event.key;
      event.preventDefault();
      
      if (key >= '0' && key <= '9') {
        handleInput(key);
      } else if (['+', '-', '*', '/', '(', ')', '.'].includes(key)) {
        handleInput(key);
      } else if (key === 'Enter' || key === '=') {
        calculateResult();
      } else if (key === 'Escape' || key === 'c' || key === 'C') {
        clearCalculator();
      } else if (key === 'Backspace') {
        handleBackspace();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [expression, mode, numberSystem]);

  const handleInput = (value) => {
    if (showingResult && !isNaN(value)) {
      setExpression(value);
      setShowingResult(false);
    } else {
      setExpression(prev => prev + value);
      setShowingResult(false);
    }
  };

  const handleButtonClick = (button) => {
    switch (button) {
      case 'C':
        clearCalculator();
        break;
      case '=':
        calculateResult();
        break;
      case '±':
        toggleSign();
        break;
      case '%':
        handleInput('/100');
        break;
      case '÷':
        handleInput('/');
        break;
      case '×':
        handleInput('*');
        break;
      case '−':
        handleInput('-');
        break;
      case '√':
        handleInput('sqrt(');
        break;
      case 'π':
        handleInput('pi');
        break;
      case 'e':
        handleInput('e');
        break;
      case '^':
        handleInput('**');
        break;
      case 'x²':
        handleInput('**2');
        break;
      case 'sin⁻¹':
        handleInput('asin(');
        break;
      case 'cos⁻¹':
        handleInput('acos(');
        break;
      case 'tan⁻¹':
        handleInput('atan(');
        break;
      case 'e^x':
        handleInput('exp(');
        break;
      case '10^x':
        handleInput('10**(');
        break;
      case '!':
        handleInput('factorial(');
        break;
      default:
        if (mode === 'programming' && ['A', 'B', 'C', 'D', 'E', 'F'].includes(button)) {
          if (numberSystem === 'hexadecimal') {
            handleInput(button);
          }
        } else {
          handleInput(button);
        }
    }
  };

  const handleBackspace = () => {
    setExpression(prev => prev.slice(0, -1));
    setShowingResult(false);
  };

  const clearCalculator = () => {
    setExpression('');
    setResult('0');
    setShowingResult(false);
  };

  const toggleSign = () => {
    if (expression.startsWith('-')) {
      setExpression(expression.slice(1));
    } else {
      setExpression('-' + expression);
    }
  };

  const calculateResult = async () => {
    if (!expression.trim()) return;

    try {
      const calculationResult = await onCalculate(expression, mode, numberSystem);
      
      if (calculationResult.error) {
        setResult('Error: ' + calculationResult.error);
      } else {
        setResult(calculationResult.formatted_result);
        setExpression(calculationResult.formatted_result);
        setShowingResult(true);
      }
    } catch (error) {
      setResult('Error: ' + error.message);
      setShowingResult(true);
    }
  };

  const handleNumberSystemChange = async (newSystem) => {
    if (result !== '0' && !result.startsWith('Error') && numberSystem !== newSystem) {
      try {
        const converted = await onConvertNumber(result, numberSystem, newSystem);
        setResult(converted.converted);
        setExpression(converted.converted);
      } catch (error) {
        console.error('Conversion failed:', error);
      }
    }
    setNumberSystem(newSystem);
  };

  const renderBasicKeypad = () => (
    <div className="grid grid-cols-4 gap-2">
      {basicButtons.flat().map((button, index) => (
        <button
          key={index}
          onClick={() => handleButtonClick(button)}
          className={`calc-button ${
            ['='].includes(button) ? 'calc-button-primary col-span-2' :
            ['C', '±', '%'].includes(button) ? 'calc-button-secondary' :
            ['÷', '×', '−', '+'].includes(button) ? 'calc-button-primary' :
            'calc-button'
          } ${button === '0' ? 'col-span-2' : ''}`}
          disabled={isLoading}
        >
          {button}
        </button>
      ))}
    </div>
  );

  const renderScientificKeypad = () => (
    <div className="space-y-2">
      <div className="grid grid-cols-6 gap-2">
        {scientificButtons.flat().map((button, index) => (
          <button
            key={index}
            onClick={() => handleButtonClick(button)}
            className="calc-button text-xs"
            disabled={isLoading}
          >
            {button}
          </button>
        ))}
      </div>
      {renderBasicKeypad()}
    </div>
  );

  const renderProgrammingKeypad = () => (
    <div className="space-y-2">
      <div className="grid grid-cols-4 gap-2">
        {programmingButtons.flat().map((button, index) => (
          <button
            key={index}
            onClick={() => handleButtonClick(button)}
            className={`calc-button text-xs ${
              numberSystem !== 'hexadecimal' && ['A', 'B', 'C', 'D', 'E', 'F'].includes(button) 
                ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            disabled={isLoading || (numberSystem !== 'hexadecimal' && ['A', 'B', 'C', 'D', 'E', 'F'].includes(button))}
          >
            {button}
          </button>
        ))}
      </div>
      {renderBasicKeypad()}
    </div>
  );

  const renderFinancialKeypad = () => (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-2">
        {financialPresets.map((preset) => (
          <button
            key={preset.type}
            onClick={() => {
              // This would open a modal or form for financial calculations
              // For now, we'll just add to expression
              setExpression(`${preset.type}(`);
            }}
            className="calc-button text-sm"
            disabled={isLoading}
          >
            {preset.name}
          </button>
        ))}
      </div>
      {renderBasicKeypad()}
    </div>
  );

  return (
    <div className="bg-calc-primary rounded-xl p-6 shadow-2xl">
      {/* Mode Tabs */}
      <div className="flex flex-wrap mb-4 bg-gray-200 rounded-lg p-1">
        {modes.map((modeOption) => (
          <button
            key={modeOption.id}
            onClick={() => setMode(modeOption.id)}
            className={`flex-1 px-3 py-2 rounded-md text-sm font-medium transition-colors ${
              mode === modeOption.id
                ? 'bg-calc-accent text-white'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            <span className="mr-1">{modeOption.icon}</span>
            {modeOption.name}
          </button>
        ))}
      </div>

      {/* Number System Selector (for programming mode) */}
      {mode === 'programming' && (
        <div className="flex flex-wrap mb-4 gap-2">
          {numberSystems.map((system) => (
            <button
              key={system.id}
              onClick={() => handleNumberSystemChange(system.id)}
              className={`px-3 py-1 rounded text-xs font-medium ${
                numberSystem === system.id
                  ? 'bg-calc-accent text-white'
                  : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
              }`}
            >
              {system.name}
            </button>
          ))}
        </div>
      )}

      {/* Display */}
      <div className="calc-display mb-4 min-h-[80px] flex flex-col justify-end">
        <div className="text-sm text-gray-400 mb-2">
          {mode.charAt(0).toUpperCase() + mode.slice(1)} Mode
          {mode === 'programming' && (
            <span className="ml-2 number-system-indicator bg-calc-accent text-white">
              {numberSystems.find(s => s.id === numberSystem)?.name}
            </span>
          )}
        </div>
        
        <input
          ref={inputRef}
          type="text"
          value={expression}
          onChange={(e) => setExpression(e.target.value)}
          placeholder="Enter expression..."
          className="expression-input text-lg mb-2"
          disabled={isLoading}
        />
        
        <div className="text-2xl font-bold">
          {isLoading ? 'Calculating...' : result}
        </div>
      </div>

      {/* Keypad */}
      <div className="no-select">
        {mode === 'basic' && renderBasicKeypad()}
        {mode === 'scientific' && renderScientificKeypad()}
        {mode === 'financial' && renderFinancialKeypad()}
        {mode === 'programming' && renderProgrammingKeypad()}
      </div>

      {/* Additional Controls */}
      <div className="mt-4 flex gap-2">
        <button
          onClick={handleBackspace}
          className="calc-button calc-button-secondary flex-1"
          disabled={isLoading}
        >
          ⌫ Backspace
        </button>
        <button
          onClick={clearCalculator}
          className="calc-button calc-button-danger flex-1"
          disabled={isLoading}
        >
          Clear All
        </button>
      </div>
    </div>
  );
};

export default Calculator;