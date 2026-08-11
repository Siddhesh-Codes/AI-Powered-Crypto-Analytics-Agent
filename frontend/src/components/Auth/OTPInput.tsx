import React, { useState, useRef, useEffect } from 'react';
import { Loader2, RefreshCw } from 'lucide-react';

interface OTPInputProps {
  onVerify: (otp: string) => Promise<void>;
  onResend: () => Promise<void>;
  email: string;
  isLoading?: boolean;
  isResending?: boolean;
}

/**
 * Professional OTP Input Component
 * 6-digit OTP input with auto-focus and paste support
 */
const OTPInput: React.FC<OTPInputProps> = ({
  onVerify,
  onResend,
  email,
  isLoading = false,
  isResending = false
}) => {
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [countdown, setCountdown] = useState(60); // 60 second countdown for resend
  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Countdown timer for resend button
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleChange = (index: number, value: string) => {
    // Only allow digits
    const digit = value.replace(/\D/g, '').slice(-1);
    
    const newOtp = [...otp];
    newOtp[index] = digit;
    setOtp(newOtp);

    // Auto-focus next input
    if (digit && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto-verify when all 6 digits are entered
    if (newOtp.every(d => d !== '') && newOtp.join('').length === 6) {
      onVerify(newOtp.join(''));
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    // Handle backspace
    if (e.key === 'Backspace' && !otp[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    
    if (pastedData.length === 6) {
      const newOtp = pastedData.split('');
      setOtp(newOtp);
      inputRefs.current[5]?.focus();
      
      // Auto-verify pasted OTP
      onVerify(pastedData);
    }
  };

  const handleResend = async () => {
    if (countdown > 0) return;
    
    setCountdown(60); // Reset countdown
    await onResend();
  };

  const clearOtp = () => {
    setOtp(['', '', '', '', '', '']);
    inputRefs.current[0]?.focus();
  };

  return (
    <div className="w-full max-w-md mx-auto">
      {/* Header */}
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 1.05a2 2 0 001.11 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </div>
        <h3 className="text-xl font-semibold text-white mb-2">Check Your Email</h3>
        <p className="text-slate-400 text-sm">
          We sent a verification code to<br />
          <span className="font-medium text-blue-400">{email}</span>
        </p>
      </div>

      {/* OTP Input Boxes */}
      <div className="flex justify-center space-x-3 mb-6">
        {otp.map((digit, index) => (
          <input
            key={index}
            ref={el => inputRefs.current[index] = el}
            type="text"
            inputMode="numeric"
            maxLength={1}
            value={digit}
            onChange={e => handleChange(index, e.target.value)}
            onKeyDown={e => handleKeyDown(index, e)}
            onPaste={handlePaste}
            disabled={isLoading}
            className={`w-12 h-12 text-center text-xl font-bold bg-slate-700 border-2 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all
              ${digit ? 'border-blue-500 bg-slate-600' : 'border-slate-600'}
              ${isLoading ? 'opacity-50 cursor-not-allowed' : 'hover:border-slate-500'}
            `}
            placeholder="•"
          />
        ))}
      </div>

      {/* Action Buttons */}
      <div className="space-y-4">
        {/* Verify Button */}
        <button
          onClick={() => onVerify(otp.join(''))}
          disabled={otp.join('').length !== 6 || isLoading}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 disabled:from-slate-600 disabled:to-slate-600 text-white font-semibold py-3 px-4 rounded-lg transition-all duration-200 flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Verifying...</span>
            </>
          ) : (
            <span>Verify Code</span>
          )}
        </button>

        {/* Resend Button */}
        <div className="flex items-center justify-between">
          <button
            onClick={clearOtp}
            className="text-slate-400 hover:text-white text-sm transition-colors"
          >
            Clear Code
          </button>
          
          <button
            onClick={handleResend}
            disabled={countdown > 0 || isResending}
            className="flex items-center space-x-2 text-sm font-medium text-blue-400 hover:text-blue-300 disabled:text-slate-500 disabled:cursor-not-allowed transition-colors"
          >
            {isResending ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Sending...</span>
              </>
            ) : countdown > 0 ? (
              <span>Resend in {countdown}s</span>
            ) : (
              <>
                <RefreshCw className="w-4 h-4" />
                <span>Resend Code</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Help Text */}
      <div className="mt-6 p-4 bg-slate-800/50 border border-slate-700 rounded-lg">
        <div className="flex items-start space-x-3">
          <div className="w-5 h-5 bg-blue-500 rounded-full flex items-center justify-center mt-0.5 flex-shrink-0">
            <span className="text-white text-xs font-bold">?</span>
          </div>
          <div className="text-sm">
            <p className="text-slate-300 font-medium mb-1">Didn't receive the code?</p>
            <ul className="text-slate-400 text-xs space-y-1">
              <li>• Check your spam/junk folder</li>
              <li>• Make sure {email} is correct</li>
              <li>• Wait up to 2 minutes for delivery</li>
              <li>• Click "Resend Code" if needed</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OTPInput;
