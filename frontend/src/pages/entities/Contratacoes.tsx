import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Contratacoes: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Contratações
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gerenciamento de contratações
        </Typography>
      </Box>

      {/* TODO: Implementar listagem de contratações */}
      <Typography variant="body1">
        Listagem de contratações será implementada aqui.
      </Typography>
    </Container>
  );
};

export default Contratacoes;