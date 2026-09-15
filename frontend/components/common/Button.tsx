type ButtonProps = {
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit';
  disabled?: boolean;
  className?: string;
};

export default function Button({ children, onClick, type = 'button', disabled = false, className = '' }: ButtonProps) {
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`rounded-lg px-4 py-2 font-medium transition ${disabled ? 'cursor-not-allowed bg-slate-300 text-slate-500' : 'bg-blue-600 text-white hover:bg-blue-700'} ${className}`}
    >
      {children}
    </button>
  );
}
