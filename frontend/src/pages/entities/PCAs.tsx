import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const PCAs: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Planos de Contratação Anual (PCAs)
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gerenciamento de Planos de Contratação Anual
        </Typography>
      </Box>

      {/* TODO: Implementar listagem de PCAs */}
      <Typography variant="body1">
        Listagem de PCAs será implementada aqui.
      </Typography>
    </Container>
  );
};

export default PCAs;