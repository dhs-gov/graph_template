import React from 'react';

const SimplifiedRecommendation = () => {
  // Data for the recommended model
  const model = {
    name: "Model A",
    contentFlagged: 12.5,  // % of content flagged
    itemsFound: 82,        // % of important items found
    efficiency: 98         // % of flagged items that are important
  };
  
  // For visualization (based on 100 documents)
  const totalDocuments = 100;
  const highPriorityCount = 15; // baseline percentage
  const foundCount = Math.round((model.itemsFound / 100) * highPriorityCount);
  const flaggedCount = Math.round(model.contentFlagged);

  return (
    <div className="p-5 bg-white rounded-lg shadow-sm">
      <div className="flex items-center mb-4">
        <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center mr-3">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-green-600" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
          </svg>
        </div>
        <h2 className="text-xl font-bold">Recommended: Model A</h2>
      </div>
      
      <div className="bg-green-50 border-l-4 border-green-400 p-3 mb-5">
        <p className="text-sm">
          Model A finds <span className="font-bold">{model.itemsFound}%</span> of important content 
          while flagging only <span className="font-bold">{model.contentFlagged}%</span> of documents for review.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-5">
        {/* Key metrics */}
        <div>
          <h3 className="text-base font-medium mb-3">Key Metrics</h3>
          
          <div className="space-y-4">
            {/* Documents Flagged */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Documents Flagged</span>
                <span className="font-medium">{model.contentFlagged}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="h-3 rounded-full bg-blue-500" 
                  style={{ width: `${model.contentFlagged}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">Lower is better - less content to review</p>
            </div>
            
            {/* Important Items Found */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Important Items Found</span>
                <span className="font-medium">{model.itemsFound}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="h-3 rounded-full bg-green-500" 
                  style={{ width: `${model.itemsFound}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">Higher is better - finds more important content</p>
            </div>
          </div>
        </div>
        
        {/* Visual representation */}
        <div>
          <h3 className="text-base font-medium mb-3">In Practice</h3>
          
          <div className="flex flex-wrap gap-1 mb-2">
            {[...Array(100)].map((_, i) => (
              <div 
                key={i} 
                className="w-3 h-3 rounded-sm" 
                style={{ 
                  backgroundColor: i < flaggedCount ? 
                    (i < foundCount ? '#4CAF50' : '#FFC107') : 
                    (i < highPriorityCount ? '#FF5252' : '#e0e0e0') 
                }}
              ></div>
            ))}
          </div>
          
          <div className="flex text-xs text-gray-600 mt-2">
            <div className="mr-3 flex items-center">
              <div className="w-3 h-3 bg-green-500 mr-1"></div>
              <span>Found ({foundCount})</span>
            </div>
            <div className="mr-3 flex items-center">
              <div className="w-3 h-3 bg-red-500 mr-1"></div>
              <span>Missed ({highPriorityCount - foundCount})</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-yellow-500 mr-1"></div>
              <span>False positives ({flaggedCount - foundCount})</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="text-sm text-gray-700 border-t pt-3">
        <p>
          <strong>Bottom line:</strong> Review {flaggedCount} documents instead of 100, 
          while still finding {foundCount} out of {highPriorityCount} important items.
        </p>
      </div>
    </div>
  );
};

export default SimplifiedRecommendation;