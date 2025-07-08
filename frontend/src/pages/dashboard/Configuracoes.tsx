import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Configuracoes: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Configurações
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Configurações do sistema
        </Typography>
      </Box>

      {/* TODO: Implementar configurações */}
      <Typography variant="body1">
        Configurações do sistema serão implementadas aqui.
      </Typography>
    </Container>
  );
};

export default Configuracoes;