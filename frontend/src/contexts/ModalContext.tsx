import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { Modal, ModalType } from '@/components/ui/Modal'

interface ModalState {
  isOpen: boolean
  title: string
  message: string
  type: ModalType
  confirmText?: string
  cancelText?: string
  onConfirm?: () => void | Promise<void>
  onCancel?: () => void
}

interface ModalContextType {
  showModal: (config: Omit<ModalState, 'isOpen'>) => void
  showConfirm: (
    title: string,
    message: string,
    onConfirm: () => void | Promise<void>,
    confirmText?: string,
    cancelText?: string,
    onCancel?: () => void
  ) => void
  showSuccess: (title: string, message: string) => void
  showError: (title: string, message: string) => void
  showInfo: (title: string, message: string) => void
  closeModal: () => void
}

const ModalContext = createContext<ModalContextType | undefined>(undefined)

export const ModalProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [modalState, setModalState] = useState<ModalState>({
    isOpen: false,
    title: '',
    message: '',
    type: 'info',
  })

  const showModal = useCallback((config: Omit<ModalState, 'isOpen'>) => {
    setModalState({
      isOpen: true,
      ...config,
    })
  }, [])

  const showConfirm = useCallback(
    (
      title: string,
      message: string,
      onConfirm: () => void | Promise<void>,
      confirmText = 'Confirm',
      cancelText = 'Cancel',
      onCancel?: () => void
    ) => {
      setModalState({
        isOpen: true,
        title,
        message,
        type: 'confirm',
        confirmText,
        cancelText,
        onConfirm,
        onCancel,
      })
    },
    []
  )

  const showSuccess = useCallback((title: string, message: string) => {
    setModalState({
      isOpen: true,
      title,
      message,
      type: 'success',
      confirmText: 'OK',
    })
  }, [])

  const showError = useCallback((title: string, message: string) => {
    setModalState({
      isOpen: true,
      title,
      message,
      type: 'error',
      confirmText: 'OK',
    })
  }, [])

  const showInfo = useCallback((title: string, message: string) => {
    setModalState({
      isOpen: true,
      title,
      message,
      type: 'info',
      confirmText: 'OK',
    })
  }, [])

  const closeModal = useCallback(() => {
    setModalState((prev) => ({ ...prev, isOpen: false }))
  }, [])

  const handleConfirm = useCallback(async () => {
    if (modalState.onConfirm) {
      await modalState.onConfirm()
    }
    closeModal()
  }, [modalState.onConfirm, closeModal])

  return (
    <ModalContext.Provider
      value={{
        showModal,
        showConfirm,
        showSuccess,
        showError,
        showInfo,
        closeModal,
      }}
    >
      {children}
      <Modal
        isOpen={modalState.isOpen}
        onClose={closeModal}
        onCancel={modalState.onCancel}
        onConfirm={modalState.onConfirm ? handleConfirm : undefined}
        title={modalState.title}
        message={modalState.message}
        type={modalState.type}
        confirmText={modalState.confirmText}
        cancelText={modalState.cancelText}
      />
    </ModalContext.Provider>
  )
}

export const useModal = () => {
  const context = useContext(ModalContext)
  if (context === undefined) {
    throw new Error('useModal must be used within a ModalProvider')
  }
  return context
}
