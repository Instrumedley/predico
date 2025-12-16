import React from 'react'
import { useFeedback } from '@/contexts/FeedbackContext'

export const Feedback: React.FC = () => {
  const { feedbacks, removeFeedback } = useFeedback()

  if (feedbacks.length === 0) {
    return null
  }

  return (
    <div className="fixed top-0 left-0 right-0 z-50 flex flex-col pointer-events-none">
      {feedbacks.map((feedback) => (
        <div
          key={feedback.id}
          className={`w-full px-6 py-4 shadow-lg pointer-events-auto transition-all duration-300 ${
            feedback.type === 'success'
              ? 'bg-green-500 text-white'
              : 'bg-red-500 text-white'
          }`}
        >
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <span className="font-medium">{feedback.message}</span>
            <button
              onClick={() => removeFeedback(feedback.id)}
              className="ml-4 text-white/80 hover:text-white transition-colors"
              aria-label="Close"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      ))}
    </div>
  )
}

