import React from 'react';
import '../../styles/StartButton.css';

interface StartButtonProps {

  onClick: () => void;

  isVisible?: boolean;

  children?: React.ReactNode;

  disabled?: boolean;

  className?: string;
}

const StartButton: React.FC<StartButtonProps> = ({ 
  onClick, 
  isVisible = true,
  children = "🌍 Keşfet",
  disabled = false,
  className = ""
}) => {
  if (!isVisible) {
    return null;
  }

  // Default focus davranışını engellemek için kullanılacaktır 
  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault(); 
    if (!disabled) {
      onClick();
    }
  };

  const handleClick = (e: React.MouseEvent) => {
    e.preventDefault();
    if (!disabled) {
      onClick();
    }
  };


  return (
    <button
      className={`start-button ${className}`.trim()}
      onMouseDown={handleMouseDown}
      onClick={handleClick}
      disabled={disabled}
      type="button"
    >
      {children}
    </button>
  );
};

export default StartButton;