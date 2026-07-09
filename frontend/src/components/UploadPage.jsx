import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import axios from 'axios';

function UploadPage({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [preview, setPreview] = useState(null);

  // Phone + OTP state
  const [phone, setPhone] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [otpSent, setOtpSent] = useState(false);
  const [verified, setVerified] = useState(false);
  const [otpLoading, setOtpLoading] = useState(false);

  // Patient phone — separate from the officer's phone used for OTP
  const [patientPhone, setPatientPhone] = useState('');

  const handleSendOtp = async () => {
    if (!phone.trim()) { setError('Enter your phone number first'); return; }
    setOtpLoading(true); setError(null);
    try {
      await axios.post('/api/otp/send', { phone });
      setOtpSent(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to send OTP');
    } finally { setOtpLoading(false); }
  };

  const handleVerifyOtp = async () => {
    if (!otpCode.trim()) { setError('Enter the OTP code'); return; }
    setOtpLoading(true); setError(null);
    try {
      await axios.post('/api/otp/verify', { phone, code: otpCode });
      setVerified(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Invalid OTP');
    } finally { setOtpLoading(false); }
  };

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) { setError('No file selected'); return; }

    if (!['image/jpeg', 'image/png', 'image/jpg', 'application/pdf',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'application/msword'].includes(file.type)) {
      setError('Please upload a JPEG, PNG, PDF, or DOCX file');
      return;
    }
    if (file.size > 10 * 1024 * 1024) { setError('File size must be less than 10MB'); return; }

    // Show preview for images
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => setPreview(e.target.result);
      reader.readAsDataURL(file);
    }

    setUploading(true); setError(null);
    try {
      const formData = new FormData();
      formData.append('file', file);
      if (verified && phone) formData.append('phone', phone);           // officer phone
      if (verified && patientPhone) formData.append('patient_phone', patientPhone); // patient phone

      const response = await axios.post('/api/analyze', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      if (response.data.success) {
        onUploadSuccess(response.data.data);
      } else {
        setError(response.data.message || 'Analysis failed');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Upload failed. Please try again.');
    } finally { setUploading(false); }
  }, [onUploadSuccess, verified, phone, patientPhone]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    multiple: false,
    disabled: uploading,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">

        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-5xl font-bold text-gray-800 mb-3">🏥 MediClaim AI</h1>
          <p className="text-xl text-gray-600">Automated Medical Receipt Fraud Detection</p>
          <p className="text-sm text-gray-500 mt-1">Upload a medical receipt to detect fraud in 30 seconds</p>
        </div>

        {/* Step 1 — Phone verification */}
        <div className={`card p-6 mb-4 ${verified ? 'border-2 border-green-400' : ''}`}>
          <div className="flex items-center mb-3">
            <span className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold mr-3 
              ${verified ? 'bg-green-500 text-white' : 'bg-blue-600 text-white'}`}>
              {verified ? '✓' : '1'}
            </span>
            <h3 className="font-bold text-gray-800 text-lg">
              {verified ? 'Phone verified ✓' : 'Verify your phone number'}
            </h3>
          </div>

          {!verified ? (
            <div className="space-y-3">
              <p className="text-sm text-gray-500">
                We'll send an OTP to confirm your identity before processing your claim.
              </p>
              <div className="flex gap-3">
                <input
                  type="tel"
                  placeholder="e.g. 0712345678"
                  value={phone}
                  onChange={e => setPhone(e.target.value)}
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
                <button
                  onClick={handleSendOtp}
                  disabled={otpLoading || otpSent}
                  className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 transition"
                >
                  {otpLoading ? 'Sending...' : otpSent ? 'OTP Sent ✓' : 'Send OTP'}
                </button>
              </div>

              {otpSent && (
                <div className="flex gap-3 mt-2">
                  <input
                    type="text"
                    placeholder="Enter 6-digit OTP"
                    maxLength={6}
                    value={otpCode}
                    onChange={e => setOtpCode(e.target.value)}
                    className="flex-1 border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-400 tracking-widest font-mono"
                  />
                  <button
                    onClick={handleVerifyOtp}
                    disabled={otpLoading}
                    className="bg-green-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-green-700 disabled:opacity-50 transition"
                  >
                    {otpLoading ? 'Verifying...' : 'Verify'}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-sm text-green-700">
                Phone <span className="font-semibold">{phone || 'not provided'}</span> verified.
                You'll receive an SMS with the analysis result.
              </p>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Patient's phone — they will receive SMS updates
                </label>
                <input
                  type="tel"
                  placeholder="e.g. 0722000000"
                  value={patientPhone}
                  onChange={e => setPatientPhone(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                />
                <p className="text-xs text-gray-400 mt-1">
                  Optional — patient phone number (for SMS notifications)
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Step 2 — Upload */}
        <div className={`card p-8 mb-6 ${!verified ? 'opacity-60 pointer-events-none' : ''}`}>
          <div className="flex items-center mb-4">
            <span className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center text-sm font-bold mr-3">2</span>
            <h3 className="font-bold text-gray-800 text-lg">Upload your receipt</h3>
          </div>

          <div
            {...getRootProps()}
            className={`border-4 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-300
              ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}
              ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            <input {...getInputProps()} />
            {uploading ? (
              <div className="flex flex-col items-center">
                <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-500 mb-4"></div>
                <p className="text-xl font-semibold text-gray-700">Analyzing receipt...</p>
                <p className="text-sm text-gray-500 mt-2">This usually takes 15–30 seconds</p>
              </div>
            ) : (
              <>
                <svg className="mx-auto h-16 w-16 text-gray-400 mb-4" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                    strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                </svg>
                <p className="text-xl font-semibold text-gray-700 mb-2">
                  {isDragActive ? 'Drop the receipt here...' : 'Drag & drop a receipt, or click to browse'}
                </p>
                <p className="text-sm text-gray-500">Supported formats: JPEG, PNG, PDF, DOCX • Max size: 10MB</p>
              </>
            )}
          </div>

          {preview && !uploading && (
            <div className="mt-6">
              <p className="text-sm text-gray-600 mb-2">Preview:</p>
              <img src={preview} alt="Receipt preview" className="max-h-64 mx-auto rounded-lg shadow-md" />
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4 mb-6">
            <div className="flex items-center">
              <span className="text-2xl mr-3">⚠️</span>
              <div>
                <p className="font-semibold text-red-800">Error</p>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Feature cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="card p-6 text-center">
            <div className="text-4xl mb-3">🔍</div>
            <h3 className="font-bold text-gray-800 mb-2">Image Forensics</h3>
            <p className="text-sm text-gray-600">Detects digital manipulation and editing</p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-4xl mb-3">💰</div>
            <h3 className="font-bold text-gray-800 mb-2">Cost Validation</h3>
            <p className="text-sm text-gray-600">Compares prices against KES market rates</p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-4xl mb-3">📱</div>
            <h3 className="font-bold text-gray-800 mb-2">SMS Alerts</h3>
            <p className="text-sm text-gray-600">Instant result notification via Africa's Talking</p>
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-xs text-gray-500">🔒 All data processed securely. Powered by Africa's Talking.</p>
        </div>
      </div>
    </div>
  );
}

export default UploadPage;