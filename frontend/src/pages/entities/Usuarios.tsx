import React from 'react';
import { Box, Typography, Container } from '@mui/material';

const Usuarios: React.FC = () => {
  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Usuários
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Gerenciamento de usuários do sistema
        </Typography>
      </Box>

      {/* TODO: Implementar listagem de usuários */}
      <Typography variant="body1">
        Listagem de usuários será implementada aqui.
      </Typography>
    </Container>
  );
};

export default Usuarios;