import React, { useState, useMemo } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Checkbox,
  IconButton,
  Toolbar,
  Typography,
  Tooltip,
  Chip,
  Skeleton,
  Alert,
} from '@mui/material';
import {
  Delete as DeleteIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  FileDownload as ExportIcon,
  FilterList as FilterIcon,
} from '@mui/icons-material';
import type { Column, SortConfig, PaginationConfig } from '../../types/app';
import { formatCurrency, formatDate, formatStatus } from '../../utils/formatters';
import { STATUS_COLORS } from '../../utils/constants';

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  loading?: boolean;
  error?: string | null;
  pagination?: PaginationConfig;
  onPaginationChange?: (pagination: PaginationConfig) => void;
  sortConfig?: SortConfig;
  onSortChange?: (sort: SortConfig) => void;
  onRowClick?: (row: T) => void;
  onEdit?: (row: T) => void;
  onDelete?: (row: T) => void;
  onView?: (row: T) => void;
  onExport?: () => void;
  onFilterOpen?: () => void;
  selectable?: boolean;
  selectedRows?: T[];
  onSelectionChange?: (selected: T[]) => void;
  emptyMessage?: string;
  title?: string;
  actions?: boolean;
  dense?: boolean;
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  error = null,
  pagination,
  onPaginationChange,
  sortConfig,
  onSortChange,
  onRowClick,
  onEdit,
  onDelete,
  onView,
  onExport,
  onFilterOpen,
  selectable = false,
  selectedRows = [],
  onSelectionChange,
  emptyMessage = 'Nenhum registro encontrado',
  title,
  actions = true,
  dense = false,
}: DataTableProps<T>) {
  const [selectedRowsState, setSelectedRowsState] = useState<T[]>(selectedRows);

  const isSelected = (row: T) => {
    return selectedRowsState.some((selectedRow) => 
      JSON.stringify(selectedRow) === JSON.stringify(row)
    );
  };

  const handleSelectAllClick = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.checked) {
      const newSelected = data;
      setSelectedRowsState(newSelected);
      onSelectionChange?.(newSelected);
    } else {
      setSelectedRowsState([]);
      onSelectionChange?.([]);
    }
  };

  const handleSelectClick = (row: T) => {
    const selectedIndex = selectedRowsState.findIndex(
      (selectedRow) => JSON.stringify(selectedRow) === JSON.stringify(row)
    );
    let newSelected: T[] = [];

    if (selectedIndex === -1) {
      newSelected = [...selectedRowsState, row];
    } else {
      newSelected = selectedRowsState.filter(
        (selectedRow) => JSON.stringify(selectedRow) !== JSON.stringify(row)
      );
    }

    setSelectedRowsState(newSelected);
    onSelectionChange?.(newSelected);
  };

  const handleSort = (column: Column<T>) => {
    if (!column.sortable || !onSortChange) return;

    const isAsc = sortConfig?.field === column.key && sortConfig?.direction === 'asc';
    onSortChange({
      field: column.key as string,
      direction: isAsc ? 'desc' : 'asc',
    });
  };

  const renderCellValue = (column: Column<T>, row: T) => {
    const value = row[column.key];

    if (column.render) {
      return column.render(value, row);
    }

    // Formatação automática baseada no tipo de valor
    if (value === null || value === undefined) {
      return '-';
    }

    if (typeof value === 'boolean') {
      return value ? 'Sim' : 'Não';
    }

    if (typeof value === 'number' && column.key.toString().includes('valor')) {
      return formatCurrency(value);
    }

    if (typeof value === 'string' && column.key.toString().includes('data')) {
      return formatDate(value);
    }

    if (typeof value === 'string' && 
        (column.key.toString().includes('status') || 
         column.key.toString().includes('situacao'))) {
      return (
        <Chip
          label={formatStatus(value)}
          color={STATUS_COLORS[value as keyof typeof STATUS_COLORS] as any}
          size="small"
        />
      );
    }

    return value;
  };

  const tableContent = useMemo(() => {
    if (loading) {
      return (
        <TableBody>
          {Array.from({ length: 5 }).map((_, index) => (
            <TableRow key={index}>
              {selectable && (
                <TableCell padding="checkbox">
                  <Skeleton variant="rectangular" width={20} height={20} />
                </TableCell>
              )}
              {columns.map((column) => (
                <TableCell key={column.key as string}>
                  <Skeleton variant="text" width="80%" />
                </TableCell>
              ))}
              {actions && (
                <TableCell>
                  <Skeleton variant="rectangular" width={100} height={30} />
                </TableCell>
              )}
            </TableRow>
          ))}
        </TableBody>
      );
    }

    if (error) {
      return (
        <TableBody>
          <TableRow>
            <TableCell colSpan={columns.length + (selectable ? 1 : 0) + (actions ? 1 : 0)}>
              <Alert severity="error">{error}</Alert>
            </TableCell>
          </TableRow>
        </TableBody>
      );
    }

    if (data.length === 0) {
      return (
        <TableBody>
          <TableRow>
            <TableCell 
              colSpan={columns.length + (selectable ? 1 : 0) + (actions ? 1 : 0)}
              align="center"
              sx={{ py: 4 }}
            >
              <Typography variant="body1" color="textSecondary">
                {emptyMessage}
              </Typography>
            </TableCell>
          </TableRow>
        </TableBody>
      );
    }

    return (
      <TableBody>
        {data.map((row, index) => {
          const isItemSelected = isSelected(row);
          
          return (
            <TableRow
              key={index}
              hover
              onClick={() => onRowClick?.(row)}
              selected={isItemSelected}
              sx={{ 
                cursor: onRowClick ? 'pointer' : 'default',
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
            >
              {selectable && (
                <TableCell padding="checkbox">
                  <Checkbox
                    checked={isItemSelected}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSelectClick(row);
                    }}
                  />
                </TableCell>
              )}
              
              {columns.map((column) => (
                <TableCell
                  key={column.key as string}
                  align={column.align || 'left'}
                  sx={{ width: column.width }}
                >
                  {renderCellValue(column, row)}
                </TableCell>
              ))}
              
              {actions && (
                <TableCell align="right">
                  <Box sx={{ display: 'flex', gap: 0.5 }}>
                    {onView && (
                      <Tooltip title="Visualizar">
                        <IconButton 
                          size="small" 
                          onClick={(e) => {
                            e.stopPropagation();
                            onView(row);
                          }}
                        >
                          <ViewIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    {onEdit && (
                      <Tooltip title="Editar">
                        <IconButton 
                          size="small" 
                          onClick={(e) => {
                            e.stopPropagation();
                            onEdit(row);
                          }}
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                    {onDelete && (
                      <Tooltip title="Excluir">
                        <IconButton 
                          size="small" 
                          color="error"
                          onClick={(e) => {
                            e.stopPropagation();
                            onDelete(row);
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    )}
                  </Box>
                </TableCell>
              )}
            </TableRow>
          );
        })}
      </TableBody>
    );
  }, [data, loading, error, columns, selectedRowsState, actions, selectable, onRowClick, onView, onEdit, onDelete, emptyMessage]);

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden' }}>
      {(title || onExport || onFilterOpen || selectedRowsState.length > 0) && (
        <Toolbar
          sx={{
            pl: { sm: 2 },
            pr: { xs: 1, sm: 1 },
            bgcolor: selectedRowsState.length > 0 ? 'action.selected' : 'inherit',
          }}
        >
          {selectedRowsState.length > 0 ? (
            <Typography
              sx={{ flex: '1 1 100%' }}
              color="inherit"
              variant="subtitle1"
              component="div"
            >
              {selectedRowsState.length} selecionado(s)
            </Typography>
          ) : (
            <Typography
              sx={{ flex: '1 1 100%' }}
              variant="h6"
              component="div"
            >
              {title}
            </Typography>
          )}

          <Box sx={{ display: 'flex', gap: 1 }}>
            {onFilterOpen && (
              <Tooltip title="Filtros">
                <IconButton onClick={onFilterOpen}>
                  <FilterIcon />
                </IconButton>
              </Tooltip>
            )}
            {onExport && (
              <Tooltip title="Exportar">
                <IconButton onClick={onExport}>
                  <ExportIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        </Toolbar>
      )}

      <TableContainer>
        <Table size={dense ? 'small' : 'medium'} stickyHeader>
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={
                      selectedRowsState.length > 0 && selectedRowsState.length < data.length
                    }
                    checked={data.length > 0 && selectedRowsState.length === data.length}
                    onChange={handleSelectAllClick}
                  />
                </TableCell>
              )}
              
              {columns.map((column) => (
                <TableCell
                  key={column.key as string}
                  align={column.align || 'left'}
                  sx={{ width: column.width }}
                >
                  {column.sortable ? (
                    <TableSortLabel
                      active={sortConfig?.field === column.key}
                      direction={
                        sortConfig?.field === column.key 
                          ? sortConfig.direction 
                          : 'asc'
                      }
                      onClick={() => handleSort(column)}
                    >
                      {column.label}
                    </TableSortLabel>
                  ) : (
                    column.label
                  )}
                </TableCell>
              ))}
              
              {actions && (
                <TableCell align="right">
                  Ações
                </TableCell>
              )}
            </TableRow>
          </TableHead>
          
          {tableContent}
        </Table>
      </TableContainer>

      {pagination && onPaginationChange && (
        <TablePagination
          rowsPerPageOptions={[10, 25, 50, 100]}
          component="div"
          count={pagination.page * pagination.size + data.length}
          rowsPerPage={pagination.size}
          page={pagination.page}
          onPageChange={(_, newPage) => {
            onPaginationChange({ ...pagination, page: newPage });
          }}
          onRowsPerPageChange={(event) => {
            onPaginationChange({
              ...pagination,
              size: parseInt(event.target.value, 10),
              page: 0,
            });
          }}
          labelRowsPerPage="Itens por página:"
          labelDisplayedRows={({ from, to, count }) => 
            `${from}-${to} de ${count !== -1 ? count : `mais de ${to}`}`
          }
        />
      )}
    </Paper>
  );
}

export default DataTable;