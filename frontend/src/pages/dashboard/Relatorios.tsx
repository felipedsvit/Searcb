import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Relatorios: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Relatórios
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Geração e visualização de relatórios
        </Typography>
      </Box>

      {/* TODO: Implementar sistema de relatórios */}
      <Typography variant="body1">
        Sistema de relatórios será implementado aqui.
      </Typography>
    </Container>
  );
};

export default Relatorios;