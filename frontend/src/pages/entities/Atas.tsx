import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Atas: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Atas de Registro de Preços
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gerenciamento de atas de registro de preços
        </Typography>
      </Box>

      {/* TODO: Implementar listagem de atas */}
      <Typography variant="body1">
        Listagem de atas será implementada aqui.
      </Typography>
    </Container>
  );
};

export default Atas;