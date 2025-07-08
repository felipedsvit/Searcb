import React from 'react';
import {
  Snackbar,
  Alert,
  AlertTitle,
  Button,
  Box,
  Slide,
} from '@mui/material';
import type { SlideProps } from '@mui/material';
import { useUIStore } from '../../stores/uiStore';

function SlideTransition(props: SlideProps) {
  return <Slide {...props} direction="up" />;
}

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useUIStore();

  if (toasts.length === 0) {
    return null;
  }

  return (
    <Box
      sx={{
        position: 'fixed',
        bottom: 16,
        right: 16,
        zIndex: (theme) => theme.zIndex.snackbar,
        display: 'flex',
        flexDirection: 'column',
        gap: 1,
        maxWidth: 400,
      }}
    >
      {toasts.map((toast) => (
        <Snackbar
          key={toast.id}
          open={true}
          autoHideDuration={toast.duration}
          onClose={() => removeToast(toast.id)}
          TransitionComponent={SlideTransition}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
        >
          <Alert
            severity={toast.type}
            onClose={() => removeToast(toast.id)}
            variant="filled"
            sx={{
              width: '100%',
              boxShadow: (theme) => theme.shadows[8],
            }}
            action={
              toast.actions && toast.actions.length > 0 ? (
                <Box sx={{ display: 'flex', gap: 1, ml: 1 }}>
                  {toast.actions.map((action, index) => (
                    <Button
                      key={index}
                      size="small"
                      color="inherit"
                      onClick={() => {
                        action.action();
                        removeToast(toast.id);
                      }}
                      sx={{
                        color: 'inherit',
                        textTransform: 'none',
                        minWidth: 'auto',
                        px: 1,
                      }}
                    >
                      {action.label}
                    </Button>
                  ))}
                </Box>
              ) : undefined
            }
          >
            <AlertTitle sx={{ mb: 0.5 }}>{toast.title}</AlertTitle>
            {toast.message}
          </Alert>
        </Snackbar>
      ))}
    </Box>
  );
};

export default ToastContainer;