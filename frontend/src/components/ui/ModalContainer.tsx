import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  IconButton,
  Box,
  Typography,
} from '@mui/material';
import { Close as CloseIcon } from '@mui/icons-material';
import { useUIStore } from '../../stores/uiStore';

export const ModalContainer: React.FC = () => {
  const { modals, closeModal } = useUIStore();

  if (modals.length === 0) {
    return null;
  }

  return (
    <>
      {modals.map((modal) => (
        <Dialog
          key={modal.id}
          open={true}
          onClose={modal.closable ? () => closeModal(modal.id) : undefined}
          maxWidth={modal.size}
          fullWidth
          PaperProps={{
            sx: {
              borderRadius: 2,
              boxShadow: (theme) => theme.shadows[24],
            },
          }}
        >
          <DialogTitle
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              pb: 1,
            }}
          >
            <Typography variant="h6" component="div">
              {modal.title}
            </Typography>
            
            {modal.closable && (
              <IconButton
                edge="end"
                color="inherit"
                onClick={() => closeModal(modal.id)}
                size="small"
                sx={{ ml: 1 }}
              >
                <CloseIcon />
              </IconButton>
            )}
          </DialogTitle>

          <DialogContent
            sx={{
              pt: 1,
              pb: modal.actions && modal.actions.length > 0 ? 1 : 3,
            }}
          >
            {typeof modal.content === 'string' ? (
              <Typography variant="body1">
                {modal.content}
              </Typography>
            ) : (
              modal.content
            )}
          </DialogContent>

          {modal.actions && modal.actions.length > 0 && (
            <DialogActions sx={{ px: 3, pb: 2 }}>
              <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end' }}>
                {modal.actions.map((action, index) => (
                  <Button
                    key={index}
                    variant={action.variant || 'contained'}
                    color={action.color || 'primary'}
                    disabled={action.disabled}
                    onClick={action.onClick}
                    startIcon={action.icon}
                    size="medium"
                  >
                    {action.label}
                  </Button>
                ))}
              </Box>
            </DialogActions>
          )}
        </Dialog>
      ))}
    </>
  );
};

export default ModalContainer;