import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Perfil: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Meu Perfil
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gerenciamento do perfil do usuário
        </Typography>
      </Box>

      {/* TODO: Implementar perfil do usuário */}
      <Typography variant="body1">
        Perfil do usuário será implementado aqui.
      </Typography>
    </Container>
  );
};

export default Perfil;