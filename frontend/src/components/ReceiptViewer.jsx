import React, { useState } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';

function ReceiptViewer({ imageUrl, elaImageUrl }) {
  const [showELA, setShowELA] = useState(false);

  return (
    <div className="receipt-viewer bg-white rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-bold text-gray-800">
          📄 Receipt Image
        </h3>
        
        {elaImageUrl && (
          <button
            onClick={() => setShowELA(!showELA)}
            className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all duration-200 ${
              showELA
                ? 'bg-red-500 text-white hover:bg-red-600'
                : 'bg-blue-500 text-white hover:bg-blue-600'
            }`}
          >
            {showELA ? '👁️ Show Original' : '🔍 Show ELA Heatmap'}
          </button>
        )}
      </div>

      {/* Info Banner */}
      {showELA && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-300 rounded-lg">
          <p className="text-sm text-yellow-800">
            <span className="font-semibold">ELA Heatmap:</span> Bright areas indicate regions that were 
            likely edited or manipulated. Uniform dark areas suggest authentic image.
          </p>
        </div>
      )}

      {/* Image Viewer with Zoom */}
      <div className="border-2 border-gray-300 rounded-lg overflow-hidden bg-gray-100" style={{ height: '600px' }}>
        <TransformWrapper
          initialScale={1}
          minScale={0.5}
          maxScale={4}
          centerOnInit={true}
        >
          {({ zoomIn, zoomOut, resetTransform }) => (
            <>
              {/* Zoom Controls */}
              <div className="absolute top-4 right-4 z-10 bg-white rounded-lg shadow-lg p-2 flex flex-col gap-2">
                <button
                  onClick={() => zoomIn()}
                  className="w-10 h-10 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-bold text-lg"
                  title="Zoom In"
                >
                  +
                </button>
                <button
                  onClick={() => zoomOut()}
                  className="w-10 h-10 bg-blue-500 text-white rounded-lg hover:bg-blue-600 font-bold text-lg"
                  title="Zoom Out"
                >
                  −
                </button>
                <button
                  onClick={() => resetTransform()}
                  className="w-10 h-10 bg-gray-500 text-white rounded-lg hover:bg-gray-600 font-bold text-xs"
                  title="Reset"
                >
                  ↺
                </button>
              </div>

              {/* Image */}
              <TransformComponent
                wrapperStyle={{
                  width: '100%',
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                <img
                  src={showELA ? elaImageUrl : imageUrl}
                  alt={showELA ? 'ELA Heatmap' : 'Receipt'}
                  className="max-w-full max-h-full object-contain"
                  style={{ cursor: 'grab' }}
                />
              </TransformComponent>
            </>
          )}
        </TransformWrapper>
      </div>

      {/* Instructions */}
      <div className="mt-4 flex items-center justify-center gap-4 text-sm text-gray-600">
        <span className="flex items-center">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
          </svg>
          Scroll to zoom
        </span>
        <span className="flex items-center">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 11.5V14m0-2.5v-6a1.5 1.5 0 113 0m-3 6a1.5 1.5 0 00-3 0v2a7.5 7.5 0 0015 0v-5a1.5 1.5 0 00-3 0m-6-3V11m0-5.5v-1a1.5 1.5 0 013 0v1m0 0V11m0-5.5a1.5 1.5 0 013 0v3m0 0V11" />
          </svg>
          Drag to pan
        </span>
        <span className="flex items-center">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Use buttons to zoom
        </span>
      </div>

      {/* Metadata Display */}
      {!showELA && (
        <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-xs font-semibold text-gray-700 mb-2">Image Information:</p>
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
            <div>
              <span className="font-semibold">Format:</span> {imageUrl?.split('.').pop()?.toUpperCase() || 'N/A'}
            </div>
            <div>
              <span className="font-semibold">View:</span> Original Receipt
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ReceiptViewer;