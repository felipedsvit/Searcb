import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Paper,
  Container,
} from '@mui/material';
import {
  TrendingUp,
  Description,
  Assignment,
  People,
} from '@mui/icons-material';

const Dashboard: React.FC = () => {
  const stats = [
    {
      title: 'Total de PCAs',
      value: '1,234',
      change: '+12%',
      changeType: 'positive' as const,
      icon: <Description />,
      color: '#1976d2',
    },
    {
      title: 'Contratos Ativos',
      value: '856',
      change: '+8%',
      changeType: 'positive' as const,
      icon: <Assignment />,
      color: '#2e7d32',
    },
    {
      title: 'Valor Total',
      value: 'R$ 45.2M',
      change: '+15%',
      changeType: 'positive' as const,
      icon: <TrendingUp />,
      color: '#ed6c02',
    },
    {
      title: 'Usuários Ativos',
      value: '23',
      change: '+2',
      changeType: 'positive' as const,
      icon: <People />,
      color: '#9c27b0',
    },
  ];

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Dashboard Executivo
        </Typography>
        <Typography variant="body1" color="textSecondary">
          Visão geral do sistema de contratações
        </Typography>
      </Box>

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            sm: '1fr 1fr',
            md: '1fr 1fr 1fr 1fr',
          },
          gap: 3,
          mb: 3,
        }}
      >
        {/* KPI Cards */}
        {stats.map((stat, index) => (
          <Card
            key={index}
              sx={{
                position: 'relative',
                overflow: 'visible',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: 4,
                  background: stat.color,
                },
              }}
            >
              <CardContent sx={{ pt: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <Box
                    sx={{
                      p: 1,
                      borderRadius: 2,
                      backgroundColor: `${stat.color}20`,
                      color: stat.color,
                      mr: 2,
                    }}
                  >
                    {stat.icon}
                  </Box>
                  <Typography variant="body2" color="textSecondary">
                    {stat.title}
                  </Typography>
                </Box>
                
                <Typography variant="h4" component="div" gutterBottom>
                  {stat.value}
                </Typography>
                
                <Typography
                  variant="body2"
                  sx={{
                    color: stat.changeType === 'positive' ? 'success.main' : 'error.main',
                  }}
                >
                  {stat.change} este mês
                </Typography>
              </CardContent>
            </Card>
        ))}
      </Box>

      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: {
            xs: '1fr',
            md: '1fr 1fr',
          },
          gap: 3,
        }}
      >
        {/* Quick Actions */}
        <Box>
          <Paper sx={{ p: 3, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Ações Rápidas
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="textSecondary">
                • Criar novo PCA
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                • Importar dados do PNCP
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                • Gerar relatório mensal
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                • Visualizar contratos vencendo
              </Typography>
            </Box>
          </Paper>
        </Box>

        {/* Recent Activity */}
        <Box>
          <Paper sx={{ p: 3, height: 300 }}>
            <Typography variant="h6" gutterBottom>
              Atividade Recente
            </Typography>
            <Box sx={{ mt: 2 }}>
              <Typography variant="body2" color="textSecondary">
                • PCA 2024/001 foi criado
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                • Contrato 2024/045 foi atualizado
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                • Usuário João Silva fez login
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                • Relatório mensal foi gerado
              </Typography>
            </Box>
          </Paper>
        </Box>
      </Box>
    </Container>
  );
};

export default Dashboard;