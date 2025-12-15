import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'

export type FeedbackType = 'success' | 'error'

interface Feedback {
  id: string
  message: string
  type: FeedbackType
}

interface FeedbackContextType {
  showFeedback: (message: string, type: FeedbackType) => void
  feedbacks: Feedback[]
  removeFeedback: (id: string) => void
}

const FeedbackContext = createContext<FeedbackContextType | undefined>(undefined)

export const FeedbackProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([])

  const showFeedback = useCallback((message: string, type: FeedbackType) => {
    const id = `feedback-${Date.now()}-${Math.random()}`
    const newFeedback: Feedback = { id, message, type }
    
    setFeedbacks((prev) => [...prev, newFeedback])
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      setFeedbacks((prev) => prev.filter((f) => f.id !== id))
    }, 5000)
  }, [])

  const removeFeedback = useCallback((id: string) => {
    setFeedbacks((prev) => prev.filter((f) => f.id !== id))
  }, [])

  return (
    <FeedbackContext.Provider value={{ showFeedback, feedbacks, removeFeedback }}>
      {children}
    </FeedbackContext.Provider>
  )
}

export const useFeedback = () => {
  const context = useContext(FeedbackContext)
  if (context === undefined) {
    throw new Error('useFeedback must be used within a FeedbackProvider')
  }
  return context
}
