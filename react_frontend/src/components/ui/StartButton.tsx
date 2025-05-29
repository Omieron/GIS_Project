import React from 'react';
import '../../styles/StartButton.css';

interface StartButtonProps {
  /** Buton tıklandığında çalışacak fonksiyon */
  onClick: () => void;
  /** Butonun görünür olup olmayacağı */
  isVisible?: boolean;
  /** Buton metnini özelleştirmek için */
  children?: React.ReactNode;
  /** Buton devre dışı bırakılabilir */
  disabled?: boolean;
  /** CSS sınıfı eklemek için */
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