import React from 'react';
import {
  Box,
  CircularProgress,
  Typography,
  LinearProgress,
  Backdrop,
} from '@mui/material';
import type { LoadingState } from '../../types/app';

interface LoadingScreenProps {
  loading: LoadingState;
  backdrop?: boolean;
  size?: number;
  fullScreen?: boolean;
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({
  loading,
  backdrop = false,
  size = 60,
  fullScreen = true,
}) => {
  if (!loading.isLoading) {
    return null;
  }

  const content = (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      minHeight={fullScreen ? '100vh' : '200px'}
      gap={2}
    >
      <CircularProgress size={size} />
      
      {loading.message && (
        <Typography variant="body1" color="textSecondary" textAlign="center">
          {loading.message}
        </Typography>
      )}
      
      {loading.progress !== undefined && (
        <Box sx={{ width: '100%', maxWidth: 300 }}>
          <LinearProgress 
            variant="determinate" 
            value={loading.progress} 
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography 
            variant="caption" 
            color="textSecondary" 
            sx={{ mt: 1, display: 'block', textAlign: 'center' }}
          >
            {Math.round(loading.progress)}%
          </Typography>
        </Box>
      )}
    </Box>
  );

  if (backdrop) {
    return (
      <Backdrop
        sx={{
          color: '#fff',
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
        }}
        open={true}
      >
        {content}
      </Backdrop>
    );
  }

  return content;
};

export default LoadingScreen;