import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Contratos: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Contratos
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gerenciamento de contratos
        </Typography>
      </Box>

      {/* TODO: Implementar listagem de contratos */}
      <Typography variant="body1">
        Listagem de contratos será implementada aqui.
      </Typography>
    </Container>
  );
};

export default Contratos;