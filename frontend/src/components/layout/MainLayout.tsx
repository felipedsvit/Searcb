import React, { useState } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Collapse,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Description as DescriptionIcon,
  Assignment as AssignmentIcon,
  Article as ArticleIcon,
  People as PeopleIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  AccountCircle as AccountCircleIcon,
  Logout as LogoutIcon,
  Notifications as NotificationsIcon,
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ExpandLess,
  ExpandMore,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { usePermissions } from '../../stores/authStore';
import { useUIStore } from '../../stores/uiStore';
import { ROUTES, ROLES } from '../../utils/constants';
import { formatInitials } from '../../utils/formatters';

const DRAWER_WIDTH = 280;
const DRAWER_WIDTH_COLLAPSED = 64;

interface MenuItem {
  id: string;
  label: string;
  icon: React.ReactNode;
  path?: string;
  roles?: string[];
  children?: MenuItem[];
}

const menuItems: MenuItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: <DashboardIcon />,
    path: ROUTES.DASHBOARD,
  },
  {
    id: 'pcas',
    label: 'PCAs',
    icon: <DescriptionIcon />,
    path: ROUTES.PCAS,
  },
  {
    id: 'contratacoes',
    label: 'Contratações',
    icon: <AssignmentIcon />,
    path: ROUTES.CONTRATACOES,
  },
  {
    id: 'contratos',
    label: 'Contratos',
    icon: <ArticleIcon />,
    path: ROUTES.CONTRATOS,
  },
  {
    id: 'atas',
    label: 'Atas de Registro',
    icon: <ArticleIcon />,
    path: ROUTES.ATAS,
  },
  {
    id: 'relatorios',
    label: 'Relatórios',
    icon: <AssessmentIcon />,
    path: ROUTES.RELATORIOS,
    roles: [ROLES.ADMIN, ROLES.GESTOR],
  },
  {
    id: 'usuarios',
    label: 'Usuários',
    icon: <PeopleIcon />,
    path: ROUTES.USUARIOS,
    roles: [ROLES.ADMIN],
  },
  {
    id: 'configuracoes',
    label: 'Configurações',
    icon: <SettingsIcon />,
    path: ROUTES.CONFIGURACOES,
    roles: [ROLES.ADMIN],
  },
];

export const MainLayout: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { canAccess } = usePermissions();
  
  const {
    sidebarOpen,
    sidebarCollapsed,
    setSidebarOpen,
    setSidebarCollapsed,
  } = useUIStore();

  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [expandedItems, setExpandedItems] = useState<string[]>([]);

  const handleDrawerToggle = () => {
    if (isMobile) {
      setSidebarOpen(!sidebarOpen);
    } else {
      setSidebarCollapsed(!sidebarCollapsed);
    }
  };

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    handleProfileMenuClose();
    logout();
  };

  const handleMenuItemClick = (item: MenuItem) => {
    if (item.path) {
      navigate(item.path);
    }
    
    if (item.children) {
      toggleExpanded(item.id);
    }

    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  const toggleExpanded = (itemId: string) => {
    setExpandedItems(prev => 
      prev.includes(itemId)
        ? prev.filter(id => id !== itemId)
        : [...prev, itemId]
    );
  };

  const renderMenuItem = (item: MenuItem, level = 0) => {
    if (item.roles && !canAccess(item.roles)) {
      return null;
    }

    const isExpanded = expandedItems.includes(item.id);
    const hasChildren = item.children && item.children.length > 0;

    return (
      <React.Fragment key={item.id}>
        <ListItem disablePadding>
          <ListItemButton
            onClick={() => handleMenuItemClick(item)}
            sx={{
              minHeight: 48,
              pl: level * 2 + 2,
              pr: 2,
              '&.Mui-selected': {
                backgroundColor: 'primary.main',
                color: 'primary.contrastText',
                '& .MuiListItemIcon-root': {
                  color: 'primary.contrastText',
                },
              },
            }}
          >
            <ListItemIcon
              sx={{
                minWidth: sidebarCollapsed ? 0 : 40,
                justifyContent: 'center',
                color: 'inherit',
              }}
            >
              {item.icon}
            </ListItemIcon>
            
            {!sidebarCollapsed && (
              <>
                <ListItemText 
                  primary={item.label}
                  sx={{ opacity: sidebarCollapsed ? 0 : 1 }}
                />
                {hasChildren && (
                  isExpanded ? <ExpandLess /> : <ExpandMore />
                )}
              </>
            )}
          </ListItemButton>
        </ListItem>

        {hasChildren && !sidebarCollapsed && (
          <Collapse in={isExpanded} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children!.map(child => renderMenuItem(child, level + 1))}
            </List>
          </Collapse>
        )}
      </React.Fragment>
    );
  };

  const drawer = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Toolbar
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: sidebarCollapsed ? 'center' : 'space-between',
          px: 2,
          minHeight: '64px !important',
        }}
      >
        {!sidebarCollapsed && (
          <Typography variant="h6" noWrap component="div" color="primary">
            SEARCB
          </Typography>
        )}
        
        {!isMobile && (
          <IconButton
            onClick={handleDrawerToggle}
            size="small"
            sx={{ color: 'primary.main' }}
          >
            {sidebarCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
          </IconButton>
        )}
      </Toolbar>
      
      <Divider />
      
      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List>
          {menuItems.map(item => renderMenuItem(item))}
        </List>
      </Box>
      
      <Divider />
      
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            p: 1,
            borderRadius: 1,
            bgcolor: 'grey.50',
          }}
        >
          <Avatar
            sx={{
              width: sidebarCollapsed ? 32 : 40,
              height: sidebarCollapsed ? 32 : 40,
              bgcolor: 'primary.main',
              fontSize: '0.875rem',
            }}
          >
            {user ? formatInitials(user.nome) : 'U'}
          </Avatar>
          
          {!sidebarCollapsed && (
            <Box sx={{ flex: 1, minWidth: 0 }}>
              <Typography variant="subtitle2" noWrap>
                {user?.nome}
              </Typography>
              <Typography variant="caption" color="textSecondary" noWrap>
                {user?.perfil}
              </Typography>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: {
            md: sidebarCollapsed 
              ? `calc(100% - ${DRAWER_WIDTH_COLLAPSED}px)`
              : `calc(100% - ${DRAWER_WIDTH}px)`,
          },
          ml: {
            md: sidebarCollapsed ? `${DRAWER_WIDTH_COLLAPSED}px` : `${DRAWER_WIDTH}px`,
          },
          transition: theme.transitions.create(['width', 'margin'], {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Sistema de Contratações
          </Typography>
          
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit">
              <Badge badgeContent={3} color="error">
                <NotificationsIcon />
              </Badge>
            </IconButton>
            
            <IconButton
              size="large"
              edge="end"
              aria-label="account of current user"
              aria-controls="primary-search-account-menu"
              aria-haspopup="true"
              onClick={handleProfileMenuOpen}
              color="inherit"
            >
              <AccountCircleIcon />
            </IconButton>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{
          width: { md: sidebarCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH },
          flexShrink: { md: 0 },
        }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={sidebarOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: DRAWER_WIDTH,
            },
          }}
        >
          {drawer}
        </Drawer>
        
        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': {
              boxSizing: 'border-box',
              width: sidebarCollapsed ? DRAWER_WIDTH_COLLAPSED : DRAWER_WIDTH,
              transition: theme.transitions.create('width', {
                easing: theme.transitions.easing.sharp,
                duration: theme.transitions.duration.enteringScreen,
              }),
              overflowX: 'hidden',
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: {
            md: sidebarCollapsed 
              ? `calc(100% - ${DRAWER_WIDTH_COLLAPSED}px)`
              : `calc(100% - ${DRAWER_WIDTH}px)`,
          },
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.leavingScreen,
          }),
        }}
      >
        <Toolbar />
        <Outlet />
      </Box>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        id="primary-search-account-menu"
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorEl)}
        onClose={handleProfileMenuClose}
      >
        <MenuItem onClick={() => {
          handleProfileMenuClose();
          navigate(ROUTES.PERFIL);
        }}>
          <ListItemIcon>
            <AccountCircleIcon fontSize="small" />
          </ListItemIcon>
          Meu Perfil
        </MenuItem>
        
        <MenuItem onClick={() => {
          handleProfileMenuClose();
          navigate(ROUTES.CONFIGURACOES);
        }}>
          <ListItemIcon>
            <SettingsIcon fontSize="small" />
          </ListItemIcon>
          Configurações
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={handleLogout}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          Sair
        </MenuItem>
      </Menu>
    </Box>
  );
};

export default MainLayout;