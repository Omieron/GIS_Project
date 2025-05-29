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

  return (
    <button
      className={`start-button ${className}`.trim()}
      onClick={onClick}
      disabled={disabled}
      type="button"
    >
      {children}
    </button>
  );
};

export default StartButton;